"""
ATHENA — API SERVER
============================================================

Thin FastAPI wrapper around pipeline.run_pipeline() so the
frontend can call one HTTP endpoint instead of running Python
directly.

Run with:
    uvicorn app:app --reload --port 8000

Then POST to:
    http://localhost:8000/report
    { "text": "...", "language": null }
"""

import os
import secrets
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from pipeline import run_pipeline
from cases import (
    list_cases,
    list_case_locations,
    get_case,
    update_status,
    escalate_case,
    acknowledge_case,
    set_follow_up_preference,
    save_translation,
    VALID_FOLLOW_UP_PREFERENCES,
    add_case_note,
    get_stats,
    get_trend,
    get_flagged_districts,
    get_related_cases,
    build_escalation_brief,
    VALID_STATUSES,
    VALID_DISCLOSURE_LEVELS,
)
from voice_service import process_voice_to_text
# NOT imported at top level on purpose -- easyocr pulls in opencv/
# scipy/scikit-image, which cost real memory at process startup even
# though EasyOCR's own Reader models are already lazy (see ocr.py).
# Deferred into report_image() below so a deploy that never receives
# an image upload never pays for this chain at all.
from nearby_help import find_nearby_help, get_call_options
from translation import translate_to_english
from consent import get_voice_recording_policy
from nhaa import CHANNELS, DEFAULT_CHANNEL

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================
#
# Minimal, deliberately not a full auth system: a single shared API
# key (set as ADMIN_API_KEY in .env) that the counsellor/admin
# dashboard sends as the X-API-Key header. No per-user accounts, no
# roles, no session tokens -- this closes the actual gap that existed
# (zero access control on case data, including reporter names/contact
# info on full-disclosure cases) without building more than a
# hackathon-scale project can realistically finish and demo reliably.
# A real deployment would want per-counsellor accounts and an audit
# log; this is the honest, bounded fix for right now.
#
# Only gates admin-facing endpoints (/cases/*, /stats*) -- everything
# a complainant's own client calls (/report, /sos, /report/image,
# /report/voice, /call-options, /nearby, /consent/voice-recording,
# /health) stays open, unchanged, exactly as before.

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


def require_admin_key(x_api_key: Optional[str] = Header(None)):
    """
    FastAPI dependency for every admin-facing route below. Fails
    closed: if ADMIN_API_KEY isn't configured on the server at all,
    admin endpoints refuse everything (503) rather than silently
    falling back to open access -- a missing env var should never be
    the thing standing between case data and the public internet.
    secrets.compare_digest avoids leaking the real key's length/value
    through response-time differences on a naive string comparison.
    """

    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Admin endpoints are not available: ADMIN_API_KEY is not configured on this server.",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header.")


def _strip_counsellor_only_fields(result):
    """
    svi.py's stress_assessment.explainability is a per-signal
    psychological-distress breakdown (pitch/pause values, which text
    signals fired) meant for an admin/counsellor reviewing a case, not
    the complainant whose own report this is -- showing a reporter in
    crisis a live readout of "your pitch variability suggests distress"
    is a UX/ethics problem this project doesn't want, even though the
    same detail is exactly what a counsellor needs. persisted in full
    to cases.db regardless (see cases.py) and surfaced via /cases/*.
    Called on every endpoint that returns run_pipeline()'s result
    directly to whoever filed the report.
    """

    stress_assessment = result.get("stress_assessment")

    if stress_assessment:
        stress_assessment.pop("explainability", None)

    return result


# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(title="Athena API")

# Allow the frontend dev server to call this API during the demo.
# Tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _seed_on_startup():
    """
    seed_demo_cases() was already written idempotent (only inserts
    when cases.db has zero rows) specifically for Railway's ephemeral
    filesystem -- every fresh deploy starts from an empty DB -- but
    nothing ever actually called it, so deploys stayed empty until
    real reports came in. Cheap: no LLM calls, all local computation.
    """
    import seed_data

    seed_data.seed_demo_cases()


# ============================================================
# REQUEST MODEL
# ============================================================

class VoiceFeatures(BaseModel):
    """
    Pre-extracted voice signal, fused with text into stress_assessment
    (see svi.py). Feature extraction itself happens upstream in the
    voice pipeline -- this is just the receiving contract. The three
    required fields are what's assumed available today; the two
    optional ones let the voice team add signal later without a
    contract change.
    """

    pitch_variation: float
    pause_ratio: float
    speech_rate_wpm: float
    avg_pause_duration_sec: Optional[float] = None
    voice_energy_variability: Optional[float] = None


