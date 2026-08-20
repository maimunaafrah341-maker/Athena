import base64
import requests
import os
import subprocess

# Bhashini API Configuration
BHASHINI_USER_ID = "YOUR_BHASHINI_USER_ID"
BHASHINI_API_KEY = "YOUR_BHASHINI_API_KEY"

LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "te": "te"
}

def convert_to_wav(input_path, output_path="temp_16k.wav"):
    """Ensures input audio is formatted properly for Bhashini ASR"""
    try:
        command = f"ffmpeg -y -i {input_path} -ar 16000 -ac 1 {output_path}"
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except Exception:
        # Fallback if ffmpeg isn't installed locally during early testing
        return input_path

def process_voice_to_text(audio_file_path, selected_language="hi"):
    """Converts spoken WAV/WebM audio file into text using Bhashini ASR"""
    clean_audio_path = convert_to_wav(audio_file_path)
    
    with open(clean_audio_path, "rb") as audio_file:
        base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")

    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {"sourceLanguage": LANG_MAP.get(selected_language, "hi")},
                    "serviceId": "",
                    "audioFormat": "wav",
                    "samplingRate": 16000
                }
            }
        ],
        "inputData": {
            "audio": [{"audioContent": base64_audio}]
        }
    }

    headers = {
        "userID": BHASHINI_USER_ID,
        "ulcaApiKey": BHASHINI_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
            json=payload,
            headers=headers,
            timeout=10
        )
        result = response.json()
        transcribed_text = result['pipelineResponse'][0]['output'][0]['source']
        return transcribed_text
    except Exception as e:
        print(f"[Warning] API call failed or keys not set. Error: {e}")
        return "मदद चाहिए"  # Mock fallback string for local testing

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