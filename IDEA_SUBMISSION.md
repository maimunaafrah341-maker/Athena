# SIH 2026 — Idea Submission Content (HEXACORE / SIH26093)

Content for the six slides of `SIH2026-IDEA-Presentation-Format.pdf`.
Six slides maximum including the title. Points, not paragraphs.

`[ ]` marks something only you can fill in from the portal.

---

## SLIDE 1 — TITLE

- **Problem Statement ID** — SIH26093
- **Problem Statement Title** — `[exact portal wording]`
- **Theme** — `[from portal]`
- **PS Category** — Software
- **Team ID** — `[ ]`
- **Team Name** — HEXACORE

---

## SLIDE 2 — IDEA TITLE + PROPOSED SOLUTION

### Idea title

**Athena — the first ninety seconds of 14566**

Two visuals and about forty words. Nothing else fits, and nothing else
is needed — feasibility belongs on slide 4, architecture on slide 3.

### VISUAL 1 — top half of the slide

The quoted report in large type, then the five results. This single
graphic covers *how it addresses the problem*.

```
  "Because of my caste I was not allowed into the temple
   and I was humiliated. A crowd is standing outside my house."

   ────────  THE SAME REPORT, IN FIVE LANGUAGES  ────────

        English   ● LOW              తెలుగు   ● CRITICAL
        हिंदी      ● LOW              বাংলা    ● CRITICAL
                                      اردو     ● CRITICAL

   The two languages a caller is most likely to use
   gave the safest-sounding answer.

   Found 8 Sep 2026 · fixed the same day · now a test in all five
```

**How to build it:** quote in ~20pt italic. Five language names in their
own scripts. LOW in grey, CRITICAL in red — the colour split *is* the
argument, so let the two columns sit far apart. Last line small, in grey.

### VISUAL 2 — bottom half

The fork is the idea. It covers *the solution* and *what is novel* at once.

```
                    ONE REPORT
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
         RISK TIER               SVI
    is someone about      how much can this
      to be hurt?        person withstand?
              │                   │
              └─────────┬─────────┘
                        ▼
          ESCALATE ON EITHER — OR ON
            NOT UNDERSTANDING AT ALL
```

**Caption, one line under it:**

> Most systems escalate when they are sure. Athena also escalates when it isn't.

### The only text on the slide

- Two scores, because *"is someone about to be hurt"* and *"how much can this person take"* are not the same question — and SIH26093 names both.
- Every legal citation is **retrieved** from the ingested bare Act, never generated.
- Five languages in native script, four also romanized.

### Moved off this slide (already covered elsewhere — do not repeat)

| Was on slide 2 | Now lives on |
| --- | --- |
| 244 automated tests | Slide 4 — it is a feasibility claim |
| The 80% caste-motive gate | Slide 4 — risk table |
| Safety map k-anonymity | Slide 4 — risk table |
| NHAA docket, five entry points | Slides 3 and 5 |
| UNDERSTAND → VERIFY → ACT → ESCALATE | Slide 3 — it is the pipeline diagram |

---

## SLIDE 3 — TECHNICAL APPROACH

### Stack

| Layer | Technology |
|---|---|
| API | Python · FastAPI · uvicorn |
| Understanding | `multilingual-e5-small` sentence embeddings — semantic similarity, not keywords |
| Retrieval | ChromaDB over ingested government source documents |
| Legal mapping | Knowledge graph: detected signals → statutory provisions |
| Response | LLM with three-provider failover (Groq → Gemini → OpenRouter), evidence-grounded prompt |
| Multimodal | Whisper transcription · librosa acoustic features · EasyOCR |
| Storage | SQLite, append-only case timeline |
| Deployment | Docker · Railway · Twilio WhatsApp |

### Pipeline (use as the flow diagram)

```
INTAKE            text · voice · photo · SOS
                  portal · WhatsApp · 14566 · IVRS · mobile
        ↓
UNDERSTANDING     signals · language · script detection
        ↓
RISK  ⊕  SVI      danger tier  ⊕  stress tier (text + voice fused)
        ↓
RETRIEVAL + KG    confidence-gated RAG → statutory provisions
        ↓
RESPONSE          grounded reply, in the reporter's language and script
        ↓
CASE + DOCKET     append-only timeline · NHAA docket ID
        ↓
COUNSELLOR        queue ordered by who is closest to harm
```

### Method

