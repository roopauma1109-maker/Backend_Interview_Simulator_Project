import streamlit as st
import requests

st.title("AI Interview Assistant")

query = st.text_input("Ask Interview Question")

if st.button("Submit"):

    response = requests.get(
        "http://127.0.0.1:8000/ask",
        params={"query": query}
    )

    data = response.json()

    st.subheader("Answer")

    st.write(data["answer"])

    st.subheader("Citations")

    for citation in data["citations"]:

        st.write(citation)