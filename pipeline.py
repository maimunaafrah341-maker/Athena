"""
ATHENA — PIPELINE ORCHESTRATOR
============================================================

Chains the already-working modules into one end-to-end flow:

    raw text
    -> understanding.understand()          (language + incident structure)
    -> risk.assess_risk()                  (risk tier/score)
    -> retrieval.retrieve()                (verified evidence)
    -> confidence gate                     (escalate if evidence is weak)
    -> response_engine.prepare_response()  (grounded Gemini answer)

This is the ONE function the frontend, a CLI, or an API route
should call. Nothing in understanding.py / risk.py / retrieval.py /
response_engine.py needs to change for this to work.
"""

from understanding import understand
from risk import assess_risk, INCIDENT_TYPE_CONFIDENCE_FLOOR
from svi import assess_stress
from kg import get_legal_guidance
from retrieval import retrieve
from response_engine import prepare_response
from cases import init_db, create_case

init_db()


# ============================================================
# CONFIGURATION
# ============================================================

# Minimum top-result similarity required before we trust retrieval
# enough to generate a grounded answer. Below this we escalate
# instead of calling Gemini.
#
# Carried over from answer_engine.py's CONFIDENCE_THRESHOLD — same
# placeholder value, same caveat: tune against real similarity
# scores from your eval set once you've logged good vs. weak
# retrievals. Not blocking for the demo.
RETRIEVAL_CONFIDENCE_THRESHOLD = 0.60

TOP_K = 5


# ============================================================
# PERSIST + RETURN
# ============================================================

def _build_reasoning_trace(result):
    """
    Restructure data the pipeline already computed into an explicit
    "why did Athena decide this" trace -- no new detection logic,
    just exposing the reasoning that was previously buried inside a
    flat response instead of shown as its own thing. Answers the
    "why is this High risk?" question a judge (or a real reviewer)
    would ask, directly from real risk_factors/citations/confidence.
    """

    incident = result.get("incident") or {}
    risk = result.get("risk") or {}
    stress = result.get("stress_assessment") or {}
    legal = result.get("legal_guidance") or {}

    return {
        "incident_classification": {
            "type": incident.get("incident_type"),
            "confidence": incident.get("confidence"),
            "confidence_breakdown": incident.get("confidence_breakdown"),
        },
        "risk_assessment": {
            "tier": risk.get("risk_tier"),
            "score": risk.get("risk_score"),
            "factors": risk.get("risk_factors", []),
        },
        "stress_assessment": {
            "tier": stress.get("svi_tier"),
            "score": stress.get("svi_score"),
            "confidence": stress.get("confidence"),
            "modalities_used": stress.get("modalities_used"),
            "factors": stress.get("contributing_factors", []),
        },
        "legal_guidance_summary": {
            "provisions_cited": [
                f"{p.get('act')} — {p.get('section')}"
                for p in (legal.get("applicable_provisions") or [])
            ],
            "escalation_contact_found": legal.get("escalation_contact") is not None,
        },
        "evidence_used": [
            {
                "source": citation.get("source"),
                "page": citation.get("page"),
                "similarity": citation.get("similarity"),
            }
            for citation in (result.get("citations") or [])
        ],
    }


SOS_RISK_FACTOR = (
    "Manual SOS trigger — user directly signaled immediate danger"
)


def _apply_sos_override(result):
    """
    A one-tap SOS button is a direct, unambiguous signal of immediate
    danger from the user themselves -- a stronger signal than
    anything understanding.py/risk.py could infer from wording. It
    always overrides the classifier's guess to Critical/escalated,
    rather than trusting whatever the (possibly terse, possibly
    generic) SOS text happened to classify as.
    """

    if result.get("risk"):
        result["risk"]["risk_tier"] = "Critical"
        result["risk"]["risk_score"] = 100
        if SOS_RISK_FACTOR not in result["risk"]["risk_factors"]:
            result["risk"]["risk_factors"].append(SOS_RISK_FACTOR)

    result["escalate"] = True

    if not result.get("reason"):
        result["reason"] = (
            "Manual SOS trigger — flagged for immediate human attention."
        )

    return result


