# ============================================================
# ATHENA — LEGAL & ESCALATION KNOWLEDGE GRAPH
# ============================================================

"""
Lightweight knowledge graph connecting a structured incident to:
    - the applicable legal provision(s) (BNS / PWDVA / SC-ST Act)
    - the correct procedural next step(s)
    - the right escalation contact for the reporter's district

Why networkx over a full graph database (Neo4j etc.): the actual
query shape here isn't a single-key lookup, it's a real multi-hop
join. A case's applicable provisions depend on TWO independent
signals converging -- incident_type, and whether caste_based_motive
fired -- and they can both add provisions at once (e.g. a caste-
motivated sexual_violence report pulls in BNS *and* SC/ST Act
3(1)(xi)/(xii) together, not one or the other). escalation_contact
is a completely separate axis again -- a district-level lookup, not
incident-level. A pair of flat dicts (incident_type -> law,
district -> contact) covers the simple case but can't express
"two signals both add provisions to the same result" without
duplicating that logic outside the data structure. A full graph
database would buy a query language, persistence, and concurrent
writes -- none of which this needs: the graph is small (a few dozen
nodes), read-only at request time, and rebuilt from the source data
below on import. That's exactly the shape networkx is for --
in-memory, in-process, zero deployment overhead, still expressive
enough for the real traversal this needs.

Data provenance: legal provisions below are transcribed directly
from the actual bare-act text now ingested into the RAG knowledge
base (data/sources/SCSTpoaact1989.pdf) -- not invented or recalled
from general knowledge. Cross-check section wording against that PDF
before trusting a citation, same discipline as everywhere else in
this project. Escalation contacts come from district_contacts.py
(see that file's docstring for its own provenance/coverage caveats).
Every item returned here carries "source": "kg_seed" -- this is a
maintained lookup table, not a live RAG retrieval, and the contract
(API_CONTRACT.md) deliberately distinguishes that from
"rag_verified" so nothing here is presented with false authority.

Scope note (2026-08-22): this only cites the SC/ST Act, matching the
project's actual target (a 14566-scoped SC/ST helpline) -- this is
the right primary framing, not a placeholder. The *mechanism* is
already general-purpose, not caste-hardcoded: caste_based_motive is
just one instance of understanding.py's generic detect_signal()
pattern (the same function backs threat_present/injury_present too),
and this module's incident_type -> provision -> step graph shape is
equally reusable. Extending to another protected characteristic
later is three additions, not a redesign: (1) a new SIGNAL_EXAMPLES
anchor set in understanding.py, (2) a confidence floor calibrated
against real multilingual test data the same way
CASTE_MOTIVE_CONFIDENCE_FLOOR was, (3) new provision/step nodes here
-- IF a verified source-law text exists for that characteristic.
Concretely: BNS 2023 Section 196 ("promoting enmity between
different groups on grounds of religion, race, place of birth,
residence, language, caste or community or any other ground
whatsoever," verified against the actual ingested BNS2023.pdf text,
pages 161-162) would let a future pass add a genuinely
identity-agnostic citation on top of the SC/ST-specific one, and BNS
298-302 (Chapter XVI, "Offences Relating to Religion," also verified
against real text) would do the same for religion specifically.
Deliberately not wired in now -- explicitly out of scope for this
pass, not a technical blocker.
"""

import networkx as nx

from district_contacts import DISTRICT_CONTACTS


# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

graph = nx.DiGraph()

SCST_ACT = "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989"
BNS = "Bharatiya Nyaya Sanhita, 2023"
PWDVA = "Protection of Women from Domestic Violence Act, 2005"


def _add_provision(node_id, act, section, description):
    graph.add_node(
        node_id,
        kind="legal_provision",
        act=act,
        section=section,
        description=description,
        source="kg_seed",
    )


def _add_step(node_id, order, action):
    graph.add_node(node_id, kind="procedural_step", order=order, action=action)


# --------------------------------------------------------
# Legal provisions -- SC/ST Act sections transcribed from the
# actual ingested bare-act text (data/sources/SCSTpoaact1989.pdf)
# --------------------------------------------------------

