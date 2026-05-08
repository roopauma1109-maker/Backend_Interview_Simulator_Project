from fastapi import FastAPI
import random
import json
import os

app = FastAPI()

file_path = os.path.join(os.path.dirname(__file__), "..", "data", "questions.json")

with open(file_path, "r", encoding="utf-8") as f:
    questions = json.load(f)


@app.get("/")
def home():
    return {"message": "API running"}

@app.get("/get-question")
def get_question():
    all_questions = []

    for category in questions.values():
        all_questions.extend(category)

    return random.choice(all_questions)

def evaluate_answer(user_answer, correct_answer):
    user_words = set(user_answer.lower().split())
    correct_words = set(correct_answer.lower().split())

    matched = user_words.intersection(correct_words)
    score_ratio = len(matched) / len(correct_words) if correct_words else 0

    if score_ratio > 0.6:
        score = 8
        feedback = "Good answer. Most key points are covered."
    elif score_ratio > 0.3:
        score = 5
        feedback = "Partial answer. Some important points are missing."
    else:
        score = 2
        feedback = "Weak answer. Try to include more relevant concepts."

    return score, feedback


@app.post("/submit-answer")
def submit_answer(data: dict):
    user_answer = data.get("user_answer", "")
    correct_answer = data.get("correct_answer", "")

    score, feedback = evaluate_answer(user_answer, correct_answer)

    return {
        "score": score,
        "feedback": feedback 
    }