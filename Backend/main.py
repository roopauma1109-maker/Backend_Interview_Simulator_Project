from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from retriever import retrieve
from prompt_engine import generate_feedback
from citations import format_citations
from admin import refresh_database

from database import engine, SessionLocal
from models import Base, Question
from crud import get_random_question


# ==================================================
# CREATE DATABASE TABLES
# ==================================================

Base.metadata.create_all(bind=engine)


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="Backend Interview Simulator API"
)


# ==================================================
# DATABASE SESSION
# ==================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==================================================
# REQUEST MODELS
# ==================================================

class AnswerRequest(BaseModel):
    answer: str


class QuestionRequest(BaseModel):
    role: str
    question: str


# ==================================================
# GET RANDOM QUESTION
# ==================================================

@app.get("/get-question")
def fetch_question(
    role: str = "python",
    db: Session = Depends(get_db)
):

    question = get_random_question(
        db,
        role
    )

    if not question:

        return {
            "question": "No questions found."
        }

    return {
        "id": question.id,
        "role": question.role,
        "question": question.question
    }


# ==================================================
# GET ALL ROLES
# ==================================================

@app.get("/roles")
def get_roles(
    db: Session = Depends(get_db)
):

    roles = db.query(
        Question.role
    ).distinct().all()

    return {
        "roles": [r[0] for r in roles]
    }


# ==================================================
# GET ALL QUESTIONS
# ==================================================

@app.get("/all-questions")
def all_questions(
    db: Session = Depends(get_db)
):

    questions = db.query(
        Question
    ).all()

    result = []

    for q in questions:

        result.append({
            "id": q.id,
            "role": q.role,
            "question": q.question
        })

    return result


# ==================================================
# ADD QUESTION
# ==================================================

@app.post("/add-question")
def add_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):

    new_question = Question(
        role=request.role,
        question=request.question
    )

    db.add(new_question)

    db.commit()

    db.refresh(new_question)

    return {
        "message": "Question added successfully",
        "id": new_question.id
    }


# ==================================================
# DELETE QUESTION
# ==================================================

@app.delete("/delete-question/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):

    question = db.query(
        Question
    ).filter(
        Question.id == question_id
    ).first()

    if not question:

        return {
            "message": "Question not found"
        }

    db.delete(question)

    db.commit()

    return {
        "message": "Question deleted successfully"
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

    answer = retrieved_docs[0].get(
        "answer",
        "No answer available."
    )

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