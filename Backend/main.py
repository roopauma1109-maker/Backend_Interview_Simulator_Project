from fastapi import FastAPI
from pydantic import BaseModel

from retriever import retrieve
from prompt_engine import generate_feedback
from citations import format_citations
from admin import refresh_database

import json
import random
import os


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="Backend Interview Simulator API"
)


# ==================================================
# REQUEST MODEL
# ==================================================

class AnswerRequest(BaseModel):
    answer: str


# ==================================================
# GET QUESTION
# ==================================================

@app.get("/get-question")
def get_question():

    try:

        # PROJECT ROOT DIRECTORY
        base_dir = os.path.dirname(
            os.path.dirname(__file__)
        )

        # QUESTIONS FILE PATH
        file_path = os.path.join(
            base_dir,
            "Data",
            "questions.json"
        )

        # LOAD JSON DATA
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # STORE ALL QUESTIONS
        all_questions = []

        # MERGE ALL CATEGORY QUESTIONS
        for category in data.values():

            all_questions.extend(category)

        # CHECK EMPTY
        if not all_questions:

            return {
                "question": "No questions available."
            }

        # RANDOM QUESTION
        random_question = random.choice(
            all_questions
        )

        return {
            "question": random_question.get(
                "question",
                "Question field missing"
            )
        }

    except Exception as e:

        return {
            "question": f"Error: {str(e)}"
        }


# ==================================================
# EVALUATE ANSWER
# ==================================================

@app.post("/evaluate-answer")
def evaluate_answer(request: AnswerRequest):

    answer = request.answer.strip()

    if not answer:

        return {
            "feedback": "Please provide an answer."
        }

    feedback = generate_feedback(answer)

    return {
        "feedback": feedback
    }


# ==================================================
# AI ASSISTANT
# ==================================================

@app.get("/ask")
def ask(query: str):

    query = query.strip()

    if not query:

        return {
            "answer": "Please enter a question.",
            "citations": []
        }

    retrieved_docs = retrieve(query)

    if not retrieved_docs:

        return {
            "answer": "No relevant answer found.",
            "citations": []
        }

    # BEST ANSWER
    answer = retrieved_docs[0].get(
        "answer",
        "No answer available."
    )

    # CITATIONS
    citations = format_citations(
        retrieved_docs
    )

    return {
        "question": query,
        "answer": answer,
        "citations": citations
    }


# ==================================================
# REFRESH DATABASE
# ==================================================

@app.post("/refresh")
def refresh():

    return refresh_database()


# ==================================================
# ROOT ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Backend Interview Simulator API Running"
    }