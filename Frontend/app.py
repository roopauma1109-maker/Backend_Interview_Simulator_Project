import streamlit as st
import requests
import os

# Load environment variables from a .env file sitting next to this script
# (e.g. Frontend/.env containing GROQ_API_KEY=...)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — GROQ_API_KEY must be set another way

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg: #f6f7fb;
        --surface: #ffffff;
        --surface2: #f3f4f8;
        --surface3: #eceef4;
        --border: #e3e5ee;
        --border2: #d6d9e6;
        --accent: #4f46e5;
        --accent2: #4338ca;
        --accent3: #6366f1;
        --teal: #0d9488;
        --teal2: #0f766e;
        --rose: #e11d48;
        --amber: #b45309;
        --success: #15803d;
        --danger: #dc2626;
        --text: #1c1f2e;
        --muted: #8a8fa3;
        --muted2: #5b5f76;
        --radius: 16px;
        --radius-sm: 10px;
        --glow: 0 4px 24px rgba(79,70,229,0.06);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }

    .stApp {
        background: var(--bg);
        background-image:
            radial-gradient(ellipse 80% 40% at 20% -10%, rgba(79,70,229,0.05) 0%, transparent 70%),
            radial-gradient(ellipse 60% 30% at 80% 110%, rgba(13,148,136,0.04) 0%, transparent 70%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

    .nav-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 22px;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        margin-bottom: 32px;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
    }
    .nav-logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 800;
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 60%, #0d9488 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.3px;
    }
    .nav-tag {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--teal2);
        background: rgba(13,148,136,0.08);
        border: 1px solid rgba(13,148,136,0.25);
        border-radius: 20px;
        padding: 2px 9px;
        margin-left: 10px;
        vertical-align: middle;
    }

    .hero {
        text-align: center;
        padding: 64px 20px 44px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(79,70,229,0.07);
        border: 1px solid rgba(79,70,229,0.22);
        color: var(--accent2);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        padding: 6px 18px;
        border-radius: 20px;
        margin-bottom: 24px;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(38px, 5.5vw, 66px);
        font-weight: 800;
        line-height: 1.08;
        margin-bottom: 20px;
        letter-spacing: -1.5px;
        background: linear-gradient(145deg, #1c1f2e 10%, #4338ca 55%, #0d9488 95%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 16px;
        color: var(--muted2);
        max-width: 480px;
        margin: 0 auto 48px;
        line-height: 1.7;
        font-weight: 400;
    }

    .stat-row {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 44px;
    }
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 28px;
        text-align: center;
        min-width: 100px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent), var(--teal));
        opacity: 0.8;
    }
    .stat-num {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent2), var(--teal2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label {
        font-size: 10px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
        font-weight: 600;
    }

    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 28px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
    }
    .card-accent {
        background: linear-gradient(145deg, #ffffff, #fafbff);
        border: 1px solid var(--border2);
        border-radius: var(--radius);
        padding: 32px;
        margin-bottom: 16px;
        box-shadow: var(--glow);
    }
    .card-glow {
        background: var(--surface);
        border: 1px solid var(--border2);
        border-radius: var(--radius);
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(79,70,229,0.05);
    }

    .question-box {
        background: linear-gradient(145deg, #ffffff, #f7f8fc);
        border: 1px solid var(--border2);
        border-left: 3px solid var(--accent);
        border-radius: var(--radius);
        padding: 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(16,24,40,0.05);
    }
    .question-box::after {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 120px; height: 120px;
        background: radial-gradient(circle, rgba(79,70,229,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .q-number {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--accent2);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .q-number::before {
        content: '';
        display: inline-block;
        width: 20px;
        height: 2px;
        background: var(--accent);
        border-radius: 2px;
    }
    .q-text {
        font-size: 20px;
        font-weight: 500;
        color: var(--text);
        line-height: 1.6;
    }

    .progress-wrap {
        background: var(--surface3);
        border-radius: 20px;
        height: 4px;
        overflow: hidden;
        margin: 18px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, var(--accent), var(--teal));
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .score-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .grade-excellent { background: rgba(21,128,61,0.08); color: #15803d; border: 1px solid rgba(21,128,61,0.25); }
    .grade-good      { background: rgba(79,70,229,0.08); color: #4338ca; border: 1px solid rgba(79,70,229,0.25); }
    .grade-fair      { background: rgba(180,83,9,0.08); color: #b45309; border: 1px solid rgba(180,83,9,0.25); }
    .grade-poor      { background: rgba(220,38,38,0.08); color: #dc2626; border: 1px solid rgba(220,38,38,0.25); }

    .keyword-section { margin: 12px 0; }
    .keyword-label {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 10px;
    }
    .keyword-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        font-family: monospace;
    }
    .chip-hit  { background: rgba(21,128,61,0.07); color: #15803d; border: 1px solid rgba(21,128,61,0.2); }
    .chip-miss { background: rgba(220,38,38,0.06); color: #dc2626; border: 1px solid rgba(220,38,38,0.18); }

    .model-answer {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 20px;
        margin-top: 16px;
    }
    .model-label {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent2);
        margin-bottom: 12px;
    }
    .model-text { font-size: 14px; color: var(--muted2); line-height: 1.7; }

    .result-header {
        text-align: center;
        padding: 48px 20px 36px;
        background: linear-gradient(145deg, #ffffff, #f7f8fc);
        border: 1px solid var(--border2);
        border-radius: var(--radius);
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(16,24,40,0.05);
    }
    .result-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse 60% 60% at 50% 0%, rgba(79,70,229,0.06) 0%, transparent 70%);
        pointer-events: none;
    }
    .result-score {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 90px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 6px;
        letter-spacing: -3px;
    }

    .chat-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 18px 24px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
    }
    .chat-header-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: linear-gradient(135deg, var(--accent), var(--teal));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
        box-shadow: 0 4px 16px rgba(79,70,229,0.22);
    }
    .chat-header-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 17px;
        font-weight: 800;
        color: var(--text);
        margin: 0;
        letter-spacing: -0.3px;
    }
    .chat-header-sub {
        font-size: 12px;
        color: var(--muted);
        margin: 2px 0 0;
    }
    .chat-online {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 7px;
        font-size: 12px;
        color: var(--success);
        font-weight: 600;
    }
    .dot-online {
        width: 7px;
        height: 7px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(21,128,61,0.35); }
        50% { opacity: 0.7; box-shadow: 0 0 0 4px rgba(21,128,61,0); }
    }

    .chat-msg-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
    }
    .chat-msg-ai {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 16px;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #4338ca, #4f46e5);
        color: #fff;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        max-width: 68%;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 4px 16px rgba(79,70,229,0.18);
    }
    .chat-avatar {
        width: 32px;
        height: 32px;
        min-width: 32px;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--accent), var(--teal));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 800;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        margin-top: 2px;
    }
    .chat-bubble-ai {
        background: var(--surface2);
        border: 1px solid var(--border2);
        color: var(--text);
        border-radius: 4px 18px 18px 18px;
        padding: 14px 18px;
        max-width: 82%;
        font-size: 14px;
        line-height: 1.7;
    }
    .chat-bubble-ai code {
        background: var(--surface3);
        border: 1px solid var(--border);
        border-radius: 5px;
        padding: 2px 7px;
        font-family: monospace;
        font-size: 13px;
        color: var(--accent2);
    }
    .chat-bubble-ai pre {
        background: var(--surface3);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px;
        overflow-x: auto;
        margin: 10px 0 0;
    }
    /* AI coach replies render via st.markdown (native Streamlit), so style that
       container directly to guarantee readable, high-contrast text regardless
       of the app's base theme. */
    .ai-reply-wrap {
        background: var(--surface2);
        border: 1px solid var(--border2);
        border-radius: 4px 18px 18px 18px;
        padding: 14px 18px;
        margin-bottom: 16px;
    }
    .ai-reply-wrap p,
    .ai-reply-wrap li,
    .ai-reply-wrap span,
    .ai-reply-wrap div {
        color: #0b0d14 !important;
        font-size: 14px !important;
        line-height: 1.75 !important;
    }
    .ai-reply-wrap strong, .ai-reply-wrap b {
        color: #0b0d14 !important;
        font-weight: 800 !important;
    }
    .ai-reply-wrap code {
        background: var(--surface3) !important;
        border: 1px solid var(--border) !important;
        border-radius: 5px !important;
        padding: 2px 7px !important;
        font-family: monospace !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        color: var(--accent2) !important;
    }
    .ai-reply-wrap pre {
        background: var(--surface3) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 16px !important;
        overflow-x: auto !important;
    }
    .ai-reply-wrap pre code {
        font-weight: 600 !important;
        color: #0b0d14 !important;
    }
    .chat-empty {
        text-align: center;
        padding: 64px 20px 32px;
        color: var(--muted);
    }
    .chat-empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
        filter: drop-shadow(0 4px 14px rgba(79,70,229,0.18));
    }
    .chat-empty-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 800;
        color: var(--text);
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    .chat-empty-sub { font-size: 15px; line-height: 1.65; color: var(--muted2); }

    .chat-input-wrap {
        background: var(--surface);
        border: 1px solid var(--border2);
        border-radius: var(--radius);
        padding: 20px 22px;
        margin-top: 8px;
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
    }
    .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: var(--muted);
        margin-top: 10px;
    }
    .model-dot {
        width: 6px;
        height: 6px;
        background: var(--amber);
        border-radius: 50%;
    }

    .stTextArea textarea {
        background: var(--surface2) !important;
        border: 1px solid var(--border2) !important;
        color: var(--text) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 14px !important;
        resize: vertical !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
        outline: none !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--muted) !important;
    }
    .stSelectbox > div > div {
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius-sm) !important;
    }
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.2px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
        border: none !important;
        color: white !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        box-shadow: 0 4px 14px rgba(79,70,229,0.22) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(79,70,229,0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        background: var(--surface) !important;
        border: 1px solid var(--border2) !important;
        color: var(--muted2) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent) !important;
        color: var(--accent2) !important;
        background: rgba(79,70,229,0.05) !important;
        transform: translateY(-1px) !important;
    }
    .stSlider > div > div { color: var(--accent2) !important; }
    hr { border-color: var(--border) !important; margin: 22px 0 !important; }
    .stAlert { border-radius: var(--radius-sm) !important; }
    .stExpander {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        background: var(--surface) !important;
    }
    .stExpander:hover {
        border-color: var(--border2) !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button { width: 100%; }

    .section-label {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    .config-summary {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 14px 20px;
        margin-bottom: 20px;
        font-size: 13px;
        color: var(--muted2);
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
    }
    .config-summary strong { color: var(--text); }
    .config-sep { color: var(--border2); margin: 0 4px; }
</style>
""", unsafe_allow_html=True)

BASE_URL      = "http://127.0.0.1:8000"
GROQ_API_URL  = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.3-70b-versatile"

TOPIC_META = {
    "python": {"icon": "🐍", "label": "Python"},
    "dbms":   {"icon": "🗄️",  "label": "DBMS"},
    "api":    {"icon": "🔌", "label": "REST API"},
    "java":   {"icon": "☕", "label": "Java"},
    "os":     {"icon": "💻", "label": "OS Concepts"},
}

DIFFICULTY_META = {
    "easy":   {"color": "#15803d", "label": "Easy",   "emoji": "🟢"},
    "medium": {"color": "#b45309", "label": "Medium", "emoji": "🟡"},
    "hard":   {"color": "#dc2626", "label": "Hard",   "emoji": "🔴"},
}

def init_state():
    defaults = {
        "page": "home",
        "session_id": None,
        "current_question": None,
        "question_number": 1,
        "total_questions": 5,
        "last_result": None,
        "answered": False,
        "topic": "python",
        "difficulty": "easy",
        "num_questions": 5,
        "chat_history": [],
        "chat_key": 0,
        "asked_questions": [],
        "session_answers": [],
        "ai_summary": None,
        "ai_summary_key": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def api_get(path, params=None):
    try:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=15)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_post(path, data=None):
    try:
        r = requests.post(f"{BASE_URL}{path}", json=data, timeout=15)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def call_groq(messages: list) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        return "⚠️ GROQ_API_KEY missing"

    last_user_msg = ""
    for m in reversed(messages):
        if m["role"] == "user":
            last_user_msg = m["content"].lower()
            break

    is_definition   = any(w in last_user_msg for w in ["what is", "what are", "define", "explain"])
    is_comparison   = any(w in last_user_msg for w in ["difference", "vs", "compare", "versus"])
    is_howto        = any(w in last_user_msg for w in ["how does", "how do", "how to", "how can"])
    is_list         = any(w in last_user_msg for w in ["list", "types", "examples", "give me"])

    if is_comparison:
        max_tok, length_hint = 350, "2–3 sentences per side in a comparison, no more"
    elif is_definition:
        max_tok, length_hint = 250, "3–4 sentences maximum — definition, key point, one example"
    elif is_howto:
        max_tok, length_hint = 400, "step-by-step but keep each step to 1 sentence; 4–6 steps max"
    elif is_list:
        max_tok, length_hint = 350, "bullet list, each item 1 short sentence, 4–6 items max"
    else:
        max_tok, length_hint = 300, "3–5 sentences, direct and to the point"

    system_msg = {
        "role": "system",
        "content": (
            "You are a sharp technical interview coach for software engineering roles. "
            "Respond concisely — interviewers value clarity over length. "
            f"Length rule for this reply: {length_hint}. "
            "Use markdown: inline `code` for terms, ``` blocks only for code snippets (≤6 lines). "
            "Lead with the direct answer, then one brief example or analogy if it genuinely helps. "
            "No preamble like 'Great question!' — just the answer."
        )
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [system_msg] + messages,
        "max_tokens": max_tok,
        "temperature": 0.5,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# =========================
# GROQ — STRUCTURED JSON HELPERS
# (question generation, answer scoring, model answers, results summary)
# =========================
import json as _json
import re as _re
import html as _html


def _render_ai_markdown(text: str) -> str:
    """Convert the limited markdown the AI coach uses (paragraphs, **bold**,
    `inline code`, ```fenced code```, and simple '-'/'*' bullet lists) into HTML,
    so it can be rendered inside a single styled div for guaranteed contrast.
    """
    if not text:
        return ""

    # Pull out fenced code blocks first so their contents aren't escaped/altered
    blocks = []

    def _stash_code_block(m):
        code = _html.escape(m.group(2).strip())
        blocks.append(f'<pre><code>{code}</code></pre>')
        return f"\x00BLOCK{len(blocks) - 1}\x00"

    text = _re.sub(r"```(\w*)\n(.*?)```", _stash_code_block, text, flags=_re.DOTALL)

    # Escape remaining text, then re-apply simple inline formatting
    escaped = _html.escape(text)
    escaped = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = _re.sub(r"`([^`]+?)`", r"<code>\1</code>", escaped)

    # Render paragraphs and bullet lists
    html_parts = []
    list_buffer = []

    def _flush_list():
        if list_buffer:
            html_parts.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_buffer) + "</ul>")
            list_buffer.clear()

    for para in escaped.split("\n"):
        stripped = para.strip()
        if not stripped:
            _flush_list()
            continue
        if stripped.startswith(("- ", "* ")):
            list_buffer.append(stripped[2:].strip())
        else:
            _flush_list()
            html_parts.append(f"<p>{stripped}</p>")
    _flush_list()

    result = "".join(html_parts) if html_parts else f"<p>{escaped}</p>"

    # Restore stashed code blocks
    for i, block in enumerate(blocks):
        result = result.replace(f"\x00BLOCK{i}\x00", block)

    return result


def _groq_json(system_prompt: str, user_prompt: str, max_tokens: int = 600, temperature: float = 0.4) -> dict:
    """Call Groq and force a JSON object back. Raises on missing key / bad response."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY missing")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt + " Respond ONLY with a valid JSON object — no markdown fences, no preamble, no commentary."},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]

    # Defensive cleanup in case the model still wraps in fences
    cleaned = _re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=_re.MULTILINE).strip()
    return _json.loads(cleaned)


