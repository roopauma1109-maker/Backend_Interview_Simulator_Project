from fastapi import FastAPI
from retriever import retrieve
from prompt_engine import build_prompt
from citations import format_citations
from admin import refresh_database

app = FastAPI()

@app.get("/ask")

def ask(query: str):

    retrieved_docs = retrieve(query)

    if not retrieved_docs:

        return {
            "answer": "No relevant answer found.",
            "citations": []
        }

    prompt = build_prompt(
        query,
        retrieved_docs
    )

    # Temporary AI response
    answer = retrieved_docs[0]["answer"]

    citations = format_citations(
        retrieved_docs
    )

    return {
        "question": query,
        "answer": answer,
        "prompt": prompt,
        "citations": citations
    }


@app.post("/refresh")

def refresh():

    return refresh_database()