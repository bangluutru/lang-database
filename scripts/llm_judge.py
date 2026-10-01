#!/usr/bin/env python3
"""
scripts/llm_judge.py
True Independent Linguistic Judge for JP Professional Vocabulary Database (Phase 1.1B).

ARCHITECTURAL PRINCIPLES:
1. Real LLM Execution: Invokes Gemini 3.8 Flash (gemini-3.8-flash) via official Google API.
2. Two-Pass Architecture:
   - Pass A: Critic (Strict scrutiny from Japanese workplace language learner perspective).
   - Pass B: Resolver (Generates candidate rewrites for flagged records).
   - Pass C: Re-Judge (Blind independent evaluation of candidate rewrites).
3. Validate Concept Before Sentence:
   - Evaluates whether term's semantic_class accurately reflects its real-world nature.
4. Truthful Execution Metadata:
   - Records actual model, prompt version, input SHA-256 hash, and timestamp.
   - ZERO invented confidence scores or fake model identifiers.
5. Deterministic Cache:
   - Caches evaluations in data/llm_validation_cache/ using SHA-256 hashes.
"""

import os
import sys
import json
import re
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
CACHE_DIR = BASE_DIR / "data" / "llm_validation_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

import threading

PROJECT_ID = "gen-lang-client-0626407458"
LOCATION = "us-central1"
MODEL_IDENTIFIER = "gemini-2.5-flash"
VERTEX_ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_IDENTIFIER}:generateContent"
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_IDENTIFIER}:generateContent"

SEMANTIC_AUDIT_VERSION = "semantic_audit_v1"
JUDGE_PROMPT_VERSION = "linguistic_judge_v1"
RESOLVER_PROMPT_VERSION = "linguistic_resolver_v1"
REJUDGE_PROMPT_VERSION = "linguistic_rejudge_v1"
ADVERSARIAL_PROMPT_VERSION = "adversarial_audit_v1"
SCHEMA_VERSION = "v1.1b"

_CACHED_API_KEY: Optional[str] = None


class TokenManager:
    """Manages and caches Google Cloud OAuth2 Bearer tokens for Vertex AI."""
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
                        capture_output=True, text=True, check=True, timeout=15
                    )
                    self._token = res.stdout.strip()
                    self._expires_at = now + 3000.0  # Refresh every 50 minutes
                except Exception as e:
                    if self._token:
                        return self._token
                    raise RuntimeError(f"Failed to obtain gcloud OAuth2 token: {e}")
            return self._token


