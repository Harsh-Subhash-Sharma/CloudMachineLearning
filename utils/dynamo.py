import boto3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
table = dynamodb.Table("InterviewSessions")

# ✅ Save a session with language support
def save_session(resume_text, jd_text, skills, questions, answers, feedback, language):
    session_id = str(uuid.uuid4())

    question_texts = []

    for q in questions:
        if isinstance(q, str):
            question_texts.append(q)
        elif isinstance(q, dict) and "question" in q:
            question_texts.append(q["question"])
        else:
            question_texts.append(str(q))  # fallback if structure is unknown

    try:
        data = {
            "session_id": session_id,
            "resume_text": resume_text,
            "jd_text": jd_text,
            "skills": skills,
            "questions": question_texts,
            "answers": answers,
            "feedback": feedback,
            "language": language
        }

        table.put_item(Item=data)
        return session_id

    except Exception as e:
        print(f"❌ DynamoDB Save Error: {e}")
        return None



# ✅ Retrieve session by session_id
def get_session(session_id):
    try:
        response = table.get_item(Key={"session_id": session_id})
        return response.get("Item", None)
    except Exception as e:
        print(f"❌ Error fetching session {session_id}: {e}")
        return None
