# Athena Backend API Contract

For Yusra (backend/API integration) and Sadaf (frontend). This reflects the
actual current behavior of `main` as of 2026-08-18 — verified by running it,
not just reading the code.

## Endpoint

```
POST http://localhost:8000/report
Content-Type: application/json
```

Also available: `GET /health` → `{"status": "ok"}`

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
  "response": "string" | null
}
```

| Field | Type | Notes |
|---|---|---|
| `incident.language` | `"en" \| "hi" \| "te"` | auto-detected |
| `incident.incident_type` | string | e.g. `"domestic_violence"`, `"harassment"`, `"stalking"`, `"other"` |
| `incident.violence_types` | string[] | subset of `["physical","threat","sexual","cyber"]` |
| `incident.immediate_danger` / `.threat_present` / `.injury_present` | bool | |
| `incident.relationship` | string \| null | e.g. `"husband"`, `"stranger"`; null if not confidently detected |
| `incident.confidence` | float 0-100 | how confident the understanding step is — **low confidence is a real, meaningful state now** (see below) |
| `risk.risk_tier` | `"Low" \| "Medium" \| "High" \| "Critical"` | |
| `risk.risk_score` | int 0-100 | |
| `risk.risk_factors` | string[] | human-readable reasons, e.g. `"Immediate danger detected"`, `"Low understanding confidence — human review recommended"` |
| `citations` | array of `{source, page, similarity}` | grounding evidence actually used in the response; empty if none |
| `top_similarity` | float | best retrieval match score |
| `escalate` | bool | **true** = show "human assistance recommended" UI; frontend should treat this as the primary signal, not risk_tier alone |
| `reason` | string \| null | why it escalated, or null when it didn't |
| `response` | string \| null | the actual message to show the user, in their input language; **null whenever escalate is true and nothing could be generated** |

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
  "response": "यह एक अत्यंत गंभीर स्थिति है..."
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
  "response": null
}
```

**3. Gemini transiently unavailable** (fails soft, never crashes):
```json
{
  "incident": {...}, "risk": {...},
  "citations": [],
  "escalate": true,
  "reason": "The response service is temporarily unavailable. Please try again in a moment.",
  "response": null
}
```

**4. Empty/whitespace-only input**:
```json
{
  "incident": null,
  "risk": null,
  "citations": [],
  "top_similarity": 0.0,
  "escalate": true,
  "reason": "Incident text cannot be empty.",
  "response": null
}
```
Frontend should validate non-empty input client-side too, but the API won't
500 if that check is skipped.

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