def groq_generate_question(topic: str, difficulty: str, exclude: list = None) -> dict:
    """Ask Groq to write one interview question for the topic/difficulty.
    Returns {"question": str, "keywords": [str, ...]}.
    Used as a fallback when the backend is unreachable or out of questions.
    """
    exclude = exclude or []
    t_label = TOPIC_META.get(topic, {}).get("label", topic)
    system_prompt = (
        "You write technical interview questions for software engineering candidates. "
        "Each question should be answerable in a few sentences, not require a live coding environment."
    )
    user_prompt = (
        f"Write ONE {difficulty}-difficulty interview question about {t_label}. "
        f"Do not repeat any of these previously-asked questions: {exclude}. "
        'Return JSON like {"question": "...", "keywords": ["term1", "term2", "term3"]} '
        "where keywords are 3-6 concepts a strong answer should mention."
    )
    data = _groq_json(system_prompt, user_prompt, max_tokens=300)
    return {
        "question": data.get("question", "Tell me about a core concept in this topic."),
        "keywords": data.get("keywords", []),
    }


def groq_evaluate_answer(question: str, user_answer: str, topic: str, keywords: list = None) -> dict:
    """Ask Groq to grade a free-text interview answer.
    Returns score (0-100), grade, matched_keywords, missed_keywords, model_answer.
    Used as a fallback / alternative to pure keyword-matching scoring.
    """
    t_label = TOPIC_META.get(topic, {}).get("label", topic)
    keyword_hint = f" Reference keywords to check for: {keywords}." if keywords else ""
    system_prompt = (
        "You are a strict but fair technical interviewer grading a candidate's spoken answer "
        f"to a {t_label} question."
    )
    user_prompt = (
        f"Question: {question}\n"
        f"Candidate's answer: {user_answer}\n\n"
        f"Grade this answer.{keyword_hint} "
        'Return JSON exactly like {"score": 0-100 integer, "grade": "Excellent|Good|Fair|Poor", '
        '"matched_keywords": ["..."], "missed_keywords": ["..."], "model_answer": "a concise ideal answer, 2-4 sentences"}'
    )
    data = _groq_json(system_prompt, user_prompt, max_tokens=500)
    return {
        "score": int(data.get("score", 0)),
        "grade": data.get("grade", "Fair"),
        "matched_keywords": data.get("matched_keywords", []),
        "missed_keywords": data.get("missed_keywords", []),
        "model_answer": data.get("model_answer", ""),
    }