class ReportRequest(BaseModel):
    text: str
    language: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    voice_features: Optional[VoiceFeatures] = None
    district: Optional[str] = None
    disclosure_level: Optional[str] = "full"
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    channel: Optional[str] = DEFAULT_CHANNEL


class StatusUpdateRequest(BaseModel):
    status: str
    note: Optional[str] = None


class EscalateRequest(BaseModel):
    note: Optional[str] = None


class NoteRequest(BaseModel):
    note: str


class FollowUpRequest(BaseModel):
    preference: str
    note: Optional[str] = None


class SosRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    text: Optional[str] = None
    voice_features: Optional[VoiceFeatures] = None
    district: Optional[str] = None
    disclosure_level: Optional[str] = "full"
    reporter_name: Optional[str] = None
    reporter_contact: Optional[str] = None
    channel: Optional[str] = DEFAULT_CHANNEL


def _validate_disclosure_level(disclosure_level):
    """
    Shared 400-on-typo check for /report and /sos -- same pattern as
    PATCH /cases/{id}/status validating against VALID_STATUSES.
    cases.create_case() also re-checks this (defense in depth, single
    source of truth in cases.py), but failing fast here with a clear
    400 is friendlier than letting a typo surface as a 500 from
    inside case creation.
    """

    if disclosure_level not in VALID_DISCLOSURE_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"disclosure_level must be one of {VALID_DISCLOSURE_LEVELS}",
        )


# ============================================================
# ROUTES
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/consent/voice-recording")
def consent_voice_recording():
    """
    Static policy content for a "what happens to my voice recording"
    consent screen -- how long it's stored, whether it's sent anywhere
    beyond this report, who can access it. Not a consent-management
    system (no per-report consent tracking, no opt-out enforcement) --
    just real content for the frontend team's consent screen to
    display instead of a placeholder. See consent.py for what backs
    this and why each claim is accurate to the current system, not
    aspirational.
    """

    return get_voice_recording_policy()


# Rounding precision for any coordinates that get persisted to a
# case -- ~3 decimal places is roughly 100m. Real-world safety-app
# precedent: an anonymous-reporting platform storing a reporter's
# exact GPS coordinates can effectively de-anonymize them (e.g.
# revealing a home address on a domestic violence case). The nearby-
# help lookup below still uses the precise coordinates the client
# sent -- only what gets written to cases.db is rounded.
LOCATION_ROUNDING_DECIMALS = 3


@app.post("/report")
def report(payload: ReportRequest):
    """
    Run one incident report through the full Athena pipeline
    and return the structured, grounded result.

    If latitude/longitude are provided (only if the user chose to
    share their location), the response also includes real nearby
    police stations/hospitals under `nearby_help` -- looked up using
    the precise coordinates, but only a rounded version is ever
    persisted to the case (see LOCATION_ROUNDING_DECIMALS above), and
    only when disclosure_level is "full" (see cases.create_case()).

    disclosure_level ("full" | "partial" | "anonymous", default
    "full") controls what gets persisted to the case, not what this
    response includes -- nearby_help still uses whatever coordinates
    were sent, same as always; only the stored case is affected. See
    API_CONTRACT.md's low-disclosure section for what each level
    actually does and the follow-up tradeoff it carries.
    """

    _validate_disclosure_level(payload.disclosure_level)

    rounded_lat = (
        round(payload.latitude, LOCATION_ROUNDING_DECIMALS)
        if payload.latitude is not None else None
    )
    rounded_lon = (
        round(payload.longitude, LOCATION_ROUNDING_DECIMALS)
        if payload.longitude is not None else None
    )

    result = run_pipeline(
        payload.text,
        language=payload.language,
        latitude=rounded_lat,
        longitude=rounded_lon,
        voice_features=(
            payload.voice_features.model_dump()
            if payload.voice_features else None
        ),
        district=payload.district,
        disclosure_level=payload.disclosure_level,
        reporter_name=payload.reporter_name,
        reporter_contact=payload.reporter_contact,
        channel=payload.channel or DEFAULT_CHANNEL,
    )

    if payload.latitude is not None and payload.longitude is not None:
        result["nearby_help"] = find_nearby_help(
            payload.latitude, payload.longitude
        )

    return _strip_counsellor_only_fields(result)


DEFAULT_SOS_TEXT = "I need immediate help right now, I am in danger."


