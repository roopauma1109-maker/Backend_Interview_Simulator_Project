# Backend Interview Simulator

## Overview

A simple full-stack application that simulates backend interview practice by serving random questions through an API and displaying them in a UI.

## Tech Stack

* **Backend:** FastAPI (Python)
* **Frontend:** Streamlit
* **Data:** JSON (`questions.json`)
* **API Docs:** Swagger (auto-generated)

## Features

* Random interview question generation via API
* JSON-based question storage
* Lightweight Streamlit UI
* Simple REST endpoint: `GET /get-question`

## How It Works

1. Questions are stored in a JSON file
2. FastAPI backend loads the data
3. `/get-question` returns a random question
4. Streamlit frontend calls the API
5. Question is displayed to the user

## Run Locally

### 1. Start Backend

```
cd Backend
uvicorn main:app --reload
```

### 2. Start Frontend

```
cd Frontend
streamlit run app.py
```

### 3. Open

* API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* UI: [http://localhost:8501](http://localhost:8501)

## API Endpoint

```
GET /get-question
```

### Sample Response

```json
{
  "question": "What is API?",
  "answer": "An API allows communication between systems."
}
```

## Learning Outcomes

* Built REST APIs using FastAPI
* Connected frontend with backend
* Worked with JSON data storage
* Understood client-server interaction

## Future Improvements

* Add answer evaluation
* Add categories/difficulty levels
* Replace JSON with database
* Improve UI/UX

## Author

Roopa
