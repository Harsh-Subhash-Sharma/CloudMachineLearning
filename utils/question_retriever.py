import json
import random

# Load JSON files
def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Match technical questions by skill
def match_technical_questions(skills, dataset):
    matched = []
    for item in dataset:
        if "skills" in item:
            if any(skill.lower() in [s.lower() for s in item["skills"]] for skill in skills):
                matched.append(item)
    return random.sample(matched, min(3, len(matched)))

# Pick 1 random behavioral & 1 situational
def get_random_question(dataset):
    return random.choice(dataset)

def get_final_question_set(skills):
    # Load all datasets
    technical_qna = load_dataset("data/technical_qna.json")
    behavioral_qna = load_dataset("data/behavioral_qna.json")
    situational_qna = load_dataset("data/situational_qna.json")

    tech_qs = match_technical_questions(skills, technical_qna)
    beh_q = get_random_question(behavioral_qna)
    sit_q = get_random_question(situational_qna)

    final_set = tech_qs + [beh_q, sit_q]
    return final_set
