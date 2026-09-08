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


# ------------------------------------------------------------------
# A hostile crowd outside the home.
#
# SIH26093's background names social boycott and displacement as
# atrocities. Before 2026-09-08 a caste temple-entry denial with a
# crowd outside the house scored Low in Hindi and English and Critical
# in Telugu, Bengali and Urdu -- one event, and the two languages most
# likely to be used gave the safest-sounding answer.
# ------------------------------------------------------------------

CROWD_REPORTS = [
    ("en", "Because of my caste I was not allowed into the temple and I was "
           "humiliated. A crowd is standing outside my house."),
    ("hi", "मेरी जाति के कारण मुझे मंदिर में घुसने नहीं दिया गया और मुझे अपमानित "
           "किया गया। मेरे घर के बाहर भीड़ खड़ी है।"),
    ("te", "నా కులం కారణంగా నన్ను గుడిలోకి రానివ్వలేదు, అవమానించారు. మా ఇంటి బయట "
           "గుంపు గుమిగూడింది."),
    ("bn", "আমার জাতের কারণে আমাকে মন্দিরে ঢুকতে দেওয়া হয়নি এবং অপমান করা হয়েছে। "
           "আমার বাড়ির বাইরে ভিড় জমেছে।"),
    ("ur", "میری ذات کی وجہ سے مجھے مندر میں داخل نہیں ہونے دیا گیا اور میری بے عزتی "
           "کی گئی۔ میرے گھر کے باہر بھیڑ کھڑی ہے۔"),
]


@pytest.mark.parametrize("language,text", CROWD_REPORTS)
def test_crowd_outside_the_home_reads_as_danger(language, text):
    incident = understand(text)

    assert incident["immediate_danger"] is True, (
        "%s did not read a crowd gathered outside the home as immediate "
        "danger; that is how a social boycott begins" % language
    )


@pytest.mark.parametrize("language,text", CROWD_REPORTS)
def test_crowd_report_still_carries_the_caste_motive(language, text):
    """The danger anchors must not crowd out the caste signal."""

    incident = understand(text)

    assert incident["caste_based_motive"] is True
    assert incident["confidence_breakdown"]["caste_based_motive"] >= CASTE_FLOOR


def test_confidence_breakdown_keys_match_their_signals():
    """
    Six of eight keys were named like the boolean they explain and two
    were not, so looking up "threat_present" returned None -- which
    reads as zero confidence in a signal that fired.
    """

    incident = understand("My husband hit me and threatened to kill me.")
    breakdown = incident["confidence_breakdown"]

    for signal in (
        "threat_present",
        "injury_present",
        "immediate_danger",
        "caste_based_motive",
        "suicidal_ideation",
    ):
        assert breakdown.get(signal) is not None, (
            "confidence_breakdown has no entry for %s" % signal
        )

    # The short keys svi.py and API_CONTRACT.md depend on must survive.
    assert breakdown["threat"] == breakdown["threat_present"]
    assert breakdown["injury"] == breakdown["injury_present"]


# ------------------------------------------------------------------
# depression_indicators and social_isolation.
#
# SIH26093 asks for both by name. They feed the Stress Vulnerability
# Index rather than the risk tier: they describe how vulnerable
# someone is, not whether they are about to be hurt.
#
# social_isolation does double duty -- the problem statement's
# background lists social boycott among the atrocities people call
# 14566 about, and boycott is an SC/ST Act offence, not just a mood.
# ------------------------------------------------------------------

DEPRESSION_REPORTS = [
    ("en", "I have not been able to leave my room for a month and I feel nothing at all."),
    ("hi", "मैं एक महीने से कमरे से बाहर नहीं निकला हूँ और मुझे कुछ महसूस नहीं होता।"),
    ("te", "నేను నెల రోజులుగా గది నుంచి బయటకు రాలేదు, నాకు ఏమీ అనిపించడం లేదు."),
    ("bn", "আমি এক মাস ধরে ঘর থেকে বেরোইনি, আমার কিছুই ভালো লাগে না।"),
    ("ur", "میں ایک مہینے سے کمرے سے باہر نہیں نکلا، مجھے کچھ محسوس نہیں ہوتا۔"),
]

