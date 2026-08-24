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
  "language": null,
  "latitude": null,
  "longitude": null,
  "voice_features": null,
  "district": null,
  "disclosure_level": "full",
  "reporter_name": null,
  "reporter_contact": null
}
```

`latitude`/`longitude` are optional — only send them if the user actively
chose to share their location (e.g. a browser geolocation prompt they
accepted). Omit/null is the default and totally fine.

- `text` (string, required): the raw report. Language is auto-detected — you
  don't need to pass `language` unless you want to force it (`"en"` / `"hi"` / `"te"`).
- `language` (string, optional): omit or send `null` in the normal case.
- `voice_features` (object, optional): pre-extracted voice signal, see
  **Stress Vulnerability Index (SVI)** below. Omit/null for text-only input,
  which is the normal case today.
- `district` (string, optional): the reporter's district (e.g. `"Karimnagar"`,
  `"Agra"`, `"Kanyakumari"`) — used only to resolve
  `legal_guidance.escalation_contact` (see **Legal & escalation guidance**
  below). Covers 554 districts across 33 states/UTs as of 2026-08-23 — see
  that section for the manual-vs-parsed confidence distinction and the
  handful of ambiguous names that are deliberately excluded. Case-
  insensitive; unrecognized/omitted district just means `escalation_contact`
  comes back `null`, not an error.
  **Not gated by `disclosure_level`** — a district name routes to a contact
  list, it doesn't identify the reporter, so it's honored even on an
  anonymous report.
- `disclosure_level` (string, optional, default `"full"`): `"full"` |
  `"partial"` | `"anonymous"` — see **Low-disclosure reporting** below.
  Omitting it is identical to sending `"full"`, so existing integrations
  don't need to change anything. 400 if you send anything else.
- `reporter_name` / `reporter_contact` (string, optional): only ever
  persisted when `disclosure_level` is `"full"` (`reporter_contact` is also
  kept for `"partial"` — see below). Harmless to send either at any
  disclosure level; they're redacted server-side, not just ignored
  client-side, so a UI bug that sends a name on an "anonymous" submission
  can't leak it.

### Response body

Always **HTTP 200** with this shape, whether things went well or not — the
frontend should branch on `escalate`/`reason`, not on HTTP status:

```json
{
  "incident": { ... } | null,
  "risk": { ... } | null,
  "stress_assessment": { ... } | null,
  "legal_guidance": null,
  "citations": [ ... ],
  "top_similarity": 0.0,
  "escalate": true | false,
  "reason": "string" | null,
  "response": "string" | null,
  "case_id": 1 | null,
  "case_status": "Escalated" | "Resolved" | null,
  "reasoning_trace": { ... } | null
}
```

| Field | Type | Notes |
|---|---|---|
| `incident.language` | `"en" \| "hi" \| "te"` | auto-detected |
| `incident.script` | `"native" \| "romanized" \| "latin"` | whether the report was written in native script (Devanagari/Telugu) or romanized (Latin letters); `"latin"` for English. The Gemini response matches this — romanized input gets a romanized reply, not a switch to native script |
| `incident.incident_type` | string | e.g. `"domestic_violence"`, `"harassment"`, `"stalking"`, `"other"` |
| `incident.violence_types` | string[] | subset of `["physical","threat","sexual","cyber"]` |
| `incident.immediate_danger` / `.threat_present` / `.injury_present` | bool | |
| `incident.relationship` | string \| null | e.g. `"husband"`, `"stranger"`; null if not confidently detected |
| `incident.location` | string \| null | a real-world place *type* mentioned in the report — one of `bus_stop`, `railway_station`, `hostel`, `home`, `workplace`, `college_campus`, `market`, `street`, `police_station`, `hospital`, `park`; null if no location is confidently mentioned (most reports won't have one — that's expected, not a bug) |
| `incident.confidence` | float 0-100 | how confident the understanding step is — **low confidence is a real, meaningful state now** (see below) |
| `incident.confidence_breakdown` | object | per-field confidence: `{incident_type, threat, injury, immediate_danger, relationship, location, caste_based_motive}`, each 0-100, calibrated the same way as `confidence` (comparable to each other, not raw similarity scores). A field can show low confidence even when its boolean came back `false`/`null` — that's the point, it explains *why* (e.g. `location: 43.4` alongside `location: null` means Athena saw a weak hint but wasn't confident enough to commit to it) |
| `incident.caste_based_motive` | bool | whether the report describes a caste-based motive (public insult/humiliation, denial of access, forced eviction because of caste — grounded in the SC/ST Act's own enumerated offences, not a generic "harassment" guess). **This raw boolean can be `true` on generic non-caste harassment text** (confirmed via live testing — caste-based insult is a semantic subset of generic insult, hard for a short-phrase embedding model to cleanly separate); don't trust it alone. `legal_guidance` only adds SC/ST Act provisions when this field's confidence clears 80 — always check `confidence_breakdown.caste_based_motive`, not just the boolean. Treat as advisory even above that bar; this is not a legal determination |
| `risk.risk_tier` | `"Low" \| "Medium" \| "High" \| "Critical"` | |
| `risk.risk_score` | int 0-100 | |
| `risk.risk_factors` | string[] | human-readable reasons, e.g. `"Immediate danger detected"`, `"Low understanding confidence — human review recommended"` |
| `risk.response_protocol` | object | `{sla, route, action}` staff-facing triage routing for this `risk_tier` (from `risk.py`'s `RESPONSE_PROTOCOL` table, added 2026-08-24 per Samreen's SLA/routing spec) — e.g. Critical: `{"sla": "Immediate", "route": "ERSS 112 Hard Override", "action": "Auto 112 Dispatch + SP Intercept"}`. Descriptive routing metadata only — nothing in this codebase actually calls ERSS-112 or dispatches police; a human still acts on it, same as `legal_guidance.escalation_contact` |
| `stress_assessment.svi_tier` | `"Low" \| "Moderate" \| "High" \| "Critical"` | Stress Vulnerability Index tier — a *different axis from `risk_tier`*, see below. Deliberately "Moderate" not "Medium" so the two tier sets are never visually confused in the UI |
| `stress_assessment.svi_score` | float 0-100 | |
| `stress_assessment.confidence` | float 0-100 | same 0-100 convention as `incident.confidence`/`risk.confidence` — do not treat as a 0-1 scale |
| `stress_assessment.modalities_used` | string[] | `["text"]` or `["text","voice"]` — tells you whether voice signal actually contributed |
| `stress_assessment.components` | object | `{text_distress_score, voice_stress_score}`, the two 0-100 sub-scores that were fused; `voice_stress_score` is `null` when voice wasn't used |
| `stress_assessment.contributing_factors` | string[] | human-readable reasons, same style as `risk.risk_factors`. Watch for the divergence factor (below) — it's the most actionable one |
| `legal_guidance` | object \| `null` | knowledge-graph lookup: applicable law/section(s), procedural next steps, district escalation contact — see **Legal & escalation guidance** below. `null` when `incident_type` isn't mapped (`"other"`, `"missing_person"`) |
| `citations` | array of `{source, page, similarity}` | grounding evidence actually used in the response; empty if none |
| `top_similarity` | float | best retrieval match score |
| `escalate` | bool | **true** = show "human assistance recommended" UI; frontend should treat this as the primary signal, not risk_tier alone. Three independent triggers, any one is enough: `risk_tier` in Critical/High, `svi_tier` is Critical, or `incident.confidence` is below 60 (this third one is real — a report the system can't reliably classify escalates even if retrieval happened to find high-similarity evidence and Gemini produced a normal-looking answer; found via live adversarial testing, not a corner case to design around) |
| `reason` | string \| null | why it escalated — can concatenate more than one of the three triggers above in a single string (space-separated sentences), not just one |
| `response` | string \| null | the actual message to show the user, in their input language; **null whenever escalate is true and nothing could be generated** |
| `case_id` | int \| null | id of the persisted case (see Case tracking below); **null only for empty/whitespace input**, where nothing is saved |
| `case_status` | string \| null | `"Escalated"` or `"Resolved"` at creation time; can change later via the `/cases` endpoints below |
| `disclosure_level` | `"full" \| "partial" \| "anonymous"` | echoes back what was actually used (the request default is `"full"`) — see **Low-disclosure reporting** below |

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

## Admin authentication

As of 2026-08-23, every endpoint that exposes case data or lets someone
change case state requires an `X-API-Key` header matching `ADMIN_API_KEY`
(set in `.env`, gitignored — ask Maimuna for the current value). Missing or
wrong key returns `401`; if the server has no `ADMIN_API_KEY` configured at
all, admin endpoints fail closed with `503` rather than silently allowing
open access.

**Gated** (send `X-API-Key`): `GET /cases`, `GET /cases/{id}`,
`GET /cases/{id}/related`, `GET /cases/{id}/brief`,
`PATCH /cases/{id}/status`, `GET /stats`, `GET /stats/trend`,
`GET /stats/districts`.

**Not gated, unchanged**: `POST /report`, `POST /sos`,
`POST /report/image`, `POST /report/voice`, `GET /call-options`,
`GET /nearby`, `GET /consent/voice-recording`, `GET /health`, and
`GET /cases/map` — the map endpoint is deliberately public since it
already returns only anonymized pins (coordinates + incident type/risk
tier, never the report content — see `list_case_locations()`'s docstring
in `cases.py`), unlike every other `/cases/*` route.

**Be honest about what this is**: one shared secret, not per-counsellor
accounts, roles, or an audit log of who accessed what. It closes the real
gap that existed (zero access control on case data, including reporter
names/contacts on full-disclosure cases) without pretending to be more
than a hackathon-scale project can realistically finish — see
`consent.py`'s `access_control_status` field, which reflects this
honestly rather than overstating it.

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
  "evidence_path": "evidence/3f9a...c1.png" | null,
  "location": "home" | null,
  "latitude": 17.385 | null,
  "longitude": 78.487 | null,
  "is_sos": false,
  "stress_assessment": { ... } | null,
  "legal_guidance": { ... } | null,
  "disclosure_level": "full",
  "reporter_name": "Priya S" | null,
  "reporter_contact": "9876543210" | null,
  "district": "Hyderabad" | null
}
```

Valid `status` values: `"New"`, `"Under Review"`, `"Escalated"`,
`"In Progress"`, `"Resolved"`, `"Closed"`.

**`stress_assessment` here is the FULL object, including `explainability`
(see SVI section below)** — unlike `/report`/`/sos`, which strip
`explainability` out before returning to the reporter. `GET /cases/*` is the
admin/counsellor-facing surface; this is the intended place to actually
render the per-signal breakdown. `null` for a case created before this
field existed, or one whose pipeline result genuinely had none.

`latitude`/`longitude` are only non-null when the reporter chose to share a
location, and are already rounded to ~100-150m before storage (see the
privacy note under Nearby Help below) — never the exact coordinate.

## Low-disclosure reporting

A reporter isn't required to identify themselves to get a real, fully
processed report — `disclosure_level` on `/report`/`/sos` controls how much
identity/location gets **persisted to the case**, without changing anything
about how the report is processed. Every level gets the full pipeline: real
`incident` classification, `risk`, `stress_assessment` (SVI), and
`legal_guidance`, and `escalate` fires exactly the same way regardless of
disclosure level.

| Level | What's persisted to the case | What's not |
|---|---|---|
| `"full"` (default) | `reporter_name`, `reporter_contact`, precise `latitude`/`longitude` | — |
| `"partial"` | `reporter_contact` (so a counsellor can still follow up) | `reporter_name`, `latitude`/`longitude` |
| `"anonymous"` | — | `reporter_name`, `reporter_contact`, `latitude`/`longitude` |

`district` is available at every level (see the request field above) — it's
a routing hint, not an identifier, so even an anonymous report can still get
a district-level `legal_guidance.escalation_contact`. Redaction happens
server-side in `cases.create_case()`, not just left out of the response — a
frontend bug that accidentally sends `reporter_name` on an anonymous
submission still can't leak it into the case record.

**The honest tradeoff, not solved further here**: a `"partial"`/`"anonymous"`
case genuinely cannot be followed up on the way a `"full"` one can — no name
to reference, no precise location to correlate against, and for
`"anonymous"` specifically, no contact method at all. That's the real cost
of low-disclosure reporting, not a gap to silently paper over. Pitch it
honestly: "you can report anonymously and still get a real risk assessment
and guidance," not "anonymous reports get the same follow-up as identified
ones."

`GET /cases/{id}` and `/cases/{id}/brief` return `disclosure_level`,
`reporter_name`, `reporter_contact` alongside everything else — a
counsellor needs to see the disclosure level before attempting any
follow-up, not discover mid-call that there's no name on file.

## Safety map (real case pins) — **fully functional today**

```
GET /cases/map
```

For a real map view (Leaflet.js + OSM tiles, no API key needed), not the old
decorative mockup. Returns only cases that have a location, and deliberately
**not** the full case object — no `original_text`, `response`, or
`citations`, just enough to place and label a pin:

```json
[
  {
    "id": 33,
    "created_at": "2026-08-21T12:34:35.491807+00:00",
    "incident_type": "harassment",
    "risk_tier": "Critical",
    "latitude": 17.385,
    "longitude": 78.487,
    "location": "street",
    "is_sos": true
  }
]
```

An empty array is a genuine "nobody's shared a location yet," not a bug —
with current test-data volume, don't expect many pins. Registered before
`/cases/{id}` in the route table specifically so `/cases/map` isn't swallowed
as an invalid `case_id`.

## Reasoning trace (the "why" behind a result)

Every `/report` response includes `reasoning_trace` — not new detection
logic, just the same `incident`/`risk`/`citations` data already in the
response, restructured to directly answer "why did Athena decide this?":

```json
{
  "incident_classification": {
    "type": "domestic_violence",
    "confidence": 100.0,
    "confidence_breakdown": {
      "incident_type": 100.0, "threat": 89.12, "injury": 93.29,
      "immediate_danger": 62.92, "relationship": 100.0, "location": 15.01
    }
  },
  "risk_assessment": {
    "tier": "Critical", "score": 100,
    "factors": ["Immediate danger detected", "Physical violence detected", "Threat detected", "Injury reported"]
  },
  "stress_assessment": {
    "tier": "Critical", "score": 85.0, "confidence": 73.73,
    "modalities_used": ["text"],
    "factors": ["Immediate danger reported", "Threat present in report", "Injury reported", "Domestic violence carries elevated baseline distress"]
  },
  "legal_guidance_summary": {
    "provisions_cited": ["Protection of Women from Domestic Violence Act, 2005 — Protection orders (Chapter IV)"],
    "escalation_contact_found": false
  },
  "evidence_used": [
    {"source": "domviolence.pdf", "page": 3, "similarity": 0.8245}
  ]
}
```

`null` only when `incident`/`risk` are both `null` (the empty-input case).

## Stress Vulnerability Index (SVI)

`stress_assessment` on every `/report`/`/sos` response (see `svi.py`). This
is a **different axis from `risk`**, not a rename of it:

- `risk_tier` answers *"how legally/physically dangerous is this
  situation"* — drives escalation.
- `svi_tier` answers *"how much acute distress does this person appear to
  be carrying right now"* — drives triage tone/pacing, e.g. whether a
  human reviewer should route the case to a trauma-informed responder.

They usually move together but aren't the same number — e.g. a calmly
worded report can still carry a highly distressed voice underneath it,
which is exactly the case `stress_assessment` is built to catch.

```json
"stress_assessment": {
  "svi_score": 71.5,
  "svi_tier": "Critical",
  "confidence": 85.04,
  "modalities_used": ["text", "voice"],
  "components": {"text_distress_score": 85.0, "voice_stress_score": 58.0},
  "contributing_factors": [
    "Immediate danger reported",
    "Threat present in report",
    "High pitch variability / voice breaks"
  ]
}
```

**Text-only vs. text+voice**: `voice_features` is optional on the request
(see above) — most reports today are text-only, so `modalities_used` will
usually be `["text"]` and `voice_stress_score` will be `null`. When voice
is present, `confidence` is generally higher (two independent signals to
cross-check instead of one) — text-only confidence is deliberately capped
lower for this reason.

**The divergence flag is the most useful single signal this produces.**
When the text-derived and voice-derived scores disagree sharply,
`contributing_factors` includes an explicit note ("Text and voice-derived
stress signals diverge sharply — possible suppressed distress or a caller
unable to speak freely; recommend human review"). This matters
specifically for a helpline context: a caller might consciously soften
their wording (or be prevented from speaking freely, e.g. someone
listening nearby) while their voice tells a different story. Don't treat
`svi_score` alone as the whole picture — a reviewer should always see
`contributing_factors`.

**Escalation**: `svi_tier: "Critical"` forces `escalate: true` the same way
`risk_tier` in `("Critical", "High")` does — either trigger alone is
enough, and both can fire together (see `reason`, which concatenates
whichever triggered).

**Honesty about calibration**: the voice-side scoring (pitch/pause/rate
deviation from a calm baseline) is a reasonable hackathon-scale heuristic,
not a clinically validated model — same caveat this codebase already
carries elsewhere (e.g. `RETRIEVAL_CONFIDENCE_THRESHOLD`). Don't pitch this
as a validated stress-detection model to judges; pitch it as an
explainable, tunable fusion layer with an honest confidence signal.

### Explainability breakdown (admin/counsellor view only)

`stress_assessment.explainability` gives the exact per-signal breakdown of
which signals pushed `svi_tier` where it landed — every entry's `points`
sum to the axis's score (`components.text_distress_score` /
`.voice_stress_score`), so this is a literal accounting, not a vague
summary:

```json
"explainability": {
  "text_signals": [
    {"signal": "immediate_danger", "label": "Immediate danger reported", "confidence": 67.65, "points": 35},
    {"signal": "threat_present", "label": "Threat present in report", "confidence": 80.66, "points": 15},
    {"signal": "incident_type_baseline", "label": "Domestic violence carries elevated baseline distress", "confidence": 100.0, "points": 20}
  ],
  "voice_signals": [
    {"signal": "pitch_variation", "label": "High pitch variability / voice breaks", "value": 0.85, "threshold": 0.35, "points": 42.5},
    {"signal": "pause_ratio", "label": "Elevated pausing in speech", "value": 0.55, "threshold": 0.15, "points": 12.0, "avg_pause_duration_sec": 2.4}
  ] | null,
  "divergence": {"detected": false, "text_score": 85.0, "voice_score": 58.0, "gap": 27.0} | null
}
```

`text_signals[].confidence` reuses `incident.confidence_breakdown`'s
per-signal numbers directly (same field, same 0-100 calibration) — not a
second, separately-invented confidence scale. Every label is
category-level (`"threat_present detected, 80.66%"`), never the original
report text or a verbatim quote — the same discipline `incident_type` and
`caste_based_motive` already follow elsewhere in this contract.
`pause_ratio`'s entry reports the real measured ratio (and
`avg_pause_duration_sec` when the voice pipeline sent it) rather than a
discrete pause-event count, since nothing in this pipeline currently
computes one — don't display a fabricated event count that isn't backed by
real data.

**This key is deliberately absent from `/report`/`/sos`/`/report/image`/
`/report/voice` responses** — those go straight to the complainant's own
client, and a live psychological-distress readout ("your pitch variability
suggests distress") is not something to show the person who just filed the
report. It's only present in `GET /cases/{id}` and `GET /cases/{id}/brief`
(as `svi_explainability`), the actual admin/counsellor-facing surface. If
you're building the counsellor dashboard, read it from there — if you're
building the reporter-facing UI, you won't see this key and shouldn't need
to.

## Legal & escalation guidance (knowledge graph) — **live** (`kg.py`)

`legal_guidance` on every `/report`/`/sos` response — a lightweight
`networkx` knowledge graph (see `kg.py` for the full tradeoff writeup
against a full graph database), not a flat lookup table, because a
case's applicable provisions come from **two independent signals
converging**: `incident_type`, and whether `caste_based_motive` fired.
Both can add provisions to the same result at once (e.g. a
caste-motivated sexual violence report pulls in BNS *and* SC/ST Act
3(1)(xi)/(xii) together) — that's real multi-hop graph traversal, not
a single-key dict lookup.

```json
"legal_guidance": {
  "applicable_provisions": [
    {
      "act": "Bharatiya Nyaya Sanhita, 2023",
      "section": "General cognizable offence",
      "description": "Physical assault, criminal intimidation, or similar offences reported here are cognizable under the Bharatiya Nyaya Sanhita, 2023 -- police are required to register an FIR without prior magistrate approval.",
      "source": "kg_seed"
    },
    {
      "act": "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
      "section": "Section 3(1)(x)",
      "description": "Intentionally insults or intimidates with intent to humiliate a member of a Scheduled Caste or Scheduled Tribe in any place within public view.",
      "source": "kg_seed"
    }
  ],
  "procedural_next_steps": [
    {"step": 1, "action": "File a complaint (FIR) at the nearest police station..."},
    {"step": 2, "action": "SC/ST Act cases are tried in a Special Court designated for the district under Section 14..."},
    {"step": 3, "action": "A Special Public Prosecutor is appointed for SC/ST Act cases under Section 15."},
    {"step": 4, "action": "You are entitled to legal aid and travel/maintenance expense support... under Section 21 of the SC/ST Act."}
  ],
  "escalation_contact": {
    "district": "Karimnagar", "state": "Telangana",
    "address": "...", "phone": "0878-2244644", "email": "...",
    "contact_person": "D. Laxmi", "contact_person_phone": "9642333464",
    "verification": "manual" | "parsed",
    "source": "kg_seed"
  } | null
}
```

**`escalation_contact.verification`** tells you how this specific
contact's confidence tier: `"manual"` means individually checked against
the source PDF (Telangana's 33 districts, plus a handful of other-state
entries); `"parsed"` means machine-extracted from the national directory
PDF's table structure and spot-checked, not row-by-row hand-verified — see
`district_contacts.py`'s module docstring for the extraction method and
what's excluded. Show this distinction to a counsellor if you're
displaying this contact in a UI — don't present both tiers with identical
visual confidence.

`null` only when `incident_type` isn't mapped in the graph at all
(`"other"`, `"missing_person"`) — a deliberate omission, not a bug; see
`kg.py`'s docstring for why `missing_person` isn't force-mapped to a
provision.

**`source` on every item is `"kg_seed"`**, never `"rag_verified"` — this
distinction is deliberate and matches the same grounding discipline as
`citations` elsewhere in this contract. `"kg_seed"` means it came from a
maintained lookup table (transcribed from real source PDFs, not
invented — see below), not a live RAG retrieval against the ingested
knowledge base. Don't blur the two.

**Data provenance, so you can trust what this actually is**:
- Legal provisions are transcribed directly from the real SC/ST Act
  bare-act text (`data/sources/SCSTpoaact1989.pdf`, now also ingested
  into the RAG knowledge base) — not recalled from general knowledge.
- `escalation_contact` comes from `district_contacts.py`. **554
  districts across 33 states/UTs as of 2026-08-23** — Telangana's 33 (and
  a handful of other pre-existing entries) individually hand-verified
  against `Sakhi-OSC Contact list Updated _list.pdf`
  (`verification: "manual"`), the remaining 518 machine-parsed from the
  national directory PDF's actual table structure via `pdfplumber`
  (`verification: "parsed"` — see above). Nothing here is invented; every
  field traces to what the source PDF actually says. 6 district names
  that collide across different states (e.g. Bilaspur exists in both
  Chhattisgarh and Himachal Pradesh) are deliberately excluded rather
  than guessed at, since `district` has no state qualifier to
  disambiguate them — see `district_contacts.py`'s docstring for the
  full list. An unrecognized (or deliberately-excluded-as-ambiguous)
  district returns `escalation_contact: null`, never a wrong or
  made-up contact.

**`caste_based_motive` is advisory, always** — even when its confidence
clears the bar to add SC/ST Act provisions (80, deliberately set
higher than `INCIDENT_TYPE_CONFIDENCE_FLOOR`'s 60 elsewhere, after
live testing found a real false positive at 76.66% on plain,
non-caste harassment text — see the field table above), this is
routing information for a human reviewer, not a legal determination. Whether a
reporter is legally a member of a Scheduled Caste/Tribe, and whether
the specific facts meet a section's elements, is a legal judgment this
system cannot and should not make on its own. Don't present
`legal_guidance` to a user as "this law applies to you" — present it as
"this may be relevant, a human reviewer should confirm."

## Related cases (honest correlation, not a clustering model)

```
GET /cases/{id}/related?days=30
```

Other cases sharing this case's **location AND incident type** (both, not
either) within the window. Deliberately AND — either field alone is a broad
category (many different households count as `"home"`; many different
people's reports count as `"stalking"`), so matching on just one produces
meaningless noise (two unrelated domestic-violence cases from different
households would "match" purely by crime category). Requiring both together
is a real, meaningfully tighter signal.

**Be honest about what this is when demoing it**: `location` is a place
*type* (`"college_campus"`), not a named real-world location — two related
results share "something happened at a college campus, and it was
stalking," not verified proof of the same physical spot. And this reflects
whatever's actually in the database — with low case volume, don't present
it as if backed by production usage it doesn't have. It's honest either
way: a real match if one exists, an empty list if not.

```json
[
  {
    "case_id": 2,
    "created_at": "2026-08-20T18:03:45+00:00",
    "incident_type": "stalking",
    "location": "college_campus",
    "risk_tier": "Medium"
  }
]
```

404 if the case doesn't exist. `[]` (not an error) if the case has no
location or no incident_type to correlate on, or nothing else matches.

## Escalation brief (for a human reviewer)

```
GET /cases/{id}/brief
```

Everything known about an escalated case, assembled into one summary
instead of making a reviewer reconstruct it from a raw report — risk,
incident details, the response given, evidence, and any related cases
(from the endpoint above) in one object. Also includes `svi_tier`,
`svi_score`, `svi_explainability` (the same object as
`stress_assessment.explainability` above — this is the intended read path
for a counsellor dashboard) and `legal_guidance`. 404 if the case doesn't
exist.

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
  "sos_cases": 0,
  "by_status": {"Escalated": 1},
  "by_risk_tier": {"Critical": 1},
  "by_incident_type": {"domestic_violence": 1},
  "by_language": {"en": 1},
  "by_location": {"home": 1}
}
```

The `by_*` fields are plain `{value: count}` maps — only keys that actually
occur in the data appear (no zero-filled entries for unused categories).

## Trend (for "Harassment ↑ Stalking ↑" style cards)

```
GET /stats/trend            -> last 7 days
GET /stats/trend?days=3     -> custom window
```

```json
{
  "window_days": 7,
  "by_day": {
    "2026-08-14": 0, "2026-08-15": 0, "2026-08-16": 0,
    "2026-08-17": 0, "2026-08-18": 0, "2026-08-19": 1, "2026-08-20": 1
  },
  "current_window_total": 2,
  "previous_window_total": 0,
  "by_incident_type_in_window": {"domestic_violence": 2}
}
```

`by_day` is zero-filled for every calendar day in the window (including
today) so a chart has no gaps. `current_window_total` vs
`previous_window_total` is the "up/down" comparison — with real but low case
volume right now, don't expect dramatic numbers; every value here is a live
query result, not a placeholder.

## Flagged districts (for the admin "flagged districts" panel)

```
GET /stats/districts            -> last 7 days vs the 7 before
GET /stats/districts?days=3     -> custom window, same semantics as /stats/trend
```

Districts whose case count rose meaningfully in the current window vs the
previous one, aggregated from the `district` reporters optionally supply on
`/report`/`/sos` (see the **Report incident** request field above) —
real SQL aggregation, not a prediction model. A district nobody named, or
one that isn't actually rising, doesn't appear:

```json
{
  "window_days": 7,
  "min_cases_to_flag": 3,
  "rising_threshold_ratio": 1.5,
  "flagged": [
    {
      "district": "Hyderabad",
      "current_window_count": 5,
      "previous_window_count": 2,
      "change_ratio": 2.5,
      "incident_type_breakdown": {"stalking": 3, "cyber_harassment": 2}
    },
    {
      "district": "Warangal",
      "current_window_count": 3,
      "previous_window_count": 0,
      "change_ratio": null,
      "incident_type_breakdown": {"domestic_violence": 3}
    }
  ]
}
```

A district is only flagged when **both** hold: at least `min_cases_to_flag`
cases in the current window (an absolute floor, so 1 case doubling to 2
never reads as a "spike"), and either the previous window had zero cases
(any real activity where there was none before is itself the pattern —
`change_ratio` is `null` here, not a divide-by-zero) or the current count is
at least `rising_threshold_ratio` times the previous one. `flagged` is
sorted with the sharpest rises (and any brand-new district) first.
`incident_type_breakdown` is the current-window incident-type counts for
that district — surfaces whether the rise is one repeating incident type
(a possible pattern) or a general increase, without claiming to identify a
specific repeat offender. These are heuristic starting-point thresholds
(same caveat as `risk.py`/`svi.py`'s scoring constants), not calibrated
against real data.

`district` is also on every case object (`/cases`, `/cases/{id}`,
`/cases/{id}/brief`) — `null` when nobody supplied one, otherwise the same
display name (e.g. `"Hyderabad"`) `escalation_contact` resolves to when it's
a known district, or the raw name capitalized when it isn't. It's stored
regardless of `disclosure_level` — see the **Report incident** request
field docs, `district` is a routing hint, not an identifier.

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

## Voice report — **wired but not yet functional, see caveat below**

```
POST http://localhost:8000/report/voice
Content-Type: multipart/form-data

file: <audio>              (required)
language: "en"|"hi"|"te"   (form field, default "hi" — which language the
                             transcription API transcribes in; it needs
                             this chosen up front, it does not auto-detect
                             language from audio)
```

Transcribes the audio via OpenAI's transcription API (`whisper-1`), then
runs the transcribed text through the same pipeline as `/report`. Same
response shape as `/report`, plus the transcription itself so you can show
the user what Athena heard (same principle as `extracted_text` on image
upload):

```json
{
  "transcription": "the text OpenAI transcribed from the audio",
  "incident": { ... }, "risk": { ... }, "citations": [ ... ],
  "escalate": true, "reason": "...", "response": "...",
  "case_id": 6, "case_status": "Escalated"
}
```

**Provider history**: originally built against Bhashini (a Government of
India ASR service, keeping voice data domestic), swapped to OpenAI
2026-08-24 because Bhashini's government approval queue never cleared
before the deadline. This is a real change in the consent story, not just a
vendor swap — see `consent.py` and the section below.

**Caveat — confirm real credits before demoing**: until `OPENAI_API_KEY` in
`.env` belongs to an account with active billing/credits, every call to
this endpoint returns the same fixed placeholder transcription regardless
of what was actually said in the audio, because the underlying API call
fails (e.g. `"You have no credits remaining"`) and silently falls back to
mock data. The endpoint being live means the wiring is done and verified
against the real API, not that voice transcription itself will work for a
demo — confirm a live, non-mock transcription immediately before presenting.

### Consent / data-retention content for a voice-recording screen

```
GET /consent/voice-recording
```

Static policy content — **not** a consent-management system (no per-report
consent tracking, no opt-out enforcement, no automated deletion pipeline).
Exists so the frontend team's consent screen has real content to render
instead of a placeholder. See `consent.py` for the full object and why each
claim in it is checked against what the code actually does, not
aspirational policy language. The honest, load-bearing facts it discloses:

- The recording is saved to disk indefinitely alongside the case — **there
  is no automatic deletion**, checked directly against the codebase (no
  cron/TTL/cleanup exists anywhere in this repo).
- It's sent to **OpenAI** (a US-based transcription API) for transcription —
  the one real third-party transfer that happens, and the only one. This
  means a voice recording briefly leaves India for processing, unlike the
  original Bhashini design — stated plainly to the reporter, not glossed
  over.
- **Case data (including a saved recording's reference) sits behind a
  single shared admin API key as of 2026-08-23** — see **Admin
  authentication** above. Real, but a single shared secret, not
  per-counsellor accounts or an audit log — the policy states this
  honestly rather than overstating it.
- Points the reader at `disclosure_level` (`/report`'s `"partial"`/
  `"anonymous"` modes) as the actual lever for reducing what's kept on a
  case, voice or not.

## Nearby help (real police stations / hospitals) — **fully functional today**

Unlike voice, this one actually works right now, no credentials needed —
free OpenStreetMap data (Overpass API), no API key.

**Option A — bundled into `/report`**: send `latitude`/`longitude` in the
request (see above) and the response includes:

```json
"nearby_help": [
  {
    "name": "Chaderghat Police Station",
    "type": "police_station",
    "phone": "91 40 27854782",
    "address": null,
    "latitude": 17.3779381,
    "longitude": 78.4917299,
    "distance_km": 0.95
  }
]
```

Sorted by distance, up to 5 police stations + 5 hospitals. `phone`/`address`
are `null` when OpenStreetMap doesn't have that data for a given place —
real gaps in crowd-sourced data, not a bug; always null-check before
rendering. `nearby_help` is only present on the response at all when
`latitude`/`longitude` were sent — omit them and there's no key, not an
empty array.

**Option B — standalone, no report needed**: `GET /nearby?latitude=X&longitude=Y&radius_km=3`
— same shape as the array above. Good for a "find help near me" button
anywhere in the app, e.g. paired with the emergency call button, without
requiring someone to file a report first.

**Privacy note, important**: the *lookup* uses whatever precise coordinates
the client sends (accuracy matters for "nearest hospital" to actually be
useful). But if the report gets persisted as a case, only a coordinate
rounded to ~100m is ever stored (`cases.latitude`/`cases.longitude`) — never
the exact value. This is deliberate: an anonymous-reporting safety app
storing someone's exact GPS could effectively de-anonymize them (e.g.
revealing a home address on a domestic violence case). Don't build a
frontend feature that expects to retrieve the *exact* coordinates back from
a saved case — the whole point is that they're not there.

## SOS (one-tap panic button) — **fully functional today**

`POST /sos` — for a panic-button UI element, separate from the normal typed
report flow.

```json
{
  "latitude": 17.384999,
  "longitude": 78.486712,
  "text": null
}
```

All fields optional. `text` defaults to a generic "I need immediate help
right now" phrase if omitted — send actual typed/pre-filled text if you have
it, but don't block the button on the user typing something first, that
defeats the point.

**The important difference from `/report`**: risk is NOT inferred from the
text here. Pressing this button is itself the strongest possible signal of
immediate danger — stronger than anything a classifier could guess from
wording — so every `/sos` call is forced to `risk.risk_tier: "Critical"` and
`escalate: true`, regardless of what the text would otherwise classify as.
Verified this actually overrides (not just happens to agree): a deliberately
vague/neutral test phrase ("I don't know what's going on, everything feels
off today", which classifies with ~0% confidence) still comes back Critical.

Response shape is otherwise identical to `/report`'s case 1-3 shapes,
including `case_id`, `reasoning_trace`, and `nearby_help` (only present when
`latitude`/`longitude` were sent — same as `/report`). Persisted cases from
this endpoint have `is_sos: true`, so a reviewer/dashboard can tell a
manually-triggered panic case apart from a regular escalated report.

`/sos` also accepts the same optional `voice_features`, `district`,
`disclosure_level`, `reporter_name`, `reporter_contact` fields as `/report`,
with identical behavior — see **Low-disclosure reporting** above. An
anonymous SOS press still forces Critical/escalated and still gets
`nearby_help` from whatever coordinates were sent live; it just won't have a
name/contact/precise location on the persisted case afterward.
**Unlike `risk`, `stress_assessment` is NOT force-overridden on `/sos`** —
pressing the button is a deliberate act that forces the danger *tier*
(that's the whole point of a panic button), but `svi_tier` stays a genuine
reading of the caller's apparent state. Overriding it would make the field
meaningless on every SOS case, exactly when a reviewer most wants to know
how the caller actually sounds. Note `/sos` already forces `escalate: true`
regardless of `svi_tier`, so this doesn't change whether an SOS case
escalates — only whether `stress_assessment` stays honest.

## Call options (real numbers for a "Call for help" button) — **fully functional today**

```
GET /call-options                                -> national helplines only
GET /call-options?latitude=X&longitude=Y         -> nearest real station + national helplines
```

```json
[
  { "label": "Nearest Police Station — Chaderghat Police Station", "phone": "91 40 27854782", "source": "nearest_station", "distance_km": 0.95 },
  { "label": "Emergency (Police / Fire / Ambulance)", "phone": "112", "source": "national" },
  { "label": "Police", "phone": "100", "source": "national" },
  { "label": "Women's Helpline", "phone": "181", "source": "national" },
  { "label": "Childline (child in distress)", "phone": "1098", "source": "national" }
]
```

The nearest-station entry only appears when a location was given AND OpenStreetMap actually has a phone number for that station (often it doesn't). The 4 national numbers are always present regardless — real, current, official Indian emergency numbers (verified 2026-08-21), not something invented.

**Important**: this endpoint only returns numbers, it never places a call. The frontend should turn a selected entry's `phone` into a `tel:` link — but always behind an explicit in-app confirmation step ("Call {label}? Cancel / Call Now"), so a live demo never accidentally dials a real number. On mobile, `tel:` links hand off to the device's own phone app; on desktop they generally do nothing, so don't rely on this being testable from a laptop browser during rehearsal.

## What the frontend needs to handle

- `incident`, `risk`, `stress_assessment`, and `legal_guidance` can all be
  `null` (case 4, plus `legal_guidance` alone is also `null` whenever
  `incident_type` is `"other"` or `"missing_person"`) — don't assume any
  of them exist.
- Within a non-null `legal_guidance`, `escalation_contact` is its own
  independent null-check — provisions/steps can be present with
  `escalation_contact: null` (no district given, or an unrecognized one).
- `response` can be `null` even when `escalate` is `false`-adjacent cases don't
  really occur, but always null-check before rendering it.
- Always render based on `escalate`/`reason`, never on HTTP status — this API
  does not use 4xx/5xx for expected failure modes.
- `citations` is always an array (possibly empty), never null/undefined.

## Known limitations (not blockers, just be aware)

- CORS is currently wide open (`allow_origins=["*"]`) — fine for local dev,
  tighten before any real deployment.
- No auth on the endpoint yet.
- `stress_assessment`'s text component (`text_distress_score`) is built
  from the same `incident` fields (`threat_present`, `injury_present`,
  `immediate_danger`, `incident_type`/`confidence`) as `risk`, via a
  different weighting — so it inherits the same known signal-detection
  gaps as `risk` for cases where those underlying fields misfire (see the
  documented romanized Hindi/Telugu and cross-signal embedding-noise
  issues). A case that scores an artificially low `risk_score` for that
  reason will also score an artificially low `text_distress_score`. The
  voice component, when present, is independent of this and isn't
  affected.
- The voice-side scoring in `stress_assessment` (pitch/pause/rate
  deviation from a fixed "calm baseline") is a heuristic starting point
  for the hackathon, not a clinically validated stress-detection model —
  don't pitch it to judges as more than that.
- `legal_guidance` only ever cites the SC/ST Act — deliberate, matching
  the actual target scope (an SC/ST-specific helpline). The detection
  *mechanism* (`caste_based_motive`, via `understanding.py`'s generic
  `detect_signal()`) isn't caste-hardcoded and could extend to another
  protected characteristic later given real source-law text — see the
  scope note in `kg.py`'s module docstring — but nothing beyond SC/ST Act
  is built or planned for this pass.
- `incident.confidence` and `risk.confidence` are the same number right now
  (both come from the understanding step) — don't read them as two
  independent signals yet.
- The app now explicitly supports reports from any age/gender (added a
  `parent` relationship category, broadened the response framing beyond
  "women's safety system" so a child reporting a parent's abuse gets an
  age-appropriate response). **Risk-scoring for this case is fixed as of
  2026-08-23**: the "My father hits me... he beats me almost every day"
  case used to score `risk_tier: Low`, `risk_score: 0` (the signal-level
  embedding-noise issue documented elsewhere in this file) — new
  multi-clause anchor examples in `understanding.py`'s `injury_present`
  fixed it, verified live to now score `risk_tier: High`. Also fixed:
  don't assume cited law always applies to the reporter —
  `domviolence.pdf` (India's PWDVA) is legally scoped to women, and this
  used to be inconsistently disclosed (one live test showed the Act named
  and scoped correctly, another omitted the Act's name entirely). Root
  cause found: the actual "aggrieved person means any woman..." definition
  (PWDVA Section 2(a), verified present in the ingested PDF at page 1) is
  a poor retrieval match for incident-style queries, so it usually isn't
  in the evidence Gemini sees alongside a protection-order provision —
  asking Gemini to "note the scope" left it guessing from training
  knowledge rather than the actual retrieved text. Fixed by stating the
  verified scope directly and mechanically in the system prompt (grounding
  rule 11) rather than depending on retrieval or Gemini's own recall — now
  requires naming the Act by its full name AND stating the women-only
  scope together whenever any cited evidence comes from it, regardless of
  what the specific retrieved chunk says. Verified 4/4 live calls now
  comply (was inconsistent before, ~2/4), with no leakage of the caveat
  into unrelated (non-PWDVA) responses. **Re-verified live 2026-08-25**
  with a fresh native-Hindi protection-order query — Act named in full
  (Hindi + English) with scope stated correctly, still holds.
- **Romanized-script queries can miss the correct source PDF when a much
  larger source exists, even though the same query in native script or
  English retrieves it correctly** — found 2026-08-25 while re-testing
  the rule above. A romanized-Hindi protection-order query
  ("...Mujhe protection order chahiye.") never retrieved `domviolence.pdf`
  (the real PWDVA text) in its top 5 evidence chunks, so the response
  correctly declined to answer the protection-order specifics rather than
  hallucinate — but also never got the chance to cite PWDVA at all. Root
  cause verified: `domviolence.pdf`'s best matching chunk actually scores
  a close 0.8215 similarity (rank #16, vs. the top result's 0.8339) — it's
  not a bad semantic match. `BNS2023.pdf` (656 chunks, by far the largest
  ingested source) fills 12 of the top 16 slots with closely-clustered
  scores, crowding the smaller, more specific source out of `top_k=5`.
  The identical query in native Devanagari or plain English retrieves
  `domviolence.pdf` cleanly in the top 5 (confirmed live) — so this is
  specifically a romanized-script embedding weakness compounding with
  source-size imbalance, the same family of romanized-script fragility
  documented elsewhere in this file, not a new class of bug. **Not fixed**:
  the real fix (e.g. a per-source diversity cap on retrieval ranking)
  touches the shared ranking logic used by every grounded response in the
  system — deliberately not attempted this close to the freeze without
  time to regression-test it against the existing retrieval-confidence
  gate and citation behavior. Failure mode is safe (no hallucination),
  just incomplete for this narrow phrasing pattern.
