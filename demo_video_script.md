# Athena — Demo Video Script (~2:30)

Practical note: don't submit a fresh live report for this recording unless
you have Gemini quota to spare — use the already-seeded Karimnagar
caste-atrocity case (or any seeded case) already sitting in the dashboard.
It shows the full pipeline output with zero API risk of a live failure
on camera.

---

**0:00–0:15 — Hook**

"Every year, thousands of Scheduled Caste and Scheduled Tribe victims
call India's National Helpline Against Atrocities — 14566 — or use its
portal, IVRS, chatbot, or app. But right now, there's no way to tell,
at first contact, whether the person on the other end is calm or in
crisis. Everyone gets treated the same."

**0:15–0:40 — What Athena does**

"Athena is a real-time Stress and Trauma Assessment layer that plugs
into NHAA's existing workflow. It reads a report — voice or text, in
English, Hindi, or Telugu — and scores a Stress Vulnerability Index in
real time, grounded in actual law, not guesses."

**0:40–1:20 — Live walkthrough (screen: dashboard.html)**

- Open the report form. Point at the channel selector: "14566 Call,
  IVRS, Portal, Chatbot, Mobile App — same pipeline behind all five,
  because that's how NHAA actually works."
- Open the seeded Karimnagar case (caste-based harassment report).
  Walk through what's on screen:
  - SVI score + Critical tier, with the explainability breakdown
    (which signals pushed it there)
  - The NHAA docket: `NHAA-2026-XXXXXXXX`, channel, status "escalated"
  - Legal grounding panel: point at the SC/ST (Prevention of
    Atrocities) Act, 1989, Section 3(1)(x) citation — "this isn't
    generic advice, it's pulled from the actual Act text we ingested,
    with the exact section that applies."

**1:20–1:50 — Counsellor dashboard**

- Switch to the case list / flagged-districts panel.
- Point at Hyderabad flagged as a rising district: "the system also
  spots patterns across cases — a district seeing a spike in a
  particular incident type gets surfaced to a human reviewer
  automatically."

**1:50–2:15 — Why this matters**

"This is the piece the problem statement is actually asking for:
triage the psychological state of a victim the moment they make
contact, so the most distressed people get counselling, legal aid, or
police intervention prioritized — not stuck in the same queue as
everyone else."

**2:15–2:30 — Close**

"Athena is live at [RAILWAY LINK]. Full source and architecture are on
GitHub. Thank you."

---

## Recording tips
- Do ONE take of any live Gemini submission, if you include one at all —
  don't retry it on camera.
- Mute notifications, close other tabs before hitting record.
- If OBS/screen recorder isn't installed, Windows has a built-in one:
  Win+Alt+R starts/stops a recording of the focused window.
