import boto3
import os
from dotenv import load_dotenv

load_dotenv()

translate_client = boto3.client('translate', region_name=os.getenv("AWS_REGION"))

# Translate text to target language (e.g. en → fr, en → hi)
def translate_text(text, target_lang):
    if target_lang == "en":
        return text  # No need to translate
    try:
        result = translate_client.translate_text(
            Text=text,
            SourceLanguageCode="en",
            TargetLanguageCode=target_lang
        )
        return result.get("TranslatedText")
    except Exception as e:
        print(f"❌ Translate Error: {e}")
        return text

# Translate to English (from uploaded JD/resume)
def translate_to_english(text):
    try:
        result = translate_client.translate_text(
            Text=text,
            SourceLanguageCode="auto",
            TargetLanguageCode="en"
        )
        return result.get("TranslatedText")
    except Exception as e:
        print(f"❌ Translate Error: {e}")
        return text