def _finalize(
    text,
    result,
    evidence_path=None,
    latitude=None,
    longitude=None,
    is_sos=False,
):
    """
    Persist every processed report as a case (see cases.py) and
    attach its id/status to the contract before returning. This is
    the ESCALATE step made real -- previously an "escalate": true
    result had nowhere to go once returned.

    latitude/longitude, if given, are expected to already be
    privacy-rounded by the caller (app.py) -- this function and
    cases.create_case() just persist whatever they're handed.
    """

    if is_sos:
        result = _apply_sos_override(result)

    case_id = create_case(
        text,
        result,
        evidence_path=evidence_path,
        latitude=latitude,
        longitude=longitude,
        is_sos=is_sos,
    )

    result["case_id"] = case_id
    result["case_status"] = "Escalated" if result["escalate"] else "Resolved"
    result["reasoning_trace"] = _build_reasoning_trace(result)

    return result


# ============================================================
# RUN FULL PIPELINE
# ============================================================

def run_pipeline(
    text,
    language=None,
    top_k=TOP_K,
    evidence_path=None,
    latitude=None,
    longitude=None,
    is_sos=False,
    voice_features=None,
    district=None,
):
    """
    Run one incident report through the full Athena pipeline.

    evidence_path: saved path of an uploaded screenshot/image, if
    this text came from OCR'd evidence rather than typed input --
    stored on the resulting case, otherwise ignored.

    latitude/longitude: optional, only if the user chose to share
    their location -- expected to already be privacy-rounded by the
    caller before reaching here (see app.py).

    is_sos: True when this report came from the one-tap SOS button
    rather than a typed report -- forces the resulting case to
    Critical/escalated regardless of what the text classifies as
    (see _apply_sos_override above).

    voice_features: optional pre-extracted voice signal (pitch
    variation, pause ratio, speech rate -- see svi.py) fused with the
    text signal into stress_assessment. None for text-only input,
    which is the normal case today.

    district: optional reporter district name (e.g. "Hyderabad"),
    used only to resolve legal_guidance.escalation_contact (see
    kg.py). None just means that field comes back null -- applicable
    legal provisions and procedural steps still get returned either
    way, district only affects the contact lookup.

    Returns a single JSON-serializable dict. This is the contract
    the frontend / API should rely on — nothing else should reach
    into understanding/risk/svi/kg/retrieval/response_engine
    directly.
    """

    # --------------------------------------------------------
    # 1. Understand the incident
    # --------------------------------------------------------
    #
    # Empty/whitespace-only input is a user error, not a pipeline
    # failure -- fail soft into the same escalate/reason contract
    # as every other guarded branch below instead of letting the
    # ValueError reach the API layer as an unhandled 500.

    try:
        incident = understand(text, language=language)

    except ValueError as e:

        # Nothing worth tracking as a case here -- there's no report
        # content, just an empty/whitespace submission.
        return {
            "incident": None,
            "risk": None,
            "stress_assessment": None,
            "legal_guidance": None,
            "citations": [],
            "top_similarity": 0.0,
            "escalate": True,
            "reason": str(e),
            "response": None,
            "case_id": None,
            "case_status": None,
            "reasoning_trace": None,
        }

    # --------------------------------------------------------
    # 2. Assess risk + stress vulnerability
    # --------------------------------------------------------

    risk_assessment = assess_risk(incident)
    stress_assessment = assess_stress(incident, voice_features)
    legal_guidance = get_legal_guidance(incident, district=district)

    # --------------------------------------------------------
    # 3. Retrieve verified evidence
    # --------------------------------------------------------

    evidence = retrieve(text, top_k=top_k)

    top_similarity = evidence[0]["similarity"] if evidence else 0.0

    # --------------------------------------------------------
    # 4. Confidence gate — never guess when evidence is weak
    # --------------------------------------------------------

    if not evidence or top_similarity < RETRIEVAL_CONFIDENCE_THRESHOLD:

        return _finalize(text, {
            "incident": incident,
            "risk": risk_assessment,
            "stress_assessment": stress_assessment,
            "legal_guidance": legal_guidance,
            "citations": [],
            "top_similarity": top_similarity,
            "escalate": True,
            "reason": (
                "No matching evidence found in the knowledge base."
                if not evidence else
                "Retrieval confidence below threshold — "
                "escalating instead of guessing."
            ),
            "response": None,
        }, evidence_path=evidence_path, latitude=latitude, longitude=longitude,
           is_sos=is_sos)

    # --------------------------------------------------------
    # 5. Generate grounded response
    # --------------------------------------------------------
    #
    # Gemini can fail transiently (server overload, timeouts, etc.).
    # That must never crash the pipeline mid-demo — fail soft into
    # an escalation instead of raising.

    try:
        result = prepare_response(incident, risk_assessment, evidence)

    except Exception:

        return _finalize(text, {
            "incident": incident,
            "risk": risk_assessment,
            "stress_assessment": stress_assessment,
            "legal_guidance": legal_guidance,
            "citations": [],
            "top_similarity": top_similarity,
            "escalate": True,
            "reason": (
                "The response service is temporarily unavailable. "
                "Please try again in a moment."
            ),
            "response": None,
        }, evidence_path=evidence_path, latitude=latitude, longitude=longitude,
           is_sos=is_sos)

    # Critical/High-risk incidents, a Critical stress/trauma reading,
    # OR low understanding confidence should each independently be
    # enough to flag for human attention, even when verified evidence
    # was available and Gemini produced a normal-looking answer.
    #
    # The third trigger closes a real gap found via live adversarial
    # testing 2026-08-21/22: retrieval similarity and understanding
    # confidence measure different things -- a short, genuinely
    # ambiguous report ("I don't know what's going on, everything
    # feels off today") can score 0% on incident.confidence (the
    # system has no real idea what happened) while retrieval still
    # coincidentally finds a chunk above RETRIEVAL_CONFIDENCE_THRESHOLD
    # by similarity alone, letting a confident-sounding, non-escalated
    # response through with nobody ever reviewing it -- directly
    # contradicting the "escalate when uncertain" design this project
    # is pitched on. risk.py already computed a "Low understanding
    # confidence" risk_factor STRING for this exact situation, but
    # that string was never actually wired to force escalate=True
    # unless it also happened to push risk/stress into a high tier,
    # which a low-signal ambiguous report structurally can't do.
    # INCIDENT_TYPE_CONFIDENCE_FLOOR is reused rather than a new
    # constant since it's already the bar risk.py uses to decide
    # whether classify_incident()'s output is trustworthy at all --
    # same question, same answer, single source of truth.
    risk_escalation = risk_assessment["risk_tier"] in ("Critical", "High")
    stress_escalation = stress_assessment["svi_tier"] == "Critical"
    understanding_escalation = incident["confidence"] < INCIDENT_TYPE_CONFIDENCE_FLOOR
    needs_human_escalation = risk_escalation or stress_escalation or understanding_escalation

    escalation_reasons = []

    if risk_escalation:
        escalation_reasons.append("High-risk incident requires human attention.")

    if stress_escalation:
        escalation_reasons.append(
            "Critical stress/trauma indicators detected — human review recommended."
        )

    if understanding_escalation:
        escalation_reasons.append(
            "Low understanding confidence — unable to reliably classify this "
            "report, human review recommended."
        )

    return _finalize(text, {
       "incident": incident,
       "risk": risk_assessment,
       "stress_assessment": stress_assessment,
       "legal_guidance": legal_guidance,
       "citations": result["citations"],
       "top_similarity": top_similarity,
       "escalate": needs_human_escalation,
       "reason": " ".join(escalation_reasons) if escalation_reasons else None,
        "response": result["response"],
    }, evidence_path=evidence_path, latitude=latitude, longitude=longitude,
       is_sos=is_sos)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_reports = [
        "My husband is threatening me and physically hurting me.",
        "मेरे पति मुझे धमकी दे रहे हैं और शारीरिक रूप से चोट पहुँचा रहे हैं।",
        "నా భర్త నన్ను బెదిరిస్తున్నాడు మరియు శారీరకంగా హింసిస్తున్నాడు.",
    ]

    for report in test_reports:

        print("\n" + "=" * 70)
        print("INPUT:", report)
        print("=" * 70)

        output = run_pipeline(report)

        print("Language:  ", output["incident"]["language"])
        print("Risk tier: ", output["risk"]["risk_tier"])
        print("Escalate:  ", output["escalate"])

        if output["escalate"]:
            print("Reason:    ", output["reason"])
        else:
            print("\nResponse:\n", output["response"])
