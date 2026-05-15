import streamlit as st
import requests
from datetime import datetime
import json
import os

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Backend Interview Simulator",
    layout="centered"
)

# ==================================================
# LOGIN SYSTEM
# ==================================================

USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == USERNAME and password == PASSWORD:

            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

# ==================================================
# MAIN APP
# ==================================================

st.title("Backend Interview Simulator")

# ==================================================
# BACKEND URL
# ==================================================

API_URL = "http://127.0.0.1:8000"

# ==================================================
# CHECK BACKEND CONNECTION
# ==================================================

try:

    response = requests.get(API_URL, timeout=5)

    if response.status_code != 200:

        st.error("Backend server is not responding.")
        st.stop()

except Exception:

    st.error("Backend server is not running.")
    st.stop()

# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==================================================
# GET QUESTION
# ==================================================

if st.button("Get Question"):

    with st.spinner("Generating question..."):

        try:

            response = requests.get(
                f"{API_URL}/get-question",
                timeout=10
            )

            if response.status_code == 200:

                data = response.json()

                question = data.get(
                    "question",
                    "No question found"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": question
                    }
                )

                st.rerun()

            else:

                st.error("Failed to get question.")

        except Exception as e:

            st.error(f"Error: {e}")

# ==================================================
# AI ASSISTANT
# ==================================================

st.subheader("AI Assistant")

query = st.text_input(
    "Ask any backend interview question"
)

if st.button("Ask AI"):

    if query.strip() == "":

        st.warning("Please enter a question.")

    else:

        try:

            response = requests.get(
                f"{API_URL}/ask",
                params={"query": query},
                timeout=10
            )

            if response.status_code == 200:

                data = response.json()

                st.write("### AI Answer")

                st.success(
                    data.get(
                        "answer",
                        "No answer found."
                    )
                )

                st.write("### Citations")

                citations = data.get(
                    "citations",
                    []
                )

                if citations:

                    st.write(citations)

                else:

                    st.info("No citations available.")

            else:

                st.error("Failed to get AI response.")

        except Exception as e:

            st.error(f"Error: {e}")

# ==================================================
# CHAT DISPLAY
# ==================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])

# ==================================================
# USER ANSWER
# ==================================================

user_answer = st.chat_input(
    "Enter your answer"
)

if user_answer:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_answer
        }
    )

    with st.spinner("Evaluating answer..."):

        try:

            payload = {
                "answer": user_answer
            }

            response = requests.post(
                f"{API_URL}/evaluate-answer",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:

                feedback = response.json().get(
                    "feedback",
                    "No feedback received."
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": feedback
                    }
                )

                # SAVE CHAT LOGS

                log_data = {
                    "answer": user_answer,
                    "feedback": feedback,
                    "time": str(datetime.now())
                }

                log_file = "chat_logs.json"

                if not os.path.exists(log_file):

                    with open(log_file, "w") as f:
                        json.dump([], f)

                with open(log_file, "r") as f:

                    logs = json.load(f)

                logs.append(log_data)

                with open(log_file, "w") as f:

                    json.dump(logs, f, indent=4)

            else:

                st.error("Failed to evaluate answer.")

        except Exception as e:

            st.error(f"Error: {e}")

    st.rerun()

# ==================================================
# CLEAR CHAT
# ==================================================

if st.button("Clear Chat"):

    st.session_state.messages = []

    st.rerun()