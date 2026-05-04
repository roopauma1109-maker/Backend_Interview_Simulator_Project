import streamlit as st
import requests

st.title("Backend Interview Simulator")

if "question" not in st.session_state:
    st.session_state.question = ""
    st.session_state.correct_answer = ""

# Get question
if st.button("Get Question"):
    res = requests.get("http://127.0.0.1:8000/get-question")
    data = res.json()
    st.session_state.question = data["question"]
    st.session_state.correct_answer = data["answer"]

# Display question
if st.session_state.question:
    st.write("Question:", st.session_state.question)

    user_answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):
        res = requests.post(
            "http://127.0.0.1:8000/submit-answer",
            json={
                "user_answer": user_answer,
                "correct_answer": st.session_state.correct_answer
            }
        )

        result = res.json()
        st.write("Score:", result["score"])
        st.write("Feedback:", result["feedback"])