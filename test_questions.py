from utils.parser import extract_text, read_text_file
from utils.skills_extractor import extract_keywords_from_resume_and_jd
from utils.question_retriever import get_final_question_set

resume_text = extract_text("static/sample_resume.docx")
jd_text = read_text_file("static/sample_jd.txt")

skills = extract_keywords_from_resume_and_jd(resume_text, jd_text)
questions = get_final_question_set(skills)

print("\n🎯 Selected Interview Questions:\n")
for q in questions:
    print(f"[{q['type'].upper()}] {q['question']}\n")
