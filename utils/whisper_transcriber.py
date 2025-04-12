from faster_whisper import WhisperModel

# Load model once
model = WhisperModel("base", device="cpu", compute_type="int8")  # You can try "medium" or "large" later

def transcribe_audio_local(audio_path, language="auto"):
    segments, _ = model.transcribe(audio_path, language=language)
    full_text = " ".join([segment.text for segment in segments])
    return full_text.strip()
