# ============================================================
# ATHENA — DISTRICT GEOCODING
# ============================================================

"""
District-name -> approximate (lat, lon), used as a map-pin fallback
for reports where the reporter didn't share GPS (denied, unavailable,
or a non-web channel like 14566/IVRS that has no location API at all)
but did give a district. Judge feedback 2026-08-29: the safety map
showed nothing for these cases even when a location was explicitly
given -- list_case_locations() in cases.py only ever returns cases
that already have latitude/longitude set, and nothing upstream of it
ever derived those from a district. This module closes that gap.

Two tiers, in order:

1. _DISTRICT_CENTROIDS -- a small hardcoded table, real coordinates
   for the district headquarters actually used by seed_data.py's demo
   cases. Instant, zero network dependency -- the live demo must never
   depend on a third-party API being reachable in front of judges,
   same reasoning as emergency_contacts.py's deterministic contact
   list. This is what makes the seeded demo map populated by default.

2. OSM Nominatim (nominatim.openstreetmap.org), for any district not
   in the table above -- real, general-purpose coverage for the
   other ~600+ Indian districts DISTRICT_CONTACTS already knows about.
   Free, no API key, but their usage policy caps this at ~1 request/
   second and requires a descriptive User-Agent identifying the app
   (not a personal contact -- see _NOMINATIM_HEADERS). Results are
   cached in-memory for the life of the process, so a repeated
   district (very likely -- most real traffic will cluster in a
   handful of districts, same as the demo data) never re-hits the
   network after the first lookup.

Returns (lat, lon) rounded to 3 decimals -- matches app.py's
LOCATION_ROUNDING_DECIMALS for GPS coordinates, ~100m precision, and
is honest about this being a district-level approximation to begin
with, not a claim of finer precision. Returns (None, None) if nothing
resolves (an unrecognised district name, or Nominatim unreachable) --
that just means no map pin, same as no district being given at all,
never an error a report submission should fail on.
"""

import requests

_DISTRICT_CENTROIDS = {
    "hyderabad": (17.385, 78.487),
    "karimnagar": (18.439, 79.129),
    "nalgonda": (17.058, 79.269),
    "hanumakonda": (18.002, 79.594),
    "warangal": (17.969, 79.594),
    "khammam": (17.247, 80.151),
    "adilabad": (19.664, 78.532),
    "nizamabad": (18.673, 78.094),
}

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Nominatim's usage policy requires a descriptive User-Agent so they
# can identify/contact a client in case of abuse -- a project name and
# repo-shaped identifier is what they ask for, not a personal email
# (this file is committed to a public repo; a personal address baked
# in here would be scraped and spammed).
_NOMINATIM_HEADERS = {
    "User-Agent": "AthenaHEXACORE-SIH26093-HackathonDemo/1.0",
}

_ROUNDING_DECIMALS = 3

# Process-lifetime cache: {normalized_district_name: (lat, lon) or (None, None)}.
# Populated lazily by Nominatim lookups only -- _DISTRICT_CENTROIDS entries
# are already instant and don't need caching.
_geocode_cache = {}


def geocode_district(district_name, timeout=5):
    """
    Resolve a district name to an approximate (lat, lon).

    Returns (None, None) if district_name is empty, or if it can't be
    resolved by either the static table or Nominatim (including any
    network failure -- this never raises, a geocoding failure should
    never block a report submission).
    """

    if not district_name:
        return None, None

    key = district_name.strip().lower()

    if not key:
        return None, None

    if key in _DISTRICT_CENTROIDS:
        return _DISTRICT_CENTROIDS[key]

    if key in _geocode_cache:
        return _geocode_cache[key]

    try:
        response = requests.get(
            _NOMINATIM_URL,
            params={
                "q": f"{district_name}, India",
                "format": "json",
                "limit": 1,
            },
            headers=_NOMINATIM_HEADERS,
            timeout=timeout,
        )

        results = response.json()

        if results:
            lat = round(float(results[0]["lat"]), _ROUNDING_DECIMALS)
            lon = round(float(results[0]["lon"]), _ROUNDING_DECIMALS)
            _geocode_cache[key] = (lat, lon)
            return lat, lon

    except Exception:
        # Network failure, timeout, malformed response -- treated the
        # same as "not found." Not cached, so a transient failure
        # (e.g. Nominatim briefly rate-limiting) gets retried on the
        # next report for this district rather than being remembered
        # as a permanent miss.
        pass

    return None, None


if __name__ == "__main__":

    test_districts = ["Karimnagar", "Hyderabad", "Kadapa", "Some Made Up Place", None, ""]

    for name in test_districts:
        lat, lon = geocode_district(name)
        print(f"{name!r:30} -> ({lat}, {lon})")
