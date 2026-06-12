from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ==================================================
# USER MODEL
# ==================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)

    password = Column(String)

# ==================================================
# CHAT HISTORY
# ==================================================

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    mode = Column(String)

    topic = Column(String)

    question = Column(String)

    answer = Column(String)

    feedback = Column(String)

    timestamp = Column(String)

# ==================================================
# INTERVIEW SESSION
# ==================================================

class InterviewSession(Base):

    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)

    topic = Column(String)

    total_score = Column(Integer, default=0)

    total_questions = Column(Integer, default=10)

    time_taken = Column(Integer, default=0)

    started_at = Column(DateTime, default=datetime.utcnow)

    completed_at = Column(DateTime, nullable=True)

    attempts = relationship(
        "Attempt",
        back_populates="session"
    )

# ==================================================
# ATTEMPTS
# ==================================================

class Attempt(Base):

    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id")
    )

    question_text = Column(String)

    user_answer = Column(String)

    is_correct = Column(Boolean)

    question_number = Column(Integer)

    session = relationship(
        "InterviewSession",
        back_populates="attempts"
    )