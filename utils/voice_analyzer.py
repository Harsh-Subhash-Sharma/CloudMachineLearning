import librosa
import numpy as np

def analyze_voice_confidence(audio_path):
    try:
        y, sr = librosa.load(audio_path)
        duration = librosa.get_duration(y=y, sr=sr)

        if duration < 1.5:
            return "🧍‍♂️ Low Confidence 👎 (Very short or clipped response)"

        # Extract features
        rms = np.mean(librosa.feature.rms(y=y))
        pitch, _ = librosa.piptrack(y=y, sr=sr)
        pitch = pitch[pitch > 0]
        pitch_variance = np.var(pitch) if len(pitch) > 0 else 0
        speech_rate = len(librosa.onset.onset_detect(y=y, sr=sr)) / duration

        # Heuristics for confidence level
        if rms > 0.02 and pitch_variance > 100 and 1.5 <= speech_rate <= 4:
            return "🎙️ Confident and Clear 👍"
        elif rms > 0.01 and pitch_variance > 30:
            return "🗣️ Slightly Hesitant 😐"
        else:
            return "🧍‍♂️ Low Confidence 👎"

    except Exception as e:
        print(f"[Voice Analyzer] Error: {e}")
        return "❌ Voice Analysis Failed"