ISOLATION_REPORTS = [
    ("en", "Nobody in the village talks to me and the shop will not sell me anything."),
    ("hi", "पूरे गाँव ने मुझसे बात करना छोड़ दिया है और दुकान वाले भी कुछ नहीं देते।"),
    ("te", "ఊళ్ళో ఎవరూ నాతో మాట్లాడరు, దుకాణంలో కూడా నాకు ఏమీ ఇవ్వరు."),
    ("bn", "গ্রামের কেউ আমার সঙ্গে কথা বলে না, দোকানেও আমাকে কিছু দেয় না।"),
    ("ur", "گاؤں کا کوئی مجھ سے بات نہیں کرتا، دکان پر بھی کچھ نہیں دیتے۔"),
]

# Every one of these fired one of the two signals during development.
NEITHER_SIGNAL = [
    ("tired", "I am exhausted after a long week at work."),
    ("sad", "I feel sad about what happened but I am managing."),
    ("alone", "I live alone in the city because of my job."),
    ("family", "My family lives in another district."),
    ("not_disclosed", "I have not told anyone about this yet."),
    ("suicidal", "I want to end my life."),
    ("domestic", "My husband hit me and threatened to kill me."),
    ("caste_assault", "My neighbour abused me using my caste name and beat me."),
]


@pytest.mark.parametrize("language,text", DEPRESSION_REPORTS)
def test_depression_indicators_detected_in_every_language(language, text):
    assert understand(text)["depression_indicators"] is True


@pytest.mark.parametrize("language,text", ISOLATION_REPORTS)
def test_social_isolation_detected_in_every_language(language, text):
    assert understand(text)["social_isolation"] is True


@pytest.mark.parametrize("label,text", NEITHER_SIGNAL)
def test_ordinary_distress_fires_neither_signal(label, text):
    """
    Both signals sit on a looser margin than the rest of the file, so
    the negatives matter more here than usual. Tiredness, situational
    sadness, living alone, and choosing not to disclose are what most
    callers say -- a signal that fires on them says nothing.
    """

    incident = understand(text)

    assert incident["depression_indicators"] is False, "%s read as depression" % label
    assert incident["social_isolation"] is False, "%s read as isolation" % label


def test_suicidal_ideation_is_not_absorbed_into_depression():
    """
    They are separate signals with very different weights -- 65 points
    against 20. Collapsing them would either lose the emergency or
    invent one.
    """

    incident = understand("I want to end my life.")

    assert incident["suicidal_ideation"] is True
    assert incident["depression_indicators"] is False


def test_isolation_raises_stress_without_raising_risk():
    """
    A boycotted person is vulnerable, not in immediate danger. These
    signals must move the Stress Vulnerability Index and leave the
    risk tier to the danger signals.
    """

    from svi import assess_stress

    incident = understand(
        "Nobody in the village talks to me and the shop will not sell me anything."
    )
    stress = assess_stress(incident)

    labels = [
        signal["signal"]
        for signal in stress["explainability"]["text_signals"]
    ]

    assert "social_isolation" in labels, "isolation did not reach the SVI"

    # Deliberately not asserting that immediate_danger stays False.
    #
    # A village boycott does currently fire it, because the anchors
    # for a hostile crowd gathered outside the home sit close to it in
    # embedding space. Hard negatives were tried on 2026-09-08 and
    # withdrawn: they separated boycott from danger in four languages
    # and, through cross-lingual similarity, suppressed danger on the
    # Urdu report of a crowd outside the house -- trading a real
    # emergency detection for a tidier queue.
    #
    # So a boycott may over-escalate. That errs toward answering too
    # fast, which is the right direction on a helpline, and the person
    # is picked up either way. Revisit with labelled data, not by
    # guessing at thresholds a week before submission.
