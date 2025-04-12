import gradio as gr
import os
from utils.parser import extract_text
from utils.skills_extractor import extract_keywords_from_resume_and_jd
from utils.question_retriever import get_final_question_set
from utils import dynamo
from utils.feedback import get_feedback_from_gpt
from utils.translate import translate_text, translate_to_english
from utils.polly import synthesize_speech
from utils.whisper_transcriber import transcribe_audio_local
from utils.voice_analyzer import analyze_voice_confidence

resume_text = ""
jd_text = ""
skills = []
questions = []
answers = []
selected_language = "en"
translated_feedback = ""
confidence_levels = []

# 🧠 Start Interview
def start_interview(resume_file, jd_input, lang_code):
    global resume_text, jd_text, skills, questions, answers, selected_language, confidence_levels
    answers = []
    confidence_levels = []
    selected_language = lang_code

    if not resume_file or not jd_input.strip():
        return gr.update(value="❌ Please upload a resume and paste the job description."), [], None, gr.update(visible=False)

    try:
        ext = os.path.splitext(resume_file.name)[1].lower()
        if ext not in [".pdf", ".docx"]:
            return gr.update(value="❌ Unsupported resume format."), [], None, gr.update(visible=False)

        resume_text_raw = extract_text(resume_file.name)
        jd_text_raw = jd_input.strip()

        resume_text = translate_to_english(resume_text_raw)
        jd_text = translate_to_english(jd_text_raw)
        skills = extract_keywords_from_resume_and_jd(resume_text, jd_text)
        questions = get_final_question_set(skills)

        first_q = questions[0]["question"]
        translated_q = translate_text(first_q, lang_code)
        q_type = questions[0]["type"].capitalize()

        audio_path = synthesize_speech(translated_q)

        return (
            gr.update(value=f"✅ Interview starting in {lang_code.upper()}..."),
            [{"role": "assistant", "content": f"[{q_type}] Question 1: {translated_q}"}],
            audio_path,
            gr.update(visible=True)
        )

    except Exception as e:
        return gr.update(value=f"❌ Error: {e}"), [], None, gr.update(visible=False)

# 💬 Interview Bot
def interview_bot(audio, message, chat_history):
    global resume_text, jd_text, skills, questions, answers, selected_language, translated_feedback, confidence_levels

    index = len(answers)

    if index >= len(questions):
        return chat_history + [{"role": "assistant", "content": "✅ Interview already completed."}], None

    # Transcribe or use text
    if audio:
        transcribed_text = transcribe_audio_local(audio, language=selected_language)
        confidence = analyze_voice_confidence(audio)
    else:
        transcribed_text = message
        confidence = "🗣️ Text response — audio not analyzed"

    answers.append(transcribed_text)
    confidence_levels.append(confidence)

    chat_history.append({"role": "user", "content": transcribed_text})

    # End of interview
    if index == len(questions) - 1:
        translated_answers = [translate_to_english(a) for a in answers]
        detailed_feedback = get_feedback_from_gpt(questions, translated_answers)

        for i, item in enumerate(detailed_feedback):
            item["confidence"] = confidence_levels[i]

        feedback_blocks = []
        for i, fb in enumerate(detailed_feedback, 1):
            block = (
                f"📌 *Question {i}:* {fb['question']}\n"
                f"🗣️ *User's Answer:* {fb['answer']}\n"
                f"💡 *Reference Answer:* {fb['reference']}\n"
                f"🔹 *Confidence Level:* {fb['confidence']}\n"
                f"🔹 *Concept Feedback:* {fb['concept_feedback']}\n"
            )
            feedback_blocks.append(block)

        final_feedback = "\n---\n".join(feedback_blocks)
        translated_feedback = translate_text(final_feedback, selected_language)

        session_id = dynamo.save_session(
            resume_text, jd_text, skills, questions, answers, translated_feedback, selected_language
        )

        chat_history.append({
            "role": "assistant",
            "content": f"✅ Interview complete! Your session ID: `{session_id}`\n\n🧠 **AI Feedback ({selected_language.upper()}):**\n\n{translated_feedback}"
        })

        return chat_history, None

    next_q = questions[index + 1]["question"]
    q_type = questions[index + 1]["type"].capitalize()
    translated_q = translate_text(next_q, selected_language)
    audio_path = synthesize_speech(translated_q)

    chat_history.append({"role": "assistant", "content": f"[{q_type}] Question {index + 2}: {translated_q}"})
    return chat_history, audio_path

