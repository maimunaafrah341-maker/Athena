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
from risk import assess_risk
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

def _finalize(text, result):
    """
    Persist every processed report as a case (see cases.py) and
    attach its id/status to the contract before returning. This is
    the ESCALATE step made real -- previously an "escalate": true
    result had nowhere to go once returned.
    """

    case_id = create_case(text, result)

    result["case_id"] = case_id
    result["case_status"] = "Escalated" if result["escalate"] else "Resolved"

    return result


# ============================================================
# RUN FULL PIPELINE
# ============================================================

def run_pipeline(text, language=None, top_k=TOP_K):
    """
    Run one incident report through the full Athena pipeline.

    Returns a single JSON-serializable dict. This is the contract
    the frontend / API should rely on — nothing else should reach
    into understanding/risk/retrieval/response_engine directly.
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
            "citations": [],
            "top_similarity": 0.0,
            "escalate": True,
            "reason": str(e),
            "response": None,
            "case_id": None,
            "case_status": None,
        }

    # --------------------------------------------------------
    # 2. Assess risk
    # --------------------------------------------------------

    risk_assessment = assess_risk(incident)

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
        })

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
            "citations": [],
            "top_similarity": top_similarity,
            "escalate": True,
            "reason": (
                "The response service is temporarily unavailable. "
                "Please try again in a moment."
            ),
            "response": None,
        })

    # Critical / High-risk incidents should be flagged for
    # human attention even when verified evidence is available.
    needs_human_escalation = risk_assessment["risk_tier"] in (
       "Critical",
       "High",
    )

    return _finalize(text, {
       "incident": incident,
       "risk": risk_assessment,
       "citations": result["citations"],
       "top_similarity": top_similarity,
       "escalate": needs_human_escalation,
       "reason": (
           "High-risk incident requires human attention."
            if needs_human_escalation
            else None
        ),
        "response": result["response"],
    })


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
