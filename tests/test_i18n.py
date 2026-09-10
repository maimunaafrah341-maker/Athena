"""
Translation-table integrity.

Pure text parsing -- no model, no database, no network -- so it runs in
milliseconds and can be the test anyone runs first.

Every bug this catches has actually happened in this project. A key
added to English and forgotten in the other four renders the English
string on a Hindi dashboard, silently, with no error anywhere; that is
exactly how "only the first two pages change language" happened. A key
referenced from markup or JavaScript but never defined renders the key
itself -- the literal text "alerts.viewCase" -- to a counsellor.
"""

import os
import re

import pytest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANGUAGES = ["en", "hi", "te", "ur", "bn"]


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


def _tables():
    """{lang: {key: value}} parsed out of web/i18n.js."""

    source = _read("web", "i18n.js")
    tables = {}

    for language in LANGUAGES:
        match = re.search(
            r"\n    %s: \{(.*?)\n    \}," % language,
            source,
            re.S,
        )

        assert match, "no translation block for %r in web/i18n.js" % language

        tables[language] = dict(
            re.findall(r'"([^"]+)":\s*"((?:[^"\\]|\\.)*)"', match.group(1))
        )

    return tables


def _keys_used():
    """Keys the dashboard actually asks for, from markup and from JS."""

    markup = set()
    for page in ("dashboard.html", "index.html"):
        markup |= set(
            re.findall(r'data-i18n(?:-[a-z-]+)?="([A-Za-z0-9.]+)"', _read("web", page))
        )

    # (?<![A-Za-z0-9_]) so querySelectorAll("div") does not read as t("div")
    script = set(
        re.findall(
            r'(?<![A-Za-z0-9_])t\("([A-Za-z]+\.[A-Za-z0-9]+)"\)',
            _read("web", "athena.js"),
        )
    )

    return markup | script


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_language_has_every_key(language):
    """
    No language may be missing a key another language defines.

    Checked against the union rather than against English, so a key
    added only to Hindi fails too -- the direction of the omission is
    not what makes it a bug.
    """

    tables = _tables()
    every_key = set().union(*(set(table) for table in tables.values()))

    missing = sorted(every_key - set(tables[language]))

    assert not missing, "%s is missing %d keys: %s" % (
        language,
        len(missing),
        missing[:10],
    )


def test_no_key_is_referenced_but_undefined():
    """A key the UI asks for and no table defines renders as itself."""

    english = _tables()["en"]
    undefined = sorted(key for key in _keys_used() if key not in english)

    assert not undefined, "referenced but never defined: %s" % undefined


@pytest.mark.parametrize("language", [lang for lang in LANGUAGES if lang != "en"])
def test_translations_are_not_left_as_english(language):
    """
    Catches keys copied into a language block and never translated.

    Not every match is a bug -- numbers, and proper nouns like "Athena"
    or "WhatsApp", are correctly identical across languages -- so this
    only flags multi-word Latin-script values, which is what an
    untranslated sentence looks like.
    """

    tables = _tables()
    english = tables["en"]

    suspects = []

    for key, value in tables[language].items():

        if english.get(key) != value:
            continue

        if not re.search(r"[A-Za-z]", value):
            continue

        if len(value.split()) < 3:
            continue

        suspects.append(key)

    assert not suspects, "%s appears to be untranslated English: %s" % (
        language,
        suspects,
    )


def test_risk_tiers_match_the_problem_statement():
    """
    SIH26093 names the categories Low / Moderate / High / Critical.

    The tier the UI renders comes from risk.py, so the two have to
    agree -- they did not until 2026-09-08, and the mismatch silently
    undercounted mid-risk cases and mis-coloured map pins.
    """

    english = _tables()["en"]

    for tier in ("low", "moderate", "high", "critical"):
        assert "risk.%s" % tier in english, "missing risk.%s" % tier

    assert "risk.medium" not in english, (
        'risk.medium is back; the problem statement says "Moderate"'
    )


# ------------------------------------------------------------------
# The case brief was built with English literals inline in athena.js
# rather than through t(), so switching the dashboard to Telugu
# translated the risk badge and left every heading around it in
# English. The parity tests above could not catch it, because they
# only check keys that are actually referenced -- a hardcoded string
# references nothing.
# ------------------------------------------------------------------

BRIEF_LABELS = [
    "CASE BRIEF",
    "NHAA DOCKET",
    "RISK LEVEL",
    "RISK SCORE",
    "SVI SCORE",
    "ENGLISH TRANSLATION",
    "AI ASSESSMENT",
    "DRAFT A REPLY",
    "STRESS / TRAUMA SIGNALS",
    "LEGAL GUIDANCE",
    "PROCEDURAL NEXT STEPS",
    "PRIORITY QUEUE",
]


