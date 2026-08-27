# ============================================================
# ATHENA — DEMO CASE SEEDING
# ============================================================

"""
Populates cases.db with a small set of realistic demo cases the
FIRST time the app starts against an empty database -- exists purely
because Railway's filesystem is ephemeral: any redeploy (a git push,
a crash-triggered restart, a manual restart) wipes cases.db back to
zero rows, which makes the dashboard, trend chart, and district
pattern detection all show nothing until real reports accumulate
again. That's a bad first impression for a judge opening the live
link cold.

Deliberately does NOT call response_engine.generate_response() (no
Gemini call) -- seeding must never depend on API quota being
available, which is the exact failure mode that triggered the last
Railway restart this was built to protect against. Everything else
(understand/assess_risk/assess_stress/get_legal_guidance/retrieve) is
local computation, so seeding is free and fast. response text below
is hand-written, short, plain-language, and deliberately avoids
stating any specific number/service/procedure not already visible
elsewhere in this codebase -- same "don't invent it" discipline
response_engine.py's prompt enforces for real Gemini answers.

Idempotent: only inserts when cases.db currently has zero rows, so
this never overwrites real reports (locally, mid-demo, or in a
future Railway session that already has real data).
"""

from datetime import datetime, timedelta, timezone

from understanding import understand
from risk import assess_risk, INCIDENT_TYPE_CONFIDENCE_FLOOR
from svi import assess_stress
from kg import get_legal_guidance
from retrieval import retrieve
from nhaa import create_nhaa_docket
from cases import init_db, create_case, get_stats


# Each entry: (text, language, district, channel, disclosure_level,
# days_ago, hand_written_response). days_ago backdates created_at so
# the trend chart and get_flagged_districts() have a realistic-looking
# window to work with instead of every case landing at the same
# instant.
SEED_REPORTS = [
    (
        "मेरे पति मुझे रोज़ मारते हैं और आज उन्होंने चाकू से धमकी दी। "
        "मुझे बहुत डर लग रहा है।",
        "hi", "Hyderabad", "portal", "full", 0,
        "यह बहुत गंभीर स्थिति है। आपकी सुरक्षा सबसे ज़रूरी है। कृपया पुलिस "
        "से संपर्क करें या किसी भरोसेमंद व्यक्ति के पास तुरंत जाएं।",
    ),
    (
        "A man from my neighbourhood forcibly touched me and threatened "
        "me when I tried to resist.",
        "en", "Hyderabad", "mobile_app", "partial", 1,
        "I'm sorry this happened to you. What you describe may be a "
        "criminal offence. Please consider filing a police complaint, "
        "and try to stay somewhere safe with someone you trust.",
    ),
    (
        "A man from my college has been following me home every day "
        "this week and waiting outside my house.",
        "en", "Hyderabad", "chatbot", "full", 3,
        "Being followed repeatedly can be frightening, and it may "
        "qualify as stalking under Indian law. Consider keeping a "
        "written record of each incident and reporting it to the "
        "police.",
    ),
    (
        "My husband shouted at me and pushed me against the wall last "
        "night. This has happened before too.",
        "en", "Hyderabad", "14566_voice", "full", 5,
        "Repeated physical aggression from a partner is a serious "
        "safety concern. A Protection Officer under the Domestic "
        "Violence Act can help you understand your options, alongside "
        "filing a police complaint if you choose to.",
    ),
    (
        "My neighbours beat me and threatened to burn our house because "
        "we are from a Scheduled Caste. They also insulted my caste in "
        "front of the whole village.",
        "en", "Karimnagar", "ivrs", "full", 2,
        "What you're describing is a serious offence, and caste-based "
        "threats and violence are specifically covered under the "
        "Scheduled Castes and Scheduled Tribes (Prevention of "
        "Atrocities) Act. Please consider approaching the police and "
        "your District Legal Services Authority.",
    ),
    (
        "Someone created a fake profile with my photos and is sending "
        "me obscene messages online.",
        "en", "Nalgonda", "portal", "full", 6,
        "Impersonation and harassment online can be reported as cyber "
        "harassment. Consider saving screenshots as evidence and filing "
        "a complaint with the police cyber cell.",
    ),
    (
        "My younger sister did not return home from tuition classes "
        "yesterday evening and her phone is switched off.",
        "en", "Hanumakonda", "portal", "full", 4,
        "A missing person report should be filed with the police as "
        "soon as possible -- Indian law does not require waiting 24 "
        "hours. Please share her last known location and description "
        "with them directly.",
    ),
    (
        "A woman from our village was taken away by an agent promising "
        "a job in another city and we have not been able to contact her "
        "for a week.",
        "en", "Khammam", "ivrs", "full", 3,
        "This may be a case of trafficking, which is a serious crime. "
        "Please report this to the police immediately with any details "
        "you have about the agent or where she was taken.",
    ),
    (
        "Someone shouted casteist insults at me in the market and told "
        "me not to come back.",
        "en", "Hyderabad", "chatbot", "anonymous", 10,
        "Caste-based insults in a public place are an offence under the "
        "SC/ST (Prevention of Atrocities) Act. Consider reporting this "
        "to the police, even without giving your full identity if you "
        "prefer.",
    ),
    (
        "Mera pati mujhe bahut daantta hai aur kabhi kabhi haath bhi "
        "uthata hai.",
        "hi", "Adilabad", "portal", "anonymous", 8,
        "Yeh ghar mein hoti hinsa ho sakti hai. Aap chahen to Protection "
        "Officer ya police se sampark kar sakte hain, apni suraksha ko "
        "sabse pehle rakhein.",
    ),
]


