def generate_feedback(answer):

    answer = answer.strip()

    # Empty answer check
    if not answer:
        return "Please provide an answer."

    # Short answer check
    if len(answer) < 20:
        return """
Your answer is too short.

Suggestions:
- Explain the concept clearly
- Add technical details
- Include examples if possible
"""

    # Good answer feedback
    return f"""
Good attempt.

Your answer:
{answer}

Suggestions for improvement:
- Add more technical explanation
- Include real-world examples
- Mention advantages and disadvantages
- Explain important concepts in detail

Overall:
Your answer shows basic understanding of the topic.
"""