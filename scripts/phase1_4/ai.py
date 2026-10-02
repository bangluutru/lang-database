"""
scripts/phase1_4/ai.py
Batch-oriented AI client for Phase 1.4 with PER-ITEM persistent caching.

Guarantees
  * Every item result is cached on disk (sharded as one JSON file per API call) keyed by
    sha256(role, model, prompt_version, item_payload) -> no item is ever sent twice.
  * Shards store the model, prompt version, the exact item inputs and raw outputs, so every AI
    artifact is reconstructible (model / input / output / time).
  * Offline rebuild: with a complete cache, `call_items(..., offline=True)` performs zero
    network calls and raises if an item is missing.
  * Roles use DIFFERENT models: generator = gemini-2.5-flash, judge = gemini-2.5-pro
    (model-level independence, an improvement over Phase 1.3D where both were flash).
"""

import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_3d.ai_client import TokenManager, clean_json_response, PROJECT_ID
from scripts.phase1_4.common import AI_CACHE_DIR
from scripts.external_api_guard import require_external_api_permission

MODELS = {
    "generator": {"model": "gemini-2.5-flash", "location": "us-central1", "max_tokens": 8192, "thinking": 0},
    "judge": {"model": "gemini-2.5-pro", "location": "us-central1", "max_tokens": 24000, "thinking": None},
}


def item_key(role: str, model: str, prompt_version: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps({"role": role, "model": model, "pv": prompt_version, "in": payload},
                     sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class BatchAI:
    def __init__(self, role: str, subdir: str):
        self.role = role
        self.cfg = MODELS[role]
        self.dir = AI_CACHE_DIR / subdir
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.index: Dict[str, Dict[str, Any]] = {}
        self.calls = 0
        self.token = TokenManager.get_instance()
        self._load()

    def _load(self):
        for p in sorted(self.dir.glob("shard-*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            for it in d["items"]:
                self.index[it["key"]] = {"output": it["output"], "shard": p.name, "model": d["model"],
                                         "prompt_version": d["prompt_version"], "created_at": d["created_at"],
                                         "input": it["input"]}

    def _endpoint(self) -> str:
        loc = self.cfg["location"]
        host = "aiplatform.googleapis.com" if loc == "global" else f"{loc}-aiplatform.googleapis.com"
        return (f"https://{host}/v1/projects/{PROJECT_ID}/locations/{loc}/publishers/google/models/"
                f"{self.cfg['model']}:generateContent")

    def _post(self, prompt: str) -> str:
        require_external_api_permission(f"Vertex AI call ({self.cfg['model']})")
        gen = {"temperature": 0.0, "topP": 0.95, "maxOutputTokens": self.cfg["max_tokens"],
               "responseMimeType": "application/json"}
        if self.cfg["thinking"] is not None:
            gen["thinkingConfig"] = {"thinkingBudget": self.cfg["thinking"]}
        body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": gen}
        delay = 2.0
        last = None
        for attempt in range(6):
            try:
                r = requests.post(self._endpoint(), headers={"Authorization": f"Bearer {self.token.get_token()}",
                                                             "Content-Type": "application/json"}, json=body, timeout=240)
                if r.status_code == 200:
                    cand = r.json().get("candidates", [])
                    if cand and cand[0].get("content", {}).get("parts"):
                        return "".join(p.get("text", "") for p in cand[0]["content"]["parts"])
                    last = f"empty candidate: {str(r.json())[:200]}"
                elif r.status_code == 401:
                    self.token.force_refresh()
                    last = "401"
                elif r.status_code in (429, 500, 503, 504):
                    last = f"HTTP {r.status_code}"
                else:
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
            except requests.RequestException as e:
                last = str(e)
            time.sleep(delay)
            delay = min(delay * 2, 60)
        raise RuntimeError(f"AI call failed after retries: {last}")

    def call_items(self, items: List[Dict[str, Any]], prompt_version: str,
                   build_prompt: Callable[[List[Dict[str, Any]]], str], batch_size: int = 12,
                   workers: int = 6, offline: bool = False, progress: bool = True) -> Dict[str, Dict[str, Any]]:
        """items: list of dicts each with a unique 'id' plus payload fields. The model must return
        {"results":[{"id":..., ...}]}. Returns {item_id: output_dict}. Cached per item."""
        model = self.cfg["model"]
        keyed = []
        for it in items:
            payload = {k: v for k, v in it.items()}
            keyed.append((item_key(self.role, model, prompt_version, payload), it))
        out: Dict[str, Dict[str, Any]] = {}
        todo = []
        for k, it in keyed:
            if k in self.index:
                out[it["id"]] = self.index[k]["output"]
            else:
                todo.append((k, it))
        if not todo:
            return out
        if offline:
            raise RuntimeError(f"{len(todo)} uncached items in offline mode (role={self.role})")
        chunks = [todo[i:i + batch_size] for i in range(0, len(todo), batch_size)]
        done = 0

        def run(chunk):
            batch_items = [it for _, it in chunk]
            prompt = build_prompt(batch_items)
            raw = self._post(prompt)
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = clean_json_response(raw)
            rows = parsed if isinstance(parsed, list) else (parsed.get("results") or parsed.get("items") or [])
            results = {str(r.get("id")): r for r in rows if isinstance(r, dict)}
            shard_items = []
            for k, it in chunk:
                r = results.get(str(it["id"]))
                if r is None:
                    continue
                shard_items.append({"key": k, "input": it, "output": r})
            if shard_items:
                sh = hashlib.sha256("".join(s["key"] for s in shard_items).encode()).hexdigest()[:16]
                rec = {"role": self.role, "model": model, "prompt_version": prompt_version,
                       "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       "items": shard_items}
                (self.dir / f"shard-{sh}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            return shard_items

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(run, c) for c in chunks]
            for f in as_completed(futs):
                try:
                    res = f.result()
                except Exception as e:
                    print(f"[ai:{self.role}] batch failed: {e}", flush=True)
                    continue
                with self._lock:
                    self.calls += 1
                    for s in res:
                        self.index[s["key"]] = {"output": s["output"], "model": model, "prompt_version": prompt_version,
                                                "input": s["input"], "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                        out[s["input"]["id"]] = s["output"]
                    done += 1
                    if progress and done % 10 == 0:
                        print(f"[ai:{self.role}] {done}/{len(chunks)} batches", flush=True)
        return out


    def provenance(self, role_items: List[Dict[str, Any]], prompt_version: str) -> Dict[str, Dict[str, Any]]:
        """item id -> {input_hash, created_at, model, prompt_version} for already-cached items."""
        out = {}
        for it in role_items:
            k = item_key(self.role, self.cfg["model"], prompt_version, it)
            rec = self.index.get(k)
            if rec:
                out[it["id"]] = {"input_hash": k, "created_at": rec.get("created_at"), "model": rec["model"],
                                 "prompt_version": rec["prompt_version"]}
        return out

    def lookup(self, items: List[Dict[str, Any]], prompt_version: str) -> Dict[str, Dict[str, Any]]:
        """Cache-only read (never calls the network)."""
        out = {}
        for it in items:
            rec = self.index.get(item_key(self.role, self.cfg["model"], prompt_version, it))
            if rec:
                out[it["id"]] = rec["output"]
        return out
