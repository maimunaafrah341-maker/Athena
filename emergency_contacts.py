# ============================================================
# ATHENA — DETERMINISTIC EMERGENCY CONTACT SURFACING
# ============================================================

"""
Attaches real, verified helpline numbers to a response by risk/stress
tier -- NOT dependent on whether the reporter shared a location, and
NOT dependent on whether retrieval.py happened to surface a chunk
mentioning them.

Why this exists: app.py's /report only attaches nearby_help.NATIONAL_
HELPLINES when the reporter shares latitude/longitude (that block
lives inside `if payload.latitude is not None and payload.longitude
is not None`). That's correct for the *nearby police station* lookup,
which genuinely needs coordinates -- but it means a Critical-risk,
no-location-shared report (the common case for anonymous/partial
disclosure) currently gets zero national helplines attached at all,
regardless of how dangerous it is. A judge caught exactly this gap:
a risk label isn't the same thing as an actual alert.

Reuses nearby_help.NATIONAL_HELPLINES rather than redefining those
four numbers here -- single source of truth, same reasoning this
codebase already applies everywhere else. Adds two new ones
(KIRAN, NCW Women Helpline) that nearby_help.py doesn't carry,
verified against the actual ingested source PDFs, not general
knowledge:
  - KIRAN: kiran_helpline_factsheet.pdf's own "how to dial"
    instructions state 1800-599-0019 (repeated twice); one body
    paragraph in the same PDF states 1800-500-0019 once, apparently a
    typo in the source itself -- going with the number given twice
    and used as the actual dial instruction.
  - NCW Women Helpline: ncw_women_helpline_factsheet.pdf -- 14490
    (short code), backed by 7827170170.
"""

from nearby_help import NATIONAL_HELPLINES as GENERAL_NATIONAL_HELPLINES

EXTRA_HELPLINES = {
    "ncw_women_helpline": {
        "label": "National Commission for Women Helpline",
        "phone": "14490",
        "source": "national",
    },
    "kiran_mental_health": {
        "label": "KIRAN Mental Health Rehabilitation Helpline",
        "phone": "1800-599-0019",
        "source": "national",
    },
}


def get_deterministic_contacts(risk_tier, svi_tier, is_sos=False, escalate=False):
    """
    Real contacts to attach to a response, chosen by risk_tier/svi_tier/
    is_sos/escalate -- always the same set for the same inputs,
    regardless of whether a location was shared or what retrieval.py
    happened to find.

    Layered rather than all-or-nothing: Critical risk (or SOS) gets the
    full general emergency set; High/Medium get the women's helpline
    numbers; svi_tier Critical/High adds KIRAN regardless of risk_tier,
    since a caller can be in acute psychological distress without an
    immediate physical-safety trigger (and this is exactly the path
    the planned suicidal-ideation detector will also feed into).

    escalate covers the case none of the tiers alone catch: pipeline.py
    already escalates to a human on a THIRD, independent trigger --
    understanding.py simply not being confident it understood the
    report at all (see run_pipeline's understanding_escalation) -- which
    can land Low/Low on both tiers while still being a real, uncertain
    situation a human needs to look at. Found via live testing: a
    genuinely ambiguous report ("I don't know what's going on, I'm
    scared") escalates correctly but was showing zero contacts, exactly
    the "risk label without an actual alert" gap flagged in review.
    Escalated-for-any-reason gets at least a baseline safety net even
    when no tier condition above already added one.
    """

    contacts = []

    if is_sos or risk_tier == "Critical":
        contacts += GENERAL_NATIONAL_HELPLINES

    elif risk_tier == "High":
        contacts += [
            c for c in GENERAL_NATIONAL_HELPLINES
            if c["phone"] in ("112", "181")
        ]
        contacts.append(EXTRA_HELPLINES["ncw_women_helpline"])

    elif risk_tier == "Medium":
        contacts.append(EXTRA_HELPLINES["ncw_women_helpline"])

    if svi_tier in ("Critical", "High"):
        contacts.append(EXTRA_HELPLINES["kiran_mental_health"])

    if escalate and not contacts:
        contacts += [
            c for c in GENERAL_NATIONAL_HELPLINES
            if c["phone"] == "181"
        ]
        contacts.append(EXTRA_HELPLINES["ncw_women_helpline"])

    # De-dupe by phone number, preserving first-seen order (e.g.
    # Critical risk + Critical stress both requesting 181/KIRAN).
    seen = set()
    deduped = []
    for contact in contacts:
        if contact["phone"] not in seen:
            seen.add(contact["phone"])
            deduped.append(contact)

    return deduped
