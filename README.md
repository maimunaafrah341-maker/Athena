# Athena

**AI-based real-time stress and trauma assessment for victims/complainants accessing a national helpline.**

Built for **SIH26093** (Ministry of Social Justice and Empowerment) — a real-time module that assesses the psychological stress, trauma, fear, and vulnerability of a caller at first contact with the **National Helpline Against Atrocities (14566)**, and routes them to the right human response instead of leaving triage to whoever happens to answer.

Core philosophy: **UNDERSTAND → VERIFY → ACT → ESCALATE.** Athena is not a chatbot that always has an answer — it's a pipeline that knows what it doesn't know, and hands a case to a human the moment it's uncertain rather than guessing.

## What it does

- **Understands** a report in English, Hindi, or Telugu — native script or romanized — using semantic similarity against curated real-world examples, not keyword matching.
- **Assesses risk** (`risk_tier`: Low/Medium/High/Critical) from detected signals — threats, injury, immediate danger, caste-based motive — with a concrete per-tier response protocol (SLA, escalation route, action).
- **Assesses stress** independently via the **Stress Vulnerability Index (SVI)** — the module this problem statement names directly — fusing text distress signals with optional voice acoustic features (pitch variation, pause ratio, speech rate) into a Low/Moderate/High/Critical tier, and flagging when text and voice disagree.
- **Grounds every legal citation** in real, ingested government source documents (Bharatiya Nyaya Sanhita 2023, the SC/ST Prevention of Atrocities Act 1989 bare act, PWDVA 2005, Mission Shakti guidelines) via a confidence-gated RAG pipeline — nothing is cited that wasn't actually retrieved above a similarity threshold.
- **Resolves an escalation contact** from a national directory of 554 districts across 33 states/UTs, provenance-tagged (manually verified vs. machine-parsed) so nothing is presented with false confidence.
- **Escalates to a human** on any of three independent triggers: Critical risk, Critical stress, or the system simply not being confident it understood the report at all.
- Supports low-disclosure reporting (anonymous / partial / full, enforced at the database layer), evidence upload with OCR, an SOS endpoint, nearby police/hospital lookup, an anonymized safety map, and district-level pattern detection for week-over-week case spikes.

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
```

Full request/response contract, known limitations, and field-level detail: [API_CONTRACT.md](API_CONTRACT.md).

## Tech stack

| Layer | Used |
|---|---|
| API server | FastAPI + uvicorn |
| Language/incident understanding | `intfloat/multilingual-e5-small` (sentence-transformers) |
| Knowledge retrieval | ChromaDB |
| Response generation | Google Gemini, with an ordered model-fallback list |
| Legal knowledge graph | `networkx.DiGraph` |
| Voice transcription | OpenAI Whisper (`whisper-1`) |
| Evidence OCR | EasyOCR |
| Frontend | Static HTML/CSS/JS ([athena.html](athena.html)), plus a [WhatsApp-style demo channel](whatsapp_demo.html) calling the same `/report` endpoint |

## Running it locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

copy env.example .env        # then fill in your real keys
python app.py                # or: uvicorn app:app --reload
```

Required in `.env`: `GEMINI_API_KEY`, `ADMIN_API_KEY`. Optional: `OPENAI_API_KEY` (voice transcription — falls back to a placeholder transcript if unset or unfunded). See [env.example](env.example) for details on each.

Open [athena.html](athena.html) or [whatsapp_demo.html](whatsapp_demo.html) in a browser with the server running on `localhost:8000`.

## Known limitations

Stated honestly rather than discovered by a judge mid-demo — full detail in `API_CONTRACT.md`'s Known Limitations section:

- Live voice transcription is billing-gated (OpenAI account has no active credits), not broken — the integration is built and was verified against a real API call.
- Legal citations are deliberately scoped to the SC/ST Act only, matching 14566's actual legal remit — the detection mechanism underneath is not hardcoded to caste and can extend to other Acts as future scope.
- Romanized-script retrieval can occasionally miss a correct smaller source document when a much larger one dominates ranking — a documented safe-failure edge case (declines rather than hallucinates), not yet fixed.
- Admin access is a single shared API key today, not per-counsellor roles or an audit log.

## Team

RAG/pipeline, backend · frontend · multilingual/voice · deployment · pitch — see the project board for current ownership.