def _case_brief_source():
    source = _read("web", "athena.js")
    start = source.index("function showCaseBrief")
    end = source.index("\nfunction ", start + 10)
    return source[start:end]


@pytest.mark.parametrize("label", BRIEF_LABELS)
def test_case_brief_has_no_hardcoded_english_headings(label):
    assert label not in _case_brief_source(), (
        "%r is hardcoded in the case brief; it will stay English on a "
        "Hindi, Telugu, Urdu or Bengali dashboard" % label
    )


def test_every_case_status_is_translatable():
    """
    The status dropdown stores English values -- that is the database
    contract -- but must display a translation.
    """

    english = _tables()["en"]

    for status in ("New", "Under Review", "Escalated",
                   "In Progress", "Resolved", "Closed"):
        key = "status.%s" % status.replace(" ", "")
        assert key in english, "no translation key for status %r" % status


def test_every_timeline_event_is_translatable():
    english = _tables()["en"]

    for event in ("reported", "status_changed", "escalated",
                  "note_added", "acknowledged"):
        assert "event.%s" % event in english, "no label for event %r" % event


# ------------------------------------------------------------------
# The demo page keeps its own table, and nothing was checking it
# ------------------------------------------------------------------
#
# web/index.html deliberately does not import i18n.js -- it is meant to
# stand alone with no build step -- so every test above walks straight
# past it. Two strings sat hardcoded in English inside a reply rendered
# entirely in Hindi until someone read a screenshot.

DEMO_LANGUAGES = ["en", "hi", "te", "ur", "bn"]


def _demo_tables():
    """{lang: {key: value}} parsed out of UI_STRINGS in web/index.html."""

    page = _read("web", "index.html")

    tables = {}

    for language in DEMO_LANGUAGES:
        match = re.search(
            r"\n    %s: \{(.*?)\n    \}," % language, page, re.DOTALL
        )

        assert match, "UI_STRINGS has no %r block" % language

        tables[language] = dict(
            re.findall(
                r'([A-Za-z][A-Za-z0-9_]*):\s*"((?:[^"\\]|\\.)*)"',
                match.group(1),
            )
        )

    return tables


@pytest.mark.parametrize("language", DEMO_LANGUAGES)
def test_the_demo_table_has_every_key(language):
    """
    A missing key renders as the literal word "undefined" in a chat
    bubble, which is worse than showing English.
    """

    tables = _demo_tables()

    missing = set(tables["en"]) - set(tables[language])

    assert not missing, "%s is missing %s" % (language, sorted(missing))


@pytest.mark.parametrize("language", [l for l in DEMO_LANGUAGES if l != "en"])
def test_the_demo_table_is_actually_translated(language):
    """
    A value copied from the English column is the failure this file
    exists to catch: it looks translated in the source and reads as
    English on the screen.
    """

    tables = _demo_tables()

    english = tables["en"]

    untranslated = sorted(
        key for key, value in tables[language].items()
        if key in english and value == english[key]
    )

    assert not untranslated, (
        "%s left these as English: %s" % (language, untranslated)
    )


@pytest.mark.parametrize("literal", [
    "Not confidently understood",
    "${riskTier} risk",
])
def test_the_risk_tag_is_not_hardcoded_english(literal):
    """
    Both of these were built straight into the message template, so a
    Hindi reply carried an English verdict underneath it. Seen live on
    2026-09-10.
    """

    assert literal not in _read("web", "index.html"), (
        "%r is hardcoded in the demo instead of coming from UI_STRINGS"
        % literal
    )


@pytest.mark.parametrize("page", ["athena.js", "index.html"])
def test_no_label_is_written_in_english_by_javascript(page):
    """
    Markup gets audited because data-i18n is visible in a diff. A
    label assigned in a handler is not, and five of them were sitting
    in athena.js: a Translate button that turned English after its
    first click, "Marking..." and "Mark reviewed" on the alerts
    queue, and "Checking..." / "Continue" on the access gate -- each
    one created a few lines away with t().

    Anything a person reads must come from the tables or from case
    data. A bare string literal here is neither.
    """

    source = _read("web", page)

    literals = re.findall(
        r'(?:textContent|innerText)\s*=\s*"([^"]*)"', source
    )

    english = [value for value in literals if re.search(r"[A-Za-z]", value)]

    assert not english, "%s writes untranslated labels: %s" % (page, english)


def test_no_error_message_is_written_in_english():
    """Same rule, for the messages shown when something has gone wrong."""

    source = _read("web", "athena.js")

    literals = re.findall(r'showError\(\s*[`"]([^`"]*)[`"]', source)

    assert not literals, "untranslated error messages: %s" % literals

