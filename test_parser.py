from utils.parser import extract_text, read_text_file

def test_resume_and_jd():
    resume_path = "static/sample_resume.docx"  # ✅ Use your actual file name
    jd_path = "static/sample_jd.txt"

    try:
        resume_text = extract_text(resume_path)
        jd_text = read_text_file(jd_path)

        print("\n📄 RESUME TEXT (First 300 chars):\n")
        print(resume_text[:300])

        print("\n📝 JOB DESCRIPTION TEXT (First 300 chars):\n")
        print(jd_text[:300])

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    test_resume_and_jd()
