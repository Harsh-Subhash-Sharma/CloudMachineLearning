import pytest
from unittest.mock import patch, MagicMock
from app import start_interview, reset_session
import gradio as gr

# ----------- TEST start_interview -----------
@patch("app.extract_text")
@patch("app.translate_to_english")
@patch("app.extract_keywords_from_resume_and_jd")
@patch("app.get_final_question_set")
@patch("app.translate_text")
@patch("app.synthesize_speech")
def test_start_interview_valid(
    mock_synthesize, mock_translate_text, mock_get_questions,
    mock_extract_skills, mock_translate_english, mock_extract_text
):
    # Mocks
    mock_resume_file = MagicMock()
    mock_resume_file.name = "resume.pdf"
    
    mock_extract_text.return_value = "Raw resume text"
    mock_translate_english.side_effect = lambda text: text  # Return same text
    mock_extract_skills.return_value = ["Python", "Machine Learning"]
    mock_get_questions.return_value = [{"question": "Tell me about Python", "type": "technical"}]
    mock_translate_text.return_value = "Parlez-moi de Python"
    mock_synthesize.return_value = "audio.mp3"

    status, chat, audio, visible = start_interview(mock_resume_file, "Job description here", "fr")

    assert "✅" in status["value"]
    assert chat[0]["role"] == "assistant"
    assert "Question 1" in chat[0]["content"]
    assert audio == "audio.mp3"
    assert visible["visible"] == True


def test_start_interview_missing_input():
    result = start_interview(None, "", "en")
    assert "❌" in result[0]["value"]
    assert result[1] == []
    assert result[2] is None
    assert result[3]["visible"] == False

def test_start_interview_invalid_format():
    mock_file = MagicMock()
    mock_file.name = "resume.txt"
    result = start_interview(mock_file, "Some JD", "en")
    assert "❌ Unsupported resume format." in result[0]["value"]


# ----------- TEST reset_session -----------
def test_reset_session():
    # Set dummy values
    from app import resume_text, jd_text, skills, answers
    resume_text = "text"
    jd_text = "jd"
    skills = ["Python"]
    answers = ["Yes"]

    reset_session()

    assert resume_text == ""
    assert jd_text == ""
    assert skills == []
    assert answers == []