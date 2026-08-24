# ============================================================
# ATHENA — STRESS VULNERABILITY INDEX (SVI) ENGINE
# ============================================================

"""
Fuses text-derived distress signals (from understanding.py's already-
computed incident structure) with optional voice-derived signals
(pitch variation, pause patterns, speech rate -- assumed pre-extracted
by the voice pipeline, not computed here) into a single Stress
Vulnerability Index.

This is a DIFFERENT axis from risk.py's risk_tier. risk.py answers
"how legally/physically dangerous is this situation" -- this answers
"how much acute psychological distress does this person appear to be
carrying right now," which matters for triage tone/pacing and whether
to route to a trauma-informed responder, not just whether to escalate.
The two usually move together but aren't the same thing: a missing-
person report carries high reporter distress even with no threat/
injury to the reporter themselves, and a calmly-worded report can
still carry a highly distressed voice underneath it.

Mirrors risk.py's shape deliberately: one public function
(assess_stress, alongside assess_risk), explainable additive scoring
with named factors instead of an opaque model, same style of
"heuristic starting point, tune from real data if there's time"
caveats already used throughout this codebase.
"""

from risk import INCIDENT_TYPE_CONFIDENCE_FLOOR


# ============================================================
# TEXT DISTRESS
# ============================================================
#
# Baseline distress weight per incident type. NOT the same numbers as
# risk.py's INCIDENT_TYPE_BASE_SCORE (that table weights legal/physical
# severity; this one weights typical psychological load of reporting
# this category of incident) -- domestic_violence and missing_person
# score here even though risk.py gives missing_person a lower weight
# than sexual_violence, because the axes being measured are different.

TEXT_DISTRESS_BASE = {
    "sexual_violence": 30,
    "trafficking": 30,
    "domestic_violence": 20,
    "missing_person": 20,
    "stalking": 15,
    "cyber_harassment": 10,
    "harassment": 10,
    "other": 0,
}


def _text_distress_score(incident):
    """
    Score text-derived distress from the incident structure
    understanding.py already computed -- no new detection logic, no
    second embedding pass. Reuses immediate_danger/threat_present/
    injury_present the same way risk.py does, but weighted for
    "how distressing does reporting this sound" rather than "how
    severe/dangerous is this."

    factors is a list of structured dicts, not plain strings --
    {signal, label, confidence, points} -- so a counsellor-facing
    breakdown (see assess_stress's "explainability") can show exactly
    which signal contributed exactly how many points, reusing
    understanding.py's confidence_breakdown values (the same
    per-signal confidence numbers already computed there) rather than
    inventing a second confidence scale. Category-level only
    ("threat_present detected, 80.66%") -- never the original report
    text, which stays out of this breakdown entirely.
    """

    score = 0
    factors = []

    confidence_breakdown = incident.get("confidence_breakdown") or {}

    if incident.get("immediate_danger"):
        points = 35
        score += points
        factors.append({
            "signal": "immediate_danger",
            "label": "Immediate danger reported",
            "confidence": confidence_breakdown.get("immediate_danger"),
            "points": points,
        })

    if incident.get("threat_present"):
        points = 15
        score += points
        factors.append({
            "signal": "threat_present",
            "label": "Threat present in report",
            "confidence": confidence_breakdown.get("threat"),
            "points": points,
        })

    if incident.get("injury_present"):
        points = 15
        score += points
        factors.append({
            "signal": "injury_present",
            "label": "Injury reported",
            "confidence": confidence_breakdown.get("injury"),
            "points": points,
        })

    # Same confidence floor risk.py uses before trusting incident_type
    # enough to apply its baseline -- a low-confidence misclassification
    # shouldn't smuggle in distress points it hasn't earned.
    confidence = incident.get("confidence", 0.0)

    if confidence >= INCIDENT_TYPE_CONFIDENCE_FLOOR:

        incident_type = incident.get("incident_type")
        base = TEXT_DISTRESS_BASE.get(incident_type, 0)

        if base > 0:
            score += base
            label = (incident_type or "incident").replace("_", " ")
            factors.append({
                "signal": "incident_type_baseline",
                "label": f"{label.capitalize()} carries elevated baseline distress",
                "confidence": confidence_breakdown.get("incident_type"),
                "points": base,
            })

    return min(score, 100), factors


