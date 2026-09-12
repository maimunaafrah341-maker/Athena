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

   Now a regression test in all five languages.
```

**How to build it:** quote in ~20pt italic. Five language names in their
own scripts. LOW in grey, CRITICAL in red — the colour split *is* the
argument, so let the two columns sit far apart. Last line small, in grey.

### VISUAL 2 — bottom half

The fork is the idea. It covers *the solution* and *what is novel* at once.

```
                  ┌──────────────────┐
             ┌───▶│    RISK TIER     │───┐
             │    │ about to be hurt?│   │
  ┌────────┐ │    └──────────────────┘   │   ┌────────────┐
  │  ONE   │─┤                           ├──▶│  ESCALATE  │
  │ REPORT │ │    ┌──────────────────┐   │   │ on either  │
  └────────┘ │    │  STRESS INDEX    │   │   │ — or on    │
       ╎     └───▶│ how much can they│───┘   │   neither  │
       ╎          │      take?       │       └────────────┘
       ╎          └──────────────────┘             ▲
       └╌╌╌╌╌╌╌╌╌ NOT UNDERSTOOD ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
```

The third route is the point: a report Athena cannot read confidently
reaches a human **without scoring at all**. Draw it as a dashed line
running past both boxes, not as a bullet under them.

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

### Risks and how each is handled — VISUAL

Framed as the five questions a judge will actually ask, because that is
what this slide is for. The question in red, the answer beside it.

**What if it gets it wrong?**

| The question | The answer |
|---|---|
| *"What if it inflates a complaint?"* | SC/ST provisions are not attached below **80% caste-motive confidence** — a floor raised *above our own false positive*, after an unrelated workplace report scored 76.66% |
| *"What if the model invents a fact?"* | **Nothing is cited that was not retrieved** above a similarity threshold; the prompt forbids answering from general knowledge |
| *"What if it misreads the language?"* | **244 automated tests**, each from a defect that actually shipped; the temple-and-crowd report is a regression test in *all five languages* |
| *"What if the map exposes someone?"* | ~100m rounding, and any district with **fewer than three reports is withheld entirely** — with the count shown, so sparse never reads as safe |
| *"What if a record is changed later?"* | The timeline is **append-only**. No edit path, no delete path — a record that can be rewritten is not evidence |

Cut from this slide to keep it to five: provider failover and the
memory-capped host. Both are operational rather than ethical, and this
slide earns more by answering the questions that carry doubt.

### Known limits we state openly

- Romanized detection is uneven — romanized Hindi scores far higher than romanized Telugu. Native script is effectively exact.
- Urdu and Bengali have not yet had a native-speaker review pass.
- Counsellor identity is a single shared key today, so the timeline records what and when, not who.

---

## SLIDE 5 — IMPACT AND BENEFITS

### VISUAL — who gets seen first

Two queues side by side. The left is the order reports arrive in; the
right is the order Athena puts them in. Report 4 is Critical and
arrived fourth.

```
   AS REPORTS ARRIVE              AS ATHENA ORDERS THEM

   Report 1   LOW                 Report 4   CRITICAL
   Report 2   MODERATE     ──▶    Report 5   HIGH
   Report 3   LOW                 Report 2   MODERATE
   Report 4   CRITICAL            Report 1   LOW
   Report 5   HIGH                Report 3   LOW
   Report 6   LOW                 Report 6   LOW

      The person closest to harm is not the person who called first.
```

Deliberately neutral wording — it describes what Athena does, not a
claim about how anyone currently works a queue.

Under it, three columns, then the closing line.

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

Every URL below was checked with a live request. Two links on the
existing slide were dead and two sources are not worth citing to this
ministry -- both noted at the bottom.

### The helpline this is built for

- **National Helpline Against Atrocities (14566)** — PIB, Ministry of Social Justice & Empowerment
  `pib.gov.in/Pressreleaseshare.aspx?PRID=1780741`
- **Ministry of Social Justice & Empowerment** — `socialjustice.gov.in`
- **NCRB, *Crime in India*** — registrations and **pendency** under the SC/ST (PoA) Act
  `ncrb.gov.in/crime-in-india.html`

### Primary legal sources — ingested into the retrieval corpus

- **SC/ST (Prevention of Atrocities) Act, 1989** — India Code
  `indiacode.nic.in/handle/123456789/1920`
- **Bharatiya Nyaya Sanhita, 2023** — Ministry of Home Affairs, official text
  `mha.gov.in/sites/default/files/250883_english_01042024.pdf`
- **Protection of Women from Domestic Violence Act, 2005**
  `indiankanoon.org/doc/542601/`

### Technical

- **Multilingual E5 text embeddings** — Wang et al., `arxiv.org/abs/2402.05672`
- **ChromaDB** — `trychroma.com`
- **OpenAI Whisper**, speech-to-text — `developers.openai.com/api/docs/guides/speech-to-text`
- **Google Gemini API** — `ai.google.dev/gemini-api/docs`
- **OpenStreetMap Overpass API** — `wiki.openstreetmap.org/wiki/Overpass_API`

### The build

- **Source code** — `github.com/maimunaafrah341-maker/Athena`
- **Live prototype** — `athena-production-af83.up.railway.app`
- **Demo video** — `[ new link ]`

### Fix before submitting

| Link | Status |
| --- | --- |
| `ncw.gov.in/telephone-directory/` | **404.** The site root works; this path is gone. Drop it, or link `ncw.gov.in` |
| `iasgyan.in/...` | Live, but it is a UPSC coaching blog. Not a source to put in front of the ministry that runs the helpline — the PIB release covers the same ground with authority |
| `indiacode.nic.in/handle/123456789/1920` | Refuses automated requests (403/404 to a script) but is indexed and opens in a browser. **Click it yourself before submitting.** If it fails, `indiankanoon.org/doc/25085007/` has the full Act |

### Only if you use the due-process point

- *Subhash Kashinath Mahajan v. State of Maharashtra* (2018)
- **SC/ST (PoA) Amendment Act, 2018** — Section 18A
- *Prathvi Raj Chauhan v. Union of India* (2020)

---

## Notes for building the slides

- Rule 2 of the template: **avoid paragraphs.** Everything above is already in points — keep it that way.
- Slide 2 is the one that has to land. Put the quoted report in large type, the two risk scores side by side underneath, and the date you found it.
- The pipeline block on slide 3 works better as a diagram than as text.
- Slide 4's table is the answer to "what if it gets it wrong?" — do not cut it for space.
