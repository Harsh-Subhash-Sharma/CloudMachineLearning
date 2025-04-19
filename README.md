🧠 AI Interview Bot
A multilingual AI-powered interview bot built using AWS Chalice, OpenAI GPT, Gradio, and AWS Translate, designed to conduct personalized interview sessions, generate feedback, and store session data using DynamoDB.

🌟 Features
📄 Resume and Job Description parsing
🧠 Skill extraction using NLP
❓ Question generation based on extracted skills
🌍 Language translation of questions and feedback
🔊 Voice input (with Whisper support)
🗣️ Feedback with confidence estimation
🧩 Session saving and retrieval via DynamoDB

🧰 Tech Stack
Python 3.12+
AWS Chalice
Gradio
OpenAI API
AWS Services: DynamoDB, Translate, Polly, Whisper (local)
dotenv

Clone the Repository
git clone https://github.com/Harsh-Subhash-Sharma/CloudMachineLearning.git
cd CloudMachineLearning

Create Virtual Environment & Install Dependencies
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt

Setup .env File
Create a .env file in the root directory and add:
OPENAI_API_KEY=your_openai_api_key
AWS_REGION=your_aws_region


🧪 Running the Project

Terminal 1 – Start the Chalice API Server
cd ~/interview-bot
cd api
source ../venv/bin/activate
chalice local --host 0.0.0.0 --port 8000

Terminal 2 – Launch Gradio Frontend
cd ..
source venv/bin/activate
python frontend_ui.py

💾 Session Management
After each interview:
A session ID will be generated (e.g. d2980647-2122-4286-ba22-81973e6a8ce0)
You can use this ID in the "Session Retrieval" tab to reload any past session, including:
Resume and Job Description
Generated Questions
Your Answers
AI Feedback (translated if needed)

