import openai
import os
from dotenv import load_dotenv
from utils.translate import translate_text  # ✅ Make sure this import is included

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_feedback_from_gpt(questions, answers, language="us"):
    detailed_feedback = []

    for i, (q, a) in enumerate(zip(questions, answers), 1):
        # Detect whether q is a dict or plain string
        if isinstance(q, dict):
            question_text = q.get("question", "")
            reference_answer = q.get("answer", "N/A")
        else:
            question_text = q
            reference_answer = "N/A"

        prompt = (
            f"You are an expert technical interviewer. Compare the candidate's answer to the reference answer.\n"
            f"📌 Question: {question_text}\n"
            f"🗣️ User's Answer: {a}\n"
            f"💡 Reference Answer: {reference_answer}\n\n"
            "🔹 Concept Feedback: Give specific feedback on how accurate and complete the user’s answer is. "
            "Point out what's missing or incorrect, but keep it professional and constructive."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful interview coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250,
        )

        concept_feedback = response.choices[0].message["content"].strip()

        # 🌍 Translate only if language is NOT English
        if language and language != "us":
            concept_feedback = translate_text(concept_feedback, language)

        formatted = {
            "question": question_text,
            "answer": a,
            "reference": reference_answer,
            "concept_feedback": concept_feedback,
            "confidence": "🔍 Analyzing..."
        }

        detailed_feedback.append(formatted)

    return detailed_feedback
