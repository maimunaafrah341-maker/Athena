"""
Test fixtures.

The only thing that has to happen before anything else is redirecting
the database. cases.py resolves DB_PATH from CASES_DB_PATH at import
time, so setting it here -- before any test imports app or cases --
keeps the API tests off the real cases.db. Without this, running the
suite files real reports into the database a counsellor is looking at.
"""

import os
import tempfile

_TEST_DB = os.path.join(tempfile.gettempdir(), "athena_test_cases.db")

# Remove any database left by a previous run, so tests start from a
# known-empty table rather than inheriting yesterday's rows.
if os.path.exists(_TEST_DB):
    try:
        os.remove(_TEST_DB)
    except OSError:
        # Windows keeps a handle open if a previous run crashed mid
        # write. Reusing the file is worse than failing loudly here,
        # but not by enough to abort the whole suite over.
        pass

os.environ["CASES_DB_PATH"] = _TEST_DB

# Seeding is skipped: these tests assert on cases they create
# themselves, and ten seeded rows arriving first makes "the case I
# just filed" ambiguous.
os.environ.setdefault("ATHENA_SKIP_SEED", "1")
