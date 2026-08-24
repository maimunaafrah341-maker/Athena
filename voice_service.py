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
# control. OpenAI's key is issued instantly on signup, no approval
# queue. If Bhashini access ever does come through, this is the only
# function that needs to change back -- run_athena_voice_pipeline()
# and everything downstream only ever sees plain transcribed text,
# never which provider produced it.
#
# Same pattern as GEMINI_API_KEY in response_engine.py: real
# credentials go in .env (gitignored, never committed), not
# hardcoded here -- this file gets committed to git.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# whisper-1, not one of the newer/cheaper gpt-4o-*-transcribe models --
# it's the most thoroughly documented, longest-established option, and
# at demo-scale usage the cost difference is not worth trading
# reliability for this close to the deadline.
OPENAI_TRANSCRIBE_MODEL = "whisper-1"

# OpenAI expects ISO-639-1 codes -- same values Athena already uses
# internally, so no new mapping table was actually needed, kept for
# symmetry with the rest of this file and in case a future language
# code ever needs translating before being sent upstream.
LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "te": "te"
}

def convert_to_wav(input_path, output_path="temp_16k.wav"):
    """Ensures input audio is formatted properly before transcription"""
    try:
        command = f"ffmpeg -y -i {input_path} -ar 16000 -ac 1 {output_path}"
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except Exception:
        return input_path

def process_voice_to_text(audio_file_path, selected_language="hi"):
    """Converts spoken WAV/WebM audio file into text using OpenAI's
    transcription API"""

    # Check if the audio file exists on your machine
    if not os.path.exists(audio_file_path):
        print(f"[Info] Audio file '{audio_file_path}' not found. Using mock input for offline testing.")
        return "मदद चाहिए"

    clean_audio_path = convert_to_wav(audio_file_path)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    data = {
        "model": OPENAI_TRANSCRIBE_MODEL,
        "language": LANG_MAP.get(selected_language, "hi"),
    }

    try:
        with open(clean_audio_path, "rb") as audio_file:

            files = {
                "file": (os.path.basename(clean_audio_path), audio_file, "audio/wav")
            }

            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                data=data,
                files=files,
                timeout=30,
            )

        result = response.json()

        if "text" not in result:
            raise ValueError(result.get("error", {}).get("message", f"unexpected response: {result}"))

        return result["text"]

    except Exception as e:
        print(f"[Warning] API call failed or key not set. Error: {e}")
        return "मदद चाहिए"

def run_athena_voice_pipeline(audio_file_path, selected_language, backend_pipeline_func=None):
    """
    Main bridge function: 
    1. Turns Audio -> Text via Bhashini
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