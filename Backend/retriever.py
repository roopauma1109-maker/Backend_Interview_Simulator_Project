import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Correct file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "../Data/questions.json"
)

# Load JSON data
with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

documents = []
all_questions = []

# Flatten category-wise questions
for category, questions in raw_data.items():

    for item in questions:

        question = item.get("question", "")
        answer = item.get("answer", "")

        combined_text = question + " " + answer

        documents.append(combined_text)

        all_questions.append({
            "category": category,
            "question": question,
            "answer": answer
        })

# Create embeddings
embeddings = model.encode(documents)

# Convert embeddings to float32 for FAISS
embeddings = np.array(
    embeddings,
    dtype="float32"
)

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

# Retrieval function
def retrieve(query, top_k=1):

    # Create query embedding
    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding,
        dtype="float32"
    )

    # Search FAISS index
    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for idx in indices[0]:

        # Prevent invalid index errors
        if idx < len(all_questions):

            results.append(
                all_questions[idx]
            )

    return results