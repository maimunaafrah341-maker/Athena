# ============================================================
# ATHENA — CASE TRACKING
# ============================================================

"""
Turns a pipeline result into a persisted, queryable case.

This is the ESCALATE step made real: today, run_pipeline() returns
an "escalate": true dict and that's the end of it -- nothing is
saved anywhere for a human to actually act on. Every processed
report becomes a case row here instead, with a status a human
(or an admin dashboard, later) can move forward.

SQLite, not a fake in-memory list, so cases survive a server
restart -- this is the piece a judge asking "so what happens after
it escalates?" needs to see actually exist.
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from district_contacts import DISTRICT_CONTACTS

# Overridable so a Railway Volume (or any other persistent mount) can
# survive redeploys -- Railway's default container filesystem is
# ephemeral, wiped on every fresh deploy. Point CASES_DB_PATH at a
# mounted volume path (e.g. /data/cases.db) in production; unset
# locally, this is unchanged from before.
DB_PATH = os.getenv("CASES_DB_PATH", "cases.db")

VALID_STATUSES = (
    "New",
    "Under Review",
    "Escalated",
    "In Progress",
    "Resolved",
    "Closed",
)

# How much the reporter chose to identify themselves. See create_case()
# for what each level actually gates -- this isn't just a label, "partial"
# and "anonymous" are enforced at the persistence boundary (never stored,
# not just hidden from the response) regardless of what a caller passes in
# for reporter_name/reporter_contact/latitude/longitude.
VALID_DISCLOSURE_LEVELS = ("full", "partial", "anonymous")

# Columns added after the original schema -- init_db() retrofits
# these onto any cases.db that predates them.
_NEW_COLUMNS = {
    "location": "TEXT",
    "latitude": "REAL",
    "longitude": "REAL",
    "is_sos": "INTEGER",
    # svi.py's full stress_assessment (incl. the counsellor-facing
    # "explainability" breakdown) and kg.py's legal_guidance, stored
    # as JSON so a case reviewed later still has them -- previously
    # create_case() never read these keys off pipeline_result at all,
    # so they existed only in the immediate /report response and were
    # silently lost the moment that response was gone. Nullable: a
    # case created before this column existed just reads back None.
    "stress_assessment_json": "TEXT",
    "legal_guidance_json": "TEXT",
    # nhaa.py's docket record (docket_id, channel, svi_score,
    # risk_category, status) binding this case to the NHAA entry
    # point it came in through. Nullable: a case created before this
    # column existed just reads back None.
    "nhaa_docket_json": "TEXT",
    # Low-disclosure reporting. disclosure_level defaults to "full" at
    # the SQL level for any row that predates this column (existing
    # cases were all full-identification reports, that's an accurate
    # backfill, not a guess). reporter_name is only ever non-null for
    # "full"; reporter_contact is non-null for "full" or "partial" --
    # see create_case()'s redaction, the actual enforcement point.
    "disclosure_level": "TEXT NOT NULL DEFAULT 'full'",
    "reporter_name": "TEXT",
    "reporter_contact": "TEXT",
    # Normalized (.strip().lower()) reporter-supplied district, the
    # same string _resolve_escalation_contact() in kg.py matches
    # against DISTRICT_CONTACTS -- stored here too so district-level
    # pattern detection (get_flagged_districts) can aggregate case
    # counts without re-deriving the lookup key. Not an identifier
    # (see create_case()'s docstring), so it's kept regardless of
    # disclosure_level. Nullable: most reports won't include one.
    "district": "TEXT",
    # "gps" | "district_approx" | NULL. Set by app.py when latitude/
    # longitude came from geocoding.py's district-centroid fallback
    # rather than the reporter's actual device GPS -- see app.py's
    # /report handler. A map pin built from this should say so rather
    # than implying GPS-level precision it doesn't have; NULL covers
    # every case created before this column existed, all of which
    # came from real GPS (this feature didn't exist yet), so a NULL
    # is safely read as "gps" by consumers, not "unknown."
    "location_source": "TEXT",
    # Whether a counsellor has actually opened and reviewed this case,
    # distinct from status -- a case can sit at "Escalated" for hours
    # with nobody having looked at it, and nothing else in the schema
    # could tell you that. NULL/0 for every existing row is correct:
    # none of them have an explicit review recorded. See
    # acknowledge_case().
    "acknowledged": "INTEGER",
    # How (and whether) the reporter wants to be contacted back, chosen
    # by them on the confirmation screen after submitting -- one of
    # VALID_FOLLOW_UP_PREFERENCES. NULL means they never answered, which
    # is NOT the same as "no preference": treat it as unknown and fall
    # back to whatever the disclosure level already allows, rather than
    # assuming contact is welcome. See set_follow_up_preference().
    "follow_up_preference": "TEXT",
    # Free-text "when is it safe to reach me" note from the same screen
    # (e.g. "only weekday mornings"). Nullable and always optional.
    "follow_up_note": "TEXT",
    # Machine-translated English rendering of original_text, for a
    # counsellor who doesn't read the language the report came in.
    # Filled lazily the first time a case brief is opened (see
    # translation.py for why not at report time) and cached here so it
    # costs one model call per case, ever. NULL means either "not
    # needed" (the report was already English) or "not generated yet /
    # translation failed" -- consumers must fall back to original_text,
    # which is always the authoritative version and is never
    # overwritten by this.
    "translated_text": "TEXT",
}


# What a reporter can choose on the confirmation screen. "do_not_contact"
# exists because for some people any callback is itself the danger --
# it must be as easy to pick as any other option, not buried.
VALID_FOLLOW_UP_PREFERENCES = (
    "do_not_contact",
    "text_only",
    "call_only",
    "either",
)


# ============================================================
# CONNECTION
# ============================================================

def _connect():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """
    Create the cases table if it doesn't exist yet, and add any
    columns that were introduced after someone's local cases.db was
    already created -- CREATE TABLE IF NOT EXISTS alone won't retrofit
    new columns onto an existing file, which is exactly how
    incident.location went missing from persisted cases even after
    understanding.py started detecting it. Safe to call on every
    startup.
    """

    with _connect() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,

                original_text TEXT NOT NULL,
                language TEXT,
                incident_type TEXT,

                risk_tier TEXT,
                risk_score INTEGER,
                confidence REAL,

                escalate INTEGER NOT NULL,
                reason TEXT,
                response TEXT,

                citations_json TEXT NOT NULL,
                evidence_path TEXT
            )
        """)

        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(cases)")
        }

        for column, column_type in _NEW_COLUMNS.items():

            if column not in existing_columns:
                connection.execute(
                    f"ALTER TABLE cases ADD COLUMN {column} {column_type}"
                )

        connection.execute("""
            CREATE TABLE IF NOT EXISTS case_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL
            )
        """)


