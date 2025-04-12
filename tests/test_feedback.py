from utils.feedback import get_feedback_from_gpt

def test_get_feedback_from_gpt():
    questions = [{"question": "What is a database?"}]
    answers = ["A structured way to store data."]
    result = get_feedback_from_gpt(questions, answers)
    assert isinstance(result, list)
    assert "question" in result[0]
    assert "concept_feedback" in result[0]
