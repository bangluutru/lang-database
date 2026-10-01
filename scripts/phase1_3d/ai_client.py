#!/usr/bin/env python3
"""
scripts/phase1_3d/ai_client.py
Unified, thread-safe AI Client for Phase 1.3D with persistent SHA-256 caching.
Supports Vertex AI (OAuth2 Bearer token via gcloud) and Gemini REST API.
Guarantees:
- Persistent disk caching by (input_hash, model, prompt_version)
- Zero repeat API calls for previously cached prompts
- Thread-safe token acquisition and caching
"""

import os
import sys
import json
import time
import hashlib
import re
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional

import requests

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROJECT_ID = "gen-lang-client-0626407458"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-flash"
VERTEX_ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_NAME}:generateContent"


class TokenManager:
    """Thread-safe OAuth2 Bearer token manager using gcloud."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._token: Optional[str] = None
        self._expires_at: float = 0.0

    @classmethod
    def get_instance(cls) -> "TokenManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = TokenManager()
            return cls._instance

    def get_token(self) -> str:
        with self._lock:
            now = time.time()
            if not self._token or now >= self._expires_at:
                try:
                    res = subprocess.run(
                        ["gcloud", "auth", "print-access-token"],
                        capture_output=True, text=True, check=True, timeout=20
                    )
                    self._token = res.stdout.strip()
                    self._expires_at = now + 1800.0  # 30 min refresh window
                except Exception as e:
                    if self._token:
                        return self._token
                    raise RuntimeError(f"Failed to obtain gcloud OAuth2 token: {e}")
            return self._token

    def force_refresh(self) -> str:
        with self._lock:
            try:
                res = subprocess.run(
                    ["gcloud", "auth", "print-access-token"],
                    capture_output=True, text=True, check=True, timeout=20
                )
                self._token = res.stdout.strip()
                self._expires_at = time.time() + 1800.0
                return self._token
            except Exception as e:
                raise RuntimeError(f"Failed to force refresh gcloud OAuth2 token: {e}")


def compute_input_hash(data: Any) -> str:
    """Computes deterministic SHA-256 hash of structured input data."""
    if isinstance(data, (dict, list)):
        payload_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    else:
        payload_bytes = str(data).encode("utf-8")
    return hashlib.sha256(payload_bytes).hexdigest()


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Strips code fences and parses JSON with robust error repair."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        candidate = m.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # Remove trailing commas
        repaired = re.sub(r',\s*([}\]])', r'\1', candidate)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse LLM response as JSON: {raw_text[:200]}...")


class AIClient:
    """Executes calls to Gemini 2.5 Flash with persistent caching."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = MODEL_NAME
        self.token_manager = TokenManager.get_instance()
        self._cache_lock = threading.Lock()

    def get_cached(self, input_hash: str) -> Optional[Dict[str, Any]]:
        cache_file = self.cache_dir / f"{input_hash}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def save_cache(self, input_hash: str, record: Dict[str, Any]) -> None:
        cache_file = self.cache_dir / f"{input_hash}.json"
        with self._cache_lock:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)

    def generate_json(self, prompt: str, input_payload: Any, prompt_version: str, max_retries: int = 4) -> Dict[str, Any]:
        """Calls Gemini and returns parsed JSON. Uses cache if available."""
        input_hash = compute_input_hash({"prompt_version": prompt_version, "input": input_payload})
        cached = self.get_cached(input_hash)
        if cached:
            return cached["output"]

        # Call Gemini via Vertex AI
        delay = 1.0
        for attempt in range(max_retries):
            try:
                token = self.token_manager.get_token()
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "topP": 0.95,
                        "maxOutputTokens": 4096,
                        "responseMimeType": "application/json"
                    }
                }
                resp = requests.post(VERTEX_ENDPOINT, headers=headers, json=payload, timeout=40)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "")
                            parsed_output = clean_json_response(raw_text)
                            cache_record = {
                                "input_hash": input_hash,
                                "model": self.model,
                                "prompt_version": prompt_version,
                                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "input": input_payload,
                                "output": parsed_output
                            }
                            self.save_cache(input_hash, cache_record)
                            return parsed_output
                    raise ValueError(f"Empty candidate in Vertex AI response: {data}")
                elif resp.status_code == 401:
                    print("[AIClient] Token expired (401), force-refreshing OAuth2 token...", flush=True)
                    self.token_manager.force_refresh()
                    time.sleep(1.0)
                    continue
                elif resp.status_code in (429, 500, 503):
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise RuntimeError(f"Vertex AI HTTP {resp.status_code}: {resp.text}")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

        raise RuntimeError("Vertex AI call failed after retries.")