_add_provision(
    "scst_3_1_x", SCST_ACT, "Section 3(1)(x)",
    "Intentionally insults or intimidates with intent to humiliate a "
    "member of a Scheduled Caste or Scheduled Tribe in any place "
    "within public view.",
)
_add_provision(
    "scst_3_1_xi", SCST_ACT, "Section 3(1)(xi)",
    "Assaults or uses force against a woman belonging to a Scheduled "
    "Caste or Scheduled Tribe with intent to dishonour or outrage "
    "her modesty.",
)
_add_provision(
    "scst_3_1_xii", SCST_ACT, "Section 3(1)(xii)",
    "Being in a position to dominate the will of a woman belonging "
    "to a Scheduled Caste or Scheduled Tribe and using that position "
    "to sexually exploit her.",
)
_add_provision(
    "scst_3_1_xv", SCST_ACT, "Section 3(1)(xv)",
    "Forces or causes a member of a Scheduled Caste or Scheduled "
    "Tribe to leave their house, village, or other place of "
    "residence.",
)
_add_provision(
    "scst_3_1_ii", SCST_ACT, "Section 3(1)(ii)",
    "Acts with intent to cause injury, insult, or annoyance to a "
    "member of a Scheduled Caste or Scheduled Tribe by dumping "
    "excreta, waste matter, or any obnoxious substance in their "
    "premises or neighbourhood.",
)
_add_provision(
    "scst_3_1_vi", SCST_ACT, "Section 3(1)(vi)",
    "Compels or entices a member of a Scheduled Caste or Scheduled "
    "Tribe into forced or bonded labour ('begar').",
)

_add_provision(
    "pwdva_general", PWDVA, "Protection orders (Chapter IV)",
    "Provides for protection orders, residence orders, and other "
    "relief for victims of domestic violence. This is a routing "
    "hint, not the full legal detail -- the grounded RAG response "
    "already draws on the fuller ingested PWDVA text for that.",
)

_add_provision(
    "bns_general", BNS, "General cognizable offence",
    "Physical assault, criminal intimidation, or similar offences "
    "reported here are cognizable under the Bharatiya Nyaya Sanhita, "
    "2023 -- police are required to register an FIR without prior "
    "magistrate approval.",
)


# --------------------------------------------------------
# Procedural steps
# --------------------------------------------------------

_add_step(
    "step_fir", 1,
    "File a complaint (FIR) at the nearest police station. This is "
    "a cognizable offence -- police are required to register it.",
)
_add_step(
    "step_scst_special_court", 2,
    "SC/ST Act cases are tried in a Special Court designated for "
    "the district under Section 14, for a speedier trial than a "
    "regular court.",
)
_add_step(
    "step_scst_prosecutor", 3,
    "A Special Public Prosecutor is appointed for SC/ST Act cases "
    "under Section 15.",
)
_add_step(
    "step_scst_legal_aid", 4,
    "You are entitled to legal aid and travel/maintenance expense "
    "support during investigation and trial under Section 21 of the "
    "SC/ST Act.",
)
_add_step(
    "step_pwdva_protection_officer", 2,
    "Approach a Protection Officer or the nearest police station -- "
    "you may seek a Protection Order under the Domestic Violence "
    "Act.",
)


# --------------------------------------------------------
# Edges: legal provision -> procedural step
# --------------------------------------------------------

SCST_STEPS = (
    "step_fir",
    "step_scst_special_court",
    "step_scst_prosecutor",
    "step_scst_legal_aid",
)

for provision_id in (
    "scst_3_1_x", "scst_3_1_xi", "scst_3_1_xii",
    "scst_3_1_xv", "scst_3_1_ii", "scst_3_1_vi",
):
    for step_id in SCST_STEPS:
        graph.add_edge(provision_id, step_id)

graph.add_edge("pwdva_general", "step_fir")
graph.add_edge("pwdva_general", "step_pwdva_protection_officer")

graph.add_edge("bns_general", "step_fir")


