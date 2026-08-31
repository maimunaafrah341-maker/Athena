# Athena — what it does, and what's shipped

_SIH26093 · National Helpline Against Atrocities · updated 31 Aug 2026_

## The problem

The bottleneck isn't the helpline — it's everything before the helpline.
The National Helpline Against Atrocities already has people who can help;
Athena is built for what happens *before* a trained human ever hears about
a case: whether the person in danger can safely reach out at all, and
whether what they say gets understood, prioritised, and acted on fast
enough when they do.

A phone line has three quiet failure points: a caller has to be somewhere
they can speak freely (not useful if the person causing harm is in the
next room), has to describe what's happening out loud in real time in
whichever language the operator happens to know, and whoever picks up has
to correctly judge severity from a few stressed minutes with no record
beyond their own memory of the call.

Athena doesn't replace that human response chain — it sits in front of
it, so a report can be made the moment someone is able to make it (typed,
spoken, or photographed, in their own language), and by the time a
counsellor sees it, it already carries a severity read, the relevant law,
and next steps.

## Why not just call the helpline / police directly

| Calling directly | Reporting through Athena |
|---|---|
| Has to be spoken, out loud, in real time | Typed, voice-noted, or photographed — whenever it's safe to |
| Needs a moment when no one nearby can overhear | Looks like ordinary phone use, not a visible "report abuse" call |
| Depends on whichever operator picks up — their training, language, judgment that day | Same explainable severity scoring, every single time |
| Severity is one person's read of a short, stressed call | Instant triage — no hold time, no queue |
| No record beyond notes the operator happens to take | Every report becomes a timestamped case with a full timeline |

It doesn't compete with the helpline — it makes the handoff to a real
counsellor faster and better-informed than a cold call ever is: they open
a case that already has the severity, the applicable law, and what to do
next.

## Why WhatsApp

The best reporting channel is the one already open on someone's phone. A
new app or unfamiliar website is itself a barrier, and for someone being
watched, a suspicious-looking app on their home screen is a real risk.

1. **It's already installed** — no download, no account, no learning a
   new interface, the single biggest drop-off point for any safety tool.
2. **It hides in plain sight** — a message in an app someone already uses
   all day draws no attention, unlike a dedicated "report" app.
3. **It's the same brain, not a new one** — the WhatsApp-style demo
   (`web/index.html`) already proves this: identical `/report` pipeline,
   same severity scoring, same case record, just reached through a chat
   window instead of a browser. Real WhatsApp integration swaps who's on
   the other end of that call, nothing about how Athena thinks.

## What's shipped

Grouped by what it actually does for a user or a counsellor, not commit
order.

### Reaching more people, in more ways
- **Five languages, text and voice** — English, Hindi, Telugu, Urdu, and
  Bengali, including romanized Hindi/Telugu, not just native script.
- **Real voice transcription** — voice notes are actually transcribed
  (Whisper via Groq's free tier), not matched against a canned script.
- **Photo evidence via OCR** — a screenshot or photo of a threat, injury,
  or document feeds straight into the same pipeline as a typed report.
- **Real nearby help** — live police stations and hospitals near the
  reporter (Overpass API), plus a one-tap SOS that forces Critical /
  escalated.

### Understanding what's actually happening
- **Stress Vulnerability Index (SVI)** — an explainable severity score
  with named, listed factors from both text and voice, not a black-box
  number.
- **SC/ST Act knowledge graph + legal guidance** — case briefs cite the
  actual applicable legal provisions and procedural next steps, grounded
  in real source documents.
- **Suicidal ideation detection** — recognised as its own case with a
  crisis-safe response path, separate from general risk scoring.
- **District-level pattern detection** — a "flagged districts" panel
  surfaces where case counts are rising week over week, with an
  incident-type breakdown.

### Turning a report into a handled case
- **Every report becomes a case** — persisted, queryable, with a full
  chronological timeline from first report through every status change
  and note.
- **Escalation workflow** — manual "Escalate now" with a note, status
  changes, and NHAA docket binding into the real national helpline's case
  categories.
- **Urgency cue** *(new)* — escalated cases now show how long they've sat
  since escalation with no update, so a stalled case is visible instead
  of buried in a timeline.
- **AI-suggested labeling** *(new)* — AI-derived sections of a case brief
  are explicitly marked "suggested, not final" — decision support, not an
  authority making the call.
- **Judge-friendly access** — a case brief can be opened via a link
  carrying its own access, so a reviewer isn't stuck at a raw login
  prompt.

### Getting it in front of people
- **Counsellor dashboard** — real stats, trends, and risk distribution,
  access-key gated, with server-side key verification instead of a
  client-side trust check.
- **WhatsApp-style demo channel** — a chat interface proving the exact
  same backend works inside a familiar messaging UI: text, voice notes,
  and photos.
- **Live deployment** — running on Railway, with a Docker fallback path
  for Hugging Face Spaces / Cloud Run.

### Fixed today
- **Admin-key gate bypass** — the counsellor dashboard's access-key
  screen only checked that *something* had been typed, not that it was
  valid, so any string silently opened an empty dashboard shell. It now
  verifies the key against the server before letting anyone through.
- **Misleading WhatsApp-demo error** — a failed report on the deployed
  demo always blamed "backend not running on localhost:8000," even in
  production. It now distinguishes an unreachable backend from a real
  backend error and reports which one actually happened.
