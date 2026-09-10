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

from response_engine import build_prompt, strip_markdown  # noqa: E402


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


# ------------------------------------------------------------------
# Markdown never reaches the reporter
# ------------------------------------------------------------------

def test_the_prompt_forbids_markdown():
    """
    A live Hindi reply on 2026-09-10 opened a section with
    "**अगले कदम:**" -- literal asterisks, in a chat bubble that
    renders no markdown, in the middle of a message about a
    break-in. Nothing in the prompt had ever asked for plain text.
    """

    prompt = build_prompt(_incident("hi", "native"), RISK, EVIDENCE)

    assert "FORMATTING:" in prompt
    assert "No markdown" in prompt


def test_the_prompt_does_not_demonstrate_the_thing_it_forbids():
    """
    The statute section wrote **Bharatiya Nyaya Sanhita, 2023** in
    markdown bold. A model shown bold in its instructions hands bold
    back, so the rule and the example contradicted each other.
    """

    prompt = build_prompt(_incident("hi", "native"), RISK, EVIDENCE)

    statute_line = [
        line for line in prompt.splitlines()
        if "Bharatiya Nyaya Sanhita" in line
    ]

    assert statute_line, "the prompt no longer names the statute in force"

    for line in statute_line:
        assert "**" not in line, (
            "the prompt still shows markdown bold to the model: %r" % line
        )


def test_the_prompt_asks_for_one_numeral_system():
    """
    The same sentence carried "2023" and "१४" -- Arabic and Devanagari
    digits -- and ran "अधिकतम१४" together with no space.
    """

    prompt = build_prompt(_incident("hi", "native"), RISK, EVIDENCE)

    assert "Western Arabic digits" in prompt
    assert "space between a word and the number" in prompt


@pytest.mark.parametrize("raw,expected", [
    ("**अगले कदम:**", "अगले कदम:"),
    ("The **Bharatiya Nyaya Sanhita, 2023** applies.",
     "The Bharatiya Nyaya Sanhita, 2023 applies."),
    ("## Next steps", "Next steps"),
    ("__Important__ notice", "Important notice"),
    ("Call *14566* now", "Call 14566 now"),
])
def test_markdown_is_stripped_from_the_reply(raw, expected):
    """
    The prompt asks; this enforces. A prompt rule is a request, and
    the cost of one that is ignored is punctuation in the middle of a
    sentence somebody is reading in a crisis.
    """

    assert strip_markdown(raw) == expected


@pytest.mark.parametrize("text", [
    "Section 3(2)(v) of the SC/ST Act",
    "2 * 3 = 6",
    "Call 14566 for help.",
    "",
])
def test_the_stripper_leaves_ordinary_text_alone(text):
    """
    A sanitiser that mangles a statute citation is worse than the
    asterisks it removes.
    """

    assert strip_markdown(text) == text


def test_the_stripper_survives_no_response():
    """generate_response can return None when every provider fails."""

    assert strip_markdown(None) is None


# ------------------------------------------------------------------
# Translation output is model output
# ------------------------------------------------------------------
#
# translation.py reuses generate_response(), so it inherits the same
# failover -- and the same habit of reaching for markdown. Its result
# goes into the case brief a counsellor reads, which renders it as
# text, so asterisks would sit there just as visibly.

@pytest.mark.parametrize("function,args", [
    ("translate_reply", ("kuch hua hai", "hi")),
    ("translate_to_english", ("कुछ हुआ है", "hi")),
])
def test_translations_are_stripped_of_markdown(monkeypatch, function, args):

    import translation

    monkeypatch.setattr(
        translation, "generate_response", lambda prompt: "**अनुवाद** किया गया"
    )

    assert getattr(translation, function)(*args) == "अनुवाद किया गया"

