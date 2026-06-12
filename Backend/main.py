from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import os

app = FastAPI(title="AI Interview Simulator API")

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
# LOAD QUESTIONS
# =========================
# =========================
# LOAD QUESTIONS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go outside Backend folder
PROJECT_DIR = os.path.dirname(BASE_DIR)

# Your file is inside Data/questions.json
DATA_PATH = os.path.join(
    PROJECT_DIR,
    "Data",
    "questions.json"
)

print("📂 Loading from:", DATA_PATH)

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        QUESTIONS = json.load(f)

    print(f"✅ Questions loaded: {len(QUESTIONS)}")

except Exception as e:
    print(f"❌ Error loading questions: {e}")
    QUESTIONS = []

# =========================
# SESSION STORE
# =========================
SESSIONS = {}

# =========================
# HELPERS
# =========================
def match_topic(q_topic, user_topic):
    if not q_topic or not user_topic:
        return False
    q = q_topic.lower().strip()
    u = user_topic.lower().strip()
    return q == u or q in u or u in q

def score_answer(user_answer: str, question: dict) -> dict:
    """Score based on keyword matching and return detailed feedback."""
    keywords = question.get("keywords", [])
    correct_answer = question.get("answer", "")
    user_lower = user_answer.lower()

    matched = [k for k in keywords if k.lower() in user_lower]
    missed = [k for k in keywords if k.lower() not in user_lower]

    if not keywords:
        score = 50
    else:
        score = int((len(matched) / len(keywords)) * 100)

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
# ROUTES
# =========================
@app.get("/")
def home():
    return {
        "status": "running",
        "questions_loaded": len(QUESTIONS),
        "topics": list(set(q["topic"] for q in QUESTIONS))
    }

@app.get("/topics")
def get_topics():
    topics = {}
    for q in QUESTIONS:
        t = q["topic"]
        if t not in topics:
            topics[t] = {"easy": 0, "medium": 0, "hard": 0}
        d = q.get("difficulty", "easy")
        if d in topics[t]:
            topics[t][d] += 1
    return {"status": "success", "topics": topics}

@app.get("/questions/{topic}")
def get_questions(topic: str, difficulty: str = None):
    filtered = [q for q in QUESTIONS if match_topic(q.get("topic", ""), topic)]
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty", "").lower() == difficulty.lower()]
    return {"status": "success", "count": len(filtered), "data": filtered}

@app.get("/interview/start")
def start_interview(topic: str, difficulty: str = "easy", num_questions: int = 5):
    filtered = [
        q for q in QUESTIONS
        if match_topic(q.get("topic", ""), topic)
        and q.get("difficulty", "").lower() == difficulty.lower()
    ]

    if not filtered:
        return {
            "status": "error",
            "message": f"No questions found for topic '{topic}' with difficulty '{difficulty}'. Try a different combination."
        }

    random.shuffle(filtered)
    selected = filtered[:min(num_questions, len(filtered))]

    session_id = str(random.randint(10000, 99999))
    SESSIONS[session_id] = {
        "index": 0,
        "questions": selected,
        "total_score": 0,
        "answers": [],
        "topic": topic,
        "difficulty": difficulty
    }

    return {
        "status": "success",
        "session_id": session_id,
        "total_questions": len(selected),
        "question": selected[0],
        "question_number": 1
    }

@app.get("/interview/next/{session_id}")
def next_question(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        return {"status": "error", "message": "Invalid session ID"}

    session["index"] += 1

    if session["index"] >= len(session["questions"]):
        avg = session["total_score"] // max(len(session["answers"]), 1)
        return {
            "status": "completed",
            "total_score": session["total_score"],
            "average_score": avg,
            "answers": session["answers"],
            "total_questions": len(session["questions"])
        }

    return {
        "status": "success",
        "question": session["questions"][session["index"]],
        "question_number": session["index"] + 1,
        "total_questions": len(session["questions"])
    }

@app.post("/interview/answer/{session_id}")
def submit_answer(session_id: str, data: dict):
    session = SESSIONS.get(session_id)
    if not session:
        return {"status": "error", "message": "Invalid session ID"}

    answer = data.get("answer", "").strip()
    if not answer:
        return {"status": "error", "message": "Answer cannot be empty"}

    q = session["questions"][session["index"]]
    result = score_answer(answer, q)

    session["total_score"] += result["score"]
    session["answers"].append({
        "question": q["question"],
        "user_answer": answer,
        "score": result["score"],
        "grade": result["grade"],
        "matched_keywords": result["matched_keywords"],
        "missed_keywords": result["missed_keywords"],
        "model_answer": result["model_answer"]
    })

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

@app.get("/interview/result/{session_id}")
def result(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        return {"status": "error", "message": "Invalid session ID"}
    avg = session["total_score"] // max(len(session["answers"]), 1)
    return {
        "status": "success",
        "topic": session["topic"],
        "difficulty": session["difficulty"],
        "total_score": session["total_score"],
        "average_score": avg,
        "answers": session["answers"],
        "total_questions": len(session["questions"])
    }