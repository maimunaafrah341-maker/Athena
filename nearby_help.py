# ============================================================
# ATHENA — NEARBY HELP
# ============================================================

"""
Real, live nearby police stations and hospitals -- not from other
users' reports (no privacy concern there), just from OpenStreetMap's
free Overpass API, queried against a location the user chooses to
share for their own benefit.

This is deliberately NOT the "other reports near you" feature we
decided against earlier: nothing here depends on any other person's
data ever having existed in this system.
"""

import math

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# amenity tag -> how we label it
AMENITY_TYPES = {
    "police": "police_station",
    "hospital": "hospital",
}


def _haversine_km(lat1, lon1, lat2, lon2):

    R = 6371.0

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearby_help(latitude, longitude, radius_km=3, limit_per_type=5):
    """
    Real police stations and hospitals within radius_km of the given
    coordinates, sorted by distance. Fails soft -- returns an empty
    list rather than raising, since this is a helpful addition to a
    report, not something that should ever break report submission.
    """

    radius_m = int(radius_km * 1000)

    query = f"""
    [out:json][timeout:10];
    (
      node["amenity"="police"](around:{radius_m},{latitude},{longitude});
      node["amenity"="hospital"](around:{radius_m},{latitude},{longitude});
    );
    out body {limit_per_type * len(AMENITY_TYPES) * 3};
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=12,
            headers={
                "User-Agent": "Athena-Safety-Platform/1.0",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        elements = response.json().get("elements", [])

    except Exception as e:
        print(f"[nearby_help] Overpass query failed: {type(e).__name__}: {e}")
        return []

    results = []

    for element in elements:

        tags = element.get("tags", {})
        amenity = tags.get("amenity")

        if amenity not in AMENITY_TYPES:
            continue

        lat = element.get("lat")
        lon = element.get("lon")

        if lat is None or lon is None:
            continue

        results.append({
            "name": tags.get("name") or AMENITY_TYPES[amenity].replace("_", " ").title(),
            "type": AMENITY_TYPES[amenity],
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "address": tags.get("addr:full") or tags.get("addr:street"),
            "latitude": lat,
            "longitude": lon,
            "distance_km": round(
                _haversine_km(latitude, longitude, lat, lon), 2
            ),
        })

    results.sort(key=lambda r: r["distance_km"])

    # Cap per type so one category doesn't crowd out the other
    capped = []
    counts = {t: 0 for t in AMENITY_TYPES.values()}

    for r in results:

        if counts[r["type"]] < limit_per_type:
            capped.append(r)
            counts[r["type"]] += 1

    return capped


# ============================================================
# CALL OPTIONS
# ============================================================
#
# Real numbers a "Call for help" button can actually dial via a
# tel: link -- confirmed current as of 2026-08-21 (India's unified
# emergency number 112, plus the older direct lines that still work
# nationwide: 100 police, 181 women's helpline, 1098 Childline for a
# child in distress). These are official public emergency numbers,
# not something retrieved from the knowledge base -- hardcoding them
# here is the correct, honest thing to do, the same way nearby real
# police-station numbers come from live OpenStreetMap data rather
# than being invented.

NATIONAL_HELPLINES = [
    {"label": "Emergency (Police / Fire / Ambulance)", "phone": "112", "source": "national"},
    {"label": "Police", "phone": "100", "source": "national"},
    {"label": "Women's Helpline", "phone": "181", "source": "national"},
    {"label": "Childline (child in distress)", "phone": "1098", "source": "national"},
]


def get_call_options(latitude=None, longitude=None):
    """
    What a "Call for help" button should offer, in priority order:
    the nearest real police station (if a location was shared AND
    OpenStreetMap actually has a phone number for it -- often it
    doesn't, that's a real data gap, not something to fake), then
    the national helplines above, which are always available
    regardless of location.

    This only decides WHICH number(s) to offer -- actually placing a
    call is a tel: link the frontend triggers, and should always sit
    behind an explicit confirmation step in the UI so a live demo
    never accidentally dials a real number.
    """

    options = []

    if latitude is not None and longitude is not None:

        nearby = find_nearby_help(latitude, longitude, radius_km=5, limit_per_type=3)

        nearest_station_with_phone = next(
            (place for place in nearby
             if place["type"] == "police_station" and place.get("phone")),
            None,
        )

        if nearest_station_with_phone:
            options.append({
                "label": f"Nearest Police Station — {nearest_station_with_phone['name']}",
                "phone": nearest_station_with_phone["phone"],
                "source": "nearest_station",
                "distance_km": nearest_station_with_phone["distance_km"],
            })

    options.extend(NATIONAL_HELPLINES)

    return options
