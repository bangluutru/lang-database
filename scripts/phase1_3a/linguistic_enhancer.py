"""
scripts/phase1_3a/linguistic_enhancer.py
Phase 1.3A & 1.3A.1 Linguistic Engine: Reading Generation, Phonetic Overrides, and Gloss Integrity.

Enforces deterministic reading generation with regression protection for:
- 貸 (かし vs たい)
- 書 (しょ vs かき)
- 額 (がく vs ひたい)
- 者 (しゃ vs もの)
- 表 (ひょう vs おもて)
- 買 (かい vs ばい)
- 顛末書, 資本金の額, 準備金の額, 課税物件表, 加盟店貸勘定, 買現先勘定, 特定輸出者, 事業計画書

Also audits gloss integrity:
- Unmatched parentheses / brackets
- Truncated phrases
- Generic domain category placeholders (e.g. "Tax Filing", "Financial Accounting")

Returns field-level provenance for reading and gloss.
"""

from typing import Tuple, List, Dict, Optional, Set
import re
import pykakasi

from scripts.phase1_3a.models import (
    NormalizedCandidate,
    QualityFlag,
    ProvenanceType
)


# Explicit phonetic regression overrides for professional compounds
PHONETIC_OVERRIDES: Dict[str, str] = {
    # The 9 mandatory regression terms
    "貸出金": "かしだしきん",
    "加盟店貸勘定": "かめいてんかしかんじょう",
    "特定輸出者": "とくていゆしゅつしゃ",
    "資本金の額": "しほんきんのがく",
    "準備金の額": "じゅんびきんのがく",
    "顛末書": "てんまつしょ",
    "事業計画書": "じぎょうけいかくしょ",
    "課税物件表": "かぜいぶっけんひょう",
    "買現先勘定": "かいげんさきかんじょう",

    # Additional professional compounds prone to pykakasi phonetic misreading
    "売現先勘定": "うりげんさきかんじょう",
    "貸倒引当金": "かしだおれひきあてきん",
    "貸付金": "かしつけきん",
    "短期貸付金": "たんきかしつけきん",
    "長期貸付金": "ちょうきかしつけきん",
    "役員貸付金": "やくいんかしつけきん",
    "従業員貸付金": "じゅうぎょういんかしつけきん",
    "貸倒損失": "かしだおれそんしつ",
    "仕訳帳": "しわけちょう",
    "総勘定元帳": "そうかんじょうもとちょう",
    "試算表": "しさんひょう",
    "精算表": "せいさんひょう",
    "残高試算表": "ざんだかしさんひょう",
    "財産目録": "ざいさんもくろく",
    "有価証券報告書": "ゆうかしょうけんほうこくしょ",
    "有価証券届出書": "ゆうかしょうけんとどけいでしょ",
    "内部統制報告書": "ないぶとうせいほうこくしょ",
    "臨時報告書": "りんじほうこくしょ",
    "確定申告書": "かくていしんこくしょ",
    "青色申告書": "あおいろしんこくしょ",
    "中間申告書": "ちゅうかんしんこくしょ",
    "修正申告書": "しゅうせいしんこくしょ",
    "納税証明書": "のうぜいしょうめいしょ",
    "源泉徴収票": "げんせんちょうしゅうひょう",
    "支払調書": "しはらいちょうしょ",
    "納付書": "のうふしょ",
    "就業規則": "しゅうぎょうきそく",
    "労働条件通知書": "ろうどうじょうけんつうちしょ",
    "出勤簿": "しゅっきんぼ",
    "賃金台帳": "ちんぎんだいちょう",
    "労働者名簿": "ろうどうしゃめいぼ",
    "協定届": "きょうていとどけ",
    "適用届": "てきようとどけ",
    "輸入申告書": "ゆにゅうしんこくしょ",
    "輸出申告書": "ゆしゅつしんこくしょ",
    "原産地証明書": "げんさんちしょうめいしょ",
    "船荷証券": "ふなにしょうけん",
    "見積書": "みつもりしょ",
    "注文書": "ちゅうもんしょ",
    "注文請書": "ちゅうもんうけしょ",
    "納品書": "のうひんしょ",
    "検収書": "けんしゅうしょ",
    "請求書": "せいきゅうしょ",
    "領収書": "りょうしゅうしょ",
    "送り状": "おくりじょう",
    "定款": "ていかん",
    "株主名簿": "かぶぬしめいぼ",
    "取締役会議事録": "とりしまりやくかいぎじろく",
    "株主総会議事録": "かぶぬしそうかいぎじろく",
    "登記申請書": "とうきしんせいしょ",
    "印鑑証明書": "いんかんしょうめいしょ",
    "登記事項証明書": "とうきじこうしょうめいしょ",
    "委任状": "いにんじょう",
    "契約書": "けいやくしょ",
    "秘密保持契約書": "ひみつほじけいやくしょ",
    "業務委託契約書": "ぎょうむいたくけいやくしょ",
    "理由書": "りゆうしょ",
    "始末書": "しまつしょ",
    "報告書": "ほうこくしょ",
    "稟議書": "りんぎしょ",
    "起案書": "きあんしょ",
    "企画書": "きかくしょ",
    "提案書": "ていあんしょ",
    "社内報": "しゃないほう",
    "議事録": "ぎじろく",
    "手付金": "てつけきん",
    "内金": "うちきん",
    "敷金": "しききん",
    "礼金": "れいきん",
    "保証金": "ほしょうきん",
    "違約金": "いやくきん",
    "手当": "てあて",
    "残業手当": "ざんぎょうてあて",
    "役職手当": "やくしょくてあて",
    "通勤手当": "つうきんてあて",
    "家族手当": "かぞくてあて",
    "住宅手当": "じゅうたくてあて",
    "深夜手当": "しんやてあて",
    "休日手当": "きゅうじつてあて"
}

