import json
import os

# ==================================================
# LOAD QUESTIONS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(
    PROJECT_DIR,
    "data",
    "questions.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:

    QUESTIONS_DATA = json.load(f)

# ==================================================
# RETRIEVE FUNCTION
# ==================================================

def retrieve(query):

    query_words = set(
        query.lower().split()
    )

    results = []

    for item in QUESTIONS_DATA:

        combined_text = (

            item.get("question", "") + " " +

            item.get("answer", "") + " " +

            " ".join(
                item.get("keywords", [])
            )

        ).lower()

        text_words = set(
            combined_text.split()
        )

        score = len(
            query_words.intersection(
                text_words
            )
        )

        if score > 0:

            results.append({
                "score": score,
                "data": item
            })

    # SORT BEST MATCHES

    results = sorted(

        results,

        key=lambda x: x["score"],

        reverse=True
    )

    return [
        r["data"]
        for r in results[:5]
    ]