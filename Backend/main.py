
from datetime import datetime
from typing import Optional
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from io import BytesIO
from pypdf import PdfReader
from pathlib import Path
import json
import random
import os
import re

from database import Base, SessionLocal, engine
from models import (
    User,
    Question,
    Resume,
    InterviewSession,
    Attempt,
    CodeSubmission,
)
from auth import hash_password, verify_password
from code_runner import router as code_runner_router


# =========================
# DATABASE INITIALIZATION
# =========================

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview Simulator API")

# Coding Arena Docker runner
app.include_router(code_runner_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# LOAD EXISTING QUESTIONS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(
    PROJECT_DIR, "Data", "questions.json"
)

print("Loading questions from:", DATA_PATH)

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        QUESTIONS = json.load(f)

    if not isinstance(QUESTIONS, list):
        raise ValueError(
            "Data/questions.json must contain a list of questions."
        )

    print(f"Questions loaded: {len(QUESTIONS)}")

except Exception as e:
    print(f"Error loading questions: {e}")
    QUESTIONS = []


# =========================
# LOAD INTERMEDIATE QUESTIONS
# =========================

INTERMEDIATE_DATA_PATH = os.path.join(
    PROJECT_DIR, "Data", "intermediate_questions.json"
)

print(
    "Loading intermediate questions from:",
    INTERMEDIATE_DATA_PATH
)

try:
    with open(
        INTERMEDIATE_DATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        INTERMEDIATE_QUESTIONS = json.load(f)

    if not isinstance(INTERMEDIATE_QUESTIONS, list):
        raise ValueError(
            "Data/intermediate_questions.json must contain a list."
        )

    print(
        f"Intermediate questions loaded: "
        f"{len(INTERMEDIATE_QUESTIONS)}"
    )

except Exception as e:
    print(f"Error loading intermediate questions: {e}")
    INTERMEDIATE_QUESTIONS = []


# =========================
# ACTIVE SESSION STORE
# =========================

SESSIONS = {}


# =========================
# REQUEST MODELS
# =========================

class AuthRequest(BaseModel):
    username: str
    password: str


class ResumeQuestionRequest(BaseModel):
    user_id: int
    resume_id: int
    num_questions: int = 5


# =========================
# AUTHENTICATION
# =========================

@app.post("/register")
def register(
    data: AuthRequest,
    db: Session = Depends(get_db)
):
    username = data.username.strip()
    password = data.password

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty."
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters."
        )

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists."
        )

    user = User(
        username=username,
        password=hash_password(password)
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username already exists."
        )

    return {
        "status": "success",
        "message": "Registration successful.",
        "user_id": user.id,
        "username": user.username
    }


@app.post("/login")
def login(
    data: AuthRequest,
    db: Session = Depends(get_db)
):
    username = data.username.strip()

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user or not verify_password(
        data.password, user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    return {
        "status": "success",
        "message": "Login successful.",
        "user_id": user.id,
        "username": user.username
    }


# =========================
# RESUME PDF UPLOAD
# =========================

@app.post("/resume/upload")
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please log in again."
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Upload a PDF resume."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Resume must be smaller than 5 MB."
        )

    try:
        reader = PdfReader(BytesIO(content))

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Password-protected PDFs are not supported."
            )

        extracted_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please upload a valid PDF."
        )

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found. Upload a text-based PDF."
        )

    resume = Resume(
        user_id=user.id,
        filename=Path(file.filename).name,
        extracted_text=extracted_text
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "status": "success",
        "message": "Resume uploaded successfully.",
        "resume_id": resume.id,
        "user_id": user.id,
        "filename": resume.filename,
        "characters_extracted": len(extracted_text)
    }


# =========================
# GET RESUME TEXT
# =========================

@app.get("/resume/{resume_id}")
def get_resume(
    resume_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found for this user."
        )

    return {
        "status": "success",
        "resume_id": resume.id,
        "filename": resume.filename,
        "extracted_text": resume.extracted_text
    }


# =========================
# RESUME-BASED QUESTION GENERATION
# =========================

