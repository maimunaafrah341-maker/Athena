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

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline import run_pipeline
from cases import list_cases, get_case, update_status, VALID_STATUSES


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