# Generic domain placeholders that must NEVER be used as glosses (Section 21 & 22)
GENERIC_GLOSS_PLACEHOLDERS: Set[str] = {
    "tax filing", "financial accounting", "labor standards", "trade procedures",
    "accounting", "finance", "tax", "hr", "trade", "legal", "business",
    "management", "purchasing", "sales", "office communication",
    "procurement", "commercial registration", "social insurance",
    "corporate law", "auditing", "bookkeeping", "corporate tax"
}


class Phase13LinguisticEnhancer:
    def __init__(self):
        self.kakasi = pykakasi.kakasi()

    def generate_reading(self, surface: str, include_provenance: bool = False):
        """
        Generates reading with regression protection and confidence level (HIGH, MEDIUM, LOW).
        If include_provenance is True, returns (reading, confidence, flags, reading_provenance).
        Otherwise returns (reading, confidence, flags) for backwards compatibility.
        """
        flags: List[QualityFlag] = []

        # 1. Exact match in verified phonetic overrides
        if surface in PHONETIC_OVERRIDES:
            if include_provenance:
                return (PHONETIC_OVERRIDES[surface], "HIGH", flags, "RULE_BASED")
            return (PHONETIC_OVERRIDES[surface], "HIGH", flags)

        # 2. Check suffix compound heuristics
        reading = None
        confidence = "MEDIUM"

        # Apply pykakasi conversion
        converted = self.kakasi.convert(surface)
        reading = "".join([item["hira"] for item in converted])

        # Regression heuristic corrections:
        # A. Suffix 〜書: should be しょ, not かき
        if surface.endswith("書") and reading.endswith("かき"):
            reading = reading[:-2] + "しょ"
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # B. Suffix 〜表: should be ひょう, not おもて
        if surface.endswith("表") and reading.endswith("おもて"):
            reading = reading[:-3] + "ひょう"
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # C. Suffix 〜額: should be がく, not ひたい
        if surface.endswith("額") and reading.endswith("ひたい"):
            reading = reading[:-3] + "がく"
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)
        if "の額" in surface and "のひたい" in reading:
            reading = reading.replace("のひたい", "のがく")
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # D. Suffix 〜者: should be しゃ, not もの
        if surface.endswith("者") and reading.endswith("もの"):
            reading = reading[:-2] + "しゃ"
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # E. Prefix 貸〜: 貸出 -> かしだし, 貸倒 -> かしだおれ, 貸付 -> かしつけ
        if surface.startswith("貸出") and reading.startswith("たいしゅつ"):
            reading = "かしだし" + reading[5:]
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)
        elif surface.startswith("貸倒") and reading.startswith("たいとう"):
            reading = "かしだおれ" + reading[4:]
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)
        elif surface.startswith("貸付") and reading.startswith("たいふ"):
            reading = "かしつけ" + reading[3:]
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # F. Prefix 買現先 / 売現先
        if surface.startswith("買現先") and reading.startswith("ばいげんさき"):
            reading = "かいげんさき" + reading[6:]
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # G. 加盟店貸〜
        if "加盟店貸" in surface and "かめいてんたい" in reading:
            reading = reading.replace("かめいてんたい", "かめいてんかし")
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)

        # Quality & confidence check
        if re.search(r"[a-zA-Z0-9\u4e00-\u9faf]", reading):
            confidence = "LOW"
            flags.append(QualityFlag.READING_REVIEW_REQUIRED)
        elif len(flags) > 0:
            confidence = "MEDIUM"
        else:
            confidence = "HIGH"

        if include_provenance:
            return (reading, confidence, flags, ProvenanceType.MODEL_ASSISTED.value)
        return (reading, confidence, flags)

    def extract_or_generate_gloss(
        self, candidate: NormalizedCandidate, include_provenance: bool = False
    ):
        """
        Extracts source-supported English gloss or generates a clean gloss.
        Audits gloss integrity per Section 22.
        If include_provenance is True, returns (gloss, confidence, flags, gloss_provenance).
        Otherwise returns (gloss, confidence, flags) for backwards compatibility.
        """
        flags: List[QualityFlag] = []
        gloss = ""
        confidence = "MEDIUM"
        gloss_prov = ProvenanceType.OFFICIAL_CURATED.value

        # 1. Look for "Official EN: ..." in source_contexts
        for ctx in candidate.source_contexts:
            m = re.search(r"Official EN:\s*([^\[\n\r]+)", ctx)
            if m:
                cand_gloss = m.group(1).strip().strip("\"' ")
                if cand_gloss:
                    gloss = cand_gloss
                    confidence = "HIGH"
                    gloss_prov = ProvenanceType.OFFICIAL_EXTRACTED.value
                    break

        # 2. Look for source definition
        if not gloss:
            for d in candidate.source_definitions:
                if d and len(d.strip()) > 3:
                    gloss = d.strip()
                    confidence = "MEDIUM"
                    gloss_prov = ProvenanceType.OFFICIAL_CURATED.value
                    break

        # 3. Fallback to descriptive placeholder if empty
        if not gloss:
            gloss = f"{candidate.normalized_surface} ({candidate.subdomain.replace('_', ' ').title()})"
            confidence = "LOW"
            gloss_prov = ProvenanceType.MODEL_ASSISTED.value
            flags.append(QualityFlag.GLOSS_REVIEW_REQUIRED)

        # Integrity audit:
        open_parens = gloss.count("(")
        close_parens = gloss.count(")")
        open_brackets = gloss.count("[")
        close_brackets = gloss.count("]")
        if open_parens != close_parens or open_brackets != close_brackets:
            flags.append(QualityFlag.MALFORMED_PARENTHESES)
            flags.append(QualityFlag.GLOSS_REVIEW_REQUIRED)
            if open_parens == close_parens + 1 and not gloss.endswith(")"):
                gloss = gloss + ")"

        # Check truncated phrase
        if re.search(r"[\(（\[,;:\-\s]$", gloss):
            flags.append(QualityFlag.TRUNCATED_GLOSS)
            flags.append(QualityFlag.GLOSS_REVIEW_REQUIRED)

        # Check generic domain placeholder
        if gloss.lower() in GENERIC_GLOSS_PLACEHOLDERS:
            flags.append(QualityFlag.GLOSS_REVIEW_REQUIRED)
            gloss = f"{candidate.normalized_surface} ({gloss.title()} concept)"

        if include_provenance:
            return (gloss, confidence, flags, gloss_prov)
        return (gloss, confidence, flags)
