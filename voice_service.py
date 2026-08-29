import requests
import os
import subprocess

from dotenv import load_dotenv

# Speech-to-text configuration
#
# Swapped from Bhashini to OpenAI's transcription API 2026-08-24 --
# Bhashini's government approval queue never cleared (Samreen's
# application sat pending ~5 days; a fresh one couldn't even be
# submitted across 3 separate accounts), and the hackathon deadline
# couldn't wait on an external approval process outside the team's
# control.
#
# Swapped again 2026-08-29 (Groq primary, OpenAI demoted to fallback):
# OpenAI's transcription API needs a funded account, and that funding
# never happened -- every voice report tonight was silently falling
# back to a fixed placeholder transcript regardless of what was
# actually said (see the except branch below). Groq hosts Whisper
# directly (whisper-large-v3-turbo, same OpenAI-compatible request
# shape) with a genuinely usable free tier, and GROQ_API_KEY already
# exists in .env from response_engine.py's LLM fallback chain -- no
# new account/key needed. Same "everything downstream only ever sees
# plain transcribed text, never which provider produced it" contract
# as before; run_athena_voice_pipeline() didn't need to change.
#
# Same pattern as GEMINI_API_KEY in response_engine.py: real
# credentials go in .env (gitignored, never committed), not
# hardcoded here -- this file gets committed to git.
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TRANSCRIBE_MODEL = "whisper-large-v3-turbo"
GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TRANSCRIBE_MODEL = "whisper-1"
OPENAI_TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"

# Both providers speak Whisper's ISO-639-1 language codes -- same
# values Athena already uses internally, so no new mapping table was
# actually needed, kept for symmetry with the rest of this file and in
# case a future language code ever needs translating before being sent
# upstream.
LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "te": "te",
    "ur": "ur",
    "bn": "bn"
}


def convert_to_wav(input_path, output_path="temp_16k.wav"):
    """Ensures input audio is formatted properly before transcription"""
    try:
        command = f"ffmpeg -y -i {input_path} -ar 16000 -ac 1 {output_path}"
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except Exception:
        return input_path


def _call_transcription_api(url, api_key, model, audio_path, language, timeout=30):
    """
    Shared multipart POST for any OpenAI-compatible /audio/transcriptions
    endpoint (Groq and OpenAI both implement this exact shape). Raises
    on any failure -- callers decide what "no result" means, this
    function doesn't swallow errors or return a placeholder itself.
    """

    headers = {"Authorization": f"Bearer {api_key}"}

    data = {
        "model": model,
        "language": LANG_MAP.get(language, "hi"),
    }

    with open(audio_path, "rb") as audio_file:

        files = {
            "file": (os.path.basename(audio_path), audio_file, "audio/wav")
        }

        response = requests.post(
            url, headers=headers, data=data, files=files, timeout=timeout,
        )

    result = response.json()

    if "text" not in result:
        raise ValueError(result.get("error", {}).get("message", f"unexpected response: {result}"))

    return result["text"]


def process_voice_to_text(audio_file_path, selected_language="hi"):
    """
    Converts spoken WAV/WebM audio file into text.

    Tries Groq's hosted Whisper first (free tier, no funded account
    needed), then OpenAI's if a key is set and Groq fails, then falls
    back to a fixed placeholder if both are unavailable -- same
    graceful-degradation shape as response_engine.py's generation
    fallback chain, just for transcription instead of chat completion.
    """

    if not os.path.exists(audio_file_path):
        print(f"[Info] Audio file '{audio_file_path}' not found. Using mock input for offline testing.")
        return "मदद चाहिए"

    clean_audio_path = convert_to_wav(audio_file_path)

    if GROQ_API_KEY:
        try:
            return _call_transcription_api(
                GROQ_TRANSCRIBE_URL, GROQ_API_KEY, GROQ_TRANSCRIBE_MODEL,
                clean_audio_path, selected_language,
            )
        except Exception as e:
            print(f"[Warning] Groq transcription failed: {type(e).__name__}: {e}")

    if OPENAI_API_KEY:
        try:
            return _call_transcription_api(
                OPENAI_TRANSCRIBE_URL, OPENAI_API_KEY, OPENAI_TRANSCRIBE_MODEL,
                clean_audio_path, selected_language,
            )
        except Exception as e:
            print(f"[Warning] OpenAI transcription failed: {type(e).__name__}: {e}")

    print("[Warning] No transcription provider available or all failed. Using placeholder.")
    return "मदद चाहिए"


def run_athena_voice_pipeline(audio_file_path, selected_language, backend_pipeline_func=None):
    """
    Main bridge function:
    1. Turns Audio -> Text via Groq/OpenAI Whisper
    2. Passes Text -> Backend Athena Engine
    """
    print(f"[1/2] Processing audio file in language: '{selected_language}'...")
    transcribed_text = process_voice_to_text(audio_file_path, selected_language)
    print(f"[Transcribed Text]: {transcribed_text}")

    print("[2/2] Passing text to Athena risk triage pipeline...")
    if backend_pipeline_func:
        response = backend_pipeline_func(transcribed_text)
    else:
        response = {
            "status": "success",
            "transcription": transcribed_text,
            "triage_summary": "Incident logged. Evaluating legal breach...",
            "language": selected_language
        }

    return response
