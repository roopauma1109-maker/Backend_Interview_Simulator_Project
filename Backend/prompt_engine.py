def build_prompt(question, retrieved_docs):

    context = ""

    for doc in retrieved_docs:

        context += f"""
Question: {doc['question']}
Answer: {doc['answer']}

"""

    prompt = f"""
You are an AI Interview Assistant.

Use the context below to answer professionally.

Context:
{context}

User Question:
{question}

Answer:
"""

    return prompt