# ============================================================
# ATHENA — NHAA DOCKET BINDING
# ============================================================

"""
Binds this module's own SVI/risk output to a docket identifier in
the shape the National Helpline Against Atrocities (14566) already
uses -- NHAA issues a docket number for every complaint under the
PoA Act 1989 / PCR Act 1955 across its five channels (14566 voice,
IVRS, Integrated Portal, chatbot, mobile app). This project doesn't
call any real NHAA system (no public API exists to hit) -- it's a
service layer that runs alongside NHAA's existing intake, attaching
a real-time Stress Vulnerability Index to the same docket concept
without touching those channels.
"""

import datetime
import uuid

CHANNELS = (
    "14566_voice",
    "ivrs",
    "portal",
    "chatbot",
    "mobile_app",
)

DEFAULT_CHANNEL = "portal"

# Risk tiers that warrant immediate human follow-up, not just a
# logged record -- same High/Critical bar pipeline.py already uses
# to decide needs_human_escalation.
ESCALATING_CATEGORIES = ("High", "Critical")


def create_nhaa_docket(channel, svi_score, risk_category):
    """
    Create a docket record binding one processed report to a
    channel + its SVI outcome.

    channel : one of CHANNELS, falls back to DEFAULT_CHANNEL if not
    recognized (an unrecognized channel string shouldn't block
    docket creation mid-triage -- it just isn't visually distinct
    in the channel selector).
    svi_score : svi.py's assess_stress()["svi_score"] (0-100).
    risk_category : svi.py's assess_stress()["svi_tier"] (Low /
    Moderate / High / Critical).
    """

    if channel not in CHANNELS:
        channel = DEFAULT_CHANNEL

    return {
        "docket_id": f"NHAA-{datetime.date.today().year}-{uuid.uuid4().hex[:8].upper()}",
        "channel": channel,
        "svi_score": svi_score,
        "risk_category": risk_category,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "escalated" if risk_category in ESCALATING_CATEGORIES else "logged",
    }
