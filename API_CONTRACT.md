# Athena Backend API Contract

For Yusra (backend/API integration) and Sadaf (frontend). This reflects the
actual current behavior of `main` as of 2026-08-18 — verified by running it,
not just reading the code.

## Endpoint

```
POST http://localhost:8000/report
Content-Type: application/json
```

Also available: `GET /health` → `{"status": "ok"}`, and `POST /report/image` for
evidence screenshots (see **Evidence upload** below).

### Request body

```json
{
  "text": "user's incident report, any of English/Hindi/Telugu",
  "language": null
}
```

- `text` (string, required): the raw report. Language is auto-detected — you
  don't need to pass `language` unless you want to force it (`"en"` / `"hi"` / `"te"`).
- `language` (string, optional): omit or send `null` in the normal case.

### Response body

Always **HTTP 200** with this shape, whether things went well or not — the
frontend should branch on `escalate`/`reason`, not on HTTP status:

```json
{
  "incident": { ... } | null,
  "risk": { ... } | null,
  "citations": [ ... ],
  "top_similarity": 0.0,
  "escalate": true | false,
  "reason": "string" | null,
  "response": "string" | null,
  "case_id": 1 | null,
  "case_status": "Escalated" | "Resolved" | null
}
```

| Field | Type | Notes |
|---|---|---|
| `incident.language` | `"en" \| "hi" \| "te"` | auto-detected |
| `incident.incident_type` | string | e.g. `"domestic_violence"`, `"harassment"`, `"stalking"`, `"other"` |
| `incident.violence_types` | string[] | subset of `["physical","threat","sexual","cyber"]` |
| `incident.immediate_danger` / `.threat_present` / `.injury_present` | bool | |
| `incident.relationship` | string \| null | e.g. `"husband"`, `"stranger"`; null if not confidently detected |
| `incident.location` | string \| null | a real-world place *type* mentioned in the report — one of `bus_stop`, `railway_station`, `hostel`, `home`, `workplace`, `college_campus`, `market`, `street`, `police_station`, `hospital`, `park`; null if no location is confidently mentioned (most reports won't have one — that's expected, not a bug) |
| `incident.confidence` | float 0-100 | how confident the understanding step is — **low confidence is a real, meaningful state now** (see below) |
| `risk.risk_tier` | `"Low" \| "Medium" \| "High" \| "Critical"` | |
| `risk.risk_score` | int 0-100 | |
| `risk.risk_factors` | string[] | human-readable reasons, e.g. `"Immediate danger detected"`, `"Low understanding confidence — human review recommended"` |
| `citations` | array of `{source, page, similarity}` | grounding evidence actually used in the response; empty if none |
| `top_similarity` | float | best retrieval match score |
| `escalate` | bool | **true** = show "human assistance recommended" UI; frontend should treat this as the primary signal, not risk_tier alone |
| `reason` | string \| null | why it escalated, or null when it didn't |
| `response` | string \| null | the actual message to show the user, in their input language; **null whenever escalate is true and nothing could be generated** |
| `case_id` | int \| null | id of the persisted case (see Case tracking below); **null only for empty/whitespace input**, where nothing is saved |
| `case_status` | string \| null | `"Escalated"` or `"Resolved"` at creation time; can change later via the `/cases` endpoints below |

## The 4 response shapes you'll actually see

**1. Normal grounded response** (evidence found, Gemini succeeded):
```json
{
  "incident": {"language": "hi", "incident_type": "domestic_violence", ...},
  "risk": {"risk_tier": "Critical", "risk_score": 100, ...},
  "citations": [{"source": "domviolence.pdf", "page": 3, "similarity": 0.82}],
  "top_similarity": 0.82,
  "escalate": true,
  "reason": "High-risk incident requires human attention.",
  "response": "यह एक अत्यंत गंभीर स्थिति है...",
  "case_id": 1,
  "case_status": "Escalated"
}
```
`escalate` is `true` here even though a response was generated — Critical/High risk always escalates in *addition* to answering. Show both.

**2. No usable evidence / off-topic / ambiguous input** — `response` may still
be present (Gemini answering "I can't verify that") or `null`, `citations`
empty or low-similarity, `escalate: true`:
```json
{
  "incident": {"violence_types": [], "immediate_danger": false, "confidence": 0.0, ...},
  "risk": {"risk_tier": "Low", "risk_factors": ["Low understanding confidence — human review recommended"], ...},
  "citations": [],
  "escalate": true,
  "reason": "No matching evidence found in the knowledge base.",
  "response": null,
  "case_id": 2,
  "case_status": "Escalated"
}
```

