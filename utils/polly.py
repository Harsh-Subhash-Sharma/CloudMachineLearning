import boto3
import os
from dotenv import load_dotenv

load_dotenv()

polly = boto3.client("polly", region_name=os.getenv("AWS_REGION"))

def synthesize_speech(text, output_path="static/speech.mp3", voice="Joanna"):
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice  # You can change this to "Matthew", "Amy", etc.
        )

        with open(output_path, "wb") as f:
            f.write(response["AudioStream"].read())

        return output_path

    except Exception as e:
        print(f"❌ Polly Error: {e}")
        return None
