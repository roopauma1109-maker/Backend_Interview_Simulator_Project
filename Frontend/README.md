# AI Interview Simulator – React frontend

## Run
```bash
# 1. Backend (from Backend/)
uvicorn main:app --reload --port 8000

# 2. Frontend (from Frontend/React-App/)
npm install
npm run dev          # http://localhost:5173
```
`.env` → `VITE_API_BASE_URL=http://127.0.0.1:8000`

Docs: `docs/API_REFERENCE.md` (verified endpoints + backend findings), `docs/coach_router_PROPOSED.py` (optional AI Coach route).

## Manual test checklist
- [ ] Register with a 7-char password → blocked client-side; 8+ chars → success toast, redirected to Login
- [ ] Register the same username again → "Username already exists."
- [ ] Login with wrong password → inline error; correct → Dashboard; refresh keeps you signed in; Logout returns to Login; `/` while signed out redirects to Login
- [ ] Dashboard shows question-bank numbers (stop the backend → warning banner instead)
- [ ] Topic Practice: topics/counts load; pick topic + difficulty + count; Start
- [ ] Submit button disabled when empty; double-click Submit only sends once; score, grade, keywords, model answer appear
- [ ] Next Question until the last, then Finish Interview → Results (totals, percentage, breakdown, insights)
- [ ] "Finish now" mid-interview shows results for answered questions only
- [ ] Restart the backend mid-interview → "session no longer exists" toast and return to setup
- [ ] Resume: non-PDF and >5 MB files rejected; drag-and-drop and click both work; progress bar; success toast
- [ ] Generate questions (1–10) → skills + question list → Start Interview → feedback → Results
- [ ] AI Coach: with no `/coach/chat` route shows the "not available" notice; after adding the router, replies arrive, Enter sends, Shift+Enter newline, auto-scroll, Clear chat
- [ ] Narrow the window below 900px: sidebar becomes a drawer; check layouts at 600px and 375px
- [ ] Enable OS "reduce motion": animations are minimised; no console errors anywhere