def groq_generate_model_answer(question: str, topic: str) -> str:
    """Ask Groq for a clean reference/model answer to a given question."""
    t_label = TOPIC_META.get(topic, {}).get("label", topic)
    system_prompt = f"You write concise, accurate model answers for {t_label} interview questions."
    user_prompt = (
        f"Question: {question}\n"
        'Return JSON like {"model_answer": "..."} with a 2-4 sentence ideal answer.'
    )
    data = _groq_json(system_prompt, user_prompt, max_tokens=250)
    return data.get("model_answer", "")


def groq_generate_summary(topic: str, difficulty: str, answers: list) -> str:
    """Ask Groq for a short personalized takeaway paragraph for the results page."""
    t_label = TOPIC_META.get(topic, {}).get("label", topic)
    condensed = [
        {
            "question": a.get("question", ""),
            "score": a.get("score", 0),
            "missed_keywords": a.get("missed_keywords", []),
        }
        for a in answers
    ]
    system_prompt = (
        "You are an encouraging but honest technical interview coach summarizing a practice session."
    )
    user_prompt = (
        f"Topic: {t_label}, Difficulty: {difficulty}. Per-question results: {condensed}\n\n"
        'Return JSON like {"summary": "..."} with a 3-5 sentence personalized takeaway: '
        "call out a clear strength, the single most important gap to fix next, and one concrete next step."
    )
    data = _groq_json(system_prompt, user_prompt, max_tokens=300)
    return data.get("summary", "")