@app.post("/resume/questions")
def generate_resume_questions(
    data: ResumeQuestionRequest,
    db: Session = Depends(get_db)
):
    if not 1 <= data.num_questions <= 10:
        raise HTTPException(
            status_code=400,
            detail="num_questions must be between 1 and 10."
        )

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == data.resume_id,
            Resume.user_id == data.user_id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found for this user."
        )

    text = resume.extracted_text
    text_lower = text.lower()

    known_skills = [
        "java", "python", "sql", "javascript", "html", "css",
        "react", "fastapi", "spring boot", "machine learning",
        "deep learning", "generative ai", "genai", "llm",
        "rag", "faiss", "langchain", "power bi", "excel",
        "pandas", "numpy", "c", "c++", "data analytics",
        "rest api", "git", "github", "iot", "sqlite",
        "mysql", "mongodb", "oops", "data structures"
    ]

    found_skills = [
        skill for skill in known_skills
        if re.search(
            r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
            text_lower
        )
    ]

    questions = []

    for skill in found_skills:
        questions.append({
            "topic": "Resume",
            "difficulty": "medium",
            "question": (
                f"You mentioned {skill} in your resume. "
                f"Explain how you have used {skill} and describe "
                "one practical example."
            ),
            "keywords": [skill],
            "answer": (
                "Explain the concept, describe your practical usage, "
                "and support it with a specific example from your work."
            )
        })

    if any(word in text_lower for word in [
        "project", "developed", "implemented", "built"
    ]):
        questions.extend([
            {
                "topic": "Resume",
                "difficulty": "medium",
                "question": (
                    "Explain one project from your resume. "
                    "What problem did it solve, and what was your role?"
                ),
                "keywords": ["project", "problem", "role"],
                "answer": (
                    "Describe the problem, your responsibilities, "
                    "the technologies used, and the outcome."
                )
            },
            {
                "topic": "Resume",
                "difficulty": "hard",
                "question": (
                    "What was the most challenging technical issue "
                    "in one of your projects, and how did you solve it?"
                ),
                "keywords": ["challenge", "solution"],
                "answer": (
                    "Explain the issue, your debugging process, "
                    "the solution, and what you learned."
                )
            }
        ])

    if any(word in text_lower for word in [
        "internship", "intern", "experience"
    ]):
        questions.append({
            "topic": "Resume",
            "difficulty": "medium",
            "question": (
                "Describe an important task or learning experience "
                "from your internship or work experience."
            ),
            "keywords": ["task", "experience", "learning"],
            "answer": (
                "Describe your task, your contribution, the tools used, "
                "and the outcome or learning."
            )
        })

    unique_questions = []
    seen = set()

    for question in questions:
        if question["question"] not in seen:
            seen.add(question["question"])
            unique_questions.append(question)

    if not unique_questions:
        unique_questions = [
            {
                "topic": "Resume",
                "difficulty": "easy",
                "question": (
                    "Walk me through your resume and explain "
                    "the skills most relevant to this role."
                ),
                "keywords": ["skills", "experience"],
                "answer": (
                    "Summarize your education, relevant skills, "
                    "projects, and experience."
                )
            },
            {
                "topic": "Resume",
                "difficulty": "medium",
                "question": (
                    "Which achievement in your resume best demonstrates "
                    "your technical ability? Explain why."
                ),
                "keywords": ["achievement", "technical"],
                "answer": (
                    "Describe the achievement, your contribution, "
                    "the skills demonstrated, and the result."
                )
            }
        ]

    random.shuffle(unique_questions)
    selected = unique_questions[:data.num_questions]

    return {
        "status": "success",
        "resume_id": resume.id,
        "detected_skills": found_skills,
        "count": len(selected),
        "questions": selected
    }


# =========================
# EXISTING HELPERS
# =========================

def match_topic(q_topic, user_topic):
    if not q_topic or not user_topic:
        return False

    q = q_topic.lower().strip()
    u = user_topic.lower().strip()

    return q == u or q in u or u in q


def score_answer(user_answer: str, question: dict) -> dict:
    keywords = question.get("keywords", [])
    correct_answer = question.get("answer", "")
    user_lower = user_answer.lower()

    matched = [
        k for k in keywords
        if k.lower() in user_lower
    ]

    missed = [
        k for k in keywords
        if k.lower() not in user_lower
    ]

    if not keywords:
        score = 50
    else:
        score = int(
            (len(matched) / len(keywords)) * 100
        )

    if score >= 80:
        grade = "Excellent"
    elif score >= 60:
        grade = "Good"
    elif score >= 40:
        grade = "Fair"
    else:
        grade = "Needs Improvement"

    return {
        "score": score,
        "grade": grade,
        "matched_keywords": matched,
        "missed_keywords": missed,
        "model_answer": correct_answer
    }


# =========================
# INTERVIEW COMPLETION HELPER
# =========================

def complete_interview_record(
    db: Session,
    session: InterviewSession
):
    if session.completed_at is None:
        session.completed_at = datetime.utcnow()

        if session.started_at:
            elapsed = (
                session.completed_at - session.started_at
            ).total_seconds()

            session.time_taken = max(0, int(elapsed))

        db.commit()
        db.refresh(session)


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "status": "running",
        "questions_loaded": len(QUESTIONS),
        "intermediate_questions_loaded": len(INTERMEDIATE_QUESTIONS),
        "topics": sorted(set(
            q["topic"] for q in QUESTIONS if "topic" in q
        ))
    }


# =========================
# GET TOPICS
# =========================