@app.post("/sos")
def sos(payload: SosRequest):
    """
    One-tap SOS. Unlike /report, risk/escalation is NOT inferred from
    text -- pressing this button is itself the strongest possible
    signal of immediate danger, so the resulting case is always
    forced Critical/Escalated regardless of what the (often short or
    generic) SOS text would otherwise classify as (see
    pipeline._apply_sos_override).

    latitude/longitude are optional (geolocation can be denied or
    unavailable even in a real emergency) but are what make this
    actually useful -- when given, the response includes real nearby
    police stations/hospitals, same as /report. `text` is optional;
    if the caller has nothing typed/pre-filled, a default SOS phrase
    is used so the pipeline still has something to classify and
    retrieve evidence against.

    disclosure_level applies the same way it does on /report -- see
    that endpoint's docstring.
    """

    _validate_disclosure_level(payload.disclosure_level)

    text = payload.text or DEFAULT_SOS_TEXT

    rounded_lat = (
        round(payload.latitude, LOCATION_ROUNDING_DECIMALS)
        if payload.latitude is not None else None
    )
    rounded_lon = (
        round(payload.longitude, LOCATION_ROUNDING_DECIMALS)
        if payload.longitude is not None else None
    )

    result = run_pipeline(
        text,
        latitude=rounded_lat,
        longitude=rounded_lon,
        is_sos=True,
        voice_features=(
            payload.voice_features.model_dump()
            if payload.voice_features else None
        ),
        district=payload.district,
        disclosure_level=payload.disclosure_level,
        reporter_name=payload.reporter_name,
        reporter_contact=payload.reporter_contact,
        channel=payload.channel or DEFAULT_CHANNEL,
    )

    if payload.latitude is not None and payload.longitude is not None:
        result["nearby_help"] = find_nearby_help(
            payload.latitude, payload.longitude
        )

    return _strip_counsellor_only_fields(result)


@app.post("/cases/{case_id}/follow-up")
def post_follow_up_preference(case_id: int, payload: FollowUpRequest):
    """
    The reporter's own answer to "how is it safe to contact you?",
    submitted from the confirmation screen straight after filing.

    Public on purpose -- the person answering this has just filed a
    report and has no counsellor key -- which is why it is deliberately
    write-only and one-shot (see cases.set_follow_up_preference for the
    threat model). It never returns the case: echoing case content back
    to an unauthenticated caller would turn a preference form into a
    way to read anyone's report by guessing an id. Callers get a bare
    acknowledgement and nothing else.
    """

    result = set_follow_up_preference(
        case_id, payload.preference, note=payload.note
    )

    if result == "invalid":
        raise HTTPException(
            status_code=400,
            detail=f"preference must be one of {VALID_FOLLOW_UP_PREFERENCES}",
        )

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Case not found")

    if result == "already_set":
        raise HTTPException(
            status_code=409,
            detail="A contact preference is already recorded for this case.",
        )

    return {"status": "saved", "case_id": case_id}


@app.get("/call-options")
def call_options(latitude: Optional[float] = None, longitude: Optional[float] = None):
    """
    Real numbers a "Call for help" button can offer -- the nearest
    real police station (if location is given and OSM has a phone
    number for it) plus India's national emergency/helpline numbers,
    which are always included regardless of location. See
    nearby_help.get_call_options for the full reasoning.

    This endpoint only returns numbers -- it never places a call.
    The frontend should always show an explicit confirmation step
    before turning any of these into a `tel:` link, so a live demo
    never accidentally dials a real number.
    """

    return get_call_options(latitude, longitude)


@app.get("/nearby")
def nearby(latitude: float, longitude: float, radius_km: float = 3):
    """
    Standalone lookup: real nearby police stations/hospitals, not
    tied to filing a report at all -- for a "find help near me"
    button anywhere in the app. Nothing here is persisted.
    """

    return find_nearby_help(latitude, longitude, radius_km=radius_km)


@app.post("/report/image")
async def report_image(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
):
    """
    Evidence upload: OCR a screenshot (e.g. threatening messages)
    and run the extracted text through the exact same pipeline as
    a typed report. The image is saved and linked to the resulting
    case so the original evidence stays available.

    `language` is a hint for OCR script selection ("en"/"hi"/"te",
    default "en") -- separate from incident-language auto-detection,
    which still runs on the extracted text same as normal.
    """

    image_bytes = await file.read()

    extension = os.path.splitext(file.filename or "")[1] or ".jpg"
    saved_name = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(EVIDENCE_DIR, saved_name)

    with open(saved_path, "wb") as f:
        f.write(image_bytes)

    from ocr import extract_text  # see the deferred-import note near the top imports

    extracted_text = extract_text(image_bytes, language=language or "en")

    if not extracted_text:

        return {
            "incident": None,
            "risk": None,
            "citations": [],
            "top_similarity": 0.0,
            "escalate": True,
            "reason": "No readable text found in the uploaded image.",
            "response": None,
            "case_id": None,
            "case_status": None,
            "extracted_text": "",
        }

    result = run_pipeline(extracted_text, evidence_path=saved_path)
    result["extracted_text"] = extracted_text

    return _strip_counsellor_only_fields(result)


