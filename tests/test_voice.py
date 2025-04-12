from utils.voice_analyzer import analyze_voice_confidence

def test_analyze_voice_confidence():
    result = analyze_voice_confidence("tests/sample_audio.mp3")
    assert result in [
        "🎙️ Confident and Clear 👍",
        "🗣️ Slightly Hesitant 😐",
        "😕 Low Confidence 👎",
    ]
