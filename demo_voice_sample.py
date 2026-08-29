"""
Presentation-day demo helper for the voice feature.

Voice capture -> Whisper transcription -> Athena pipeline is fully wired
(see voice_service.py / app.py's /report/voice) and, as of 2026-08-29,
actually works live -- voice_service.py now transcribes via Groq's
hosted Whisper (free tier) instead of OpenAI's (which needed a funded
account that never happened). This script predates that fix and was
built as a workaround for the OpenAI billing gap; kept as a zero-
network-dependency backup in case Groq is unreachable/rate-limited live
during judging, not because live transcription is still broken.

  --sample (default)
      Replays a pre-recorded incident: play the audio for the audience,
      then run its known, verified transcript through the real pipeline.
      Shows the actual downstream engine (language understanding, risk
      tier, legal citations, SVI, escalation) end to end, with zero
      dependency on any transcription provider being reachable.

  --live
      Hands the keyboard to a judge. They type what they'd say -- Hindi,
      Telugu, Urdu, Bengali, or English, native or romanized script --
      and it runs through the exact same pipeline a spoken report would
      hit after transcription. Everything downstream of speech-to-text
      is real and live; only the mic-to-text hop is stood in for by
      typing.

Update SAMPLE_TRANSCRIPT / SAMPLE_AUDIO_FILE / SAMPLE_DISTRICT below
once Samreen's recording is final -- they're currently pre-filled with
a scenario already verified earlier tonight (correct SC/ST Act citations,
Critical tier, Karimnagar escalation contact).
"""

import os
import sys
import argparse

sys.path.insert(0, r"c:\Users\Maimuna Afrah\Athena")
sys.stdout.reconfigure(encoding="utf-8")

from pipeline import run_pipeline

SAMPLE_AUDIO_FILE = "samreen_demo_sample.wav"
SAMPLE_TRANSCRIPT = (
    "Meri jaati ke karan mujhe mandir mein ghusne nahi diya gaya aur "
    "sabke saamne apmaanit kiya gaya. Bheed abhi mujhe ghar ke bahar "
    "ghera kiye khadi hai."
)
SAMPLE_DISTRICT = "Karimnagar"


def show_result(text, district=None):
    try:
        result = run_pipeline(text, district=district)
    except Exception as e:
        print(f"[Pipeline error on this input: {e}]")
        print("(Try rephrasing it, or switch back to the prepared sample.)\n")
        return

    print("=" * 70)
    print("TRANSCRIPT:", text)
    print("-" * 70)
    inc = result["incident"]
    print("language:", inc["language"], "script:", inc["script"])
    print("incident_type:", inc["incident_type"], "relationship:", inc["relationship"])
    print("immediate_danger:", inc["immediate_danger"])
    print()
    print("risk_tier:", result["risk"]["risk_tier"], "| escalate:", result["escalate"])
    if result["stress_assessment"]:
        print("svi_tier:", result["stress_assessment"]["svi_tier"])
    print()
    if result["legal_guidance"]:
        print("legal_guidance:")
        for p in result["legal_guidance"]["applicable_provisions"]:
            print(" -", p["act"], "|", p["section"])
        ec = result["legal_guidance"]["escalation_contact"]
        if ec:
            print("escalation_contact:", ec["district"], "|", ec["phone"])
    else:
        print("legal_guidance: none matched (low confidence / insufficient evidence)")
    print()
    print("RESPONSE:")
    print(result["response"])
    print("=" * 70)
    print()


def run_sample():
    print("[Recorded-sample mode]\n")
    if os.path.exists(SAMPLE_AUDIO_FILE):
        print(f"Now play: {SAMPLE_AUDIO_FILE}")
    else:
        print(f"(Note: '{SAMPLE_AUDIO_FILE}' not found in this folder --")
        print(" update SAMPLE_AUDIO_FILE at the top of this script once")
        print(" Samreen's recording is saved, or just play it separately.)")
    print("This is the exact, verified transcript of that recording --")
    print("not a live ASR call. Live transcription does work now (Groq's")
    print("hosted Whisper, see /report/voice), this mode just avoids any")
    print("network dependency during the actual presentation.\n")
    show_result(SAMPLE_TRANSCRIPT, district=SAMPLE_DISTRICT)


def run_live():
    print("[Live judge mode]\n")
    print("Type a sentence as if reporting an incident -- Hindi, Telugu, or")
    print("English, native script or romanized. Everything past this point")
    print("(language detection, risk tiering, legal citations, escalation)")
    print("runs for real, live, on whatever is typed. Type 'quit' to stop.\n")
    while True:
        try:
            text = input("Your report: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text or text.lower() == "quit":
            break
        district = input("District (optional, Enter to skip): ").strip() or None
        print()
        show_result(text, district=district)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena voice-demo helper")
    parser.add_argument(
        "--live", action="store_true",
        help="Let someone type input live instead of running the prepared sample",
    )
    args = parser.parse_args()

    run_live() if args.live else run_sample()
