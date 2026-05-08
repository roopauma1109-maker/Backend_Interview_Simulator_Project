def format_citations(retrieved_docs):

    citations = []

    for i, doc in enumerate(retrieved_docs):

        citations.append(
            f"{i+1}. {doc['question']}"
        )

    return citations