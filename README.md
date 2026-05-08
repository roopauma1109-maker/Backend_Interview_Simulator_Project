# 📘 Backend Interview Simulator – Week 2

## 📌 Overview

The Backend Interview Simulator is a full-stack application designed to help users practice backend interview questions through a simple API-driven system.

In Week 2, the focus is on improving backend structure, introducing API-based question retrieval using FastAPI, and integrating a frontend interface using Streamlit for real-time interaction.

---

## 🏗️ System Architecture

JSON File → FastAPI Backend → REST API (/get-question) → Streamlit Frontend → User Interface

- Questions are stored in a structured JSON file  
- FastAPI serves questions via REST API  
- Streamlit acts as the client UI  
- Frontend fetches data dynamically from backend  

---

## ⚙️ Tech Stack

- Backend: FastAPI (Python)  
- Frontend: Streamlit  
- Data Storage: JSON (questions.json)  
- API Testing: Swagger UI (/docs)  
- Communication: REST API  

---

## 🚀 Features (Week 2 Enhancements)

- Random interview question generation via API  
- Clean RESTful endpoint design  
- JSON-based data management  
- Frontend-backend integration  
- Interactive UI using Streamlit  
- Auto-generated API documentation (Swagger UI)  

---

## 🔄 How It Works

1. Interview questions are stored in questions.json  
2. FastAPI loads and processes the data  
3. API endpoint /get-question returns a random question  
4. Streamlit frontend sends request to backend API  
5. Response is displayed in UI in real-time  

---

## 📡 API Endpoint

GET /get-question

### Sample Response

{
  "question": "What is API?",
  "answer": "An API allows communication between different software systems."
}

---

## ▶️ How to Run Locally

### 1. Start Backend

cd Backend  
uvicorn main:app --reload  

### 2. Start Frontend

cd Frontend  
streamlit run app.py  

---

## 🌐 Access Links

- Backend API: http://127.0.0.1:8000  
- Swagger Docs: http://127.0.0.1:8000/docs  
- Frontend UI: http://localhost:8501  

---

## 🧠 Key Learnings (Week 2)

- Building REST APIs using FastAPI  
- JSON-based data handling  
- API request/response flow  
- Frontend-backend integration  
- Client-server architecture  
- Real-time data fetching using HTTP  

---

## 📈 Week 1 vs Week 2 Improvements

Week 1: Basic backend setup  
Week 2: API-driven system with frontend integration  

- Static execution → Dynamic API system  
- No UI → Streamlit UI added  
- Local logic → Client-server communication  

---

## 🔮 Future Improvements (Week 3)

- Answer evaluation system  
- Category-based questions (DBMS, OS, CN)  
- Difficulty levels (Easy / Medium / Hard)  
- Database integration instead of JSON  
- Score tracking system  
- User session history  

---

## 👨‍💻 Author

Roopa