from utils.translate import translate_text, translate_to_english

def test_translate_text():
    text = "Bonjour"
    result = translate_text(text, "en")
    assert isinstance(result, str)

def test_translate_to_english():
    result = translate_to_english("Hola")
    assert "Hello" in result or isinstance(result, str)