# ============================================================
# VOICE STRESS
# ============================================================
#
# Calibrated from Samreen's 2026-08-24 acoustic distress-index (ADI)
# handoff -- her "Low Risk" band per metric (pitch_variation 0.00-0.35,
# pause_ratio < 0.15, speech_rate 130-160 WPM) is used as the calm
# baseline below, and her formula weights (pitch 0.50 / pause 0.30 /
# rate 0.20) replace the earlier even-ish split. Not claimed as
# clinically validated -- same caveat pipeline.py already carries for
# RETRIEVAL_CONFIDENCE_THRESHOLD: tune against real labeled voice
# samples if there's time before the deadline. This module keeps the
# continuous deviation-from-baseline scoring (rather than Samreen's
# discrete per-metric Low/Moderate/High/Critical step bands) so the
# score doesn't jump discontinuously at a band edge -- same actual
# calm/moderate/high/critical cut points, graded between them instead
# of stepped. NOTE: this raises pitch/pause sensitivity noticeably
# (pitch now flags above 0.35 instead of 0.60, pause above 0.15 instead
# of 0.25) -- re-check against the Demo Scenarios sheet before the
# 27th freeze in case any scripted call now lands a different tier.
CALM_SPEECH_RATE_RANGE = (130, 160)    # words/min, Samreen's Low Risk band
CALM_PAUSE_RATIO_CEILING = 0.15        # fraction of speaking time spent paused
PITCH_CALM_CEILING = 0.35              # pitch_variation (0-1); above this, flag

VOICE_WEIGHTS = {
    "pitch": 0.5,
    "pause": 0.3,
    "rate": 0.2,
}

REQUIRED_VOICE_FIELDS = ("pitch_variation", "pause_ratio", "speech_rate_wpm")


def _voice_stress_score(voice_features):
    """
    Score voice-derived stress from pre-extracted features.

    Returns (None, []) when voice_features is absent or missing a
    required field -- this is a normal, expected outcome (most reports
    are text-only, or the voice pipeline hasn't shipped yet), not an
    error, matching the rest of this codebase's pattern of treating
    "no signal available" as a valid None rather than forcing a guess.

    factors is a list of structured dicts (signal, label, value,
    threshold, points), same reasoning as _text_distress_score above.
    "value" is the actual measured number (e.g. pitch_variation: 0.71)
    -- there's no discrete pause-event count available from
    voice_features (only pause_ratio, and optionally
    avg_pause_duration_sec), so the pause factor reports the real
    ratio/duration this system actually computed rather than
    fabricating an event count nothing here tracks.
    """

    if not voice_features:
        return None, []

    if any(voice_features.get(field) is None for field in REQUIRED_VOICE_FIELDS):
        return None, []

    factors = []

    # Pitch variation: single-sided (only "too erratic" is penalized).
    # A "too flat" / monotone direction can also indicate distress
    # (dissociation, emotional numbing) but modeling that non-monotonic
    # relationship needs real calibration data this project doesn't
    # have yet -- deliberately not guessing at it.
    pitch_variation = max(0.0, min(1.0, voice_features["pitch_variation"]))
    pitch_component = pitch_variation * 100

    if pitch_variation > PITCH_CALM_CEILING:
        points = round(VOICE_WEIGHTS["pitch"] * pitch_component, 2)
        factors.append({
            "signal": "pitch_variation",
            "label": "High pitch variability / voice breaks",
            "value": round(pitch_variation, 2),
            "threshold": PITCH_CALM_CEILING,
            "points": points,
        })

    # Pause ratio: single-sided (elevated pausing -- searching for
    # words, choking up -- reads as distress; unusually fluent speech
    # doesn't reliably read as calm on its own).
    pause_ratio = voice_features["pause_ratio"]
    pause_component = 0.0

    if pause_ratio > CALM_PAUSE_RATIO_CEILING:
        pause_component = min(
            1.0,
            (pause_ratio - CALM_PAUSE_RATIO_CEILING) / (1 - CALM_PAUSE_RATIO_CEILING),
        ) * 100

        pause_factor = {
            "signal": "pause_ratio",
            "label": "Elevated pausing in speech",
            "value": round(pause_ratio, 2),
            "threshold": CALM_PAUSE_RATIO_CEILING,
            "points": round(VOICE_WEIGHTS["pause"] * pause_component, 2),
        }

        if voice_features.get("avg_pause_duration_sec") is not None:
            pause_factor["avg_pause_duration_sec"] = voice_features["avg_pause_duration_sec"]

        factors.append(pause_factor)

    # Speech rate: two-sided. Pressured/rapid speech (panic) and
    # unusually slow/flat speech (freeze response, dissociation) are
    # both recognized stress presentations -- unlike pitch/pause above,
    # this one genuinely needs both directions modeled.
    rate = voice_features["speech_rate_wpm"]
    low, high = CALM_SPEECH_RATE_RANGE
    rate_component = 0.0

    if rate > high:
        rate_component = min(1.0, (rate - high) / high) * 100
        factors.append({
            "signal": "speech_rate_wpm",
            "label": "Pressured / rapid speech rate",
            "value": rate,
            "threshold": high,
            "points": round(VOICE_WEIGHTS["rate"] * rate_component, 2),
        })

    elif rate < low:
        rate_component = min(1.0, (low - rate) / low) * 100
        factors.append({
            "signal": "speech_rate_wpm",
            "label": "Unusually slow / flat speech rate",
            "value": rate,
            "threshold": low,
            "points": round(VOICE_WEIGHTS["rate"] * rate_component, 2),
        })

    score = (
        VOICE_WEIGHTS["pitch"] * pitch_component
        + VOICE_WEIGHTS["pause"] * pause_component
        + VOICE_WEIGHTS["rate"] * rate_component
    )

    return round(min(score, 100), 2), factors


