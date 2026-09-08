"""
End-to-end API behaviour, through FastAPI's TestClient.

These are the checks that were being run by hand against a live server
after every change. Every one of them guards something that would be
invisible until a real person hit it: an admin endpoint that stopped
requiring a key, a follow-up token that stopped being checked, an empty
report that answered 200 and escalated nothing.

conftest.py redirects the database to a temp file before these import.
"""

import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402

KEY = os.getenv("ADMIN_API_KEY") or ""

client = TestClient(app)

auth = {"X-API-Key": KEY}


# Endpoints that must never answer without a key. Each is a read or a
# write over real case data.
ADMIN_GETS = [
    "/stats",
    "/stats/trend",
    "/stats/districts",
    "/cases",
    "/cases/map",
]


@pytest.fixture(scope="module")
def case_id():
    """One real case, filed through the pipeline, reused by the tests."""

    response = client.post(
        "/report",
        json={
            "text": "My neighbour abused me using my caste name and beat me.",
            "district": "Hyderabad",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body.get("case_id"), "report did not produce a case"

    return body["case_id"], body.get("follow_up_token")


# ------------------------------------------------------------------
# Public surface
# ------------------------------------------------------------------

def test_health_is_public():
    assert client.get("/health").status_code == 200


def test_call_options_returns_real_numbers():
    """
    The emergency numbers must not depend on retrieval having found
    anything. They are a hardcoded, always-available source.
    """

    body = client.get("/call-options").json()

    assert body, "no call options returned"
    assert any(option["phone"] == "112" for option in body), (
        "112 missing from the emergency numbers"
    )


@pytest.mark.parametrize("text", ["", "   ", "\n"])
def test_empty_report_is_rejected(text):
    """
    This answered 200 with an empty response and escalate: true --
    claiming an escalation with no case behind it.
    """

    response = client.post("/report", json={"text": text})

    assert response.status_code == 400


def test_sos_needs_no_text():
    """Pressing the button is itself the signal."""

    response = client.post("/sos", json={})

    assert response.status_code == 200
    assert response.json()["risk"]["risk_tier"] == "Critical"


# ------------------------------------------------------------------
# Admin gating
# ------------------------------------------------------------------

@pytest.mark.parametrize("path", ADMIN_GETS)
def test_admin_endpoints_require_a_key(path):
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("path", ADMIN_GETS)
def test_admin_endpoints_accept_the_key(path):
    assert client.get(path, headers=auth).status_code == 200


def test_a_wrong_key_is_rejected():
    assert client.get("/stats", headers={"X-API-Key": "not-the-key"}).status_code == 401


# ------------------------------------------------------------------
# The reporter's follow-up preference: public, token-gated, one-shot
# ------------------------------------------------------------------

def test_follow_up_requires_the_token(case_id):
    identifier, _ = case_id

    response = client.post(
        "/cases/%s/follow-up" % identifier,
        json={"preference": "text_only"},
    )

    assert response.status_code == 403


def test_follow_up_rejects_a_wrong_token(case_id):
    identifier, _ = case_id

    response = client.post(
        "/cases/%s/follow-up" % identifier,
        json={"preference": "text_only", "token": "wrong"},
    )

    assert response.status_code == 403


def test_follow_up_is_accepted_once_then_refused(case_id):
    """
    One-shot by design: the token is handed to whoever filed the
    report, and a preference that can be overwritten is a preference
    anyone holding the link can overwrite.
    """

    identifier, token = case_id

    first = client.post(
        "/cases/%s/follow-up" % identifier,
        json={"preference": "text_only", "note": "after 6pm", "token": token},
    )

    assert first.status_code == 200

    second = client.post(
        "/cases/%s/follow-up" % identifier,
        json={"preference": "call_only", "token": token},
    )

    assert second.status_code == 409


def test_follow_up_token_does_not_work_on_another_case(case_id):
    """The token is per case, not a general pass."""

    _, token = case_id

    response = client.post(
        "/cases/999999/follow-up",
        json={"preference": "text_only", "token": token},
    )

    assert response.status_code == 403


def test_follow_up_rejects_an_invalid_preference(case_id):
    identifier, token = case_id

    response = client.post(
        "/cases/%s/follow-up" % identifier,
        json={"preference": "whenever", "token": token},
    )

    assert response.status_code in (400, 409)


# ------------------------------------------------------------------
# Counsellor actions
# ------------------------------------------------------------------

def test_case_brief_carries_the_translation_slot(case_id):
    identifier, _ = case_id

    brief = client.get("/cases/%s/brief" % identifier, headers=auth).json()

    assert "summary_translated" in brief


def test_acknowledge_is_idempotent(case_id):
    identifier, _ = case_id
    path = "/cases/%s/acknowledge" % identifier

    assert client.post(path, json={}, headers=auth).status_code == 200
    assert client.post(path, json={}, headers=auth).status_code == 200


def test_notes_and_escalate_accept_the_key(case_id):
    identifier, _ = case_id

    assert client.post(
        "/cases/%s/notes" % identifier,
        json={"note": "Called, no answer."},
        headers=auth,
    ).status_code == 200

    assert client.post(
        "/cases/%s/escalate" % identifier, json={}, headers=auth
    ).status_code == 200


def test_unknown_case_is_404_not_500(case_id):
    assert client.get("/cases/999999", headers=auth).status_code == 404


# ------------------------------------------------------------------
# Map privacy
# ------------------------------------------------------------------

def test_map_never_exposes_reporter_identity():
    """
    Pins carry district-level coordinates by necessity. They must not
    carry anything that identifies who filed the report.
    """

    body = client.get("/cases/map", headers=auth).json()

    forbidden = {
        "original_text",
        "reporter_name",
        "reporter_contact",
        "response",
        "district",
    }

    for pin in body["pins"]:
        leaked = forbidden & set(pin)
        assert not leaked, "map pin exposes %s" % sorted(leaked)


def test_map_reports_its_own_suppression():
    """
    A map that silently drops sparse districts reads as "no atrocities
    reported here". It has to say how many it withheld.
    """

    body = client.get("/cases/map", headers=auth).json()

    assert "suppressed" in body
    assert "min_group_size" in body
    assert body["min_group_size"] >= 3


def test_the_helpline_offers_its_own_number():
    """
    14566 was missing from NATIONAL_HELPLINES until 2026-09-08, so
    Athena offered a person in danger every national number except the
    one this project exists to serve.
    """

    numbers = {option["phone"] for option in client.get("/call-options").json()}

    assert "14566" in numbers, "the NHAA helpline is not offered to reporters"
    assert "112" in numbers


def test_mental_health_support_is_offered():
    """
    SIH26093 asks the system to detect suicidal ideation and recommend
    counselling. Detecting it while offering only police numbers is
    identifying a crisis and routing it nowhere.
    """

    numbers = {option["phone"] for option in client.get("/call-options").json()}

    assert "1800-599-0019" in numbers, "KIRAN is not offered"
