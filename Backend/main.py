from fastapi import FastAPI
from pydantic import BaseModel

from Backend.retriever import retrieve
from Backend.prompt_engine import generate_feedback
from Backend.citations import format_citations
from Backend.admin import refresh_database

app = FastAPI(
    title="Backend Interview Simulator API"
)


# ---------------- REQUEST MODEL ---------------- #

class AnswerRequest(BaseModel):
    answer: str


# ---------------- GET QUESTION ---------------- #

@app.get("/get-question")
def get_question():

    sample_question = "What is DBMS?"

    return {
        "question": sample_question
    }


# ---------------- EVALUATE ANSWER ---------------- #

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


# ---------------- AI ASSISTANT ---------------- #

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

    # Best retrieved answer
    answer = retrieved_docs[0]["answer"]

    # Generate citations
    citations = format_citations(retrieved_docs)

    return {
        "question": query,
        "answer": answer,
        "citations": citations
    }


# ---------------- REFRESH DATABASE ---------------- #

@app.post("/refresh")
def refresh():

    return refresh_database()


# ---------------- ROOT ENDPOINT ---------------- #

@app.get("/")
def home():

    return {
        "message": "Backend Interview Simulator API Running"
    }