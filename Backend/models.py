from sqlalchemy import Column, Integer, String, Text
from database import Base

class Question(Base):

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    role = Column(String, index=True)

    question = Column(Text) 