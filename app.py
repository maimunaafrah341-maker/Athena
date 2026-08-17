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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pipeline import run_pipeline


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
