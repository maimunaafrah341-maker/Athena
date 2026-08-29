# ============================================================
# ATHENA — TEXT-TO-SPEECH
# ============================================================

"""
Synthesizes Athena's text response into spoken audio via Google Cloud
Text-to-Speech's REST API (simple API-key auth, not a service-account/
OAuth setup -- same lightweight "raw requests.post(), not an SDK
object" pattern already used for Groq/OpenRouter in response_engine.py
and Groq/OpenAI in voice_service.py).

Deliberately NOT wired into /report or /report/voice -- synthesis
costs real latency and (past the free tier) money on every call, most
of which nobody will ever play back. Exposed as its own on-demand
POST /tts endpoint instead (see app.py), called only when someone
actually taps a "listen" button on a response already shown as text.
A TTS failure must never be able to block a report being submitted;
keeping this fully decoupled from the report endpoints is what
guarantees that, not exception handling alone.

Requires GOOGLE_TTS_API_KEY in .env (from Google Cloud Console ->
APIs & Services -> Credentials, with the Cloud Text-to-Speech API
enabled on that project) -- unset as of 2026-08-30, so this is built
and should be structurally correct, but hasn't been verified against a
real API call yet. Verify a live synthesis before relying on this in a
demo, same caveat every other new provider swap in this codebase has
carried.

Voice selection per language is a best-effort mapping to Google's
Indian-locale Standard voices -- en/hi/te/bn are well-established in
Google's voice catalog; ur (Urdu) specifically is NOT confirmed
against Google's current voice list (no way to verify without a real
API call) -- if synthesis fails for Urdu specifically, that's the
first thing to check, not assumed broken code.
"""

import base64
import requests

import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")
GOOGLE_TTS_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"

# language code (Athena's internal SUPPORTED_LANGUAGES keys) -> Google
# Cloud TTS (languageCode, voice name). Standard tier, not WaveNet/
# Neural2 -- Standard has the larger free-tier monthly character
# quota, and voice-quality difference doesn't matter much for a short
# triage response played back once.
VOICE_MAP = {
    "en": {"languageCode": "en-IN", "name": "en-IN-Standard-A"},
    "hi": {"languageCode": "hi-IN", "name": "hi-IN-Standard-A"},
    "te": {"languageCode": "te-IN", "name": "te-IN-Standard-A"},
    "ur": {"languageCode": "ur-IN", "name": "ur-IN-Standard-A"},
    "bn": {"languageCode": "bn-IN", "name": "bn-IN-Standard-A"},
}

_MAX_CHARS = 5000  # Google's own hard limit per synthesize call


def synthesize_speech(text, language="en"):
    """
    Returns raw MP3 bytes, or None if synthesis isn't available/failed
    -- never raises. A missing API key, an unsupported language/voice,
    a network failure, or an over-length input are all treated the
    same way: no audio, not an error the caller has to handle
    specially. The caller (app.py's /tts) turns None into a clear
    "not available" response rather than a fake/silent success.
    """

    if not GOOGLE_TTS_API_KEY:
        print("[Warning] GOOGLE_TTS_API_KEY not set -- TTS unavailable.")
        return None

    if not text or not text.strip():
        return None

    text = text[:_MAX_CHARS]

    voice = VOICE_MAP.get(language, VOICE_MAP["en"])

    payload = {
        "input": {"text": text},
        "voice": voice,
        "audioConfig": {"audioEncoding": "MP3"},
    }

    try:
        response = requests.post(
            GOOGLE_TTS_URL,
            params={"key": GOOGLE_TTS_API_KEY},
            json=payload,
            timeout=30,
        )

        result = response.json()

        if "audioContent" not in result:
            raise ValueError(result.get("error", {}).get("message", f"unexpected response: {result}"))

        return base64.b64decode(result["audioContent"])

    except Exception as e:
        print(f"[Warning] TTS synthesis failed (language={language!r}): {type(e).__name__}: {e}")
        return None


if __name__ == "__main__":

    audio = synthesize_speech("This is a test of Athena's text to speech.", "en")

    if audio:
        with open("_local/tts_test_output.mp3", "wb") as f:
            f.write(audio)
        print(f"Wrote {len(audio)} bytes to _local/tts_test_output.mp3")
    else:
        print("No audio returned -- check GOOGLE_TTS_API_KEY is set and valid.")
