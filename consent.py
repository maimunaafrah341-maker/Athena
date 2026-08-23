# ============================================================
# ATHENA — CONSENT & DATA-RETENTION POLICY
# ============================================================

"""
A static, honest description of what actually happens to a reporter's
voice recording today -- not a full consent-management system (no
per-user consent tracking, no opt-out enforcement, no automated
deletion pipeline). The frontend team builds the actual consent
screen; this just gives it real content to render instead of a
placeholder.

Every claim below is checked against what the code actually does as
of 2026-08-23, not aspirational policy language:
- /report/voice (app.py) saves the uploaded audio to EVIDENCE_DIR
  ("evidence/") under a random filename, referenced by the case's
  evidence_path -- same mechanism /report/image uses for screenshots.
- voice_service.py sends that audio (base64-encoded) to Bhashini
  (dhruva-api.bhashini.gov.in, a Government of India ASR service) for
  transcription. This is the one real third-party transfer that
  happens.
- Nothing in this codebase deletes or expires evidence files -- no
  cron job, no TTL, no cleanup routine exists anywhere in the repo
  (checked directly, not assumed).
- app.py has no authentication/access-control layer at all (CORS is
  wide open). "Who can access it" is answered honestly below rather
  than implying a protection that doesn't exist yet.

If any of these mechanics change (deletion gets implemented, an auth
layer gets added, a different ASR provider is used), this object must
be updated to match -- don't let it drift into describing an aspirational
system instead of the real one.
"""


VOICE_RECORDING_POLICY = {
    "what_happens_to_your_recording": [
        "Your voice recording is saved as part of your case, so a "
        "counsellor reviewing your report can hear the original audio, "
        "not just a text version of what was said.",
        "It is sent to Bhashini, a Government of India language service, "
        "to convert your speech into text so Athena can process your "
        "report. This transfer happens for every voice report -- it's "
        "required to transcribe what you said.",
    ],
    "retention": {
        "how_long_stored": (
            "Indefinitely alongside your case record. There is currently "
            "no automatic deletion after a fixed period."
        ),
        "deletion_on_request": (
            "Not yet available as a self-service action. Contact the "
            "helpline directly if you want a specific recording deleted."
        ),
    },
    "used_beyond_this_report": {
        "sent_to_third_parties": True,
        "third_parties": [
            {
                "name": "Bhashini (Government of India ASR service)",
                "purpose": "Speech-to-text transcription of your report only.",
            }
        ],
        "used_for_training_or_other_purposes": False,
        "note": (
            "Your recording is not currently used for anything beyond "
            "processing this specific report and transcribing it."
        ),
    },
    "who_can_access_it": {
        "summary": (
            "Your case record, including a link to the saved recording, "
            "is accessible through this helpline's case-review system."
        ),
        "access_control_status": (
            "A dedicated access-control layer restricting this "
            "specifically to authorized counsellors has not been built "
            "yet. This is a real, current limitation, not a guarantee of "
            "restricted access -- stated honestly rather than implying a "
            "protection that doesn't exist."
        ),
    },
    "your_choices": {
        "can_report_without_voice": True,
        "can_report_anonymously": True,
        "note": (
            "You can submit a text-only report instead, and/or set "
            "disclosure_level to \"partial\" or \"anonymous\" on your "
            "report to limit how much identifying information is kept "
            "with your case -- see the Low-disclosure reporting section "
            "of the API contract."
        ),
    },
    "last_updated": "2026-08-23",
}


def get_voice_recording_policy():
    """
    Returns the static voice-recording consent/retention policy.
    A function (not just a module-level constant import) so the
    frontend-facing endpoint in app.py has one clear call site to wire
    up, and so this can grow into something that varies by
    deployment/region later without changing the API shape.
    """

    return VOICE_RECORDING_POLICY
