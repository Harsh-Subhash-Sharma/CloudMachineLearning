import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_feedback_from_gpt(questions, answers):
    detailed_feedback = []

    for i, (q, a) in enumerate(zip(questions, answers), 1):
        question_text = q["question"]
        reference_answer = q["answer"]

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

        # Append the feedback block (without audio confidence yet)
        formatted = {
            "question": question_text,
            "answer": a,
            "reference": reference_answer,
            "concept_feedback": concept_feedback,
            "confidence": "🔍 Analyzing..."  # Placeholder for voice analysis
        }

        detailed_feedback.append(formatted)

    return detailed_feedback