def _escalate_and_reason(risk_assessment, stress_assessment, incident):
    """Mirrors pipeline.py's needs_human_escalation logic exactly --
    kept in sync manually since seeding intentionally doesn't call
    run_pipeline() (that would require Gemini)."""

    risk_escalation = risk_assessment["risk_tier"] in ("Critical", "High")
    stress_escalation = stress_assessment["svi_tier"] == "Critical"
    understanding_escalation = (
        incident["confidence"] < INCIDENT_TYPE_CONFIDENCE_FLOOR
    )

    reasons = []

    if risk_escalation:
        reasons.append("High-risk incident requires human attention.")
    if stress_escalation:
        reasons.append(
            "Critical stress/trauma indicators detected — human review "
            "recommended."
        )
    if understanding_escalation:
        reasons.append(
            "Low understanding confidence — unable to reliably classify "
            "this report, human review recommended."
        )

    escalate = risk_escalation or stress_escalation or understanding_escalation

    return escalate, (" ".join(reasons) if reasons else None)


def seed_demo_cases(force=False):
    """
    Insert SEED_REPORTS into cases.db if it's currently empty.

    force=True bypasses the empty-check (only ever used for local
    testing of this script itself -- never called that way from the
    app).
    """

    init_db()

    if not force and get_stats()["total_cases"] > 0:
        print("[seed_data] cases.db already has data -- skipping seed.")
        return

    print(f"[seed_data] Seeding {len(SEED_REPORTS)} demo cases...")

    now = datetime.now(timezone.utc)

    for text, language, district, channel, disclosure_level, days_ago, response_text in SEED_REPORTS:

        incident = understand(text, language=language)
        risk_assessment = assess_risk(incident)
        stress_assessment = assess_stress(incident)
        legal_guidance = get_legal_guidance(incident, district=district)

        evidence = retrieve(text, top_k=3)
        citations = [
            {
                "source": doc.get("source"),
                "page": doc.get("page"),
                "similarity": doc.get("similarity"),
            }
            for doc in evidence
        ]

        escalate, reason = _escalate_and_reason(
            risk_assessment, stress_assessment, incident
        )

        nhaa_docket = create_nhaa_docket(
            channel, stress_assessment.get("svi_score"),
            stress_assessment.get("svi_tier"),
        )

        pipeline_result = {
            "incident": incident,
            "risk": risk_assessment,
            "stress_assessment": stress_assessment,
            "legal_guidance": legal_guidance,
            "citations": citations,
            "escalate": escalate,
            "reason": reason,
            "response": response_text,
            "nhaa_docket": nhaa_docket,
        }

        created_at = (now - timedelta(days=days_ago)).isoformat()

        create_case(
            text,
            pipeline_result,
            disclosure_level=disclosure_level,
            district=district,
            created_at=created_at,
        )

    print("[seed_data] Done.")


if __name__ == "__main__":
    seed_demo_cases()
