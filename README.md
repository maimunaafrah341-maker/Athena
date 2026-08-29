# Athena

**AI-based real-time stress and trauma assessment for victims/complainants accessing a national helpline.**

Built for **SIH26093** (Ministry of Social Justice and Empowerment) — a real-time module that assesses the psychological stress, trauma, fear, and vulnerability of a caller at first contact with the **National Helpline Against Atrocities (14566)**, and routes them to the right human response instead of leaving triage to whoever happens to answer.

Core philosophy: **UNDERSTAND → VERIFY → ACT → ESCALATE.** Athena is not a chatbot that always has an answer — it's a pipeline that knows what it doesn't know, and hands a case to a human the moment it's uncertain rather than guessing.

> 🎥 **[Watch the demo](https://youtu.be/BsoHkgnQuOM)** — a real report going through the full pipeline: voice intake, stress scoring, an SC/ST Act citation pulled from the actual ingested Act text, and escalation to the counsellor dashboard.

## What it does

- **Understands** a report in English, Hindi, Telugu, Urdu, or Bengali — native script or romanized (Latin script for Hindi/Telugu/Urdu/Bengali) — using semantic similarity against curated real-world examples, not keyword matching. The interface itself (not just the complaint text) is also localized into Hindi/Telugu/Urdu/Bengali, so a reporter doesn't need to already read English to get through the report form. Urdu/Bengali support is new (2026-08-29) and hasn't had a native-speaker review pass yet — see `eval_pipeline.py`.
- **Places a report on the safety map even without GPS.** If a reporter shares a district but denies/lacks location access, `geocoding.py` resolves an approximate district-level pin (OSM Nominatim, with a cached/offline table for common districts) instead of the case simply not appearing — clearly labeled "(approx.)" rather than implying GPS precision it doesn't have.
- **Assesses risk** (`risk_tier`: Low/Medium/High/Critical) from detected signals — threats, injury, immediate danger, caste-based motive — with a concrete per-tier response protocol (SLA, escalation route, action).
- **Assesses stress** independently via the **Stress Vulnerability Index (SVI)** — the module this problem statement names directly — fusing text distress signals with voice acoustic features (pitch variation, pause ratio, speech rate, real-extracted from the actual audio via `voice_features.py`/librosa, not placeholder values) into a Low/Moderate/High/Critical tier, and flagging when text and voice disagree.
- **Grounds every legal citation** in real, ingested government source documents (Bharatiya Nyaya Sanhita 2023, the SC/ST Prevention of Atrocities Act 1989 bare act, PWDVA 2005, Mission Shakti guidelines) via a confidence-gated RAG pipeline — nothing is cited that wasn't actually retrieved above a similarity threshold.
- **Resolves an escalation contact** from a national directory of 554 districts across 33 states/UTs, provenance-tagged (manually verified vs. machine-parsed) so nothing is presented with false confidence.
- **Escalates to a human** on any of three independent triggers: Critical risk, Critical stress, or the system simply not being confident it understood the report at all.
- **Binds every case to an NHAA docket** (`nhaa.py`) — channel-agnostic across 14566 voice, IVRS, the Integrated Portal, chatbot, and mobile app, so the same pipeline runs no matter which of NHAA's real entry points a report came through, and every finalized case gets a docket ID the same way a real NHAA complaint does.
- Supports low-disclosure reporting (anonymous / partial / full, enforced at the database layer), evidence upload with OCR, an SOS endpoint, nearby police/hospital lookup, an anonymized safety map, and district-level pattern detection for week-over-week case spikes.
- **Never shows an empty dashboard.** Realistic demo cases auto-seed on first startup if the database is empty (`seed_data.py`) — safe insurance against an ephemeral host wiping storage on redeploy, and it never touches or overwrites real report data.

## Architecture

```
report text/voice
      │
      ▼
understanding.py   → language, script, incident type, signals, confidence
      │
      ▼
risk.py            → risk_tier + response_protocol
      │
      ▼
svi.py             → Stress Vulnerability Index (svi_tier, contributing_factors)
      │
      ▼
retrieval.py        → ChromaDB semantic search over verified source documents
  + kg.py            → SC/ST Act provisions + district escalation contact
      │
      ▼
response_engine.py → Gemini phrases a grounded reply from retrieved evidence only
      │
      ▼
pipeline.py         → escalate decision (risk / stress / low-confidence), case record
  + nhaa.py          → NHAA docket bound to channel + SVI/risk outcome
```

Full request/response contract, known limitations, and field-level detail: [API_CONTRACT.md](API_CONTRACT.md).

## Tech stack

| Layer | Used |
|---|---|
| API server | FastAPI + uvicorn |
| Language/incident understanding | `intfloat/multilingual-e5-small` (sentence-transformers) |
| Knowledge retrieval | ChromaDB |
| Response generation | Groq (primary), Google Gemini, then OpenRouter — an ordered cross-provider fallback so one provider's outage/quota can't take generation down |
| Legal knowledge graph | `networkx.DiGraph` |
| Voice transcription | Groq-hosted Whisper (`whisper-large-v3-turbo`, primary), falling back to OpenAI Whisper (`whisper-1`) |
| Evidence OCR | EasyOCR |
| Frontend | Static HTML/CSS/JS ([web/dashboard.html](web/dashboard.html)), plus a [WhatsApp-style demo channel](web/index.html) calling the same `/report` endpoint |

## Running it locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

copy env.example .env        # then fill in your real keys
python app.py                # or: uvicorn app:app --reload
```

Required in `.env`: `ADMIN_API_KEY`, `GROQ_API_KEY` (primary for both response generation and voice transcription). Optional: `GEMINI_API_KEY`/`OPENROUTER_API_KEY` (generation fallback tiers), `OPENAI_API_KEY` (voice transcription fallback). Voice transcription falls back to a placeholder transcript only if both Groq and OpenAI are unset/unavailable. See [env.example](env.example) for details on each.

With the server running, open:
- `http://localhost:8000/` — the WhatsApp-style citizen-facing demo
- `http://localhost:8000/dashboard.html` — the report form + counsellor dashboard (needs `ADMIN_API_KEY` to unlock case data)

## Known limitations

Stated honestly rather than discovered by a judge mid-demo — full detail in `API_CONTRACT.md`'s Known Limitations section:

- Live voice transcription now works end-to-end (2026-08-29: swapped from OpenAI, which needed a funded account that never happened, to Groq's hosted Whisper, which has a genuinely usable free tier) — verified against real audio (`demo_audio/caste_harassment_hindi.ogg`), not a placeholder.
- The hosted deployment is currently memory-constrained on its free-tier plan (this stack needs ~1-2GB RAM) — see the [demo video](https://youtu.be/BsoHkgnQuOM) for a full live walkthrough rather than relying on the hosted link being up.
- Legal citations are deliberately scoped to the SC/ST Act only, matching 14566's actual legal remit — the detection mechanism underneath is not hardcoded to caste and can extend to other Acts as future scope.
- Romanized-script retrieval can occasionally miss a correct smaller source document when a much larger one dominates ranking — a documented safe-failure edge case (declines rather than hallucinates), not yet fixed.
- Admin access is a single shared API key today, not per-counsellor roles or an audit log.

## Team

| Name | Focus |
|---|---|
| **Maimuna** | Team lead · RAG, AI pipeline & backend — understanding, risk, SVI, knowledge graph, retrieval |
| **Yusra** | Backend / API integration — voice transcription integration, endpoint testing |
| **Sadaf** | Frontend — UI/UX, report flow, safety map |
| **Samreen** | Multilingual & voice — audio input pipeline |
| **Saboora** | Deployment / DevOps — infrastructure and hosting |
| **Nuvaira** | Pitch & problem research — problem-statement grounding, presentation |