@app.get("/topics")
def get_topics():
    topics = {}

    for q in QUESTIONS:
        t = q.get("topic")

        if not t:
            continue

        if t not in topics:
            topics[t] = {
                "easy": 0,
                "medium": 0,
                "hard": 0
            }

        difficulty = q.get("difficulty", "easy").lower()

        if difficulty in topics[t]:
            topics[t][difficulty] += 1

    return {
        "status": "success",
        "topics": topics
    }


# =========================
# GET QUESTIONS
# =========================

@app.get("/questions/{topic}")
def get_questions(
    topic: str,
    difficulty: Optional[str] = None
):
    filtered = [
        q for q in QUESTIONS
        if match_topic(q.get("topic", ""), topic)
    ]

    if difficulty:
        filtered = [
            q for q in filtered
            if q.get("difficulty", "").lower()
            == difficulty.lower()
        ]

    return {
        "status": "success",
        "count": len(filtered),
        "data": filtered
    }


# =========================
# INTERMEDIATE TOPICS
# =========================

@app.get("/intermediate/topics")
def get_intermediate_topics():
    topics = {}

    for q in INTERMEDIATE_QUESTIONS:
        topic = q.get("topic")

        if not topic:
            continue

        topics[topic] = topics.get(topic, 0) + 1

    return {
        "status": "success",
        "total_questions": len(INTERMEDIATE_QUESTIONS),
        "topics": topics
    }


# =========================
# INTERMEDIATE QUESTIONS
# =========================

@app.get("/intermediate/questions/{topic}")
def get_intermediate_questions(topic: str):
    filtered = [
        q for q in INTERMEDIATE_QUESTIONS
        if match_topic(q.get("topic", ""), topic)
    ]

    return {
        "status": "success",
        "count": len(filtered),
        "data": filtered
    }


# =========================
# START INTERVIEW
# =========================

@app.get("/interview/start")
def start_interview(
    topic: str,
    difficulty: str = "easy",
    num_questions: int = 5,
    user_id: Optional[int] = None,
    question_level: str = "basic",
    db: Session = Depends(get_db)
):
    if not 1 <= num_questions <= 50:
        raise HTTPException(
            status_code=400,
            detail="num_questions must be between 1 and 50."
        )

    if user_id is not None:
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

    if question_level.lower() == "basic":
        question_bank = QUESTIONS

    elif question_level.lower() == "intermediate":
        question_bank = INTERMEDIATE_QUESTIONS

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid question level. Use basic or intermediate."
        )

    filtered = [
        q for q in question_bank
        if match_topic(q.get("topic", ""), topic)
        and q.get("difficulty", "").lower() == difficulty.lower()
    ]

    if not filtered:
        return {
            "status": "error",
            "message": (
                f"No questions found for topic '{topic}' "
                f"with difficulty '{difficulty}' "
                f"and level '{question_level}'. "
                "Try a different combination."
            )
        }

    random.shuffle(filtered)
    selected = filtered[:min(num_questions, len(filtered))]

    db_session = InterviewSession(
        user_id=user_id,
        topic=topic,
        difficulty=difficulty,
        total_questions=len(selected),
        total_score=0
    )

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    session_id = str(db_session.id)

    SESSIONS[session_id] = {
        "index": 0,
        "questions": selected,
        "total_score": 0,
        "answers": [],
        "topic": topic,
        "difficulty": difficulty,
        "question_level": question_level,
        "db_session_id": db_session.id
    }

    return {
        "status": "success",
        "session_id": session_id,
        "total_questions": len(selected),
        "question_level": question_level,
        "question": selected[0],
        "question_number": 1
    }


# =========================
# NEXT QUESTION
# =========================