**3. Gemini transiently unavailable** (fails soft, never crashes):
```json
{
  "incident": {...}, "risk": {...},
  "citations": [],
  "escalate": true,
  "reason": "The response service is temporarily unavailable. Please try again in a moment.",
  "response": null,
  "case_id": 3,
  "case_status": "Escalated"
}
```

**4. Empty/whitespace-only input** — the only case with no `case_id`:
```json
{
  "incident": null,
  "risk": null,
  "citations": [],
  "top_similarity": 0.0,
  "escalate": true,
  "reason": "Incident text cannot be empty.",
  "response": null,
  "case_id": null,
  "case_status": null
}
```
Frontend should validate non-empty input client-side too, but the API won't
500 if that check is skipped.

## Case tracking

Every processed report (except empty input) is now persisted as a **case** —
this is what happens after `escalate: true`, not a dead end. Status starts as
`"Escalated"` or `"Resolved"` and can move through
`New → Under Review → Escalated → In Progress → Resolved → Closed` from there
(useful for an admin view — "My reports" on the frontend maps directly to this).

```
GET  /cases                      -> list, most recent first
GET  /cases?status=Escalated     -> filter by status
GET  /cases/{id}                 -> one case, 404 if it doesn't exist
PATCH /cases/{id}/status         -> body: {"status": "Under Review"}, 400 if invalid, 404 if missing
```

A case object looks like:
```json
{
  "id": 1,
  "created_at": "2026-08-18T14:02:11.123456+00:00",
  "status": "Escalated",
  "original_text": "...",
  "language": "hi",
  "incident_type": "domestic_violence",
  "risk_tier": "Critical",
  "risk_score": 100,
  "confidence": 98.66,
  "escalate": true,
  "reason": "High-risk incident requires human attention.",
  "response": "...",
  "citations": [ ... ],
  "evidence_path": "evidence/3f9a...c1.png" | null
}
```

Valid `status` values: `"New"`, `"Under Review"`, `"Escalated"`,
`"In Progress"`, `"Resolved"`, `"Closed"`.

## Stats (for dashboard cards)

```
GET /stats
```

Real, computed aggregates over every case — **use this instead of hardcoded
numbers** on any dashboard/overview card ("Community reports," "Active
alerts," risk breakdowns, etc.):

```json
{
  "total_cases": 1,
  "escalated_cases": 1,
  "cases_with_evidence": 1,
  "by_status": {"Escalated": 1},
  "by_risk_tier": {"Critical": 1},
  "by_incident_type": {"domestic_violence": 1},
  "by_language": {"en": 1}
}
```

The `by_*` fields are plain `{value: count}` maps — only keys that actually
occur in the data appear (no zero-filled entries for unused categories).

## Evidence upload (screenshots)

```
POST http://localhost:8000/report/image
Content-Type: multipart/form-data

file: <image>       (required)
language: "en"|"hi"|"te"   (optional form field, default "en" — OCR script hint, not incident language)
```

OCR-extracts the text from the image (e.g. a screenshot of threatening
messages), then runs it through the **exact same pipeline** as `/report` —
same response shape, same `case_id`/`case_status`, plus one extra field:

```json
{
  "extracted_text": "the text OCR actually read from the image",
  "incident": { ... }, "risk": { ... }, "citations": [ ... ],
  "escalate": true, "reason": "...", "response": "...",
  "case_id": 5, "case_status": "Escalated"
}
```

**Show `extracted_text` to the user before/alongside the result** — OCR can
misread things, and the user should be able to see what Athena actually
understood from their screenshot, same principle as showing citations.

If OCR finds no readable text at all, you get the same no-case shape as empty
text input, with `"reason": "No readable text found in the uploaded image."`
and `"extracted_text": ""`.

The uploaded image is saved server-side and linked to the case via
`evidence_path` — not currently served back over HTTP (no `GET` route for the
file itself yet), just tracked for now.

## What the frontend needs to handle

- `incident` and `risk` can both be `null` (case 4) — don't assume they exist.
- `response` can be `null` even when `escalate` is `false`-adjacent cases don't
  really occur, but always null-check before rendering it.
- Always render based on `escalate`/`reason`, never on HTTP status — this API
  does not use 4xx/5xx for expected failure modes.
- `citations` is always an array (possibly empty), never null/undefined.

## Known limitations (not blockers, just be aware)

- CORS is currently wide open (`allow_origins=["*"]`) — fine for local dev,
  tighten before any real deployment.
- No auth on the endpoint yet.
- `incident.confidence` and `risk.confidence` are the same number right now
  (both come from the understanding step) — don't read them as two
  independent signals yet.
