# 🚀 AI Interview Simulator & AI Assitant

An AI-powered interview preparation platform built using **Python**, **FastAPI**, **Groq API**, and **Llama 3.3 70B**. The application helps students, developers, and job seekers prepare for technical interviews through structured practice sessions and an intelligent AI Coach.

---

# 📖 Overview

AI Interview Simulator provides an interactive environment for practicing technical interview questions across multiple domains while receiving AI-powered guidance and explanations.

The platform combines interview preparation, concept learning, and AI assistance into a single application.

---

# ✨ Features

## 🎯 Interview Practice

* Topic-based interview preparation
* Multiple difficulty levels (Easy, Medium, Hard)
* Configurable number of questions
* Interactive interview sessions
* Structured technical question sets

## 🤖 AI Coach

* Powered by Groq API and Llama 3.3 70B
* Instant technical explanations
* Interview preparation guidance
* Concept clarification
* Real-time AI assistance

## 📚 Supported Topics

* Python
* DBMS
* REST API
* Java
* Operating Systems

## 🎨 Modern User Interface

* Responsive design
* Clean dashboard
* Easy navigation
* User-friendly experience

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn

### Frontend

* HTML
* CSS
* JavaScript

### AI Integration

* Groq API
* Llama 3.3 70B

### Data Storage

* JSON

---

# 📂 Project Structure

```text
Backend_Interview_Simulator_Project/
│
├── Backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env
│
├── Frontend/
│   ├── app.py
│   ├── index.html
│   ├── style.css
│   └── assets/
│
├── data/
│   └── questions.json
│
└── README.md
```

---

# ⚙️ Prerequisites

Before running the application, ensure the following are installed:

* Python 3.10 or later
* pip
* Groq API Key

---

# 📦 Installation

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r Backend/requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file inside the **Backend** directory.

```env
GROQ_API_KEY=your_groq_api_key
```

Replace the value with your actual Groq API key.

---

# ▶️ Running the Backend

Navigate to the Backend folder:

```bash
cd Backend
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend server will run at:

```text
http://127.0.0.1:8000
```

### API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 💻 Running the Frontend

Open a new terminal and navigate to the Frontend folder:

```bash
cd Frontend
```

Run the frontend application:

```bash
streamlit run app.py
```

---

# 🎮 How to Use

## Interview Simulator

1. Launch the application.
2. Select a technical topic.
3. Choose a difficulty level.
4. Select the number of questions.
5. Start the interview session.
6. Answer questions and improve your interview skills.

## AI Coach

1. Open the AI Coach section.
2. Ask any technical question.
3. Receive an AI-generated explanation.
4. Learn concepts and interview strategies.

---

# 📋 Topics Covered

### Python

* Data Types
* Functions
* OOP Concepts
* Decorators
* Exception Handling

### DBMS

* Normalization
* ACID Properties
* SQL Joins
* Transactions
* Indexing

### REST API

* HTTP Methods
* Status Codes
* Authentication
* CRUD Operations

### Java

* Inheritance
* Polymorphism
* Collections Framework
* Exception Handling
* Multithreading

### Operating Systems

* Processes and Threads
* CPU Scheduling
* Deadlocks
* Memory Management
* Synchronization

---

# 📈 Learning Outcomes

This project demonstrates:

* FastAPI Backend Development
* REST API Design
* AI Integration with Groq
* Prompt Engineering
* Full-Stack Development
* JSON Data Handling
* Modern UI/UX Design
* Technical Interview Preparation Systems

---

# 🎯 Future Enhancements

* User Authentication
* Progress Tracking Dashboard
* Interview History
* Performance Analytics
* Resume-Based Question Generation
* Voice-Based Interviews
* Personalized Learning Paths
* Advanced AI Evaluation

---

# 👩‍💻 Author

**Roopa T**

---

