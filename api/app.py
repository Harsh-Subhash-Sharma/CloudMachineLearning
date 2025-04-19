import sys
import os
sys.path.append(os.path.abspath('..'))

from chalice import Chalice, Response
from utils.parser import extract_text
from utils.skills_extractor import extract_keywords_from_resume_and_jd
from utils.question_retriever import get_final_question_set
from utils.feedback import get_feedback_from_gpt
from utils.whisper_transcriber import transcribe_audio_local
from utils.voice_analyzer import analyze_voice_confidence
from utils.translate import translate_text
from utils.polly import synthesize_speech
from utils import dynamo

app = Chalice(app_name='interview-bot-api')


@app.route('/')
def index():
    return {'message': 'Interview Bot API is live 🎯'}


@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    request = app.current_request
    body = request.json_body
    return {'text': extract_text(body['filename'])}


@app.route('/extract-skills', methods=['POST'])
def extract_skills():
    req = app.current_request.json_body
    resume = req['resume']
    jd = req['job_description']
    return {'skills': extract_keywords_from_resume_and_jd(resume, jd)}


@app.route('/get-questions', methods=['POST'])
def get_questions():
    req = app.current_request.json_body
    return {'questions': get_final_question_set(req['skills'])}



@app.route('/get-feedback', methods=['POST'])
def get_feedback():
    req = app.current_request.json_body
    questions = req.get("questions", [])
    answers = req.get("answers", [])
    language = req.get("language", "us")  # Default fallback to English
    return {'feedback': get_feedback_from_gpt(questions, answers, language)}



@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    req = app.current_request.json_body
    return {'text': transcribe_audio_local(req['audio_path'], req['language'])}


@app.route('/voice-confidence', methods=['POST'])
def voice_confidence():
    req = app.current_request.json_body
    return {'confidence': analyze_voice_confidence(req['audio_path'])}


@app.route('/speak-question', methods=['POST'])
def speak_question():
    req = app.current_request.json_body
    return {'audio_path': synthesize_speech(req['text'])}


@app.route('/translate', methods=['POST'])
def translate():
    req = app.current_request.json_body
    return {'text': translate_text(req['text'], req['target_language'])}


@app.route('/save-session', methods=['POST'])
def save_session():
    req = app.current_request.json_body
    sid = dynamo.save_session(
        req['resume_text'], req['jd_text'], req['skills'],
        req['questions'], req['answers'], req['feedback'],
        req['language']
    )
    return {'session_id': sid}


@app.route('/get-session/{session_id}')
def get_session(session_id):
    return dynamo.get_session(session_id)
