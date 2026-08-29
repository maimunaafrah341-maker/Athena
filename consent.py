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
of 2026-08-29, not aspirational policy language:
- /report/voice (app.py) saves the uploaded audio to EVIDENCE_DIR
  ("evidence/") under a random filename, referenced by the case's
  evidence_path -- same mechanism /report/image uses for screenshots.
- voice_service.py sends that audio to Groq's hosted Whisper API
  (api.groq.com, a US company) for transcription -- swapped from
  OpenAI 2026-08-29 because OpenAI's transcription API needed a
  funded account that never happened, and Groq's free tier actually
  works. Falls back to OpenAI's transcription API only if a
  OPENAI_API_KEY is configured and the Groq call fails; falls back to
  a fixed placeholder transcript if neither is available. This is the
  one real third-party transfer that happens either way. Originally
  built against Bhashini (a Government of India ASR service, domestic
  transfer only); every provider swap since (OpenAI 2026-08-24, Groq
  2026-08-29) has kept the same real change in the privacy story --
  recordings leave India for processing -- stated plainly below
  rather than glossed over.
- Nothing in this codebase deletes or expires evidence files -- no
  cron job, no TTL, no cleanup routine exists anywhere in the repo
  (checked directly, not assumed).
- app.py gates admin-facing endpoints (/cases/*, /stats*) behind a
  single shared API key as of 2026-08-23 -- real, but a minimal
  single-shared-secret check, not per-counsellor accounts, roles, or
  an audit log. "Who can access it" is answered honestly below rather
  than overstating what this actually is.

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
        "It is sent to Groq (a US-based AI company) to convert your "
        "speech into text so Athena can process your report -- and, in "
        "the rare case that fails, to OpenAI (also US-based) instead. "
        "This transfer happens for every voice report -- it's required "
        "to transcribe what you said, and it means your recording "
        "briefly leaves India for processing.",
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
                "name": "Groq (transcription API, United States)",
                "purpose": "Speech-to-text transcription of your report (primary).",
            },
            {
                "name": "OpenAI (transcription API, United States)",
                "purpose": "Speech-to-text transcription of your report, only if Groq's transcription attempt fails.",
            },
        ],
        "used_for_training_or_other_purposes": False,
        "note": (
            "Your recording is not currently used for anything beyond "
            "processing this specific report and transcribing it. Per "
            "Groq's and OpenAI's API terms, audio submitted through "
            "their APIs is not used to train their models -- this is a "
            "real contractual claim from each provider, not something "
            "Athena's own code enforces or can verify independently."
        ),
    },
    "who_can_access_it": {
        "summary": (
            "Your case record, including a link to the saved recording, "
            "is accessible through this helpline's case-review system."
        ),
        "access_control_status": (
            "Case data, including recordings, is behind a shared "
            "access key used by this helpline's staff -- it is not "
            "openly accessible. This is a single shared credential, "
            "not individual counsellor accounts or an audit log of who "
            "viewed what -- a real but still basic protection, stated "
            "honestly rather than overstated."
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
    "last_updated": "2026-08-29",
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