# ============================================================
# FUSION + CONFIDENCE
# ============================================================
#
# Even 50/50 weighting when voice is present -- deliberately round
# rather than an asymmetric split neither number could be justified
# well enough to defend. The real point of fusing voice in at all: a
# caller can consciously soften their words while their voice betrays
# more distress underneath (or vice versa, e.g. a coerced caller
# forcing a calm voice) -- see the divergence flag below, which is
# arguably the most useful single signal this engine produces.
TEXT_WEIGHT_WITH_VOICE = 0.5
VOICE_WEIGHT_WITH_VOICE = 0.5

# Confidence ceiling when only one modality is available -- can't
# cross-validate a single signal against a second one, so text-only
# confidence is capped below what text+voice agreement can reach.
TEXT_ONLY_CONFIDENCE_CAP = 0.75

# How far apart text_distress_score and voice_stress_score need to be
# (0-100 scale) before it's worth flagging as a genuine disagreement
# rather than ordinary noise.
DIVERGENCE_FLAG_THRESHOLD = 50


def _tier(score):
    """Same cut points as risk.py's tiers, for consistent judge-facing
    explanation ("same thresholds, different construct") -- just
    "Moderate" instead of "Medium" to keep the two axes visually
    distinct in the UI."""

    if score >= 60:
        return "Critical"
    if score >= 40:
        return "High"
    if score >= 20:
        return "Moderate"
    return "Low"


