from utils.parser import extract_text, read_text_file
from utils.skills_extractor import extract_keywords_from_resume_and_jd

resume_path = "static/sample_resume.docx"
jd_path = "static/sample_jd.txt"

resume_text = extract_text(resume_path)
jd_text = read_text_file(jd_path)

skills = extract_keywords_from_resume_and_jd(resume_text, jd_text)

print("\n🧠 Extracted Skills / Entities:\n")
for skill in skills:
    print("-", skill)
