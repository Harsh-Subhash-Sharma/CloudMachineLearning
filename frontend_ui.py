import gradio as gr
import requests

API_BASE = "http://172.30.166.134:8000"

# Language code map for AWS Translate
LANG_CODE_MAP = {
    "us English": "en",
    "fr French": "fr",
    "es Spanish": "es"
}

# Store session state
session_state = {
    "questions": [],
    "answers": [],
    "current_index": 0,
    "language": "us English",
    "resume_text": "",
    "jd_text": "",
    "skills": [],
    "feedback": []
}

def start_interview(resume_file, jd_text, language):
    session_state["answers"] = []
    session_state["current_index"] = 0
    session_state["questions"] = []
    session_state["language"] = language
    session_state["jd_text"] = jd_text

    parsed = requests.post(f"{API_BASE}/parse-resume", json={
        "filename": resume_file.name
    }).json()
    resume_text = parsed.get("text", "")
    session_state["resume_text"] = resume_text

    extracted = requests.post(f"{API_BASE}/extract-skills", json={
        "resume": resume_text,
        "job_description": jd_text
    }).json()
    skills = extracted.get("skills", [])
    session_state["skills"] = skills

    raw_qs = requests.post(f"{API_BASE}/get-questions", json={"skills": skills}).json().get("questions", [])
    translated_questions = []
    lang_code = LANG_CODE_MAP.get(language, "en")

    for q in raw_qs:
        q_text = q["question"] if isinstance(q, dict) else str(q)
        if lang_code != "en":
            try:
                translated = requests.post(f"{API_BASE}/translate", json={
                    "text": q_text,
                    "target_language": lang_code
                }).json().get("text", q_text)
                translated_questions.append(translated)
            except Exception:
                translated_questions.append(q_text)
        else:
            translated_questions.append(q_text)

    session_state["questions"] = translated_questions
    first_question = translated_questions[0] if translated_questions else "No questions generated"
    return resume_text, "\n".join(skills), first_question

def submit_answer(answer):
    session_state["answers"].append(answer)
    session_state["current_index"] += 1

    if session_state["current_index"] < len(session_state["questions"]):
        next_q = session_state["questions"][session_state["current_index"]]
        return "", next_q, gr.update(visible=True), gr.update(visible=False)
    else:
        return "", "All questions answered. Click below for feedback.", gr.update(visible=False), gr.update(visible=True)

def generate_feedback():
    answers = session_state["answers"]
    lang_code = LANG_CODE_MAP.get(session_state["language"], "en")

    response = requests.post(f"{API_BASE}/get-feedback", json={
        "questions": session_state["questions"],
        "answers": answers,
        "language": lang_code
    })

    feedback = response.json().get("feedback", [])
    session_state["feedback"] = feedback

    formatted_feedback = []
    for f in feedback:
        block = (
            f"📌 Question: {f['question']}\n"
            f"🗣️ Your Answer: {f['answer']}\n"
            f"💡 Reference Answer: {f['reference']}\n"
            f"🔹 Feedback: {f['concept_feedback']}\n"
        )

        if lang_code != "en":
            try:
                translated = requests.post(f"{API_BASE}/translate", json={
                    "text": block,
                    "target_language": lang_code
                }).json().get("text", block)
                formatted_feedback.append(translated)
            except Exception:
                formatted_feedback.append(block)
        else:
            formatted_feedback.append(block)

    # Save session
    save_resp = requests.post(f"{API_BASE}/save-session", json={
        "resume_text": session_state["resume_text"],
        "jd_text": session_state["jd_text"],
        "skills": session_state["skills"],
        "questions": session_state["questions"],
        "answers": session_state["answers"],
        "feedback": session_state["feedback"],
        "language": lang_code
    })

    session_id = save_resp.json().get("session_id", "N/A")

    return f"✅ Interview complete! Your session ID: `{session_id}`\n\n" + "\n---\n".join(formatted_feedback)

def fetch_session(session_id):
    try:
        response = requests.get(f"{API_BASE}/get-session/{session_id}")
        data = response.json()

        qna_blocks = []
        for q, a, f in zip(data['questions'], data['answers'], data['feedback']):
            block = (
                f"📌 {q}\n"
                f"🗣️ {a}\n"
                f"💬 {f.get('concept_feedback', 'No feedback')}"
            )
            qna_blocks.append(block)

        formatted = (
            f"📄 Resume:\n{data['resume_text']}\n\n"
            f"📋 Job Description:\n{data['jd_text']}\n\n"
            f"🧠 Skills:\n{', '.join(data['skills'])}\n\n"
            f"🧪 Session Details:\n" + "\n\n".join(qna_blocks)
        )

        return formatted
    except Exception as e:
        return f"❌ Error retrieving session: {str(e)}"

# UI
with gr.Blocks() as demo:
    with gr.Tab("🎤 Interview"):
        gr.Markdown("# 🧠 Interview Bot – One Question at a Time")

        with gr.Row():
            resume_file = gr.File(label="📄 Upload Resume")
            jd_text = gr.Textbox(label="📋 Paste Job Description")

        lang = gr.Dropdown(
            choices=["us English", "fr French", "es Spanish"],
            value="us English",
            label="🌍 Interview Language"
        )
        start_button = gr.Button("🚀 Start Interview")

        resume_output = gr.Textbox(label="📄 Extracted Resume Text")
        skills_output = gr.Textbox(label="🧠 Skills Extracted")
        question_box = gr.Textbox(label="❓ Interview Question", lines=2)

        answer_input = gr.Textbox(label="✍️ Your Answer", lines=2)
        next_button = gr.Button("➡️ Next Question", visible=True)
        feedback_button = gr.Button("📊 Get Feedback", visible=False)
        feedback_output = gr.Textbox(label="💬 AI Feedback", lines=6)

        start_button.click(
            fn=start_interview,
            inputs=[resume_file, jd_text, lang],
            outputs=[resume_output, skills_output, question_box]
        )

        next_button.click(
            fn=submit_answer,
            inputs=[answer_input],
            outputs=[answer_input, question_box, next_button, feedback_button]
        )

        feedback_button.click(
            fn=generate_feedback,
            outputs=feedback_output
        )

    with gr.Tab("📂 Session Retrieval"):
        gr.Markdown("## 🔍 Retrieve Past Session by ID")
        session_id_input = gr.Textbox(label="🔑 Enter Session ID")
        fetch_button = gr.Button("📥 Fetch Session")
        session_output = gr.Textbox(label="📝 Session Details", lines=20)

        fetch_button.click(
            fn=fetch_session,
            inputs=session_id_input,
            outputs=session_output
        )

demo.launch()
