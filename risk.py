# ============================================================
# ATHENA — RISK ASSESSMENT
# ============================================================

"""
Risk assessment module for Athena.

Takes the structured incident produced by understanding.py
and assigns an explainable risk tier.

Risk levels:
    Critical
    High
    Medium
    Low
"""


# ============================================================
# INCIDENT-TYPE BASELINE SEVERITY
# ============================================================
#
# The threat/injury/immediate_danger signals in understanding.py are
# short-phrase embedding matches -- noisy enough that a stalking
# report with no explicit threat/injury wording (e.g. "someone is
# following me right now") could score 0 and never escalate, purely
# because none of those specific phrase patterns happened to fire.
#
# incident_type itself is usually the more reliable signal (it's
# matched against far more anchor examples, and understanding.py's
# calibrated confidence already tells us how much to trust it) --
# so categories that are inherently serious get a baseline score
# independent of whether the finer-grained signals also fired.
# domestic_violence is 0 here deliberately: it's already well
# covered by the physical/threat/injury signals above, which fire
# reliably for it.

INCIDENT_TYPE_BASE_SCORE = {
    "domestic_violence": 0,
    "sexual_violence": 35,
    "trafficking": 35,
    "missing_person": 25,
    "stalking": 20,
    "cyber_harassment": 15,
    "harassment": 10,
    "other": 0,
}

# Only trust incident_type enough to apply its baseline when
# understanding.py was actually confident about the classification --
# otherwise a low-confidence/neutral misclassification (e.g. "pizza
# dough" weakly matching "trafficking") would smuggle in points it
# hasn't earned. Matches the confidence bar used below for the
# "human review recommended" factor.
INCIDENT_TYPE_CONFIDENCE_FLOOR = 60


# ============================================================
# RISK ASSESSMENT
# ============================================================

def assess_risk(incident):
    """
    Assess the severity of a structured incident.

    Parameters
    ----------
    incident : dict
        Structured output from understanding.py.

    Returns
    -------
    dict
        Risk assessment containing:
        - risk_tier
        - risk_score
        - risk_factors
        - confidence
    """

    score = 0
    risk_factors = []

    # --------------------------------------------------------
    # Extract fields safely
    # --------------------------------------------------------

    incident_type = incident.get("incident_type")
    violence_types = incident.get("violence_types", [])
    immediate_danger = incident.get("immediate_danger", False)
    threat_present = incident.get("threat_present", False)
    injury_present = incident.get("injury_present", False)
    confidence = incident.get("confidence", 0.0)

    # --------------------------------------------------------
    # Immediate danger
    # --------------------------------------------------------

    if immediate_danger:
        score += 40
        risk_factors.append("Immediate danger detected")

    # --------------------------------------------------------
    # Physical violence
    # --------------------------------------------------------

    if "physical" in violence_types:
        score += 25
        risk_factors.append("Physical violence detected")

    # --------------------------------------------------------
    # Threat
    # --------------------------------------------------------

    if threat_present or "threat" in violence_types:
        score += 20
        risk_factors.append("Threat detected")

    # --------------------------------------------------------
    # Injury
    # --------------------------------------------------------

    if injury_present:
        score += 20
        risk_factors.append("Injury reported")

    # --------------------------------------------------------
    # Sexual violence
    # --------------------------------------------------------

    if "sexual" in violence_types:
        score += 25
        risk_factors.append("Sexual violence detected")

    # --------------------------------------------------------
    # Severe violence indicators
    # --------------------------------------------------------

    if "weapon" in violence_types:
        score += 30
        risk_factors.append("Weapon involvement detected")

    # --------------------------------------------------------
    # Incident-type baseline (see INCIDENT_TYPE_BASE_SCORE above --
    # covers incidents like stalking that don't reliably trip the
    # phrase-level signals but are still inherently serious)
    # --------------------------------------------------------

    if confidence >= INCIDENT_TYPE_CONFIDENCE_FLOOR:

        base_score = INCIDENT_TYPE_BASE_SCORE.get(incident_type, 0)

        if base_score > 0:
            score += base_score
            label = (incident_type or "incident").replace("_", " ")
            risk_factors.append(
                f"{label.capitalize()} classified with high confidence"
            )

    # --------------------------------------------------------
    # Determine risk tier
    # --------------------------------------------------------

    if score >= 60:
        risk_tier = "Critical"

    elif score >= 40:
        risk_tier = "High"

    elif score >= 20:
        risk_tier = "Medium"

    else:
        risk_tier = "Low"

    # --------------------------------------------------------
    # Confidence adjustment
    # --------------------------------------------------------

    # If the understanding model is uncertain, Athena should
    # avoid pretending that the assessment is highly certain.

    if confidence < 60:
        risk_factors.append(
            "Low understanding confidence — human review recommended"
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "risk_tier": risk_tier,
        "risk_score": min(score, 100),
        "risk_factors": risk_factors,
        "confidence": confidence
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_incident = {
        "incident_type": "domestic_violence",
        "violence_types": ["physical", "threat"],
        "immediate_danger": True,
        "threat_present": True,
        "injury_present": True,
        "relationship": "husband",
        "location": None,
        "confidence": 98.31
    }

    result = assess_risk(test_incident)

    print("\n" + "=" * 70)
    print("ATHENA RISK ASSESSMENT")
    print("=" * 70)

    for key, value in result.items():
        print(f"{key:15}: {value}")