def assess_stress(incident, voice_features=None):
    """
    Compute the Stress Vulnerability Index for a structured incident,
    optionally fused with pre-extracted voice features.

    Parameters
    ----------
    incident : dict
        Structured output from understanding.understand().
    voice_features : dict | None
        Pre-extracted voice signal: pitch_variation, pause_ratio,
        speech_rate_wpm (required if present), plus optional
        avg_pause_duration_sec / voice_energy_variability. None for
        text-only input.

    Returns
    -------
    dict
        svi_score, svi_tier, confidence, modalities_used, components,
        contributing_factors -- see API_CONTRACT.md.
    """

    text_score, text_factors = _text_distress_score(incident)
    voice_score, voice_factors = _voice_stress_score(voice_features)

    incident_confidence = incident.get("confidence", 0.0)  # 0-100

    # Plain-language strings for contributing_factors -- unchanged
    # format from before this function had structured factors, derived
    # from the same structured list rather than duplicated separately,
    # so the two can never drift out of sync with each other.
    factors = [f["label"] for f in text_factors]

    divergence = None

    if voice_score is not None:

        svi_score = (
            TEXT_WEIGHT_WITH_VOICE * text_score
            + VOICE_WEIGHT_WITH_VOICE * voice_score
        )

        agreement = 1 - abs(text_score - voice_score) / 100
        confidence = (incident_confidence / 100) * (0.5 + 0.5 * agreement) * 100
        modalities_used = ["text", "voice"]

        factors = factors + [f["label"] for f in voice_factors]

        gap = abs(text_score - voice_score)
        divergence = {
            "detected": gap >= DIVERGENCE_FLAG_THRESHOLD,
            "text_score": round(text_score, 2),
            "voice_score": voice_score,
            "gap": round(gap, 2),
        }

        if divergence["detected"]:
            factors.append(
                "Text and voice-derived stress signals diverge sharply -- "
                "possible suppressed distress or a caller unable to speak "
                "freely; recommend human review"
            )

    else:
        svi_score = text_score
        confidence = (incident_confidence / 100) * TEXT_ONLY_CONFIDENCE_CAP * 100
        modalities_used = ["text"]

    if incident_confidence < INCIDENT_TYPE_CONFIDENCE_FLOOR:
        factors.append("Low understanding confidence -- stress estimate less reliable")

    svi_score = round(min(svi_score, 100), 2)
    confidence = round(max(0.0, min(confidence, 100.0)), 2)

    # Counsellor/admin-facing breakdown of exactly which signals pushed
    # the tier where it landed -- deliberately kept out of the
    # complainant-facing response (app.py strips this key before
    # returning /report, /sos, /report/image, /report/voice results;
    # it's only surfaced via the case-detail/brief endpoints an admin
    # dashboard would call). See _text_distress_score/_voice_stress_
    # score above for what "signal"/"points"/"value" mean per entry.
    explainability = {
        "text_signals": text_factors,
        "voice_signals": voice_factors if voice_score is not None else None,
        "divergence": divergence,
    }

    return {
        "svi_score": svi_score,
        "svi_tier": _tier(svi_score),
        "confidence": confidence,
        "modalities_used": modalities_used,
        "components": {
            "text_distress_score": round(text_score, 2),
            "voice_stress_score": voice_score,
        },
        "contributing_factors": factors,
        "explainability": explainability,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    text_only_incident = {
        "incident_type": "domestic_violence",
        "immediate_danger": True,
        "threat_present": True,
        "injury_present": True,
        "confidence": 98.31,
    }

    calm_voice = {
        "pitch_variation": 0.15,
        "pause_ratio": 0.15,
        "speech_rate_wpm": 125,
    }

    agreeing_distressed_voice = {
        "pitch_variation": 0.85,
        "pause_ratio": 0.55,
        "speech_rate_wpm": 210,
    }

    print("\n" + "=" * 70)
    print("TEXT ONLY")
    print("=" * 70)
    for key, value in assess_stress(text_only_incident).items():
        print(f"{key:20}: {value}")

    print("\n" + "=" * 70)
    print("TEXT + AGREEING DISTRESSED VOICE")
    print("=" * 70)
    for key, value in assess_stress(text_only_incident, agreeing_distressed_voice).items():
        print(f"{key:20}: {value}")

    calm_text_incident = {
        "incident_type": "harassment",
        "immediate_danger": False,
        "threat_present": False,
        "injury_present": False,
        "confidence": 92.0,
    }

    highly_distressed_voice = {
        "pitch_variation": 0.95,
        "pause_ratio": 0.75,
        "speech_rate_wpm": 230,
    }

    print("\n" + "=" * 70)
    print("CALM TEXT + DISTRESSED VOICE (divergence case)")
    print("=" * 70)
    for key, value in assess_stress(calm_text_incident, highly_distressed_voice).items():
        print(f"{key:20}: {value}")
