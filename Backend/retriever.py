import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load questions
with open("Data/questions.json", "r") as f:
    data = json.load(f)

documents = []

for item in data:
    documents.append(
        item["question"] + " " + item["answer"]
    )

# Create embeddings
embeddings = model.encode(documents)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

def retrieve(query, top_k=2):

    query_embedding = model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    results = []

    for idx in indices[0]:

        results.append(data[idx])

    return results