# 🔁 Reset
def reset_session():
    global resume_text, jd_text, skills, questions, answers, selected_language, translated_feedback, confidence_levels
    resume_text = ""
    jd_text = ""
    skills = []
    questions = []
    answers = []
    translated_feedback = ""
    confidence_levels = []
    selected_language = "en"
    return gr.update(value=""), [], None, gr.update(visible=False)

# 📜 Load Past Session
def load_session(session_id):
    session = dynamo.get_session(session_id)
    if not session:
        return "❌ Session not found."

    output = f"### Session ID: `{session['session_id']}`\n\n"
    output += f"**🌍 Language Used:** {session.get('language', 'en').upper()}\n\n"
    output += f"**📝 Job Description:**\n{session['jd_text']}\n\n"
    output += f"**💡 Skills:** {', '.join(session['skills'])}\n\n"

    for i, (q, a) in enumerate(zip(session["questions"], session["answers"]), 1):
        output += f"**Q{i}:** {q}\n**A{i}:** {a}\n\n"

    if session.get("feedback"):
        output += f"\n**💬 GPT Feedback:**\n{session['feedback']}\n"

    return output

# 🖥️ Interface
with gr.Blocks() as demo:
    with gr.Tab("💬 Interview"):
        gr.Markdown("## 🤖 Interview Bot")
        gr.Markdown("**Note:** You can answer in 🇺🇸 English, 🇫🇷 French, 🇪🇸 Spanish, 🇮🇳 Hindi, or 🇩🇪 German.")
        resume_input = gr.File(label="📌 Upload Resume (PDF or DOCX)")
        jd_input = gr.Textbox(lines=6, label="📝 Paste Job Description Here")

        lang_dropdown = gr.Dropdown(
            label="🌍 Choose Interview Language",
            choices=[
                ("🇺🇸 English", "en"),
                ("🇫🇷 French", "fr"),
                ("🇪🇸 Spanish", "es"),
                ("🇮🇳 Hindi", "hi"),
                ("🇩🇪 German", "de"),
            ],
            value="en",
            interactive=True
        )

        start_button = gr.Button("🎯 Start Interview")
        status = gr.Textbox(label="Status", interactive=False)

        with gr.Column(visible=False) as chat_column:
            chatbot = gr.Chatbot(label="Chat", type="messages")
            audio_player = gr.Audio(label=None, type="filepath", interactive=False)

            with gr.Row():
                text_input = gr.Textbox(placeholder="Type your answer...", lines=1, max_lines=1, show_label=False, scale=3)
                audio_input = gr.Audio(type="filepath", label=None, interactive=True, scale=1)
                submit = gr.Button("➤", variant="primary", scale=0)

        reset = gr.Button("🔄 Start New Interview")

        start_button.click(
            fn=start_interview,
            inputs=[resume_input, jd_input, lang_dropdown],
            outputs=[status, chatbot, audio_player, chat_column]
        )

        submit.click(
            fn=interview_bot,
            inputs=[audio_input, text_input, chatbot],
            outputs=[chatbot, audio_player]
        ).then(
            fn=lambda: None,
            inputs=[],
            outputs=[audio_input],
            queue=False
        )

        reset.click(
            fn=reset_session,
            inputs=[],
            outputs=[status, chatbot, audio_player, chat_column]
        )

    with gr.Tab("📜 Session History"):
        gr.Markdown("### 🔍 View a Past Interview Session")
        session_input = gr.Textbox(label="Enter your Session ID")
        view_btn = gr.Button("View Session")
        session_display = gr.Markdown()

        view_btn.click(fn=load_session, inputs=[session_input], outputs=[session_display])

if __name__ == "__main__":
    demo.launch()