# --------------------------------------------------------
# Edges: incident_type -> legal provision (general path, applies
# regardless of caste_based_motive)
# --------------------------------------------------------

INCIDENT_TYPE_TO_PROVISION = {
    "domestic_violence": "pwdva_general",
    "sexual_violence": "bns_general",
    "harassment": "bns_general",
    "stalking": "bns_general",
    "trafficking": "bns_general",
    "cyber_harassment": "bns_general",
    # missing_person and other: no general provision mapped -- see
    # get_legal_guidance's docstring on why this stays unmapped
    # rather than forcing a weak guess.
}

for incident_type in (
    "domestic_violence", "sexual_violence", "harassment", "stalking",
    "trafficking", "cyber_harassment", "missing_person", "other",
):
    graph.add_node(incident_type, kind="incident_type")

for incident_type, provision_id in INCIDENT_TYPE_TO_PROVISION.items():
    graph.add_edge(incident_type, provision_id)


# --------------------------------------------------------
# Edges: caste-motivated incident_type -> SC/ST Act provision(s)
#
# Which SC/ST Act clause applies depends on the KIND of act
# (violence_types / incident_type), not just "caste_based_motive"
# alone -- a caste-motivated sexual_violence report maps to
# 3(1)(xi)/(xii), while a caste-motivated harassment report maps to
# 3(1)(x). This is the two-signals-converging case described in the
# module docstring.
# --------------------------------------------------------

CASTE_MOTIVE_PROVISIONS = {
    "sexual_violence": ["scst_3_1_xi", "scst_3_1_xii"],
    "harassment": ["scst_3_1_x"],
    "stalking": ["scst_3_1_x"],
    "domestic_violence": ["scst_3_1_xv"],
    "trafficking": ["scst_3_1_vi"],
    "cyber_harassment": ["scst_3_1_x"],
    # missing_person, other: not mapped -- see docstring below.
}

for incident_type, provision_ids in CASTE_MOTIVE_PROVISIONS.items():
    caste_node = f"{incident_type}__caste_motivated"
    graph.add_node(caste_node, kind="incident_type_caste_motivated")
    for provision_id in provision_ids:
        graph.add_edge(caste_node, provision_id)


# Confidence floor before caste_based_motive is trusted enough to
# add SC/ST Act provisions -- same discipline as
# INCIDENT_TYPE_CONFIDENCE_FLOOR in risk.py/svi.py, but set higher
# (80, not 60) and deliberately conservative. Live multilingual
# testing 2026-08-22 found "Someone keeps insulting and threatening
# me at work" (no caste mention at all) fires caste_based_motive=True
# at 76.66% -- a real false positive sitting inside the 0.07-0.17
# margin range this codebase's own NEUTRAL_MARGIN calibration treats
# as "genuine incident," not noise. That's the same short-phrase-
# embedding limitation already documented elsewhere in this project
# (see athena_known_issues.md's cross-signal noise entries) -- caste-
# based insult is a semantic subset of generic insult, so no amount
# of additional positive-only anchor examples can perfectly separate
# them with this detection approach. 80 was chosen because all 7
# genuine positives tested came back at 100% confidence, comfortably
# clear of both the old and new floor, while the one confirmed false
# positive (76.66%) now falls below it. This signal carries higher
# stakes than the others (misclassifying a protected-characteristic
# motive in either direction is a real harm), so it's always advisory
# even when it clears this bar -- see get_legal_guidance's docstring.
CASTE_MOTIVE_CONFIDENCE_FLOOR = 80


# ============================================================
# ESCALATION CONTACT LOOKUP
# ============================================================

def _resolve_escalation_contact(district):

    if not district:
        return None

    contact = DISTRICT_CONTACTS.get(district.strip().lower())

    if not contact:
        return None

    return {**contact, "source": "kg_seed"}


# ============================================================
# PUBLIC API
# ============================================================

