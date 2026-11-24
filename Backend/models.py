
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False, index=True)
    question = Column(Text, nullable=False)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String)
    topic = Column(String)
    question = Column(Text)
    answer = Column(Text)
    feedback = Column(Text)
    timestamp = Column(String)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    topic = Column(String)
    difficulty = Column(String, default="easy")
    total_score = Column(Integer, default=0)
    total_questions = Column(Integer, default=10)
    time_taken = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")

    attempts = relationship(
        "Attempt",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id"),
        nullable=False,
    )
    question_text = Column(Text)
    user_answer = Column(Text)
    is_correct = Column(Boolean)
    question_number = Column(Integer)
    score = Column(Integer, default=0)
    details = Column(Text, nullable=True)

    session = relationship(
        "InterviewSession",
        back_populates="attempts",
    )


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    language = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    verdict = Column(String, nullable=False)

    total_test_cases = Column(Integer, default=0)
    passed_test_cases = Column(Integer, default=0)
    failed_test_cases = Column(Integer, default=0)

    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