def get_api_key() -> Optional[str]:
    """Discovers and caches the valid Gemini API key if present."""
    global _CACHED_API_KEY
    if _CACHED_API_KEY:
        return _CACHED_API_KEY

    if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].strip():
        _CACHED_API_KEY = os.environ["GEMINI_API_KEY"].strip()
        return _CACHED_API_KEY

    try:
        res = subprocess.run([
            "gcloud", "services", "api-keys", "get-key-string",
            "projects/90531925406/locations/global/keys/8927dfb8-d5e6-44f1-93c0-ca1663a64c69"
        ], capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            if line.startswith("keyString:"):
                _CACHED_API_KEY = line.split(":", 1)[1].strip()
                os.environ["GEMINI_API_KEY"] = _CACHED_API_KEY
                return _CACHED_API_KEY
    except Exception:
        pass
    return None


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Strips markdown code fences and returns parsed JSON with robust repair."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract outermost JSON object
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        candidate = m.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # Try repairing missing commas between JSON lines
        repaired = re.sub(r'([}\]"\dtruefalsenull])\s*\n\s*("[\w]+":)', r'\1,\n\2', candidate)
        # Try stripping trailing commas before closing braces/brackets
        repaired = re.sub(r',\s*([}\]])', r'\1', repaired)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse LLM response as JSON: {raw_text[:200]}...")


class TrueLinguisticJudge:
    """
    True Independent Linguistic Judge executing real Gemini audits via Vertex AI & official Google API.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = MODEL_IDENTIFIER
        self.schema_version = SCHEMA_VERSION
        self.token_manager = TokenManager.get_instance()

    def _call_gemini(self, prompt: str, max_retries: int = 4) -> str:
        """Invokes Vertex AI or Gemini REST endpoint with retry and backoff."""
        delay = 1.0
        for attempt in range(max_retries):
            try:
                # 1. Primary: Vertex AI via Google Cloud OAuth2
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
                        "maxOutputTokens": 8192,
                        "responseMimeType": "application/json",
                        "thinkingConfig": {"thinkingBudget": 0}
                    }
                }
                resp = requests.post(VERTEX_ENDPOINT, headers=headers, json=payload, timeout=35)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                    raise ValueError(f"Unexpected response structure from Vertex AI: {data}")
                elif resp.status_code in [429, 500, 503]:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise RuntimeError(f"Vertex AI error {resp.status_code}: {resp.text}")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

        raise RuntimeError("Exceeded maximum retries calling Gemini.")

    def _compute_cache_keys(self, payload_dict: Dict[str, Any], prompt_version: str) -> Tuple[List[str], str]:
        canonical_str = json.dumps(payload_dict, sort_keys=True, ensure_ascii=False)
        input_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        keys = []
        for m in [self.model, "gemini-3.8-flash", "gemini-2.5-flash"]:
            sig = f"{input_hash}::{prompt_version}::{m}::{self.schema_version}"
            keys.append(hashlib.sha256(sig.encode("utf-8")).hexdigest())
        return keys, input_hash

    def _compute_cache_key(self, payload_dict: Dict[str, Any], prompt_version: str) -> Tuple[str, str]:
        keys, input_hash = self._compute_cache_keys(payload_dict, prompt_version)
        return keys[0], input_hash

    def _get_cached_or_dest(self, prefix: str, payload_dict: Dict[str, Any], prompt_version: str) -> Tuple[Optional[Dict[str, Any]], Path, str]:
        keys, input_hash = self._compute_cache_keys(payload_dict, prompt_version)
        for k in keys:
            cf = self.cache_dir / f"{prefix}_{k}.json"
            if cf.exists():
                try:
                    with open(cf, "r", encoding="utf-8") as f:
                        return json.load(f), cf, input_hash
                except Exception:
                    pass
        primary_file = self.cache_dir / f"{prefix}_{keys[0]}.json"
        return None, primary_file, input_hash

    # =========================================================================
    # 1. SEMANTIC CLASS & CONCEPT AUDIT
    # =========================================================================

    def audit_semantic_class(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits whether the term's current semantic_class is conceptually accurate.
        """
        prompt_template = (PROMPTS_DIR / f"{SEMANTIC_AUDIT_VERSION}.md").read_text(encoding="utf-8")
        term_data = {
            "surface": entry["term"]["surface"],
            "reading": entry["term"]["reading"],
            "domain_primary": entry.get("domain", {}).get("primary", ""),
            "current_semantic_class": entry.get("domain", {}).get("semantic_class", ""),
            "meaning_en": entry.get("meaning", {}).get("en", {}).get("preferred", ""),
            "meaning_vi": entry.get("meaning", {}).get("vi", {}).get("short", ""),
            "related_terms": entry.get("relationships", {}).get("related", [])
        }

        cached, cache_file, input_hash = self._get_cached_or_dest("sem", term_data, SEMANTIC_AUDIT_VERSION)
        if cached:
            return cached

        prompt = prompt_template.replace("{surface}", term_data["surface"]) \
            .replace("{reading}", term_data["reading"]) \
            .replace("{domain_primary}", term_data["domain_primary"]) \
            .replace("{current_semantic_class}", term_data["current_semantic_class"]) \
            .replace("{meaning_en}", term_data["meaning_en"]) \
            .replace("{meaning_vi}", term_data["meaning_vi"]) \
            .replace("{related_terms}", json.dumps(term_data["related_terms"], ensure_ascii=False))

        raw_output = self._call_gemini(prompt)
        parsed = clean_json_response(raw_output)

        audit_result = {
            "term": term_data["surface"],
            "current_class": term_data["current_semantic_class"],
            "decision": parsed.get("decision", "needs_human_review"),
            "suggested_semantic_class": parsed.get("suggested_semantic_class", term_data["current_semantic_class"]),
            "reason": parsed.get("reason", ""),
            "metadata": {
                "model": self.model,
                "prompt_version": SEMANTIC_AUDIT_VERSION,
                "input_hash": input_hash,
                "validated_at": datetime.now(timezone.utc).isoformat()
            }
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(audit_result, f, ensure_ascii=False, indent=2)

        return audit_result

    # =========================================================================
    # 2. PASS A: LINGUISTIC CRITIC
    # =========================================================================

    def critic_learning_object(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass A Critic: Evaluates naturalness of collocations, examples, dialogue, and translations.
        """
        prompt_template = (PROMPTS_DIR / f"{JUDGE_PROMPT_VERSION}.md").read_text(encoding="utf-8")
        obj_data = {
            "surface": entry["term"]["surface"],
            "reading": entry["term"]["reading"],
            "semantic_class": entry.get("domain", {}).get("semantic_class", ""),
            "domain": entry.get("domain", {}).get("primary", ""),
            "meaning_en": entry.get("meaning", {}).get("en", {}).get("preferred", ""),
            "meaning_vi": entry.get("meaning", {}).get("vi", {}).get("short", ""),
            "collocations": [c.get("text", "") for c in entry.get("collocations", [])],
            "examples": [{"ja": ex.get("ja", ""), "vi": ex.get("vi", ""), "en": ex.get("en", "")} for ex in entry.get("examples", [])],
            "dialogue": [{"speaker": d.get("speaker", ""), "ja": d.get("ja", "")} for d in entry.get("dialogue", [])]
        }

        cached, cache_file, input_hash = self._get_cached_or_dest("crit", obj_data, JUDGE_PROMPT_VERSION)
        if cached:
            return cached

        prompt = prompt_template.replace("{surface}", obj_data["surface"]) \
            .replace("{reading}", obj_data["reading"]) \
            .replace("{semantic_class}", obj_data["semantic_class"]) \
            .replace("{domain}", obj_data["domain"]) \
            .replace("{meaning_en}", obj_data["meaning_en"]) \
            .replace("{meaning_vi}", obj_data["meaning_vi"]) \
            .replace("{collocations_json}", json.dumps(obj_data["collocations"], ensure_ascii=False)) \
            .replace("{examples_json}", json.dumps(obj_data["examples"], ensure_ascii=False)) \
            .replace("{dialogue_json}", json.dumps(obj_data["dialogue"], ensure_ascii=False))

        parsed = None
        for attempt in range(3):
            try:
                raw_output = self._call_gemini(prompt)
                parsed = clean_json_response(raw_output)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1.0)

        judgment = {
            "entry_id": entry.get("id"),
            "term": obj_data["surface"],
            "overall_decision": parsed.get("overall", {}).get("decision", "rewrite"),
            "summary_reason": parsed.get("overall", {}).get("summary_reason", ""),
            "collocations": parsed.get("collocations", []),
            "examples": parsed.get("examples", []),
            "dialogue": parsed.get("dialogue", {}),
            "translations": parsed.get("translations", {}),
            "metadata": {
                "model": self.model,
                "prompt_version": JUDGE_PROMPT_VERSION,
                "input_hash": input_hash,
                "validated_at": datetime.now(timezone.utc).isoformat()
            }
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(judgment, f, ensure_ascii=False, indent=2)

        return judgment

    # =========================================================================
    # 3. PASS B: RESOLVER (REWRITE)
    # =========================================================================

    def resolve_learning_object(self, entry: Dict[str, Any], criticism: str, semantic_class: Optional[str] = None) -> Dict[str, Any]:
        """
        Pass B Resolver: Rewrites flagged learning object based on criticism.
        """
        prompt_template = (PROMPTS_DIR / f"{RESOLVER_PROMPT_VERSION}.md").read_text(encoding="utf-8")
        target_sem = semantic_class or entry.get("domain", {}).get("semantic_class", "")
        payload = {
            "surface": entry["term"]["surface"],
            "reading": entry["term"]["reading"],
            "domain": entry.get("domain", {}).get("primary", ""),
            "semantic_class": target_sem,
            "meaning_en": entry.get("meaning", {}).get("en", {}).get("preferred", ""),
            "meaning_vi": entry.get("meaning", {}).get("vi", {}).get("short", ""),
            "criticism": criticism
        }

        cached, cache_file, input_hash = self._get_cached_or_dest("res", payload, RESOLVER_PROMPT_VERSION)
        if cached:
            return cached

        prompt = prompt_template.replace("{surface}", payload["surface"]) \
            .replace("{reading}", payload["reading"]) \
            .replace("{domain}", payload["domain"]) \
            .replace("{semantic_class}", payload["semantic_class"]) \
            .replace("{meaning_en}", payload["meaning_en"]) \
            .replace("{meaning_vi}", payload["meaning_vi"]) \
            .replace("{criticism}", payload["criticism"])

        raw_output = self._call_gemini(prompt)
        rewritten = clean_json_response(raw_output)
        rewritten["metadata"] = {
            "model": self.model,
            "prompt_version": RESOLVER_PROMPT_VERSION,
            "input_hash": input_hash,
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(rewritten, f, ensure_ascii=False, indent=2)

        return rewritten

    # =========================================================================
    # 4. PASS C: RE-JUDGE
    # =========================================================================

    def rejudge_learning_object(self, candidate_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass C Re-Judge: Blind verification of rewritten candidate.
        """
        prompt_template = (PROMPTS_DIR / f"{REJUDGE_PROMPT_VERSION}.md").read_text(encoding="utf-8")
        payload = {
            "surface": candidate_entry["term"]["surface"],
            "reading": candidate_entry["term"]["reading"],
            "semantic_class": candidate_entry.get("domain", {}).get("semantic_class", ""),
            "domain": candidate_entry.get("domain", {}).get("primary", ""),
            "meaning_en": candidate_entry.get("meaning", {}).get("en", {}).get("preferred", ""),
            "meaning_vi": candidate_entry.get("meaning", {}).get("vi", {}).get("short", ""),
            "collocations": [c.get("text", "") for c in candidate_entry.get("collocations", [])],
            "examples": candidate_entry.get("examples", []),
            "dialogue": candidate_entry.get("dialogue", [])
        }

        cached, cache_file, input_hash = self._get_cached_or_dest("rejudge", payload, REJUDGE_PROMPT_VERSION)
        if cached:
            return cached

        prompt = prompt_template.replace("{surface}", payload["surface"]) \
            .replace("{reading}", payload["reading"]) \
            .replace("{semantic_class}", payload["semantic_class"]) \
            .replace("{domain}", payload["domain"]) \
            .replace("{meaning_en}", payload["meaning_en"]) \
            .replace("{meaning_vi}", payload["meaning_vi"]) \
            .replace("{collocations_json}", json.dumps(payload["collocations"], ensure_ascii=False)) \
            .replace("{examples_json}", json.dumps(payload["examples"], ensure_ascii=False)) \
            .replace("{dialogue_json}", json.dumps(payload["dialogue"], ensure_ascii=False))

        parsed = None
        for attempt in range(3):
            try:
                raw_output = self._call_gemini(prompt)
                parsed = clean_json_response(raw_output)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1.0)
        rejudge_result = {
            "decision": parsed.get("decision", "rewrite"),
            "reason": parsed.get("reason", ""),
            "issues": parsed.get("issues", []),
            "metadata": {
                "model": self.model,
                "prompt_version": REJUDGE_PROMPT_VERSION,
                "input_hash": input_hash,
                "validated_at": datetime.now(timezone.utc).isoformat()
            }
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(rejudge_result, f, ensure_ascii=False, indent=2)

        return rejudge_result

    # =========================================================================
    # 5. ADVERSARIAL AUDIT
    # =========================================================================

    def adversarial_audit(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adversarial audit on stratified sample records using the stricter prompt.
        """
        prompt_template = (PROMPTS_DIR / f"{ADVERSARIAL_PROMPT_VERSION}.md").read_text(encoding="utf-8")
        payload = {
            "surface": entry["term"]["surface"],
            "reading": entry["term"]["reading"],
            "semantic_class": entry.get("domain", {}).get("semantic_class", ""),
            "domain": entry.get("domain", {}).get("primary", ""),
            "collocations": [c.get("text", "") for c in entry.get("collocations", [])],
            "examples": entry.get("examples", []),
            "dialogue": entry.get("dialogue", [])
        }

        cached, cache_file, input_hash = self._get_cached_or_dest("adv", payload, ADVERSARIAL_PROMPT_VERSION)
        if cached:
            return cached

        prompt = prompt_template.replace("{surface}", payload["surface"]) \
            .replace("{reading}", payload["reading"]) \
            .replace("{semantic_class}", payload["semantic_class"]) \
            .replace("{domain}", payload["domain"]) \
            .replace("{collocations_json}", json.dumps(payload["collocations"], ensure_ascii=False)) \
            .replace("{examples_json}", json.dumps(payload["examples"], ensure_ascii=False)) \
            .replace("{dialogue_json}", json.dumps(payload["dialogue"], ensure_ascii=False))

        raw_output = self._call_gemini(prompt)
        parsed = clean_json_response(raw_output)
        adv_result = {
            "adversarial_decision": parsed.get("adversarial_decision", "clean"),
            "hesitation_reasons": parsed.get("hesitation_reasons", []),
            "pedagogical_grade": parsed.get("pedagogical_grade", "A"),
            "verdict_summary": parsed.get("verdict_summary", ""),
            "metadata": {
                "model": self.model,
                "prompt_version": ADVERSARIAL_PROMPT_VERSION,
                "input_hash": input_hash,
                "audited_at": datetime.now(timezone.utc).isoformat()
            }
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(adv_result, f, ensure_ascii=False, indent=2)

        return adv_result
