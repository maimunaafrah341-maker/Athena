"""
Risk vocabulary and escalation shape.

Cheap, and guards a mismatch that was not cosmetic: risk.py said
"Medium" while svi.py said "Moderate", the frontend assumed they
agreed, and two live dashboard bugs followed -- mid-risk cases
undercounted in the tier chart, mid-risk pins drawn in the low-risk
colour.
"""

import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from emergency_contacts import get_deterministic_contacts  # noqa: E402
from risk import RESPONSE_PROTOCOL  # noqa: E402
from svi import _tier  # noqa: E402


# SIH26093: "Categorize victims into Low, Moderate, High, and Critical
# Risk categories."
PROBLEM_STATEMENT_TIERS = ["Low", "Moderate", "High", "Critical"]


def test_tiers_match_the_problem_statement():
    assert list(RESPONSE_PROTOCOL) == PROBLEM_STATEMENT_TIERS


def test_medium_is_gone():
    assert "Medium" not in RESPONSE_PROTOCOL, (
        'the problem statement says "Moderate"; "Medium" also collides '
        "with svi.py's stress axis"
    )


def test_svi_bands_use_the_same_vocabulary():
    """
    Two axes, same words. They differed once, and the frontend read
    them as one scale.
    """

    assert {_tier(score) for score in (5, 25, 45, 70)} <= set(PROBLEM_STATEMENT_TIERS)


@pytest.mark.parametrize("tier", PROBLEM_STATEMENT_TIERS)
def test_every_tier_resolves_contacts(tier):
    """A tier the contact table has never heard of returns nothing."""

    get_deterministic_contacts(tier, "Moderate")


def test_contacts_escalate_with_severity():
    """
    More contacts as risk rises. A Critical case offering fewer numbers
    than a Low one would be a silent inversion.
    """

    counts = [
        len(get_deterministic_contacts(tier, "Moderate"))
        for tier in PROBLEM_STATEMENT_TIERS
    ]

    assert counts == sorted(counts), "contact counts do not rise with risk: %s" % counts
    assert counts[-1] > counts[0], "Critical offers no more than Low"


@pytest.mark.parametrize("tier", PROBLEM_STATEMENT_TIERS)
def test_every_tier_has_a_route_and_an_action(tier):
    """
    RESPONSE_PROTOCOL is routing metadata a counsellor acts on. A tier
    missing its route is a case with nowhere to go.
    """

    protocol = RESPONSE_PROTOCOL[tier]

    for field in ("sla", "route", "action"):
        assert protocol.get(field), "%s has no %s" % (tier, field)


# SIH26093: "Automatically recommend counselling, legal aid, medical
# assistance, police intervention, witness protection, or emergency
# support based on risk level." Counselling (Tele-MANAS/KIRAN), legal
# aid (DLSA) and police (SP/DM, 112) were already routed. Medical aid
# and witness protection were named nowhere until a coverage review on
# 2026-09-18 read the problem statement back against the table.
@pytest.mark.parametrize("tier", ["High", "Critical"])
def test_top_tiers_route_medical_aid_and_witness_protection(tier):
    action = RESPONSE_PROTOCOL[tier]["action"]

    assert "Medical Aid" in action, "%s routes no medical assistance" % tier
    assert "Witness Protection" in action, "%s routes no witness protection" % tier


@pytest.mark.parametrize("tier", ["Low", "Moderate"])
def test_lower_tiers_do_not_promise_witness_protection(tier):
    """
    A referral offered at every tier is not a referral. Witness
    protection belongs to the tiers threat and intimidation drive.
    """

    assert "Witness Protection" not in RESPONSE_PROTOCOL[tier]["action"]


@pytest.mark.parametrize("tier", ["High", "Critical"])
def test_a_medical_capable_number_reaches_the_top_tiers(tier):
    """
    112 is India's unified emergency number, police, fire AND ambulance,
    so "medical assistance" is a real number on the reply and not only
    a line in the staff-facing protocol.
    """

    phones = {c["phone"] for c in get_deterministic_contacts(tier, "Moderate")}

    assert "112" in phones, "%s offers no ambulance-capable number" % tier