def get_legal_guidance(incident, district=None):
    """
    Look up applicable legal provisions, procedural next steps, and
    an escalation contact for a structured incident (the output of
    understanding.understand()).

    Returns the legal_guidance shape locked in API_CONTRACT.md, or
    None when nothing in the graph applies (e.g. incident_type
    "other", or "missing_person" -- not mapped, see below).

    IMPORTANT: SC/ST Act provisions are only added when
    incident["caste_based_motive"] is True AND its confidence
    (incident["confidence_breakdown"]["caste_based_motive"]) clears
    CASTE_MOTIVE_CONFIDENCE_FLOOR -- and even then this is advisory
    routing information for a human reviewer, not a legal
    determination. Whether a reporter is legally a member of a
    Scheduled Caste/Tribe, and whether the specific facts meet a
    section's elements, is a legal judgment this system cannot and
    should not make on its own.

    missing_person is deliberately not mapped to any provision here.
    A caste-motivated abduction could plausibly engage the SC/ST Act
    (e.g. via Section 3(2)(v), serious IPC/BNS offences against an
    SC/ST person), but that mapping needs a clearer basis than what's
    been transcribed so far -- left out rather than guessed at.
    """

    incident_type = incident.get("incident_type")

    if incident_type not in graph:
        return None

    provision_ids = list(graph.successors(incident_type))

    caste_confidence = (
        incident.get("confidence_breakdown") or {}
    ).get("caste_based_motive", 0.0)

    if (
        incident.get("caste_based_motive")
        and caste_confidence >= CASTE_MOTIVE_CONFIDENCE_FLOOR
    ):
        caste_node = f"{incident_type}__caste_motivated"

        if caste_node in graph:
            provision_ids += list(graph.successors(caste_node))

    if not provision_ids:
        return None

    applicable_provisions = []
    steps_seen = {}

    for provision_id in provision_ids:

        node = graph.nodes[provision_id]

        applicable_provisions.append({
            "act": node["act"],
            "section": node["section"],
            "description": node["description"],
            "source": node["source"],
        })

        for step_id in graph.successors(provision_id):
            steps_seen[step_id] = graph.nodes[step_id]

    # Renumber sequentially after sorting by each step's internal
    # "order" hint -- multiple provisions can point to steps that
    # happen to share the same hint (e.g. two different order=2
    # steps from two different provision paths), so the hint is only
    # used for relative ordering, not reused as the displayed number.
    procedural_next_steps = [
        {"step": index, "action": step["action"]}
        for index, step in enumerate(
            sorted(steps_seen.values(), key=lambda s: s["order"]),
            start=1,
        )
    ]

    return {
        "applicable_provisions": applicable_provisions,
        "procedural_next_steps": procedural_next_steps,
        "escalation_contact": _resolve_escalation_contact(district),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("PLAIN DOMESTIC VIOLENCE (no caste motive)")
    print("=" * 70)
    incident = {
        "incident_type": "domestic_violence",
        "caste_based_motive": False,
        "confidence_breakdown": {"caste_based_motive": 10.0},
    }
    result = get_legal_guidance(incident, district="Hyderabad")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("CASTE-MOTIVATED HARASSMENT, HIGH CONFIDENCE, DISTRICT=Karimnagar")
    print("=" * 70)
    incident = {
        "incident_type": "harassment",
        "caste_based_motive": True,
        "confidence_breakdown": {"caste_based_motive": 91.4},
    }
    result = get_legal_guidance(incident, district="Karimnagar")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("CASTE-MOTIVATED SIGNAL BUT LOW CONFIDENCE -- SC/ST Act should NOT appear")
    print("=" * 70)
    incident = {
        "incident_type": "harassment",
        "caste_based_motive": True,
        "confidence_breakdown": {"caste_based_motive": 22.0},
    }
    result = get_legal_guidance(incident, district=None)
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("UNKNOWN DISTRICT -- escalation_contact should be None, not an error")
    print("=" * 70)
    incident = {
        "incident_type": "stalking",
        "caste_based_motive": False,
        "confidence_breakdown": {"caste_based_motive": 5.0},
    }
    result = get_legal_guidance(incident, district="Some Made Up Place")
    for key, value in result.items():
        print(f"{key}: {value}")