@app.get("/interview/next/{session_id}")
def next_question(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = SESSIONS.get(session_id)

    if not session:
        return {
            "status": "error",
            "message": "Invalid session ID or active interview has expired."
        }

    session["index"] += 1

    if session["index"] >= len(session["questions"]):
        db_session = db.query(InterviewSession).filter(
            InterviewSession.id == session["db_session_id"]
        ).first()

        if db_session:
            complete_interview_record(db, db_session)

        average = (
            session["total_score"]
            // max(len(session["answers"]), 1)
        )

        return {
            "status": "completed",
            "total_score": session["total_score"],
            "average_score": average,
            "answers": session["answers"],
            "total_questions": len(session["questions"])
        }

    return {
        "status": "success",
        "question": session["questions"][session["index"]],
        "question_number": session["index"] + 1,
        "total_questions": len(session["questions"])
    }


# =========================
# SUBMIT ANSWER
# =========================

@app.post("/interview/answer/{session_id}")
def submit_answer(
    session_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    session = SESSIONS.get(session_id)

    if not session:
        return {
            "status": "error",
            "message": "Invalid session ID or active interview has expired."
        }

    answer = data.get("answer", "").strip()

    if not answer:
        return {
            "status": "error",
            "message": "Answer cannot be empty"
        }

    if session["index"] >= len(session["questions"]):
        return {
            "status": "error",
            "message": "Interview has already finished"
        }

    q = session["questions"][session["index"]]
    result = score_answer(answer, q)

    session["total_score"] += result["score"]

    answer_record = {
        "question": q["question"],
        "user_answer": answer,
        "score": result["score"],
        "grade": result["grade"],
        "matched_keywords": result["matched_keywords"],
        "missed_keywords": result["missed_keywords"],
        "model_answer": result["model_answer"]
    }

    session["answers"].append(answer_record)

    db_session = db.query(InterviewSession).filter(
        InterviewSession.id == session["db_session_id"]
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found in database."
        )

    attempt = Attempt(
        session_id=db_session.id,
        question_text=q["question"],
        user_answer=answer,
        is_correct=result["score"] >= 60,
        question_number=session["index"] + 1,
        score=result["score"],
        details=json.dumps({
            "grade": result["grade"],
            "matched_keywords": result["matched_keywords"],
            "missed_keywords": result["missed_keywords"],
            "model_answer": result["model_answer"]
        })
    )

    db.add(attempt)

    db_session.total_score = session["total_score"]

    db.commit()

    return {
        "status": "success",
        "score": result["score"],
        "grade": result["grade"],
        "matched_keywords": result["matched_keywords"],
        "missed_keywords": result["missed_keywords"],
        "model_answer": result["model_answer"],
        "total_score": session["total_score"],
        "questions_answered": len(session["answers"]),
        "total_questions": len(session["questions"])
    }


# =========================
# GET INTERVIEW RESULT
# =========================

@app.get("/interview/result/{session_id}")
def result(
    session_id: str,
    db: Session = Depends(get_db)
):
    try:
        db_session_id = int(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID."
        )

    db_session = db.query(InterviewSession).filter(
        InterviewSession.id == db_session_id
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    complete_interview_record(db, db_session)

    attempts = (
        db.query(Attempt)
        .filter(Attempt.session_id == db_session.id)
        .order_by(Attempt.question_number.asc())
        .all()
    )

    answers = []

    for attempt in attempts:
        try:
            details = json.loads(attempt.details or "{}")
        except (TypeError, json.JSONDecodeError):
            details = {}

        answers.append({
            "question": attempt.question_text,
            "user_answer": attempt.user_answer,
            "score": attempt.score or 0,
            "grade": details.get("grade", "Needs Improvement"),
            "matched_keywords": details.get("matched_keywords", []),
            "missed_keywords": details.get("missed_keywords", []),
            "model_answer": details.get("model_answer", "")
        })

    total_score = db_session.total_score or 0
    answered_count = len(answers)

    average = (
        total_score // max(answered_count, 1)
    )

    return {
        "status": "success",
        "topic": db_session.topic,
        "difficulty": db_session.difficulty,
        "total_score": total_score,
        "average_score": average,
        "answers": answers,
        "total_questions": db_session.total_questions
    }


# =========================
# INTERVIEW HISTORY
# =========================

@app.get("/interview/history/{user_id}")
def get_interview_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.started_at.desc())
        .all()
    )

    history = []

    for item in sessions:
        answered_count = (
            db.query(Attempt)
            .filter(Attempt.session_id == item.id)
            .count()
        )

        average = (
            item.total_score // max(answered_count, 1)
        )

        history.append({
            "session_id": item.id,
            "topic": item.topic,
            "difficulty": item.difficulty,
            "total_score": item.total_score or 0,
            "average_score": average,
            "total_questions": item.total_questions,
            "questions_answered": answered_count,
            "time_taken": item.time_taken or 0,
            "started_at": (
                item.started_at.isoformat()
                if item.started_at else None
            ),
            "completed_at": (
                item.completed_at.isoformat()
                if item.completed_at else None
            )
        })

    return {
        "status": "success",
        "count": len(history),
        "history": history
    }


# =========================
# CODING SUBMISSION HISTORY
# =========================

@app.get("/coding/history/{user_id}")
def get_coding_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    submissions = (
        db.query(CodeSubmission)
        .filter(CodeSubmission.user_id == user_id)
        .order_by(CodeSubmission.submitted_at.desc())
        .all()
    )

    history = []

    for item in submissions:
        history.append({
            "id": item.id,
            "language": item.language,
            "code": item.code,
            "verdict": item.verdict,
            "total_test_cases": item.total_test_cases,
            "passed_test_cases": item.passed_test_cases,
            "failed_test_cases": item.failed_test_cases,
            "submitted_at": (
                item.submitted_at.isoformat()
                if item.submitted_at else None
            )
        })

    return {
        "status": "success",
        "count": len(history),
        "history": history
    }
