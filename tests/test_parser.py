from utils.parser import extract_text

def test_extract_text_docx():
    result = extract_text("tests/test_resume.docx")
    assert isinstance(result, str)