@app.post("/report/voice")
async def report_voice(
    file: UploadFile = File(...),
    language: str = Form("hi"),
):
    """
    Voice report: transcribes spoken audio via Bhashini (through
    voice_service.py) and runs the transcribed text through the
    exact same pipeline as a typed report.

    `language` selects which language Bhashini transcribes in
    ("en"/"hi"/"te", default "hi") -- Bhashini needs this chosen up
    front, it doesn't auto-detect the spoken language from audio the
    way Whisper does (see API_CONTRACT.md).

    NOTE: until real BHASHINI_USER_ID/BHASHINI_API_KEY credentials
    are set in .env, voice_service.py's ASR call fails and silently
    falls back to a fixed placeholder transcription regardless of
    what was actually said -- this endpoint being live doesn't mean
    voice transcription itself is live yet.

    Calls process_voice_to_text() directly rather than going through
    run_athena_voice_pipeline()'s callback wrapper -- that wrapper
    only returns backend_pipeline_func's result when a callback is
    given, with no way to also get the transcription back out, so
    calling the underlying ASR function directly (same pattern as
    the OCR endpoint above) is what actually lets us return both.

    Also runs the saved audio through voice_features.py to feed
    svi.py's voice-fusion scoring (pitch_variation, pause_ratio,
    speech_rate_wpm) -- previously this endpoint transcribed the audio
    and then discarded it, so every voice report was scored on text
    alone even though svi.py has had voice-fusion logic sitting ready
    and unused since 2026-08-24. librosa is imported lazily here, same
    reasoning as easyocr above: it pulls in numba/llvmlite, real
    memory at process startup that a deploy receiving zero voice
    uploads shouldn't have to pay for. A feature-extraction failure
    (corrupt audio, a clip too short for reliable pitch tracking) never
    blocks the report -- extract_voice_features() returns None rather
    than raising, and run_pipeline() already treats voice_features=None
    as the normal text-only case.
    """

    audio_bytes = await file.read()

    extension = os.path.splitext(file.filename or "")[1] or ".wav"
    saved_name = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(EVIDENCE_DIR, saved_name)

    with open(saved_path, "wb") as f:
        f.write(audio_bytes)

    transcription = process_voice_to_text(saved_path, language)

    from voice_features import extract_voice_features
    voice_features = extract_voice_features(saved_path, transcript=transcription)

    result = run_pipeline(
        transcription,
        evidence_path=saved_path,
        channel="14566_voice",
        voice_features=voice_features,
    )
    result["transcription"] = transcription

    return _strip_counsellor_only_fields(result)


@app.get("/stats", dependencies=[Depends(require_admin_key)])
def get_case_stats():
    """
    Real aggregate counts over every case -- total, escalated, by
    status/risk tier/incident type/language. For dashboard cards
    that should show actual numbers instead of hardcoded demo ones.
    """

    return get_stats()


@app.get("/stats/trend", dependencies=[Depends(require_admin_key)])
def get_case_trend(days: int = 7):
    """
    Day-by-day case counts and incident-type breakdown for the last
    `days` days vs the window before that. ?days= to change the
    window (default 7).
    """

    return get_trend(days=days)


@app.get("/stats/districts", dependencies=[Depends(require_admin_key)])
def get_case_flagged_districts(days: int = 7):
    """
    Districts with a week-over-week case-count rise, each with an
    incident-type breakdown for the current window -- the "flagged
    districts" panel data for the admin dashboard. Real aggregation
    over the district reporters supplied at report time (see
    cases.create_case()), not a prediction -- a quiet district or one
    nobody named simply doesn't appear. ?days= changes the window
    (default 7, matching /stats/trend). See get_flagged_districts()'s
    docstring for exactly what "flagged" requires.
    """

    return get_flagged_districts(days=days)


