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
import uuid
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline import run_pipeline
from cases import (
    list_cases,
    get_case,
    update_status,
    get_stats,
    get_trend,
    get_related_cases,
    build_escalation_brief,
    VALID_STATUSES,
)
from voice_service import process_voice_to_text
from ocr import extract_text

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)


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


# ============================================================
# REQUEST MODEL
# ============================================================

class ReportRequest(BaseModel):
    text: str
    language: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: str


# ============================================================
# ROUTES
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/report")
def report(payload: ReportRequest):
    """
    Run one incident report through the full Athena pipeline
    and return the structured, grounded result.
    """

    return run_pipeline(
        payload.text,
        language=payload.language,
    )


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

    return result


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
    """

    audio_bytes = await file.read()

    extension = os.path.splitext(file.filename or "")[1] or ".wav"
    saved_name = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(EVIDENCE_DIR, saved_name)

    with open(saved_path, "wb") as f:
        f.write(audio_bytes)

    transcription = process_voice_to_text(saved_path, language)

    result = run_pipeline(transcription, evidence_path=saved_path)
    result["transcription"] = transcription

    return result


@app.get("/stats")
def get_case_stats():
    """
    Real aggregate counts over every case -- total, escalated, by
    status/risk tier/incident type/language. For dashboard cards
    that should show actual numbers instead of hardcoded demo ones.
    """

    return get_stats()


@app.get("/stats/trend")
def get_case_trend(days: int = 7):
    """
    Day-by-day case counts and incident-type breakdown for the last
    `days` days vs the window before that. ?days= to change the
    window (default 7).
    """

    return get_trend(days=days)


@app.get("/cases")
def get_cases(status: Optional[str] = None):
    """
    List cases, most recent first. Optional ?status= filter, e.g.
    /cases?status=Escalated
    """

    return list_cases(status=status)


@app.get("/cases/{case_id}")
def get_case_by_id(case_id: int):

    case = get_case(case_id)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return case


@app.get("/cases/{case_id}/related")
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


@app.get("/cases/{case_id}/brief")
def get_case_brief(case_id: int):
    """
    Human-reviewer-facing escalation brief: everything known about
    the case plus any related cases, assembled into one summary
    instead of making a reviewer piece it together themselves.
    """

    brief = build_escalation_brief(case_id)

    if brief is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return brief


@app.patch("/cases/{case_id}/status")
def patch_case_status(case_id: int, payload: StatusUpdateRequest):
    """
    Move a case to a new status, e.g. "Under Review" -> "Resolved".
    """

    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {VALID_STATUSES}",
        )

    case = update_status(case_id, payload.status)

    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    return case
