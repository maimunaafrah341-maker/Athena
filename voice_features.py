# ============================================================
# ATHENA — VOICE ACOUSTIC FEATURE EXTRACTION
# ============================================================

"""
Extracts the three required VoiceFeatures fields (pitch_variation,
pause_ratio, speech_rate_wpm) plus the optional ones
(avg_pause_duration_sec, voice_energy_variability) from a real audio
file, using librosa.

svi.py's voice-fusion logic (_voice_stress_score, calibrated from
Samreen's 2026-08-24 acoustic distress-index handoff) has existed
since before this file did, but nothing ever computed real numbers for
it -- /report/voice transcribed audio and threw the audio itself away
without measuring anything acoustic. This closes that gap.

Design note on pitch_variation specifically: Samreen's handoff defines
calm/high/critical bands on a 0-1 scale (see svi.py's
PITCH_CALM_CEILING etc.) but the underlying acoustic formula that
produced her numbers isn't available here -- only the calibration
target values are. This module computes the coefficient of variation
(std/mean) of the voiced F0 contour, which is the standard acoustic
correlate of "pitch variability," then linearly rescales it so a
raw CoV in the neighborhood of typical calm conversational speech
(~0.05-0.10) lands near 0 and a raw CoV around clearly agitated/
crying speech (~0.45+) lands near 1 -- chosen by running this
extractor against this project's own real demo recordings (see
voice_features.py's __main__ block) and checking the output lands in
a sane place relative to how distressed each clip actually sounds, not
derived from a validated dataset. Same "heuristic starting point, not
clinically validated" caveat svi.py already carries -- flagged here
too rather than implied to be more rigorous than it is.

Every extraction failure (corrupt file, unreadable format, a clip too
short/quiet to have any voiced frames) returns None for every field
rather than raising -- matches svi.py's own contract that a missing
voice signal is a normal, expected "text-only" case, never an error
that should block a report.
"""

import numpy as np
import librosa

SR = 16000  # resample target; matches voice_service.py's ffmpeg conversion

# Human voice fundamental frequency range (pyin needs bounds) --
# C2 (~65Hz) to C6 (~1047Hz) comfortably covers adult male and female
# speech, including raised/strained pitch under distress.
F0_MIN = librosa.note_to_hz("C2")
F0_MAX = librosa.note_to_hz("C6")

# Raw coefficient-of-variation anchor points mapped to the 0-1 scale
# svi.py's PITCH_CALM_CEILING/scoring expects -- see module docstring
# for how these were chosen.
PITCH_COV_FLOOR = 0.05
PITCH_COV_CEILING = 0.45

# librosa.effects.split's silence threshold -- audio quieter than this
# many dB below the clip's own peak counts as a pause. 30dB is
# librosa's own documented default for speech; not re-tuned here.
SILENCE_TOP_DB = 30

# Below this, F0 tracking doesn't have enough context to be trustworthy
# -- testing against this project's own real demo clips found a 2.5s
# clip producing a near-maximum pitch_variation (0.97) that was almost
# certainly noise from too few stable voiced frames, not a real signal
# (see voice_features.py's module docstring / __main__ notes). Better
# to report "no pitch signal" (None, same as no voice fusion at all)
# than inject a number this unreliable into a safety-relevant score.
MIN_DURATION_FOR_PITCH_SEC = 5.0
MIN_VOICED_FRAMES_FOR_PITCH = 20


def _pitch_variation(y, sr, total_duration_sec):

    if total_duration_sec < MIN_DURATION_FOR_PITCH_SEC:
        return None

    f0, voiced_flag, _voiced_probs = librosa.pyin(
        y, fmin=F0_MIN, fmax=F0_MAX, sr=sr
    )

    voiced_f0 = f0[voiced_flag & ~np.isnan(f0)]

    if len(voiced_f0) < MIN_VOICED_FRAMES_FOR_PITCH or np.mean(voiced_f0) <= 0:
        return None

    cov = float(np.std(voiced_f0) / np.mean(voiced_f0))

    scaled = (cov - PITCH_COV_FLOOR) / (PITCH_COV_CEILING - PITCH_COV_FLOOR)

    return round(max(0.0, min(1.0, scaled)), 3)


def _pause_features(y, sr, total_duration_sec):

    if total_duration_sec <= 0:
        return None, None

    intervals = librosa.effects.split(y, top_db=SILENCE_TOP_DB)

    if len(intervals) == 0:
        # Nothing detected as speech at all -- entire clip is "pause."
        return 1.0, round(float(total_duration_sec), 2)

    voiced_duration_sec = float(sum(
        (end - start) / sr for start, end in intervals
    ))

    pause_ratio = max(0.0, min(1.0, 1 - (voiced_duration_sec / total_duration_sec)))

    # Average gap between consecutive voiced intervals (not counting
    # any leading/trailing silence outside the first/last detected
    # speech) -- None if there's only one contiguous voiced interval,
    # since there's no gap to measure.
    gaps = [
        float(intervals[i][0] - intervals[i - 1][1]) / sr
        for i in range(1, len(intervals))
    ]

    avg_pause_duration_sec = round(float(np.mean(gaps)), 2) if gaps else None

    return round(float(pause_ratio), 3), avg_pause_duration_sec


def _speech_rate_wpm(transcript, total_duration_sec):

    if not transcript or total_duration_sec <= 0:
        return None

    word_count = len(transcript.split())

    if word_count == 0:
        return None

    return round(word_count / (total_duration_sec / 60), 1)


def _voice_energy_variability(y):

    rms = librosa.feature.rms(y=y)[0]

    if len(rms) < 2 or np.mean(rms) <= 0:
        return None

    return round(float(np.std(rms) / np.mean(rms)), 3)


def extract_voice_features(audio_path, transcript=None):
    """
    Returns a dict matching app.py's VoiceFeatures shape:
    {pitch_variation, pause_ratio, speech_rate_wpm,
    avg_pause_duration_sec, voice_energy_variability}, or None if the
    file can't be loaded/analyzed at all.

    transcript, if given (the ASR output for this same audio -- see
    app.py's /report/voice), is what speech_rate_wpm is computed from;
    without it, speech_rate_wpm stays None and svi.py's
    _voice_stress_score() correctly treats the whole feature set as
    unusable (it requires all three core fields present) rather than
    silently fusing on two of three signals.
    """

    try:
        y, sr = librosa.load(audio_path, sr=SR, mono=True)
    except Exception:
        return None

    if y is None or len(y) == 0:
        return None

    total_duration_sec = len(y) / sr

    try:
        pitch_variation = _pitch_variation(y, sr, total_duration_sec)
        pause_ratio, avg_pause_duration_sec = _pause_features(y, sr, total_duration_sec)
        speech_rate_wpm = _speech_rate_wpm(transcript, total_duration_sec)
        voice_energy_variability = _voice_energy_variability(y)
    except Exception:
        return None

    return {
        "pitch_variation": pitch_variation,
        "pause_ratio": pause_ratio,
        "speech_rate_wpm": speech_rate_wpm,
        "avg_pause_duration_sec": avg_pause_duration_sec,
        "voice_energy_variability": voice_energy_variability,
    }


if __name__ == "__main__":

    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "demo_audio/caste_harassment_hindi.ogg"
    transcript_arg = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Analyzing: {path}")
    features = extract_voice_features(path, transcript=transcript_arg)
    print(features)
