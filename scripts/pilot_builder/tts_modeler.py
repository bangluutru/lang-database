"""
scripts/pilot_builder/tts_modeler.py
TTS modeling module for professional Japanese vocabulary.
Ensures engine-independent pronunciation modeling, specifically handling:
- Display form vs spoken form
- Pure Latin acronyms (FOB, CIF, KPI, TTB, TTS)
- Slash compounds (B/L, L/C, D/P, D/A)
- Mixed Latin/Japanese compounds (e-Tax, HSコード, 日欧EPA, FCL貨物)
- Numeric prefixes (1年内..., 1株当たり..., 2割特例)
- Standard Kanji/Kana terms
"""

import re

# Comprehensive mapping for Latin / Symbol / Acronym elements to spoken Katakana and Kana readings
ACRONYM_SPEECH_MAP = {
    "B/L": {"speech": "ビーエル", "reading": "びーえる"},
    "L/C": {"speech": "エルシー", "reading": "えるしー"},
    "D/P": {"speech": "ディーピー", "reading": "でぃーぴー"},
    "D/A": {"speech": "ディーエー", "reading": "でぃーえー"},
    "FOB": {"speech": "エフオービー", "reading": "えふおーびー"},
    "CIF": {"speech": "シーアイエフ", "reading": "しーあいえふ"},
    "CFR": {"speech": "シーエフアール", "reading": "しーえふあーる"},
    "EXW": {"speech": "イーエックスダブリュー", "reading": "いーえっくすだぶりゅー"},
    "FCA": {"speech": "エフシーエー", "reading": "えふしーえー"},
    "CPT": {"speech": "シーピーティー", "reading": "しーぴーてぃー"},
    "CIP": {"speech": "シーアイピー", "reading": "しーあいぴー"},
    "DAP": {"speech": "ディーエーピー", "reading": "でぃーえーぴー"},
    "DPU": {"speech": "ディーピーユー", "reading": "でぃーぴーゆー"},
    "DDP": {"speech": "ディーディーピー", "reading": "でぃーでぃーぴー"},
    "FAS": {"speech": "エフエーエス", "reading": "えふえーえす"},
    "HSコード": {"speech": "エイチエスココード", "reading": "えいちえすこーど"},
    "HS": {"speech": "エイチエス", "reading": "えいちえす"},
    "EPA": {"speech": "イーピーエー", "reading": "いーぴーえー"},
    "NPO": {"speech": "エヌピーオー", "reading": "えぬぴーおー"},
    "e-Tax": {"speech": "イータックス", "reading": "いーたっくす"},
    "KPI": {"speech": "ケーピーアイ", "reading": "けーぴーあい"},
    "TTB": {"speech": "ティーティービー", "reading": "てぃーてぃーびー"},
    "TTS": {"speech": "ティーティーエス", "reading": "てぃーてぃーえす"},
    "TTM": {"speech": "ティーティーエム", "reading": "てぃーてぃーえむ"},
    "FCL": {"speech": "エフシーエル", "reading": "えふしーえる"},
    "LCL": {"speech": "エルシーエル", "reading": "えるしーえる"},
    "CFS": {"speech": "シーエフエス", "reading": "しーえふえす"},
    "CY": {"speech": "シーワイ", "reading": "しーわい"},
    "X線": {"speech": "エックスせん", "reading": "えっくすせん"},
    "B/S": {"speech": "ビーエス", "reading": "びーえす"},
    "P/L": {"speech": "ピーエル", "reading": "ぴーえる"},
    "EDINET": {"speech": "エディネット", "reading": "えでぃねっと"},
    "ASBJ": {"speech": "エーエスビージェイ", "reading": "えーえすびーじぇい"},
    "JICPA": {"speech": "ジェイアイシーピーエー", "reading": "じぇいあいしーぴーえー"},
}

NUMERIC_REPLACEMENTS = [
    ("1年内返済予定の長期借入金", "一年内返済予定の長期借入金", "いちねんないへんさいよていのちょうきかりいれきん"),
    ("1株当たり当期純利益", "一株当たり当期純利益", "ひとかぶあたりとうきじゅんりえき"),
    ("2割特例", "二割特例", "にわりとくれい"),
]


def model_tts(surface: str, current_reading: str) -> dict:
    """
    Builds structured, engine-independent TTS metadata for a term.
    """
    # 1. Check direct numerical replacements
    for num_surf, num_speech, num_read in NUMERIC_REPLACEMENTS:
        if surface == num_surf:
            return {
                "display_text": surface,
                "speech_text": num_speech,
                "preferred_reading": num_read,
                "pronunciation_type": "numeric_compound",
                "pause_after_term_ms": 1200
            }

    # 2. Check exact acronym match
    if surface in ACRONYM_SPEECH_MAP:
        mapping = ACRONYM_SPEECH_MAP[surface]
        pron_type = "acronym_word" if surface == "EDINET" else "acronym_alphabet"
        return {
            "display_text": surface,
            "speech_text": mapping["speech"],
            "preferred_reading": mapping["reading"],
            "pronunciation_type": pron_type,
            "pause_after_term_ms": 1200
        }

    # 3. Check compound terms with Latin/symbols
    speech_text = surface
    has_replacement = False
    
    # Check known compounds
    for acr, mapping in ACRONYM_SPEECH_MAP.items():
        if acr in surface:
            speech_text = speech_text.replace(acr, mapping["speech"])
            has_replacement = True

    # Fix typo in readings like 'くりーんはーえる' -> 'くりーんびーえる'
    clean_reading = current_reading
    if "はーえる" in clean_reading and "B/L" in surface:
        clean_reading = clean_reading.replace("はーえる", "びーえる")
    if "B/L" in surface and not clean_reading.endswith("びーえる"):
        clean_reading = clean_reading.replace("bl", "びーえる")

    if has_replacement or re.search(r'[A-Za-z/0-9]', surface):
        return {
            "display_text": surface,
            "speech_text": speech_text,
            "preferred_reading": clean_reading,
            "pronunciation_type": "mixed_compound",
            "pause_after_term_ms": 1200
        }

    # 4. Standard Kanji / Kana term
    return {
        "display_text": surface,
        "speech_text": surface,
        "preferred_reading": current_reading,
        "pronunciation_type": "standard_kanji_kana",
        "pause_after_term_ms": 1200
    }
