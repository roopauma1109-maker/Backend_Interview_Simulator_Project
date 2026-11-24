"""
PROPOSED / OPTIONAL — Backend/coach_router.py   (not applied automatically, UNTESTED)

Smallest backend addition that gives the React AI Coach page something to call.
Nothing in your existing code is modified.

To enable it:
  1) pip install groq
  2) set GROQ_API_KEY (and optionally GROQ_MODEL) in the backend's environment
  3) in main.py, after `app = FastAPI(...)`, add:
         from coach_router import router as coach_router
         app.include_router(coach_router)

IMPORTANT: copy the system prompt and model name from your Streamlit AI Coach so behaviour
matches. The values below are placeholders, because that source was not available.
"""
import os
from typing import List, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

SYSTEM_PROMPT = os.getenv(
    "COACH_SYSTEM_PROMPT",
    "You are a helpful, concise interview coach. Give practical advice on answering "
    "technical and behavioural interview questions.",
)


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class CoachRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: List[ChatTurn] = []


@router.post("/coach/chat")
def coach_chat(data: CoachRequest):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="AI Coach is not configured: GROQ_API_KEY is missing on the server.")

    try:
        from groq import Groq
    except ImportError:
        raise HTTPException(status_code=503, detail="The 'groq' package is not installed on the server.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": t.role, "content": t.content} for t in data.history[-10:]]
    messages.append({"role": "user", "content": data.message})

    try:
        completion = Groq(api_key=api_key).chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=0.6,
            max_tokens=700,
        )
    except Exception:
        raise HTTPException(status_code=502, detail="The AI Coach provider request failed. Please try again.")

    return {"status": "success", "reply": completion.choices[0].message.content}
