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