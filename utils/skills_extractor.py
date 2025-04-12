import boto3
import os
from dotenv import load_dotenv

load_dotenv()  # Load AWS credentials and region from .env

comprehend = boto3.client("comprehend", region_name=os.getenv("AWS_REGION"))

def extract_entities(text):
    if len(text) > 4800:
        text = text[:4800]  # Comprehend limit is 5000 bytes

    response = comprehend.detect_entities(
        Text=text,
        LanguageCode="en"
    )

    entities = response["Entities"]
    results = []

    for ent in entities:
        if ent["Type"] in ["OTHER", "ORGANIZATION", "TITLE"]:
            results.append(ent["Text"])

    return list(set(results))  # Remove duplicates

def extract_keywords_from_resume_and_jd(resume_text, jd_text):
    resume_entities = extract_entities(resume_text)
    jd_entities = extract_entities(jd_text)

    combined = list(set(resume_entities + jd_entities))
    return combined
