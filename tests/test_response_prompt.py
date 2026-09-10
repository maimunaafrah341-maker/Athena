"""
The prompt is where the response's guarantees actually live.

Tested by building it directly rather than by calling a provider: the
rules below are deterministic, and asserting on generated text would
make the suite slow, costly and dependent on a model behaving the same
way twice.
"""

import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from response_engine import build_prompt  # noqa: E402


def _incident(language, script):
    return {
        "language": language,
        "script": script,
        "original_text": "Someone broke into my house and hit me.",
        "incident_type": "harassment",
        "confidence": 100.0,
        "immediate_danger": True,
        "threat_present": True,
        "injury_present": True,
        "caste_based_motive": False,
        "suicidal_ideation": False,
        "relationship": None,
        "location": None,
        "district": None,
        "confidence_breakdown": {"incident_type": 100.0},
    }


RISK = {"risk_tier": "High", "risk_score": 50, "risk_factors": []}

EVIDENCE = [
    {
        "text": "House trespass is punishable with imprisonment.",
        "source": "BNS2023.pdf",
        "page": 218,
        "similarity": 0.83,
    }
]


# Every language whose speakers may type in Latin letters. Urdu and
# Bengali reached script detection later than Hindi and Telugu and this
# rule was never extended with them, so romanized Urdu got a reply in
# Perso-Arabic script -- the exact switch the rule exists to prevent.
@pytest.mark.parametrize("language", ["hi", "te", "ur", "bn"])
def test_romanized_input_asks_for_a_romanized_reply(language):
    prompt = build_prompt(_incident(language, "romanized"), RISK, EVIDENCE)

    assert "romanized" in prompt.lower(), (
        "romanized %s does not ask for a romanized reply, so the person "
        "gets native script back" % language
    )


@pytest.mark.parametrize("language", ["hi", "te", "ur", "bn"])
def test_native_input_does_not_ask_for_romanization(language):
    """The rule must not fire in reverse and romanize native script."""

    prompt = build_prompt(_incident(language, "native"), RISK, EVIDENCE)

    assert "Respond ONLY in" in prompt
    assert "romanized" not in prompt.lower()


def test_reference_markers_are_banned_in_every_language():
    """
    The English ban held and the model translated the marker instead,
    so a Hindi reply opened with "साक्ष्य 1 के अनुसार" -- the system's
    internal scaffolding, shown to someone whose house had just been
    broken into.
    """

    prompt = build_prompt(_incident("hi", "native"), RISK, EVIDENCE)

    for translated_marker in ("साक्ष्य", "సాక్ష్యం", "شواہد", "প্রমাণ"):
        assert translated_marker in prompt, (
            "the prompt does not forbid the %r form of the evidence "
            "marker" % translated_marker
        )


def test_the_repealed_penal_code_is_named_as_forbidden():
    """
    The Bharatiya Nyaya Sanhita 2023 replaced the Indian Penal Code.
    A reply grounded in real BNS text called it भारतीय दंड संहिता,
    because that is the familiar Hindi phrase for penal law.
    """

    prompt = build_prompt(_incident("hi", "native"), RISK, EVIDENCE)

    assert "Bharatiya Nyaya Sanhita" in prompt
    assert "भारतीय दंड संहिता" in prompt, (
        "the prompt does not name the repealed statute it must avoid"
    )
