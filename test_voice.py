from voice_service import run_athena_voice_pipeline

if __name__ == "__main__":
    print("--- Starting Athena Voice Module Test ---")
    
    # Testing mock voice input in Hindi ('hi')
    mock_audio_file = "sample.wav" 
    selected_language = "hi"
    
    result = run_athena_voice_pipeline(mock_audio_file, selected_language)
    
    print("\n--- Final Pipeline Result ---")
    print(result)
    