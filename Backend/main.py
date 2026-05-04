from fastapi import FastAPI
import random
import json

app = FastAPI()

# Load questions
with open("../data/questions.json") as f:
    questions = json.load(f)

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/get-question")
def get_question():
    q = random.choice(questions)
    return q

@app.post("/submit-answer")
def submit_answer(data: dict):
    user_answer = data.get("user_answer", "")
    correct_answer = data.get("correct_answer", "")

    # Basic evaluation (Week 1)
    if user_answer.lower() in correct_answer.lower():
        score = 8
        feedback = "Good answer"
    else:
        score = 4
        feedback = "Needs improvement"

    return {
        "score": score,
        "feedback": feedback
    }