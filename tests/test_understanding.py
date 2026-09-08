"""
Regression tests for classification bugs that were found live.

Every case here is a real defect this project shipped, not a
hypothetical. They are slow -- the embedding model loads once, around
20 seconds -- which is the price of testing the thing that actually
decides whether someone's report is treated as an emergency.

The sentences are the ones that FOUND each bug, and deliberately are
not the anchor sentences added to fix it. A test that reuses the anchor
proves the anchor was added, not that the behaviour generalises.
"""

import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from understanding import detect_language, detect_script, understand  # noqa: E402


CASTE_FLOOR = 80.0


# ------------------------------------------------------------------
# Caste motive -- fired in English only until 2026-09-08.
#
# kg.py gates the SC/ST Act provisions on this signal, so a caste
# atrocity reported in any other language received no statutory
# citations at all, on a project built for the National Helpline
# Against Atrocities.
# ------------------------------------------------------------------

CASTE_REPORTS = [
    ("en", "My neighbour abused me using my caste name and beat me."),
    ("hi", "मेरे पड़ोसी ने मेरी जाति का नाम लेकर गाली दी और मुझे मारा।"),
    ("te", "నా పొరుగువాడు నా కులం పేరు చెప్పి తిట్టి నన్ను కొట్టాడు."),
    ("bn", "আমার প্রতিবেশী আমাকে জাত তুলে গালি দিয়েছে এবং মারধর করেছে।"),
    ("ur", "میرے پڑوسی نے میری ذات کا نام لے کر گالی دی اور مجھے مارا۔"),
]


@pytest.mark.parametrize("language,text", CASTE_REPORTS)
def test_caste_motive_detected_in_every_language(language, text):
    incident = understand(text)

    assert incident["caste_based_motive"] is True, (
        "caste motive missed in %s" % language
    )

    confidence = incident["confidence_breakdown"]["caste_based_motive"]

    assert confidence >= CASTE_FLOOR, (
        "%s detected caste at %.1f%%, below the %.0f%% floor kg.py "
        "requires before attaching SC/ST provisions"
        % (language, confidence, CASTE_FLOOR)
    )


@pytest.mark.parametrize("language,text", CASTE_REPORTS)
def test_caste_report_is_not_classified_as_domestic_violence(language, text):
    """
    get_legal_guidance() routes on incident_type, not on the caste
    signal, so a caste atrocity typed as domestic violence gets the
    Protection of Women from Domestic Violence Act -- confidently, and
    wrongly. A neighbour is not a domestic relationship.
    """

    incident = understand(text)

    assert incident["incident_type"] != "domestic_violence", (
        "%s typed a neighbour caste assault as domestic violence, which "
        "routes it to the wrong statute" % language
    )


# ------------------------------------------------------------------
# The hard negatives the caste fix could have broken.
# ------------------------------------------------------------------

NON_CASTE_REPORTS = [
    ("en", "My husband hit me and threatened to kill me."),
    ("hi", "मेरे पति ने मुझे मारा और जान से मारने की धमकी दी।"),
    ("te", "నా భర్త నన్ను కొట్టాడు మరియు చంపుతానని బెదిరించాడు."),
    ("bn", "আমার স্বামী আমাকে মারধর করেছে এবং হত্যার হুমকি দিয়েছে।"),
    ("ur", "میرے شوہر نے مجھے مارا اور جان سے مارنے کی دھمکی دی۔"),
]


@pytest.mark.parametrize("language,text", NON_CASTE_REPORTS)
def test_domestic_violence_does_not_fire_caste_motive(language, text):
    incident = understand(text)

    assert incident["caste_based_motive"] is False, (
        "%s attached a caste motive to a report with no caste element, "
        "which would cite the SC/ST Act at someone it does not apply to"
        % language
    )


# ------------------------------------------------------------------
# Anonymous perpetrator -- scored Low with no signals until the
# hard-negative banks were widened. Same event, named or not.
# ------------------------------------------------------------------

def test_anonymous_perpetrator_is_not_downgraded():
    named = understand("My husband hit me and threatened to kill me.")
    anonymous = understand("Someone hit me and threatened to kill me.")

    for signal in ("threat_present", "injury_present"):
        assert anonymous[signal] is True, (
            "not naming the attacker suppressed %s; the same report with "
            '"my husband" gives %s' % (signal, named[signal])
        )


def test_threat_against_you_is_not_read_as_suicidal_ideation():
    """Both sentences contain "kill me". Only one is self-harm."""

    incident = understand("He hit me and said he will kill me tonight.")

    assert incident["suicidal_ideation"] is False


def test_genuine_suicidal_ideation_still_detected():
    """The guard above must not cost the signal it protects."""

    incident = understand("I don't want to live anymore.")

    assert incident["suicidal_ideation"] is True


# ------------------------------------------------------------------
# Script detection -- Urdu and Bengali reached detect_language()
# later than Hindi and Telugu and detect_script() was never extended,
# so native text was recorded as "latin" on every case.
# ------------------------------------------------------------------

NATIVE_SCRIPTS = [
    ("hi", "मुझे मदद चाहिए"),
    ("te", "నాకు సహాయం కావాలి"),
    ("bn", "আমার সাহায্য দরকার"),
    ("ur", "مجھے مدد چاہیے"),
]


@pytest.mark.parametrize("language,text", NATIVE_SCRIPTS)
def test_native_script_is_reported_as_native(language, text):
    assert detect_language(text) == language
    assert detect_script(text, language) == "native"


def test_unsupported_script_falls_back_to_english_not_a_guess():
    """
    Native Tamil once scored 100% Hindi and got a romanized Hindi
    reply. A safe default beats a confident mistake.
    """

    assert detect_language("எனக்கு உதவி வேண்டும்") == "en"


def test_empty_input_is_safe():
    for text in ("", "   ", "\n"):
        assert detect_language(text) == "en"
