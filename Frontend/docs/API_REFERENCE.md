# API integration reference (derived from the uploaded `main.py`)

Base URL: `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`). CORS in `main.py` is `allow_origins=["*"]`, so the Vite dev origin (`http://localhost:5173`) works **without any backend change**; the React app sends no cookies/credentials.

> `main.py` and `main_1.py` were byte-identical. `auth.py` and `Data/questions.json` were not uploaded, so the real topic names are read at runtime from `GET /topics`.

## Endpoints used by the frontend

| Method & path | Request | Success response | Errors |
|---|---|---|---|
| `POST /register` | JSON `{username, password}` (password ≥ 8 chars) | `{status, message, user_id, username}` | 400 empty username / short password, 409 duplicate (`detail`) |
| `POST /login` | JSON `{username, password}` | `{status, message, user_id, username}` | 401 `Invalid username or password.` |
| `GET /` | – | `{status, questions_loaded, topics[]}` | – |
| `GET /topics` | – | `{status, topics: {<name>: {easy, medium, hard}}}` | – |
| `GET /interview/start` | query `topic`, `difficulty` (lowercase), `num_questions` (1–50) | `{status, session_id (string), total_questions, question{topic,difficulty,question,keywords,answer}, question_number:1}` | **HTTP 200** `{status:"error", message}` when no questions match; 400 for bad count |
| `POST /interview/answer/{session_id}` | JSON `{answer}` | `{status, score 0-100, grade, matched_keywords, missed_keywords, model_answer, total_score, questions_answered, total_questions}` | **HTTP 200** `{status:"error", message}` for invalid session / empty answer / finished |
| `GET /interview/next/{session_id}` | – | `{status:"success", question, question_number, total_questions}` or `{status:"completed", total_score, average_score, answers, total_questions}` | HTTP 200 `status:"error"` for invalid session |
| `GET /interview/result/{session_id}` | – | `{status, topic, difficulty, total_score, average_score, answers[], total_questions}` | HTTP 200 `status:"error"` for invalid session |
| `POST /resume/upload` | **query** `user_id`; multipart field **`file`** (PDF ≤ 5 MB) | `{status, message, resume_id, user_id, filename, characters_extracted}` | 404 user not found, 400 not PDF/empty/encrypted/unreadable/no text, 413 too large |
| `POST /resume/questions` | JSON `{user_id, resume_id, num_questions (1–10)}` | `{status, resume_id, detected_skills[], count, questions[{topic,difficulty,question,keywords,answer}]}` | 400, 404 `Resume not found for this user.` |

Each `answers[]` item: `{question, user_answer, score, grade, matched_keywords, missed_keywords, model_answer}`.
`average_score` = integer average of per-question scores (0–100) → used as the percentage.

Handled centrally in `src/services/api.js`: the HTTP-200 `status:"error"` responses are converted into rejected promises, FastAPI `detail` strings/validation arrays are turned into readable messages, and timeouts / network failures get their own messages.

## Findings that affect the UI

1. **No tokens or server sessions.** `/login` returns only `user_id`. The frontend keeps `{user_id, username}` in `localStorage` so refresh doesn't log the user out; this is a convenience, not security (anyone can forge it, and `/resume/*` trusts the `user_id` it is given). Real protection needs a backend change (e.g. signed tokens).
2. **Topic interview sessions are in-memory** (`SESSIONS` dict): lost on backend restart, not linked to a user, 5-digit random ids, never written to the `interview_sessions`/`attempts` tables. There is **no endpoint that lists past sessions**, so "Recent results" can only show the latest session started in this browser tab, and statistics are limited to what `GET /` and `GET /topics` return.
3. **`/interview/next` is not idempotent** (it advances the index on every call). The UI only calls it after an answer is evaluated and guards against double clicks.
4. **No resume-interview session/evaluation endpoint.** `/interview/answer/{id}` works only on sessions made by `/interview/start`. Resume questions carry their own `keywords` and `answer`, so the frontend scores them locally with a direct port of `score_answer()` (`src/services/scoring.js`) and keeps the result in `sessionStorage`. Optional backend improvement: an endpoint that turns the generated questions into a server session.
5. **Answers and keywords are sent to the browser** with every question (`question.answer`, `question.keywords`). The UI never shows them before submission, but they are visible in the network tab.
6. **No "AI feedback".** `main.py` scores by keyword matching. `prompt_engine.generate_feedback()` and `retriever.py` exist but are not imported by `main.py`, so feedback shown is grade + matched/missed keywords + model answer. (`retriever.py` also looks for `data/questions.json`, while `main.py` uses `Data/questions.json` – a case mismatch that breaks on Linux.)
7. **`seed.py` expects `questions.json` to be a dict by role, `main.py` expects a list.** The `questions` table is empty and unused by `main.py`.
8. **AI Coach / Groq: missing.** No Groq code or coach route was in the uploaded files, and the Streamlit source was not provided. The React page calls `POST /coach/chat` with `{message, history:[{role,content}]}` and expects `{reply}`. `docs/coach_router_PROPOSED.py` is an optional, untested router that provides it while keeping the key on the server. Align its prompt/model with your Streamlit coach before using it.