@app.get("/cases", dependencies=[Depends(require_admin_key)])
def get_cases(status: Optional[str] = None):
    """
    List cases, most recent first. Optional ?status= filter, e.g.
    /cases?status=Escalated
    """

    return list_cases(status=status)


@app.get("/cases/map")
def get_case_map_locations():
    """
    Real pins for a safety map -- coordinates + incident type/risk
    tier only, deliberately not the full case (see
    list_case_locations' docstring). Registered before
    /cases/{case_id} so "map" is never swallowed as a case_id path
    param.
    """

    return list_case_locations()


@app.get("/cases/{case_id}", dependencies=[Depends(require_admin_key)])
def get_case_by_id(case_id: int):

    case = get_case(case_id)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return case


@app.get("/cases/{case_id}/related", dependencies=[Depends(require_admin_key)])
def get_case_related(case_id: int, days: int = 30):
    """
    Other cases sharing this case's location and/or incident type
    within the last `days` days. Real query over real fields, not a
    clustering model -- an empty list is a genuine "nothing found",
    not a bug.
    """

    related = get_related_cases(case_id, days=days)

    if related is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return related


@app.get("/cases/{case_id}/brief", dependencies=[Depends(require_admin_key)])
def get_case_brief(case_id: int):
    """
    Human-reviewer-facing escalation brief: everything known about
    the case plus any related cases, assembled into one summary
    instead of making a reviewer piece it together themselves.

    If the report came in a language other than English and hasn't been
    translated yet, an English rendering is generated here -- on first
    open, once per case, cached on the case afterwards. Done lazily on
    purpose: it's a counsellor-only reading aid, so making a reporter
    in distress wait on an extra model call to produce it would be the
    wrong trade (see translation.py). A failure is non-fatal -- the
    brief returns with the original text alone, which is the
    authoritative version regardless.
    """

    brief = build_escalation_brief(case_id)

    if brief is None:
        raise HTTPException(status_code=404, detail="Case not found")

    if not brief.get("summary_translated"):

        translated = translate_to_english(
            brief.get("summary"),
            source_language=brief.get("language"),
        )

        if translated:
            save_translation(case_id, translated)
            brief["summary_translated"] = translated

    return brief


@app.patch("/cases/{case_id}/status", dependencies=[Depends(require_admin_key)])
def patch_case_status(case_id: int, payload: StatusUpdateRequest):
    """
    Move a case to a new status, e.g. "Under Review" -> "Resolved".
    Logged to the case's timeline; optional payload.note is attached
    to that log entry.
    """

    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {VALID_STATUSES}",
        )

    case = update_status(case_id, payload.status, note=payload.note)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return case


@app.post("/cases/{case_id}/escalate", dependencies=[Depends(require_admin_key)])
def post_case_escalate(case_id: int, payload: EscalateRequest):
    """
    The "Escalate now" action: sets status to "Escalated", logs it as
    a distinct timeline event, and returns the district's escalation
    contact (if the case has a known district on file) so the
    counsellor sees exactly who to notify without a separate lookup.
    """

    result = escalate_case(case_id, note=payload.note)

    if result is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return result


@app.post("/cases/{case_id}/acknowledge", dependencies=[Depends(require_admin_key)])
def post_case_acknowledge(case_id: int):
    """
    Marks a case as reviewed by a counsellor -- distinct from status,
    so a stalled Escalated case that nobody has actually opened yet
    is visible as such (see cases.acknowledge_case docstring).
    """

    case = acknowledge_case(case_id)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return case


@app.post("/cases/{case_id}/notes", dependencies=[Depends(require_admin_key)])
def post_case_note(case_id: int, payload: NoteRequest):
    """
    Add a counsellor free-text note to a case's timeline, e.g. context
    from a follow-up call that isn't captured anywhere else.
    """

    case = add_case_note(case_id, payload.note)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return case


# ============================================================
# STATIC FRONTEND
# ============================================================
#
# Mounted last, after every API route above -- Starlette matches routes
# in registration order, so /report, /cases, etc. are always resolved
# by the real handlers first and only an unmatched path falls through
# to a static file lookup. Deliberately points at web/ (a folder
# containing only the public frontend files -- index.html [the
# WhatsApp-style demo], dashboard.html [the counsellor view],
# athena.css/js, demo_audio/) rather than the repo root, so .env,
# cases.db, chroma_db/, and the source PDFs are never reachable over
# HTTP even by path-guessing. html=True serves web/index.html for "/".
from fastapi.staticfiles import StaticFiles  # noqa: E402

app.mount("/", StaticFiles(directory="web", html=True), name="web")
