from utils.whisper_transcriber import transcribe_audio_local

def test_transcribe_audio_local():
    result = transcribe_audio_local("tests/sample_audio.mp3", language="en")
    assert isinstance(result, str)
