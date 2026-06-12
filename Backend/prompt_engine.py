def generate_feedback(user_answer, correct_answer):

    user_answer = user_answer.lower()

    correct_answer = correct_answer.lower()

    user_words = set(
        user_answer.split()
    )

    correct_words = set(
        correct_answer.split()
    )

    common_words = user_words.intersection(
        correct_words
    )

    similarity = len(common_words) / max(
        len(correct_words),
        1
    )

    # ==================================================
    # FEEDBACK
    # ==================================================

    if similarity >= 0.7:

        return f"""
Excellent answer.

You covered most important concepts.

Model Answer:
{correct_answer}
"""

    elif similarity >= 0.4:

        return f"""
Good answer but missing some important points.

Try to explain more clearly with technical details.

Model Answer:
{correct_answer}
"""

    else:

        return f"""
Your answer needs improvement.

Focus on key concepts and technical explanation.

Model Answer:
{correct_answer}
"""