- Signals detected by similarity against curated real-world examples, with **hard negatives** and a neutral margin — so "I want to kill him" does not read as suicidal ideation.
- **Nothing is cited below the retrieval confidence threshold.**
- **Three independent escalation triggers** — Critical risk, Critical stress, or low understanding confidence.
- Working prototype is deployed and reachable now.

---

## SLIDE 4 — FEASIBILITY AND VIABILITY

### Feasible because it is already running

- Live deployment; WhatsApp intake working end to end through Twilio.
- **244 automated tests**, every one encoding a defect that actually shipped.
- Escalation directory covering **554 districts across 33 states and UTs**, provenance-tagged as manually verified or machine-parsed.

### Risks and how each is handled

| Risk | Mitigation |
|---|---|
| An AI **over-charging** a complaint | SC/ST provisions gated at ≥80% caste-motive confidence — set at 80 rather than 60 because live testing found *"Someone keeps insulting and threatening me at work"*, with no caste element at all, firing at **76.66%**. Nothing is cited that was not retrieved. Athena produces triage support, never a finding, and does not register an FIR |
| Model asserting something unsupported | Evidence-grounded prompt; citations built only from retrieved documents |
| Wrong language → wrong assessment | Tested in five languages; the temple/crowd report is a test case in all five |
| Re-identifying a reporter from the map | Coordinates rounded to ~100m **and** districts with fewer than three reports withheld entirely |
| Memory-capped free-tier host | Voice acoustic features behind a flag; the transcript-only path still assesses, escalates and replies |
| Model provider outage | Three-provider failover |
| Counsellor accountability | Append-only case timeline with no edit or delete path |

### Known limits we state openly

- Romanized detection is uneven — romanized Hindi scores far higher than romanized Telugu. Native script is effectively exact.
- Urdu and Bengali have not yet had a native-speaker review pass.
- Counsellor identity is a single shared key today, so the timeline records what and when, not who.

---

## SLIDE 5 — IMPACT AND BENEFITS

### For the person calling

- Answered **in their own language and script**, in seconds.
- Told plainly **what happens next** — a reference ID, the provisions their report may fall under, real numbers.
- **14566 offered first, at every tier**; 112 when they are in danger; KIRAN whenever stress is high, whether or not the word "suicide" appears.
- Can report **anonymously**, and can say *do not contact me* — recorded and honoured.

### For the counsellor

- A queue ordered by **who is closest to harm**, not who called first.
- A brief that shows **the basis, not just a verdict** — which phrases triggered which signal, at what confidence.
- "Nobody has looked at this" is tracked separately from "in progress", so a Critical case cannot sit unseen.

### For NHAA

- Every case **docketed**, channel-agnostic across all five entry points.
- District-level pattern detection for week-over-week spikes.

### Why it matters

- **Pendency, not volume, is the constraint.** Triage is what lets scarce human attention reach the right case *today*.
- **Reaches people who cannot read English** — the interface is localized, not just the complaint field.
- **Evidentiary integrity** — an append-only record, because a timeline that can be rewritten is not evidence.

---

## SLIDE 6 — RESEARCH AND REFERENCES

### Primary legal sources (ingested into the retrieval corpus)

- **SC/ST (Prevention of Atrocities) Act, 1989**, with the 2015 and 2018 amendments — bare act
- **Bharatiya Nyaya Sanhita, 2023** — the code in force; replaced the IPC
- **Protection of Women from Domestic Violence Act, 2005**
- **Mission Shakti** guidelines

### Data and institutional sources

- **NCRB, *Crime in India*** — registrations, chargesheeting, and **pendency** under the SC/ST (PoA) Act  `[verify figures from the NCRB report or the PIB release, not a secondary article]`
- **Ministry of Social Justice and Empowerment** — NHAA / 14566, `nhapoa.gov.in`

### Case law consulted on due process

- *Subhash Kashinath Mahajan v. State of Maharashtra* (2018)
- **SC/ST (PoA) Amendment Act, 2018** — Section 18A
- *Prathvi Raj Chauhan v. Union of India* (2020)

### The build

- Repository — `github.com/maimunaafrah341-maker/Athena`
- Live prototype — `athena-production-af83.up.railway.app`
- Demo video — `[new link]`

---

## Notes for building the slides

- Rule 2 of the template: **avoid paragraphs.** Everything above is already in points — keep it that way.
- Slide 2 is the one that has to land. Put the quoted report in large type, the two risk scores side by side underneath, and the date you found it.
- The pipeline block on slide 3 works better as a diagram than as text.
- Slide 4's table is the answer to "what if it gets it wrong?" — do not cut it for space.
