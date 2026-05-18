import json

from database import SessionLocal, engine
from models import Question, Base


# CREATE TABLES
Base.metadata.create_all(bind=engine)

db = SessionLocal()


with open("../Data/questions.json", "r", encoding="utf-8") as file:

    data = json.load(file)


for role, questions in data.items():

    for q in questions:

        question_text = q.get("question")

        if question_text:

            question = Question(
                role=role,
                question=question_text
            )

            db.add(question)


db.commit()

db.close()

print("Database seeded successfully")