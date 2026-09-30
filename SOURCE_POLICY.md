# Source Policy & Data Governance Specification

## 1. Overview & Core Principles

The **JP Professional Vocabulary Database** is built as an authoritative, traceable, and machine-queryable linguistic knowledge asset. Ingesting data from the Internet requires strict adherence to legal compliance, intellectual property rights, data provenance, and automated auditability.

Under no circumstances is the Internet treated as "free raw data." Every single source ingested or referenced must pass through our **Source Governance Pipeline** before any term enters the candidate pool.

---

## 2. Source Classification: Traffic Light Model

| Tier | Status | Description | Allowed Actions | Disallowed Actions | Examples |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GREEN** | Official Open Public Data | Official Japanese Government public datasets under government public licenses (e.g., PDL-1.0, Government of Japan Website Terms of Use, FSA EDINET Taxonomy Statement). | Direct file download, structured parsing (Excel, ZIP, XML), canonical transformation, verbatim term storage with source link. | Claiming copyright ownership of official raw government taxonomies; omitting mandatory attribution. | 金融庁 (FSA) 2026 EDINET Taxonomy, 国税庁 (NTA) Tax Answer & Glossaries. |
| **YELLOW** | Reference & Terminology Discovery | Industry associations, professional standards committees, and semi-governmental research bodies with proprietary rights on their prose. | Terminology discovery, conceptual relation mapping, standard index extraction, cross-referencing. | Bulk copying of explanatory prose, articles, textbook text, or long-form proprietary explanations. All definitions must be independently authored. | 日本公認会計士協会 (JICPA), 企業会計基準委員会 (ASBJ), JETRO (日本貿易振興機構). |
| **RED** | Prohibited / High Risk | Commercial subscription dictionaries, private paywalled databases, blogs without licenses, copyrighted training materials, sites with anti-scraping paywalls. | None. Strictly excluded from the pipeline. | Web scraping behind logins, bypassing Cloudflare/reCAPTCHA/WAFs, bulk copying commercial Japanese-Vietnamese dictionaries. | Commercial paywalled dictionaries, private course materials. |

---

## 3. Provenance & Non-Contamination Rule

A strict architectural rule of this database is:
> **Source Facts and AI-Generated / Linguistic-Engineered Content Must Never Be Conflated.**

1. **Source Facts (`source_data` / `sources`):**
   - Contains the exact Japanese surface as published by the authoritative source (e.g. 金融庁 勘定科目リスト).
   - Contains the official code, standard ID, taxonomy element ID, or regulatory reference.
   - Contains immutable metadata (download URL, SHA-256 hash, download timestamp).
2. **Generated & Enriched Data (`meaning`, `examples`, `dialogue`, `tts`, `collocations`):**
   - The Vietnamese translations, learner explanations, English mappings, natural workplace examples, conversation dialogues, audio TTS hints, and PRO difficulty tiers are created by our linguistic engineering pipeline.
   - These are **never** attributed to the government or professional association (e.g., we do not claim that FSA provided the Vietnamese translation).

---

## 4. Policy on Annual Taxonomies & Drafts (e.g., FSA EDINET)

1. **Production Baseline:**
   - The production database is anchored to **2026年版EDINETタクソノミ (Official Final Version)** published November 11, 2025.
2. **Draft Treatment:**
   - When a draft version (such as **2027年版EDINETタクソノミ（案）**) is analyzed for forward compatibility, it is strictly placed in:
     `staging/fsa_edinet_2027_draft/`
   - Any candidate originating solely from the draft must bear the metadata:
     `source_status: "draft"`
   - No draft-exclusive entry is permitted in the production release without explicit approval and status marking.

---

## 5. Anti-Bot and Scraping Ethics

1. **No Circumvention:** We never bypass CAPTCHA, bot detection, or scrape rate limits.
2. **Structured-First:** Direct downloadable structured formats (Excel `.xlsx`, ZIP archives, XML) are prioritized over web page scraping.
3. **Respectful Requests:** All web fetch operations must include explicit headers, rate limiting (minimum 1.0s delay between requests), and standard browser User-Agents.
4. **Reproducibility:** All downloads are mediated by scripted tools in `scripts/download_sources.py` which compute and log cryptographic checksums (SHA-256).