def grade_class(grade):
    g = grade.lower()
    if "excellent" in g: return "grade-excellent"
    if "good" in g:      return "grade-good"
    if "fair" in g:      return "grade-fair"
    return "grade-poor"

def score_color(score):
    if score >= 80: return "#15803d"
    if score >= 60: return "#4338ca"
    if score >= 40: return "#b45309"
    return "#dc2626"

def score_emoji(score):
    if score >= 80: return "🏆"
    if score >= 60: return "👍"
    if score >= 40: return "💪"
    return "📚"

def render_nav():
    current = st.session_state.get("page", "home")
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        st.markdown(
            '<div class="nav-logo">🎯 InterviewAI <span class="nav-tag">BETA</span></div>',
            unsafe_allow_html=True
        )
    with c2:
        on_interview = current in ("home", "interview", "result")
        if st.button("🏠 Practice", key="nav_practice",
                     type="primary" if on_interview else "secondary",
                     use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with c3:
        on_chat = current == "chat"
        if st.button("💬 AI Coach", key="nav_chat",
                     type="primary" if on_chat else "secondary",
                     use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

def page_home():
    render_nav()

    st.markdown("""
    <div class="hero">
        <div class="hero-badge">✦ AI-Powered Interview Prep</div>
        <div class="hero-title">Ace Your Technical<br>Interview</div>
        <div class="hero-sub">
            Practice with curated questions, get instant AI feedback,
            and pinpoint exactly what to improve — topic by topic.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stat-row">
        <div class="stat-card"><div class="stat-num">25+</div><div class="stat-label">Questions</div></div>
        <div class="stat-card"><div class="stat-num">5</div><div class="stat-label">Topics</div></div>
        <div class="stat-card"><div class="stat-num">3</div><div class="stat-label">Levels</div></div>
        <div class="stat-card"><div class="stat-num">AI</div><div class="stat-label">Feedback</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-accent">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Configure Your Session</div>', unsafe_allow_html=True)

    st.markdown("**Select Topic**")
    topic_cols = st.columns(5)
    for i, (key, meta) in enumerate(TOPIC_META.items()):
        with topic_cols[i]:
            selected = st.session_state.topic == key
            if st.button(
                f"{meta['icon']} {meta['label']}",
                key=f"topic_{key}",
                type="primary" if selected else "secondary",
                use_container_width=True
            ):
                st.session_state.topic = key
                st.rerun()

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        diff = st.selectbox(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            format_func=lambda x: f"{DIFFICULTY_META[x]['emoji']} {DIFFICULTY_META[x]['label']}",
            index=["easy", "medium", "hard"].index(st.session_state.difficulty)
        )
        st.session_state.difficulty = diff
    with col2:
        num_q = st.slider("Number of Questions", min_value=3, max_value=10,
                          value=st.session_state.num_questions)
        st.session_state.num_questions = num_q

    st.markdown("")
    t_meta = TOPIC_META.get(st.session_state.topic, {"icon": "📚", "label": st.session_state.topic})
    d_meta = DIFFICULTY_META.get(st.session_state.difficulty, {"emoji": "⚪", "label": st.session_state.difficulty})
    st.markdown(f"""
    <div class="config-summary">
        Ready to start:
        <strong>{t_meta['icon']} {t_meta['label']}</strong>
        <span class="config-sep">·</span>
        <strong>{d_meta['emoji']} {d_meta['label']}</strong>
        <span class="config-sep">·</span>
        <strong>{num_q} Questions</strong>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        with st.spinner("Setting up your interview..."):
            resp = api_get("/interview/start", {
                "topic": st.session_state.topic,
                "difficulty": st.session_state.difficulty,
                "num_questions": st.session_state.num_questions
            })
        if resp.get("status") == "error":
            # Backend unreachable — fall back to a Groq-generated interview session
            with st.spinner("Backend unavailable, generating questions with AI..."):
                try:
                    q_data = groq_generate_question(st.session_state.topic, st.session_state.difficulty)
                    st.session_state.session_id       = "groq-local"
                    st.session_state.current_question = {
                        "question": q_data["question"],
                        "keywords": q_data["keywords"],
                    }
                    st.session_state.question_number  = 1
                    st.session_state.total_questions  = st.session_state.num_questions
                    st.session_state.answered         = False
                    st.session_state.last_result       = None
                    st.session_state.asked_questions  = [q_data["question"]]
                    st.session_state.session_answers  = []
                    st.session_state.ai_summary       = None
                    st.session_state.ai_summary_key   = None
                    st.session_state.page             = "interview"
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Backend error and AI fallback failed: {e}")
        else:
            st.session_state.session_id       = resp["session_id"]
            st.session_state.current_question = resp["question"]
            st.session_state.question_number  = 1
            st.session_state.total_questions  = resp["total_questions"]
            st.session_state.answered         = False
            st.session_state.last_result      = None
            st.session_state.page             = "interview"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <div style="text-align:center;margin-top:12px;">
        <span style="font-size:13px;color:#8a8fa3;">
            💬 Want to study a concept first?
        </span>
    </div>
    """, unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        if st.button("Open AI Coach →", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

def page_interview():
    render_nav()

    if not st.session_state.current_question:
        st.error("No active interview. Please start from Home.")
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    q      = st.session_state.current_question
    q_num  = st.session_state.question_number
    total  = st.session_state.total_questions
    t_meta = TOPIC_META.get(st.session_state.topic, {"icon": "📚", "label": "Interview"})
    d_meta = DIFFICULTY_META.get(st.session_state.difficulty, {"emoji": "⚪", "label": "Medium"})
    pct    = int((q_num - 1) / total * 100)

    hc1, hc2, hc3 = st.columns([2, 2, 1])
    with hc1:
        st.markdown(f"""
        <div style="font-size:13px;color:#8a8fa3;font-weight:600;letter-spacing:0.3px;">
            {t_meta['icon']} {t_meta['label']} &nbsp;·&nbsp; {d_meta['emoji']} {d_meta['label']}
        </div>
        """, unsafe_allow_html=True)
    with hc2:
        st.markdown(f"""
        <div class="progress-wrap">
            <div class="progress-fill" style="width:{pct}%"></div>
        </div>
        """, unsafe_allow_html=True)
    with hc3:
        st.markdown(f"""
        <div style="text-align:right;font-size:13px;font-weight:700;color:#4338ca;letter-spacing:0.5px;">
            {q_num} / {total}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    ai_tag = ' <span class="nav-tag" style="margin-left:8px;">AI GENERATED</span>' if st.session_state.session_id == "groq-local" else ""
    st.markdown(f"""
    <div class="question-box">
        <div class="q-number">Question {q_num} of {total}{ai_tag}</div>
        <div class="q-text">{q.get('question', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.answered:
        answer = st.text_area(
            "Your Answer",
            placeholder="Type your answer here — mention key terms and concepts...",
            height=150,
            key=f"ans_{q_num}",
            label_visibility="collapsed"
        )
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                if not answer or not answer.strip():
                    st.warning("Please write an answer before submitting.")
                else:
                    with st.spinner("Evaluating your answer..."):
                        if st.session_state.session_id == "groq-local":
                            try:
                                result = groq_evaluate_answer(
                                    q.get("question", ""), answer, st.session_state.topic,
                                    keywords=q.get("keywords")
                                )
                            except Exception as e:
                                result = {"status": "error", "message": str(e)}
                        else:
                            result = api_post(f"/interview/answer/{st.session_state.session_id}",
                                              {"answer": answer})
                            if result.get("status") == "error":
                                # Backend hiccup mid-session — fall back to Groq grading
                                try:
                                    result = groq_evaluate_answer(
                                        q.get("question", ""), answer, st.session_state.topic
                                    )
                                except Exception as e:
                                    result = {"status": "error", "message": str(e)}
                    st.session_state.last_result = result
                    st.session_state.answered    = True
                    if st.session_state.session_id == "groq-local" and "score" in result:
                        st.session_state.session_answers.append({
                            "question": q.get("question", ""),
                            "user_answer": answer,
                            **result,
                        })
                    st.rerun()
        with col2:
            if st.button("⏭ Skip", use_container_width=True):
                if st.session_state.session_id != "groq-local":
                    api_post(f"/interview/answer/{st.session_state.session_id}", {"answer": "skipped"})
                st.session_state.answered    = True
                st.session_state.last_result = None
                st.rerun()

    if st.session_state.answered and st.session_state.last_result:
        result       = st.session_state.last_result
        score        = result.get("score", 0)
        grade        = result.get("grade", "")
        matched      = result.get("matched_keywords", [])
        missed       = result.get("missed_keywords", [])
        model_answer = result.get("model_answer", "")
        if not model_answer:
            # Backend didn't supply a model answer — generate one with Groq
            try:
                model_answer = groq_generate_model_answer(q.get("question", ""), st.session_state.topic)
            except Exception:
                model_answer = "Model answer unavailable."

        st.markdown("<br>", unsafe_allow_html=True)
        fc1, fc2 = st.columns([1, 2])

        with fc1:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:32px 20px;">
                <div style="font-size:9px;color:#8a8fa3;margin-bottom:10px;
                            letter-spacing:2px;text-transform:uppercase;font-weight:700;">Your Score</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:58px;
                            font-weight:800;color:{score_color(score)};line-height:1;letter-spacing:-2px;">
                    {score}
                </div>
                <div style="font-size:14px;color:#8a8fa3;margin-bottom:16px;">/100</div>
                <div style="font-size:28px;margin:8px 0;">{score_emoji(score)}</div>
                <span class="score-badge {grade_class(grade)}">{grade}</span>
            </div>
            """, unsafe_allow_html=True)

        with fc2:
            matched_chips = " ".join([f'<span class="chip chip-hit">✓ {k}</span>' for k in matched]) \
                if matched else '<span style="color:#8a8fa3;font-size:13px;">None matched</span>'
            missed_chips  = " ".join([f'<span class="chip chip-miss">✗ {k}</span>' for k in missed]) \
                if missed else '<span style="color:#15803d;font-size:13px;">All keywords covered! 🎉</span>'

            st.markdown(f"""
            <div class="card-glow" style="padding:22px;">
                <div class="keyword-section">
                    <div class="keyword-label">✅ Keywords You Mentioned</div>
                    <div class="keyword-row">{matched_chips}</div>
                </div>
                <div class="keyword-section" style="margin-top:20px;">
                    <div class="keyword-label">💡 Keywords to Include</div>
                    <div class="keyword-row">{missed_chips}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("📖 View Model Answer"):
            st.markdown(f"""
            <div style="background:#f3f4f8;border-radius:10px;padding:20px;
                        color:#5b5f76;line-height:1.75;font-size:14px;">
                {model_answer}
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.answered:
        st.markdown("")
        is_last   = st.session_state.question_number >= st.session_state.total_questions
        btn_label = "🏁 View Results" if is_last else "Next Question →"

        if st.button(btn_label, type="primary", use_container_width=True):
            if st.session_state.session_id == "groq-local":
                if is_last:
                    st.session_state.page = "result"
                    st.rerun()
                else:
                    with st.spinner("Generating next question..."):
                        try:
                            q_data = groq_generate_question(
                                st.session_state.topic, st.session_state.difficulty,
                                exclude=st.session_state.asked_questions
                            )
                            st.session_state.current_question = {
                                "question": q_data["question"],
                                "keywords": q_data["keywords"],
                            }
                            st.session_state.asked_questions.append(q_data["question"])
                            st.session_state.question_number += 1
                            st.session_state.answered         = False
                            st.session_state.last_result      = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ Could not generate next question: {e}")
            elif is_last:
                st.session_state.page = "result"
                st.rerun()
            else:
                with st.spinner("Loading next question..."):
                    resp = api_get(f"/interview/next/{st.session_state.session_id}")
                if resp.get("status") == "completed":
                    st.session_state.page = "result"
                    st.rerun()
                elif resp.get("status") == "success":
                    st.session_state.current_question = resp["question"]
                    st.session_state.question_number  = resp["question_number"]
                    st.session_state.answered         = False
                    st.session_state.last_result      = None
                    st.rerun()
                else:
                    st.error(resp.get("message", "Something went wrong."))

def page_result():
    render_nav()

    if st.session_state.session_id == "groq-local":
        answers    = st.session_state.session_answers
        avg        = round(sum(a.get("score", 0) for a in answers) / len(answers)) if answers else 0
        topic      = st.session_state.topic
        difficulty = st.session_state.difficulty
        total_q    = len(answers)
    else:
        resp = api_get(f"/interview/result/{st.session_state.session_id}")
        if resp.get("status") == "error":
            st.error(resp["message"])
            if st.button("← Back to Home"):
                st.session_state.page = "home"
                st.rerun()
            return

        avg        = resp.get("average_score", 0)
        answers    = resp.get("answers", [])
        topic      = resp.get("topic", st.session_state.topic)
        difficulty = resp.get("difficulty", st.session_state.difficulty)
        total_q    = resp.get("total_questions", len(answers))

    t_meta = TOPIC_META.get(topic, {"icon": "📚", "label": topic.upper()})

    if avg >= 80:
        verdict     = "Outstanding Performance!"
        verdict_sub = "You have a strong command of the concepts. You're interview-ready."
    elif avg >= 60:
        verdict     = "Solid Understanding"
        verdict_sub = "Good work! Review the missed keywords to sharpen your edge."
    elif avg >= 40:
        verdict     = "Keep Practising"
        verdict_sub = "You have a foundation — study the model answers and try again."
    else:
        verdict     = "More Study Needed"
        verdict_sub = "Go through the model answers carefully and attempt again."

    st.markdown(f"""
    <div class="result-header">
        <div style="font-size:10px;color:#8a8fa3;margin-bottom:12px;
                    letter-spacing:2px;text-transform:uppercase;font-weight:700;">
            {t_meta['icon']} {t_meta['label']} &nbsp;·&nbsp;
            {DIFFICULTY_META.get(difficulty, {}).get('emoji','⚪')} {difficulty.capitalize()} &nbsp;·&nbsp;
            {total_q} Questions
        </div>
        <div class="result-score" style="color:{score_color(avg)}">{avg}</div>
        <div style="font-size:12px;color:#8a8fa3;margin-bottom:16px;letter-spacing:1px;">AVERAGE SCORE</div>
        <div style="font-size:22px;font-weight:800;color:#1c1f2e;margin-bottom:10px;
                    font-family:'Space Grotesk',sans-serif;letter-spacing:-0.5px;">
            {score_emoji(avg)} {verdict}
        </div>
        <div style="font-size:14px;color:#5b5f76;max-width:440px;margin:0 auto;">{verdict_sub}</div>
    </div>
    """, unsafe_allow_html=True)

    if answers:
        cols = st.columns(len(answers))
        for i, (a, col) in enumerate(zip(answers, cols)):
            with col:
                s = a.get("score", 0)
                st.markdown(f"""
                <div style="text-align:center;background:#ffffff;border:1px solid #e3e5ee;
                            border-radius:10px;padding:16px 6px;box-shadow:0 1px 3px rgba(16,24,40,0.04);">
                    <div style="font-size:22px;font-weight:800;font-family:'Space Grotesk',sans-serif;
                                color:{score_color(s)};letter-spacing:-1px;">{s}</div>
                    <div style="font-size:10px;color:#8a8fa3;margin-top:4px;font-weight:700;
                                letter-spacing:1px;">Q{i+1}</div>
                </div>
                """, unsafe_allow_html=True)

    # AI Coach summary — generated once per result set via Groq, cached in session state
    st.markdown("<br>", unsafe_allow_html=True)
    if answers:
        cache_key = f"{topic}|{difficulty}|{total_q}|{avg}"
        if st.session_state.get("ai_summary_key") != cache_key:
            try:
                with st.spinner("AI Coach is reviewing your session..."):
                    st.session_state.ai_summary = groq_generate_summary(topic, difficulty, answers)
                    st.session_state.ai_summary_key = cache_key
            except Exception:
                st.session_state.ai_summary = None
                st.session_state.ai_summary_key = cache_key

        if st.session_state.get("ai_summary"):
            st.markdown(f"""
            <div class="card-glow" style="display:flex;gap:16px;align-items:flex-start;">
                <div class="chat-avatar" style="margin-top:2px;">AI</div>
                <div>
                    <div class="model-label" style="margin-bottom:8px;">AI Coach Takeaway</div>
                    <div style="font-size:14px;color:#1c1f2e;line-height:1.7;">{st.session_state.ai_summary}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Detailed Review</div>', unsafe_allow_html=True)

    for i, a in enumerate(answers):
        s       = a.get("score", 0)
        matched = a.get("matched_keywords", [])
        missed  = a.get("missed_keywords", [])
        m_chips = " ".join([f'<span class="chip chip-hit">✓ {k}</span>' for k in matched]) or "—"
        x_chips = " ".join([f'<span class="chip chip-miss">✗ {k}</span>' for k in missed]) \
                  or '<span style="color:#15803d;font-size:12px">All covered! 🎉</span>'

        q_label = a.get("question", "")
        q_label = q_label[:72] + "..." if len(q_label) > 72 else q_label

        with st.expander(f"Q{i+1} · {q_label} — {s}/100"):
            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown(f"""
                <div class="keyword-section">
                    <div class="keyword-label">Your Answer</div>
                    <div style="background:#f6f7fb;border-radius:8px;padding:14px;
                                font-size:13px;color:#5b5f76;line-height:1.65;border:1px solid #e3e5ee;">
                        {a.get('user_answer', 'Skipped')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with rc2:
                st.markdown(f"""
                <div class="keyword-section">
                    <div class="keyword-label">Keywords Hit</div>
                    <div class="keyword-row" style="margin-bottom:14px">{m_chips}</div>
                    <div class="keyword-label">Keywords Missed</div>
                    <div class="keyword-row">{x_chips}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="model-answer" style="margin-top:14px">
                <div class="model-label">Model Answer</div>
                <div class="model-text">{a.get('model_answer', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("🔁 Retry Same Config", type="primary", use_container_width=True):
            resp2 = api_get("/interview/start", {
                "topic":         st.session_state.topic,
                "difficulty":    st.session_state.difficulty,
                "num_questions": st.session_state.num_questions
            })
            if resp2.get("status") == "success":
                st.session_state.session_id       = resp2["session_id"]
                st.session_state.current_question = resp2["question"]
                st.session_state.question_number  = 1
                st.session_state.total_questions  = resp2["total_questions"]
                st.session_state.answered         = False
                st.session_state.last_result      = None
                st.session_state.page             = "interview"
                st.rerun()
            else:
                with st.spinner("Backend unavailable, generating questions with AI..."):
                    try:
                        q_data = groq_generate_question(st.session_state.topic, st.session_state.difficulty)
                        st.session_state.session_id       = "groq-local"
                        st.session_state.current_question = {
                            "question": q_data["question"],
                            "keywords": q_data["keywords"],
                        }
                        st.session_state.question_number  = 1
                        st.session_state.total_questions  = st.session_state.num_questions
                        st.session_state.answered         = False
                        st.session_state.last_result      = None
                        st.session_state.asked_questions  = [q_data["question"]]
                        st.session_state.session_answers  = []
                        st.session_state.ai_summary       = None
                        st.session_state.ai_summary_key   = None
                        st.session_state.page             = "interview"
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Backend error and AI fallback failed: {e}")
    with btn2:
        if st.button("💬 Ask AI Coach", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    with btn3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

def page_chat():
    render_nav()

    st.markdown("""
    <div class="chat-header">
        <div class="chat-header-icon">🤖</div>
        <div>
            <div class="chat-header-title">AI Interview Coach</div>
            <div class="chat-header-sub">Powered by Groq · Llama 3.3 70B · Concise answers</div>
        </div>
        <div class="chat-online">
            <div class="dot-online"></div>
            Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-empty">
            <div class="chat-empty-icon">💬</div>
            <div class="chat-empty-title">Ask me anything about tech interviews</div>
            <div class="chat-empty-sub">
                Concepts · Code · Tips · Explanations — ask a question below to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-msg-user">
                    <div class="chat-bubble-user">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                av_col, msg_col = st.columns([0.05, 0.95])
                with av_col:
                    st.markdown('<div class="chat-avatar">AI</div>', unsafe_allow_html=True)
                with msg_col:
                    st.markdown(
                        f'<div class="ai-reply-wrap">{_render_ai_markdown(msg["content"])}</div>',
                        unsafe_allow_html=True
                    )

        st.markdown("<br>", unsafe_allow_html=True)
        clr_c, _ = st.columns([1, 4])
        with clr_c:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    st.markdown("")
    st.markdown('<div class="chat-input-wrap">', unsafe_allow_html=True)

    inp_col, btn_col = st.columns([5, 1])
    with inp_col:
        user_input = st.text_area(
            "message",
            placeholder="Ask about any concept, topic, or interview tip...",
            height=80,
            key=f"chat_input_{st.session_state.chat_key}",
            label_visibility="collapsed"
        )
    with btn_col:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("Send ➤", type="primary", use_container_width=True)

    st.markdown("""
    <div class="model-badge">
        <div class="model-dot"></div>
        Groq · llama-3.3-70b-versatile · Fast inference
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if send and user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        with st.spinner("Thinking..."):
            try:
                reply = call_groq(st.session_state.chat_history)
            except Exception as e:
                reply = f"⚠️ Something went wrong: {e}"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.chat_key += 1
        st.rerun()

page = st.session_state.get("page", "home")

if page == "home":
    page_home()
elif page == "interview":
    page_interview()
elif page == "result":
    page_result()
elif page == "chat":
    page_chat()
else:
    page_home()