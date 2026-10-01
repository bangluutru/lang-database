"""
scripts/canary/validator.py
Independent Validation Gates for Phase 1.2C:
- Gate A: Schema & Provenance Integrity
- Gate B: Production & Canary Deduplication, Orthographic Variant, Abbreviation & Polysemy Resolution
- Gate C: Japanese Linguistic Quality & Semantic Soundness
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import re
import unicodedata
import yaml

from scripts.canary.models import (
    CanaryState,
    CanaryCandidateRecord,
    GateStatus,
    GateResult
)
from scripts.canary.state_machine import PromotionStateMachine
from scripts.linguistic_validator import VIETNAMESE_DIACRITICS_RE


# Known Orthographic Variant Pairs: variant -> canonical form
KNOWN_ORTHOGRAPHIC_VARIANTS = {
    "売り掛け金": "売掛金",
    "買い掛け金": "買掛金",
    "取引き先": "取引先",
    "棚卸し資産": "棚卸資産",
    "受取手形(受取手形)": "受取手形",
    "貸借対照表(B/S)": "貸借対照表",
    "損益計算書(P/L)": "損益計算書",
    "キャッシュ・フロー計算書(C/F)": "キャッシュ・フロー計算書",
    "減価償却(有形固定資産)": "減価償却累計額",
    "引当金(賞与)": "賞与引当金",
}

# Known Abbreviation Pairs: abbreviation -> full form
KNOWN_ABBREVIATIONS_MAP = {
    "J-SOX": "日本版SOX法",
    "BCP": "事業継続計画",
    "NDA": "秘密保持契約",
    "CSR": "企業の社会的責任",
    "KPI": "重要業績評価指標",
    "PDCA": "PDCAサイクル",
    "B/L": "船荷証券",
    "L/C": "信用状",
    "PO": "発注書",
    "FOB": "本船渡し条件",
    "CIF": "運賃保険料込み条件",
    "NACCS": "輸出入・港湾関連情報処理システム",
}

# Known Polysemous Terms & Cross-domain Sense Ambiguities
KNOWN_POLYSEMOUS_SENSES = {
    "査定": {
        "hr": "人事考課・勤務評定 (Performance Evaluation)",
        "tax": "課税標準額の決定・税額査定 (Tax Assessment)",
        "insurance": "損害保険の損害査定 (Loss Adjustment)"
    },
    "解約": {
        "hr": "労働契約の合意解約・解雇 (Termination of Employment)",
        "legal": "契約の合意解約・中途解約 (Contract Rescission)",
        "finance": "定期預金・信託の解約 (Account Liquidation)"
    },
    "手付金": {
        "legal": "契約締結の証拠金・解約手付 (Earnest Money)",
        "trade": "貿易契約の前払金・手付 (Trade Deposit)"
    },
    "引当": {
        "accounting": "将来の費用損失に対する引当金計上 (Provisions)",
        "purchasing": "受注に対する倉庫在庫の確保・引当 (Stock Allocation)"
    }
}


class CanaryValidator:
    def __init__(
        self,
        taxonomy_path: Path,
        production_path: Path,
        golden_v1_path: Path,
        golden_v1_1_path: Path
    ):
        self.taxonomy_path = taxonomy_path
        self.production_path = production_path
        self.golden_v1_path = golden_v1_path
        self.golden_v1_1_path = golden_v1_1_path

        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy = yaml.safe_load(f).get("domains", {})

        # Load baselines for Gate B dedup
        self.baseline_index: Dict[str, Dict[str, Any]] = {}
        self._load_baselines()

    def _load_baselines(self):
        """Indexes all production and Golden Pilot surfaces."""
        paths_to_load = [self.production_path, self.golden_v1_path, self.golden_v1_1_path]
        for p in paths_to_load:
            if not p.exists():
                continue
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    surface = rec.get("term", {}).get("surface", "")
                    if surface and surface not in self.baseline_index:
                        self.baseline_index[surface] = {
                            "id": rec.get("id"),
                            "surface": surface,
                            "domain": rec.get("domain", {}).get("primary", ""),
                            "subdomain": rec.get("domain", {}).get("subdomain", "")
                        }

    # -------------------------------------------------------------------------
    # Gate A: Schema & Provenance Integrity
    # -------------------------------------------------------------------------
    def validate_gate_a_schema(self, record: CanaryCandidateRecord) -> GateResult:
        reasons = []
        details = {}

        # 1. Surface existence and normalization check
        if not record.surface or not record.surface.strip():
            reasons.append("Surface string is empty.")
        if not record.normalized_surface or not record.normalized_surface.strip():
            reasons.append("Normalized surface string is empty.")

        # 2. Domain & Subdomain validity against taxonomy
        if record.domain not in self.taxonomy:
            reasons.append(f"Invalid domain '{record.domain}' not found in taxonomy.")
        else:
            subdomains = self.taxonomy[record.domain].get("subdomains", {})
            if record.subdomain not in subdomains:
                reasons.append(
                    f"Invalid subdomain '{record.subdomain}' for domain '{record.domain}'."
                )

        # 3. Source Evidence completeness
        if not record.source_evidence:
            reasons.append("Candidate has zero source evidence records.")
        else:
            for idx, ev in enumerate(record.source_evidence):
                sid = ev.get("source_id")
                ver = ev.get("source_version")
                loc = ev.get("source_locator")
                hsh = ev.get("raw_snapshot_hash")
                exact = ev.get("source_term_exact")

                if not sid:
                    reasons.append(f"Evidence #{idx} missing source_id.")
                if not ver:
                    reasons.append(f"Evidence #{idx} missing source_version.")
                if not loc:
                    reasons.append(f"Evidence #{idx} missing source_locator.")
                if not hsh:
                    reasons.append(f"Evidence #{idx} missing raw_snapshot_hash.")
                if not exact:
                    reasons.append(f"Evidence #{idx} missing source_term_exact.")

                # Draft source guard
                if sid == "fsa-edinet-2027-draft" or ver == "2027-draft":
                    reasons.append(f"Evidence #{idx} uses prohibited draft source '{sid}'.")

                # Licensing guard
                if ev.get("reuse_status") == "RED":
                    reasons.append(f"Evidence #{idx} has prohibited RED reuse status.")

        # 4. Authority Class & Reuse Status
        if record.authority_class not in {"A", "B", "C"}:
            reasons.append(f"Invalid authority_class '{record.authority_class}'.")
        if record.reuse_status not in {"GREEN", "YELLOW"}:
            reasons.append(f"Invalid or prohibited reuse_status '{record.reuse_status}'.")

        status = GateStatus.PASS if not reasons else GateStatus.FAIL
        details["checked_fields"] = ["surface", "domain", "subdomain", "source_evidence", "authority_class", "reuse_status"]
        return GateResult("Gate_A_Schema_Integrity", status, reasons, details)

    # -------------------------------------------------------------------------
    # Gate B: Production Dedup, Variants, Abbreviations, Polysemy
    # -------------------------------------------------------------------------
    def validate_gate_b_dedup(
        self,
        record: CanaryCandidateRecord,
        current_batch_surfaces: Dict[str, str]
    ) -> GateResult:
        reasons = []
        details = {}
        surface = record.surface
        domain = record.domain

        # 1. Exact Duplicate against Baseline
        if surface in self.baseline_index:
            base_rec = self.baseline_index[surface]
            base_domain = base_rec["domain"]
            # Check for polysemy / different sense
            if surface in KNOWN_POLYSEMOUS_SENSES and domain != base_domain:
                details["polysemy_detected"] = True
                details["baseline_domain"] = base_domain
                details["candidate_domain"] = domain
                reasons.append(
                    f"Possible different sense of existing baseline term '{surface}' ({base_domain} vs {domain})."
                )
                return GateResult("Gate_B_Production_Dedup", GateStatus.NEEDS_REVIEW, reasons, details)
            else:
                reasons.append(
                    f"Exact duplicate of baseline record {base_rec['id']} ('{surface}' in domain '{base_domain}')."
                )
                return GateResult("Gate_B_Production_Dedup", GateStatus.FAIL, reasons, details)

        # 2. Duplicate within Current Batch
        if surface in current_batch_surfaces and current_batch_surfaces[surface] != record.candidate_id:
            reasons.append(
                f"Duplicate term within current canary batch: collides with {current_batch_surfaces[surface]}."
            )
            return GateResult("Gate_B_Production_Dedup", GateStatus.FAIL, reasons, details)

        # 3. Known Orthographic Variant Matching
        if surface in KNOWN_ORTHOGRAPHIC_VARIANTS:
            canonical_form = KNOWN_ORTHOGRAPHIC_VARIANTS[surface]
            reasons.append(
                f"Orthographic variant detected: '{surface}' is variant of canonical form '{canonical_form}'."
            )
            details["variant_target"] = canonical_form
            return GateResult("Gate_B_Production_Dedup", GateStatus.NEEDS_REVIEW, reasons, details)

        # 4. Known Abbreviation Matching
        if surface in KNOWN_ABBREVIATIONS_MAP:
            full_form = KNOWN_ABBREVIATIONS_MAP[surface]
            reasons.append(
                f"Abbreviation detected: '{surface}' is abbreviation of '{full_form}'."
            )
            details["abbreviation_full_form"] = full_form
            return GateResult("Gate_B_Production_Dedup", GateStatus.NEEDS_REVIEW, reasons, details)

        # 5. Reverse Abbreviation Matching
        for abbrev, full_form in KNOWN_ABBREVIATIONS_MAP.items():
            if surface == full_form and abbrev in self.baseline_index:
                details["alias_canonical"] = self.baseline_index[abbrev]["id"]
                reasons.append(
                    f"Full canonical form '{surface}' matches existing abbreviation '{abbrev}' in baseline."
                )

        details["dedup_passed"] = True
        return GateResult("Gate_B_Production_Dedup", GateStatus.PASS, reasons, details)

    # -------------------------------------------------------------------------
    # Gate C: Japanese Linguistic Quality
    # -------------------------------------------------------------------------
    def validate_gate_c_linguistics(self, record: CanaryCandidateRecord) -> GateResult:
        reasons = []
        details = {}
        surface = record.surface
        reading = record.reading
        gloss = record.meaning_gloss

        # 1. Surface character composition
        # Japanese terms should contain Kanji, Hiragana, Katakana, or recognized ASCII acronyms
        has_japanese = bool(re.search(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", surface))
        has_valid_ascii = bool(re.match(r"^[A-Za-z0-9\/\-\(\)\s]+$", surface))
        if not (has_japanese or has_valid_ascii):
            reasons.append(f"Surface '{surface}' contains unsupported script characters.")

        # 2. Reading format validation
        if not reading or not reading.strip():
            reasons.append(f"Reading is empty for candidate '{surface}'.")
        else:
            # Reading must be pure Hiragana/Katakana (no raw Kanji, no broken tokens)
            is_valid_reading = bool(re.match(r"^[\u3040-\u309F\u30A0-\u30FF\u30FC・\s]+$", reading))
            if not is_valid_reading:
                reasons.append(f"Reading '{reading}' contains non-kana characters for '{surface}'.")

        # 3. Reading length vs surface heuristic (checks for corrupted pykakasi output)
        if reading and len(surface) > 0:
            ratio = len(reading) / max(len(surface), 1)
            if ratio > 6.0:
                reasons.append(f"Abnormally high reading/surface ratio ({ratio:.1f}) for '{surface}'.")

        # 4. Translation/Gloss quality check (detect Vietnamese diacritic leakage in English gloss)
        if gloss:
            if VIETNAMESE_DIACRITICS_RE.search(gloss):
                reasons.append(f"Meaning gloss contains Vietnamese diacritics leakage: '{gloss}'.")

        # 5. Artificial Accounting Template markers in non-accounting terms
        accounting_markers = ["帳簿照合", "補助元帳", "仕訳内容", "計上内容や残高"]
        if record.domain not in ("accounting", "finance"):
            for m in accounting_markers:
                if m in surface:
                    reasons.append(f"Artificial accounting template marker '{m}' found in non-accounting term '{surface}'.")

        status = GateStatus.PASS if not reasons else GateStatus.FAIL
        details["surface_len"] = len(surface)
        details["reading_len"] = len(reading)
        return GateResult("Gate_C_Linguistic_Quality", status, reasons, details)

    # -------------------------------------------------------------------------
    # Comprehensive Validation Runner
    # -------------------------------------------------------------------------
    def validate_candidate(
        self,
        record: CanaryCandidateRecord,
        current_batch_surfaces: Dict[str, str]
    ) -> bool:
        """Executes Gates A, B, and C, updating the record's gate_results and state."""
        res_a = self.validate_gate_a_schema(record)
        res_b = self.validate_gate_b_dedup(record, current_batch_surfaces)
        res_c = self.validate_gate_c_linguistics(record)

        record.gate_results = {
            res_a.gate_name: res_a.to_dict(),
            res_b.gate_name: res_b.to_dict(),
            res_c.gate_name: res_c.to_dict(),
        }

        all_pass = (
            res_a.status == GateStatus.PASS
            and res_b.status == GateStatus.PASS
            and res_c.status == GateStatus.PASS
        )

        if all_pass:
            PromotionStateMachine.transition(
                record,
                CanaryState.VALIDATION_PASSED,
                actor="canary_validator",
                reason="Passed Gates A, B, and C successfully."
            )
            return True
        else:
            # Determine specific failure or review state
            if res_b.details.get("polysemy_detected"):
                target_state = CanaryState.SENSE_AMBIGUOUS
            elif res_b.details.get("variant_target"):
                target_state = CanaryState.VARIANT_DETECTED
            elif res_b.details.get("abbreviation_full_form"):
                target_state = CanaryState.NEEDS_REVIEW
            elif any("RED reuse" in r for r in res_a.reasons):
                target_state = CanaryState.LICENSING_BLOCKED
            elif any("Exact duplicate" in r for r in res_b.reasons):
                target_state = CanaryState.DUPLICATE_DETECTED
            elif any("missing" in r for r in res_a.reasons):
                target_state = CanaryState.INSUFFICIENT_EVIDENCE
            else:
                target_state = CanaryState.REJECTED

            PromotionStateMachine.transition(
                record,
                target_state,
                actor="canary_validator",
                reason=f"Failed validation: {res_a.reasons + res_b.reasons + res_c.reasons}"
            )
            return False