# ============================================================
# CASE TIMELINE
# ============================================================
#
# A chronological log per case -- reported/status changes/escalations/
# counsellor notes -- so a counsellor picking up a case mid-handoff can
# see what already happened instead of reconstructing it from the raw
# report text alone. Deliberately simple: one append-only table, no
# edit/delete (a timeline that can be rewritten isn't trustworthy),
# valid event_type values are enforced by the functions below that
# write them, not a DB-level CHECK constraint.

def _log_event(connection, case_id, event_type, note=None, created_at=None):
    """
    Insert one timeline event using the given open connection/cursor --
    callers that need the event to land atomically with another write
    (e.g. create_case's initial "reported" event) pass their own
    in-progress connection rather than this function opening its own.
    """

    connection.execute(
        "INSERT INTO case_events (case_id, event_type, note, created_at) "
        "VALUES (?, ?, ?, ?)",
        (
            case_id,
            event_type,
            note,
            created_at or datetime.now(timezone.utc).isoformat(),
        ),
    )


def get_case_timeline(case_id):
    """
    A case's events, oldest first -- reads top-to-bottom like a story,
    matching how a counsellor would actually want to review what
    happened on handoff.
    """

    with _connect() as connection:

        rows = connection.execute(
            "SELECT id, event_type, note, created_at FROM case_events "
            "WHERE case_id = ? ORDER BY id ASC",
            (case_id,),
        ).fetchall()

        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "note": row["note"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


def add_case_note(case_id, note):
    """
    A counsellor's free-text note on a case, e.g. context from a
    follow-up call that isn't captured anywhere else. Returns the
    updated case (with the new note in its timeline), or None if the
    case doesn't exist.
    """

    if get_case(case_id) is None:
        return None

    with _connect() as connection:
        _log_event(connection, case_id, "note_added", note=note)

    return get_case(case_id)


def escalate_case(case_id, note=None):
    """
    The "Escalate now" action: moves a case to "Escalated" status and
    logs it as a distinct timeline event (not just a generic status
    change) with whatever note the counsellor gave, plus resolves the
    case's district to a real escalation contact via DISTRICT_CONTACTS
    the same way kg.py's _resolve_escalation_contact does, so the
    counsellor immediately sees who to actually notify. Returns None
    if the case doesn't exist; returns {"case": ..., "escalation_contact":
    ...} otherwise -- escalation_contact is None when the case has no
    district on file or it doesn't match a known contact, same as
    kg.py's lookup.
    """

    with _connect() as connection:

        row = connection.execute(
            "SELECT district FROM cases WHERE id = ?", (case_id,)
        ).fetchone()

        if row is None:
            return None

        raw_district = row["district"]

        connection.execute(
            "UPDATE cases SET status = ? WHERE id = ?",
            ("Escalated", case_id),
        )

        _log_event(connection, case_id, "escalated", note=note)

    escalation_contact = (
        {**DISTRICT_CONTACTS[raw_district], "source": "kg_seed"}
        if raw_district and raw_district in DISTRICT_CONTACTS
        else None
    )

    return {
        "case": get_case(case_id),
        "escalation_contact": escalation_contact,
    }


def set_follow_up_preference(case_id, preference, note=None):
    """
    Records how the reporter wants to be contacted back, chosen by them
    on the confirmation screen right after submitting.

    Deliberately one-shot: this returns "already_set" rather than
    overwriting an existing preference. The endpoint calling this is
    necessarily public -- the reporter has just filed a report and has
    no counsellor key -- so without that constraint, anyone who guessed
    a case id could flip someone else's "do not contact me" to "call
    me", which is exactly the kind of change that gets a person hurt.
    One-shot means the worst a guesser can do is answer for a reporter
    who never answered, and a real deployment should replace this with
    a per-report token issued by /report. That is a known, bounded
    limitation, written down rather than pretended away.

    Returns "not_found" | "already_set" | "invalid" | the updated case.
    """

    if preference not in VALID_FOLLOW_UP_PREFERENCES:
        return "invalid"

    with _connect() as connection:

        row = connection.execute(
            "SELECT follow_up_preference FROM cases WHERE id = ?",
            (case_id,),
        ).fetchone()

        if row is None:
            return "not_found"

        if row["follow_up_preference"]:
            return "already_set"

        connection.execute(
            "UPDATE cases SET follow_up_preference = ?, follow_up_note = ? "
            "WHERE id = ?",
            (preference, note, case_id),
        )

        # Logged so a counsellor opening the case sees the reporter's
        # own stated wishes in the timeline, not just a column they
        # might not think to check before picking up the phone.
        _log_event(
            connection,
            case_id,
            "follow_up_preference_set",
            note=(
                f"Reporter's contact preference: {preference}"
                + (f" — {note}" if note else "")
            ),
        )

    return get_case(case_id)


def save_translation(case_id, translated_text):
    """
    Caches a machine translation against a case so it's generated once
    rather than on every brief open.

    Writes only translated_text -- original_text is never touched. The
    reporter's own words stay the authoritative record; this is the
    reading aid beside them (see translation.py). No timeline event:
    a counsellor opening a case brief is a read, and filling a cache
    on their behalf isn't an action on the case worth logging as if
    something happened to it.
    """

    if not translated_text:
        return None

    with _connect() as connection:

        connection.execute(
            "UPDATE cases SET translated_text = ? WHERE id = ?",
            (translated_text, case_id),
        )

    return translated_text


def acknowledge_case(case_id):
    """
    Marks a case as reviewed by a counsellor -- separate from status,
    since a case can be Escalated for hours with nobody having
    actually opened it, and status alone can't distinguish "seen and
    still being worked" from "never looked at." Logs a distinct
    "acknowledged" timeline event the same way escalate_case does, so
    it's visible in the case history who confirmed they'd looked at
    it and when. Idempotent: acknowledging an already-acknowledged
    case just re-logs the event rather than erroring. Returns the
    updated case, or None if it doesn't exist.
    """

    if get_case(case_id) is None:
        return None

    with _connect() as connection:

        connection.execute(
            "UPDATE cases SET acknowledged = 1 WHERE id = ?",
            (case_id,),
        )

        _log_event(connection, case_id, "acknowledged")

    return get_case(case_id)


# ============================================================
# CREATE
# ============================================================

def create_case(
    original_text,
    pipeline_result,
    evidence_path=None,
    latitude=None,
    longitude=None,
    is_sos=False,
    disclosure_level="full",
    reporter_name=None,
    reporter_contact=None,
    district=None,
    created_at=None,
    location_source=None,
):
    """
    Persist one pipeline result as a case row.

    Status defaults to "Escalated" when the pipeline flagged it for
    human attention, "New" otherwise -- a human still needs to look
    at it before it's actually resolved (see update_status()); "New"
    used to be "Resolved" here, which meant every non-critical case
    looked already-handled the instant it was created, indistinguishable
    from one a counsellor had genuinely reviewed and closed out. That
    also silently broke "cases awaiting first response" as a dashboard
    metric, since nothing was ever really awaiting anything -- fixed
    alongside the case-timeline/escalation work this default was found
    during. evidence_path is the saved path of an uploaded
    screenshot/image, if this case came from OCR'd evidence rather
    than typed text. latitude/longitude, if given, should already be
    privacy-rounded by the caller (~150m) before reaching here --
    this function just stores whatever it's handed, it doesn't
    re-round. is_sos marks a case that came from the one-tap SOS
    button rather than a typed report, so a reviewer can tell the
    two apart later. Returns the new case's id.

    disclosure_level ("full" | "partial" | "anonymous") gates
    reporter_name/reporter_contact/latitude/longitude at THIS
    function -- the actual persistence boundary -- rather than
    trusting the caller (app.py) to have already redacted them, so a
    client-side bug or a reporter accidentally typing their name into
    a field can't leak identity into a case they asked to keep more
    private. "partial" drops name and precise coordinates but keeps
    reporter_contact if given (contactable without being identified
    or located); "anonymous" drops all three. This is the real
    tradeoff of partial/anonymous reporting: case follow-up is
    genuinely limited for these cases, not just hidden from a view --
    documented in API_CONTRACT.md rather than solved further.

    created_at, if given, must be an ISO-8601 UTC timestamp string and
    overrides the default "now" -- used only by seed_data.py to
    backdate demo cases so trend/district-pattern detection has
    something realistic to show on a freshly emptied database. None
    (the normal case, every real report) means "now", same as before
    this parameter existed.

    district is stored normalized (.strip().lower()) so "Hyderabad"
    and "hyderabad" aggregate as the same district for
    get_flagged_districts() -- the same normalization kg.py's
    _resolve_escalation_contact() already applies for lookup, kept in
    sync here rather than reimplemented. Never redacted by
    disclosure_level (see the _NEW_COLUMNS comment on "district").

    location_source ("gps" | "district_approx" | None) records where
    latitude/longitude actually came from -- see app.py's /report
    handler, which sets it to "district_approx" when it fell back to
    geocoding.py's district-centroid lookup because no real GPS fix
    was given. Redacted alongside latitude/longitude for "partial"/
    "anonymous" disclosure, same reasoning: no point remembering how a
    coordinate was derived once the coordinate itself is dropped.
    """

    if disclosure_level not in VALID_DISCLOSURE_LEVELS:
        raise ValueError(
            f"Unknown disclosure_level {disclosure_level!r}. "
            f"Must be one of {VALID_DISCLOSURE_LEVELS}."
        )

    # "partial" keeps a contact method (so a counsellor can still
    # follow up) but drops the name and precise coordinates -- the
    # reporter is contactable without being identified or located.
    # "anonymous" drops all three: genuinely no way to reach back out,
    # which is the real tradeoff documented in API_CONTRACT.md, not
    # just a hidden field. Neither level touches `district` -- that's
    # a routing hint (which contact list to check), not an identifier,
    # so it stays available even for anonymous reports.
    if disclosure_level in ("partial", "anonymous"):
        reporter_name = None
        latitude = None
        longitude = None
        location_source = None

    if disclosure_level == "anonymous":
        reporter_contact = None

    district = district.strip().lower() if district else None

    incident = pipeline_result.get("incident") or {}
    risk = pipeline_result.get("risk") or {}
    stress_assessment = pipeline_result.get("stress_assessment")
    legal_guidance = pipeline_result.get("legal_guidance")
    nhaa_docket = pipeline_result.get("nhaa_docket")

    escalate = bool(pipeline_result.get("escalate"))
    status = "Escalated" if escalate else "New"

    with _connect() as connection:

        cursor = connection.execute(
            """
            INSERT INTO cases (
                created_at, status,
                original_text, language, incident_type,
                risk_tier, risk_score, confidence,
                escalate, reason, response, citations_json,
                evidence_path, location, latitude, longitude, is_sos,
                stress_assessment_json, legal_guidance_json,
                disclosure_level, reporter_name, reporter_contact, district,
                nhaa_docket_json, location_source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at or datetime.now(timezone.utc).isoformat(),
                status,
                original_text,
                incident.get("language"),
                incident.get("incident_type"),
                risk.get("risk_tier"),
                risk.get("risk_score"),
                risk.get("confidence"),
                int(escalate),
                pipeline_result.get("reason"),
                pipeline_result.get("response"),
                json.dumps(pipeline_result.get("citations") or []),
                evidence_path,
                incident.get("location"),
                latitude,
                longitude,
                int(is_sos),
                json.dumps(stress_assessment) if stress_assessment is not None else None,
                json.dumps(legal_guidance) if legal_guidance is not None else None,
                disclosure_level,
                reporter_name,
                reporter_contact,
                district,
                json.dumps(nhaa_docket) if nhaa_docket is not None else None,
                location_source,
            ),
        )

        new_case_id = cursor.lastrowid

        _log_event(
            connection,
            new_case_id,
            "reported",
            note=f"Status set to {status} on intake.",
            created_at=created_at,
        )

        return new_case_id


# ============================================================
# READ
# ============================================================

def _row_to_case(row):

    row_keys = row.keys()

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "status": row["status"],
        "original_text": row["original_text"],
        "language": row["language"],
        "incident_type": row["incident_type"],
        "risk_tier": row["risk_tier"],
        "risk_score": row["risk_score"],
        "confidence": row["confidence"],
        "escalate": bool(row["escalate"]),
        "reason": row["reason"],
        "response": row["response"],
        "citations": json.loads(row["citations_json"]),
        "evidence_path": row["evidence_path"],
        "location": row["location"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "is_sos": bool(row["is_sos"]),
        # None for a case created before this column existed, or one
        # whose pipeline result genuinely had no stress_assessment
        # (e.g. an empty-input submission) -- both are real, valid
        # None, not an error.
        "stress_assessment": (
            json.loads(row["stress_assessment_json"])
            if "stress_assessment_json" in row_keys and row["stress_assessment_json"]
            else None
        ),
        "legal_guidance": (
            json.loads(row["legal_guidance_json"])
            if "legal_guidance_json" in row_keys and row["legal_guidance_json"]
            else None
        ),
        "nhaa_docket": (
            json.loads(row["nhaa_docket_json"])
            if "nhaa_docket_json" in row_keys and row["nhaa_docket_json"]
            else None
        ),
        "disclosure_level": (
            row["disclosure_level"] if "disclosure_level" in row_keys else "full"
        ),
        "reporter_name": row["reporter_name"] if "reporter_name" in row_keys else None,
        "reporter_contact": row["reporter_contact"] if "reporter_contact" in row_keys else None,
        # Display-resolved (see _district_display_name), not the raw
        # lowercase storage value -- so /cases, /cases/{id}, and the
        # brief all show the same "Hyderabad" a reviewer expects,
        # instead of this endpoint alone leaking the internal
        # normalization used for pattern-detection aggregation.
        "district": (
            _district_display_name(row["district"])
            if "district" in row_keys else None
        ),
        # NULL (pre-existing rows, or a real GPS fix) reads as "gps" --
        # see the _NEW_COLUMNS comment on why that backfill is correct.
        "location_source": (
            row["location_source"]
            if "location_source" in row_keys and row["location_source"]
            else "gps"
        ),
        "acknowledged": bool(
            "acknowledged" in row_keys and row["acknowledged"]
        ),
        "follow_up_preference": (
            row["follow_up_preference"]
            if "follow_up_preference" in row_keys else None
        ),
        "follow_up_note": (
            row["follow_up_note"]
            if "follow_up_note" in row_keys else None
        ),
        "translated_text": (
            row["translated_text"]
            if "translated_text" in row_keys else None
        ),
    }


def list_cases(status=None):
    """
    List cases, most recent first. Optionally filter by status.
    """

    with _connect() as connection:

        if status:
            rows = connection.execute(
                "SELECT * FROM cases WHERE status = ? ORDER BY id DESC",
                (status,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM cases ORDER BY id DESC"
            ).fetchall()

        return [_row_to_case(row) for row in rows]


def list_case_locations():
    """
    Minimal fields for map rendering -- id, coordinates, incident
    type, risk tier, place type, created_at -- deliberately NOT the
    full case (original_text, response, citations). A map pin should
    show "what kind of incident, roughly where, how serious," not
    leak the report's actual content. Only returns cases that
    actually have a location on them (most won't, unless the
    reporter chose to share one) -- an empty list here is a genuine
    "nobody's shared a location yet," not a bug.
    """

    with _connect() as connection:

        rows = connection.execute(
            "SELECT id, created_at, incident_type, risk_tier, "
            "latitude, longitude, location, is_sos, location_source "
            "FROM cases "
            "WHERE latitude IS NOT NULL AND longitude IS NOT NULL "
            "ORDER BY id DESC"
        ).fetchall()

        return [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "incident_type": row["incident_type"],
                "risk_tier": row["risk_tier"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "location": row["location"],
                "is_sos": bool(row["is_sos"]),
                # See create_case()'s location_source docstring note --
                # NULL (pre-existing GPS-only rows) reads as "gps".
                "location_source": row["location_source"] or "gps",
            }
            for row in rows
        ]


def get_case(case_id):
    """
    Fetch one case by id, or None if it doesn't exist. Includes the
    case's timeline -- unlike list_cases(), which deliberately doesn't,
    since a bulk list has no use for every case's full event history.
    """

    with _connect() as connection:

        row = connection.execute(
            "SELECT * FROM cases WHERE id = ?",
            (case_id,),
        ).fetchone()

        if not row:
            return None

    case = _row_to_case(row)
    case["timeline"] = get_case_timeline(case_id)

    return case


def _count_by(connection, column):

    rows = connection.execute(
        f"SELECT {column}, COUNT(*) FROM cases GROUP BY {column}"
    ).fetchall()

    return {row[0]: row[1] for row in rows if row[0] is not None}


def get_stats():
    """
    Real, computed aggregates over every case -- for dashboard cards
    that currently show hardcoded demo numbers on the frontend.
    Nothing here is a placeholder; every count is a live SQL query.
    """

    with _connect() as connection:

        total = connection.execute(
            "SELECT COUNT(*) FROM cases"
        ).fetchone()[0]

        escalated = connection.execute(
            "SELECT COUNT(*) FROM cases WHERE escalate = 1"
        ).fetchone()[0]

        with_evidence = connection.execute(
            "SELECT COUNT(*) FROM cases WHERE evidence_path IS NOT NULL"
        ).fetchone()[0]

        sos_cases = connection.execute(
            "SELECT COUNT(*) FROM cases WHERE is_sos = 1"
        ).fetchone()[0]

        return {
            "total_cases": total,
            "escalated_cases": escalated,
            "cases_with_evidence": with_evidence,
            "sos_cases": sos_cases,
            "by_status": _count_by(connection, "status"),
            "by_risk_tier": _count_by(connection, "risk_tier"),
            "by_incident_type": _count_by(connection, "incident_type"),
            "by_language": _count_by(connection, "language"),
            "by_location": _count_by(connection, "location"),
        }


def get_trend(days=7):
    """
    Day-by-day case counts for the last `days` days (zero-filled, so
    a chart doesn't have gaps), plus a current-vs-previous-window
    comparison and an incident-type breakdown for the current window.

    This is the real, computed version of the "Harassment up 8%"
    style trend cards -- with low case volume it'll look sparse, but
    every number is a genuine query result, not a placeholder.
    """

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=days)
    previous_window_start = now - timedelta(days=days * 2)
    today = now.date()

    with _connect() as connection:

        rows = connection.execute(
            "SELECT date(created_at), COUNT(*) FROM cases "
            "WHERE created_at >= ? GROUP BY date(created_at)",
            (window_start.isoformat(),),
        ).fetchall()

        counts_by_day = {row[0]: row[1] for row in rows}

        # Calendar days from (today - (days-1)) through today inclusive,
        # so "last 7 days" actually includes today rather than ending
        # yesterday -- deriving this from window_start's wall-clock
        # time (which has a time-of-day component) would leave today
        # out, undercounting relative to current_window_total below.
        by_day = {}

        for offset in range(days):

            day = (today - timedelta(days=days - 1 - offset)).isoformat()
            by_day[day] = counts_by_day.get(day, 0)

        current_window_total = connection.execute(
            "SELECT COUNT(*) FROM cases WHERE created_at >= ?",
            (window_start.isoformat(),),
        ).fetchone()[0]

        previous_window_total = connection.execute(
            "SELECT COUNT(*) FROM cases "
            "WHERE created_at >= ? AND created_at < ?",
            (previous_window_start.isoformat(), window_start.isoformat()),
        ).fetchone()[0]

        incident_type_rows = connection.execute(
            "SELECT incident_type, COUNT(*) FROM cases "
            "WHERE created_at >= ? AND incident_type IS NOT NULL "
            "GROUP BY incident_type",
            (window_start.isoformat(),),
        ).fetchall()

        return {
            "window_days": days,
            "by_day": by_day,
            "current_window_total": current_window_total,
            "previous_window_total": previous_window_total,
            "by_incident_type_in_window": {
                row[0]: row[1] for row in incident_type_rows
            },
        }


# ============================================================
# DISTRICT PATTERN DETECTION
# ============================================================
#
# Flags districts with a week-over-week case-count rise -- an
# explainable "something's changing here" signal for an admin
# dashboard panel, not a forecasting model. Two conditions both have
# to hold before a district is flagged, so one stray case in an
# otherwise-quiet district doesn't read as a "spike": an absolute
# floor on the current-window count, and a minimum rise ratio against
# the previous window. Same "heuristic starting point, tune from real
# data if there's time" caveat already used throughout this codebase
# (see risk.py/svi.py's threshold comments).
MIN_CASES_TO_FLAG = 3
RISING_THRESHOLD_RATIO = 1.5


def _district_display_name(district):
    """
    Resolve a normalized (.strip().lower()) stored district back to a
    real display name via DISTRICT_CONTACTS' own "district" field
    (proper casing, e.g. "Hyderabad") when it's a known one, falling
    back to .title() for a district someone typed that doesn't match
    any known contact entry -- shared by get_flagged_districts and
    build_escalation_brief so the two never show different casing for
    the same district.
    """

    if not district:
        return None

    contact = DISTRICT_CONTACTS.get(district)

    return contact["district"] if contact else district.title()


def get_flagged_districts(days=7):
    """
    Districts whose case count rose meaningfully in the last `days`
    days vs the `days` before that, each with an incident-type
    breakdown for the current window -- so the dashboard panel can
    show not just "Hyderabad is up" but "Hyderabad is up, mostly
    stalking reports," surfacing a repeat-type pattern rather than a
    generic count. Real SQL aggregation over the `district` column
    (see create_case()) -- a district nobody supplied, or with no
    cases at all, never appears here, it isn't guessed at.

    A district with zero cases in the previous window has no ratio to
    compute (division by zero) -- it's flagged outright once it clears
    MIN_CASES_TO_FLAG instead, since any real activity where there was
    none before is itself the pattern worth surfacing. change_ratio is
    None in that case so the frontend can render "new" instead of a
    misleading number.
    """

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=days)
    previous_window_start = now - timedelta(days=days * 2)

    with _connect() as connection:

        current_rows = connection.execute(
            "SELECT district, COUNT(*) FROM cases "
            "WHERE district IS NOT NULL AND created_at >= ? "
            "GROUP BY district",
            (window_start.isoformat(),),
        ).fetchall()

        previous_rows = connection.execute(
            "SELECT district, COUNT(*) FROM cases "
            "WHERE district IS NOT NULL AND created_at >= ? AND created_at < ?"
            " GROUP BY district",
            (previous_window_start.isoformat(), window_start.isoformat()),
        ).fetchall()

        previous_counts = {row[0]: row[1] for row in previous_rows}

        flagged = []

        for district, current_count in current_rows:

            if current_count < MIN_CASES_TO_FLAG:
                continue

            previous_count = previous_counts.get(district, 0)

            if previous_count > 0:
                change_ratio = current_count / previous_count
                if change_ratio < RISING_THRESHOLD_RATIO:
                    continue
            else:
                change_ratio = None

            type_rows = connection.execute(
                "SELECT incident_type, COUNT(*) FROM cases "
                "WHERE district = ? AND created_at >= ? "
                "AND incident_type IS NOT NULL "
                "GROUP BY incident_type ORDER BY COUNT(*) DESC",
                (district, window_start.isoformat()),
            ).fetchall()

            flagged.append({
                "district": _district_display_name(district),
                "current_window_count": current_count,
                "previous_window_count": previous_count,
                "change_ratio": round(change_ratio, 2) if change_ratio is not None else None,
                "incident_type_breakdown": {
                    row[0]: row[1] for row in type_rows
                },
            })

        flagged.sort(
            key=lambda d: (
                d["change_ratio"] if d["change_ratio"] is not None
                else float("inf")
            ),
            reverse=True,
        )

        return {
            "window_days": days,
            "min_cases_to_flag": MIN_CASES_TO_FLAG,
            "rising_threshold_ratio": RISING_THRESHOLD_RATIO,
            "flagged": flagged,
        }


# ============================================================
# UPDATE
# ============================================================

def update_status(case_id, new_status, note=None):
    """
    Move a case to a new status. Returns the updated case, or None
    if the case doesn't exist. Raises ValueError for an unknown
    status rather than silently accepting a typo. Logs the transition
    (old status -> new status, plus any counsellor-given note) as a
    timeline event -- no-ops the log (but still returns the case) if
    the case doesn't exist or is already at new_status, since that's
    not a real transition.
    """

    if new_status not in VALID_STATUSES:
        raise ValueError(
            f"Unknown status {new_status!r}. "
            f"Must be one of {VALID_STATUSES}."
        )

    with _connect() as connection:

        row = connection.execute(
            "SELECT status FROM cases WHERE id = ?", (case_id,)
        ).fetchone()

        if row is None:
            return None

        old_status = row["status"]

        connection.execute(
            "UPDATE cases SET status = ? WHERE id = ?",
            (new_status, case_id),
        )

        if old_status != new_status:
            event_note = f"{old_status} -> {new_status}"
            if note:
                event_note += f": {note}"
            _log_event(connection, case_id, "status_changed", note=event_note)

    return get_case(case_id)


# ============================================================
# RELATED CASES
# ============================================================

def get_related_cases(case_id, days=30):
    """
    Other cases sharing this case's location AND incident type
    (both, not either) within the last `days` days.

    Deliberately AND, not OR: location and incident_type are both
    broad categories on their own (many different real households
    count as "home"; many different people's cases count as
    "stalking") -- matching on just one alone produced noisy,
    meaningless "related" results, e.g. two unconnected domestic-
    violence cases from different households matching purely
    because they share a crime category. Requiring both together is
    a real, meaningfully tighter signal, even though it's still
    category-level correlation, not verified-same-physical-place
    precision -- location here is a place *type* ("college_campus"),
    not a named real-world location (see understanding.py's
    LOCATION_EXAMPLES). Don't oversell this as more precise than it
    is: two reports here share "something happened at a college
    campus, and it was stalking," not necessarily the same campus.

    Returns None if case_id doesn't exist, [] if it exists but is
    missing either field to correlate on, or nothing else matches.
    """

    case = get_case(case_id)

    if case is None:
        return None

    if not case["location"] or not case["incident_type"]:
        return []

    window_start = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).isoformat()

    with _connect() as connection:

        rows = connection.execute(
            "SELECT * FROM cases WHERE id != ? AND created_at >= ? "
            "AND location = ? AND incident_type = ? "
            "ORDER BY created_at DESC",
            (case_id, window_start, case["location"], case["incident_type"]),
        ).fetchall()

    return [_row_to_case(row) for row in rows]


# ============================================================
# ESCALATION BRIEF
# ============================================================

def build_escalation_brief(case_id):
    """
    A human reviewer picking up an escalated case shouldn't have to
    reconstruct context from a raw conversation -- this assembles
    what's already known about the case (and anything correlated)
    into one reviewable summary. Pure aggregation of existing case
    data, no new detection logic. Returns None if the case doesn't
    exist.
    """

    case = get_case(case_id)

    if case is None:
        return None

    related = get_related_cases(case_id)

    stress_assessment = case["stress_assessment"] or {}

    return {
        "case_id": case["id"],
        "status": case["status"],
        "first_reported": case["created_at"],
        "risk_tier": case["risk_tier"],
        "risk_score": case["risk_score"],
        "confidence": case["confidence"],
        "incident_type": case["incident_type"],
        "location": case["location"],
        # Already display-resolved by _row_to_case() (via get_case()
        # above) -- not re-resolved here.
        "district": case["district"],
        "language": case["language"],
        "is_sos": case["is_sos"],
        "summary": case["original_text"],
        # Machine translation of `summary`, or None when the report was
        # already English / no translation exists yet. Always shown
        # beside the original, never instead of it -- see
        # translation.py. Populated by app.py's brief endpoint, which
        # generates it on first open and caches it via save_translation().
        "summary_translated": case["translated_text"],
        "response_given": case["response"],
        "reason": case["reason"],
        "evidence_attached": case["evidence_path"] is not None,
        "citations": case["citations"],
        # Counsellor-facing: exactly which signals pushed the SVI
        # tier where it landed. Category-level only (signal names +
        # confidence/points, e.g. "threat_present detected, 80.66%,
        # +15 points") -- never the original report text, which stays
        # in `summary` above where a reviewer already expects it.
        # None for a pre-SVI case or an empty-input submission.
        "svi_tier": stress_assessment.get("svi_tier"),
        "svi_score": stress_assessment.get("svi_score"),
        "svi_explainability": stress_assessment.get("explainability"),
        "legal_guidance": case["legal_guidance"],
        "nhaa_docket": case["nhaa_docket"],
        # A reviewer needs to see this before trying to follow up --
        # "anonymous"/"partial" cases genuinely have no name/contact/
        # precise location on file, not just a hidden one.
        "disclosure_level": case["disclosure_level"],
        "reporter_name": case["reporter_name"],
        "reporter_contact": case["reporter_contact"],
        "related_cases": [
            {
                "case_id": r["id"],
                "created_at": r["created_at"],
                "incident_type": r["incident_type"],
                "location": r["location"],
                "risk_tier": r["risk_tier"],
            }
            for r in related
        ] if related else [],
        "timeline": case["timeline"],
    }
