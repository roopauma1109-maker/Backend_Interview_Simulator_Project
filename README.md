# 📘 Backend Interview Simulator – Week 3

## 📌 Overview
Backend Interview Simulator is a full-stack interview practice system designed to simulate backend interview scenarios. In Week 3, it is upgraded into a RAG-powered intelligent system with embedding-based retrieval, category support, and improved frontend-backend interaction.

## 🏗️ Architecture
JSON/Dataset → Embedding Layer (Sentence Transformers) → RAG Retrieval System → FastAPI Backend (REST API) → Streamlit Frontend → UI

## ⚙️ Tech Stack
- FastAPI (Python)
- Streamlit
- Sentence Transformers (Embeddings)
- JSON Data Storage
- Swagger UI (/docs)
- REST + RAG Pipeline

## 🚀 Features (Week 3)
- Embedding-based question retrieval
- Category filtering (DBMS, OS, CN, etc.)
- RAG-based intelligent selection
- FastAPI REST endpoints
- Real-time Streamlit UI
- Improved response relevance

## 🔄 System Flow
Questions stored in JSON → Embeddings generated → User request from UI → FastAPI processes → RAG retrieves relevant question → Response sent → UI displays result

## 📡 API Endpoints
GET /get-question  
GET /get-question?category=DBMS  

## ▶️ How to Run

### Backend
cd Backend  
uvicorn main:app --reload  

http://127.0.0.1:8000  
http://127.0.0.1:8000/docs  

### Frontend
cd Frontend  
streamlit run app.py  

http://localhost:8501  

## 🧪 Sample Output

Question: What is normalization in DBMS?  
Answer: Normalization is the process of organizing data to reduce redundancy and improve integrity.

## 🧠 Key Learnings
- RAG systems
- Embedding similarity search
- FastAPI backend design
- API integration with frontend
- Intelligent retrieval systems

## 📊 Progress
Week 2: Random API-based questions  
Week 3: Intelligent RAG-based retrieval system  

## 👨‍💻 Author
Roopa