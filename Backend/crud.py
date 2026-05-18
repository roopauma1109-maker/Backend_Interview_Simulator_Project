from sqlalchemy.orm import Session
from models import Question
import random


def get_random_question(
    db: Session,
    role: str
):

    questions = db.query(Question).filter(
        Question.role == role
    ).all()

    if not questions:
        return None

    return random.choice(questions)