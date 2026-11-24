import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { AlertCircle, Bot, Send, Trash2, User } from 'lucide-react';
import { coachChat } from '../services/api.js';
import Button from '../components/Button.jsx';

const SUGGESTIONS = [
  'How should I answer "Tell me about yourself"?',
  'How do I explain a project clearly in an interview?',
  'What are common mistakes in technical interviews?',
];

function TypingDots() {
  return (
    <div className="msg msg-assistant">
      <span className="msg-avatar"><Bot size={16} /></span>
      <div className="bubble typing" aria-label="AI Coach is typing">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="dot"
            animate={{ y: [0, -4, 0], opacity: [0.4, 1, 0.4] }}
            transition={{ repeat: Infinity, duration: 0.9, delay: i * 0.15 }}
          />
        ))}
      </div>
    </div>
  );
}

export default function AICoach() {
  const reduce = useReducedMotion();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [unavailable, setUnavailable] = useState(false);
  const endRef = useRef(null);
  const idRef = useRef(1);
  const sendingRef = useRef(false);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'end' });
  }, [messages, sending, reduce]);

  const send = async (override) => {
    const text = (override ?? input).trim();
    if (!text || sendingRef.current) return;
    sendingRef.current = true;

    const history = messages.filter((m) => !m.error).slice(-10).map(({ role, content }) => ({ role, content }));
    setMessages((m) => [...m, { id: idRef.current++, role: 'user', content: text }]);
    setInput('');
    setSending(true);

    try {
      const res = await coachChat(text, history);
      if (!res.reply) throw new Error('The coach returned an empty response.');
      setUnavailable(false);
      setMessages((m) => [...m, { id: idRef.current++, role: 'assistant', content: res.reply }]);
    } catch (err) {
      const missing = err.status === 404 || err.status === 405;
      setUnavailable(missing);
      setMessages((m) => [
        ...m,
        {
          id: idRef.current++,
          role: 'assistant',
          error: true,
          content: missing
            ? 'The AI Coach endpoint (POST /coach/chat) is not available on the backend yet.'
            : err.message,
        },
      ]);
    } finally {
      sendingRef.current = false;
      setSending(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="chat-page">
      <header className="row-between">
        <div>
          <h1 className="page-title">AI Coach</h1>
          <p className="muted">Ask for interview tips, answer structure or preparation advice.</p>
        </div>
        <Button variant="ghost" icon={Trash2} disabled={!messages.length || sending} onClick={() => { setMessages([]); setUnavailable(false); }}>
          Clear chat
        </Button>
      </header>

      {unavailable && (
        <div className="banner banner-warning" role="alert">
          <AlertCircle size={18} />
          <span>
            The current backend has no AI Coach route. Add the optional router from <code>docs/coach_router_PROPOSED.py</code>{' '}
            (it keeps the Groq key on the server) and try again.
          </span>
        </div>
      )}

      <div className="card chat">
        <div className="chat-scroll" aria-live="polite">
          {messages.length === 0 && !sending && (
            <div className="empty-state chat-empty">
              <Bot size={30} />
              <h3>How can I help you prepare?</h3>
              <div className="chips center-chips">
                {SUGGESTIONS.map((s) => (
                  <button key={s} type="button" className="chip chip-button" onClick={() => send(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <motion.div
                key={m.id}
                className={`msg msg-${m.role}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
              >
                <span className="msg-avatar">{m.role === 'user' ? <User size={16} /> : <Bot size={16} />}</span>
                <div className={`bubble${m.error ? ' bubble-error' : ''}`}>{m.content}</div>
              </motion.div>
            ))}
          </AnimatePresence>

          {sending && <TypingDots />}
          <div ref={endRef} />
        </div>

        <div className="chat-input">
          <label htmlFor="coach-input" className="sr-only">Message the AI Coach</label>
          <textarea
            id="coach-input"
            className="textarea"
            rows={2}
            value={input}
            placeholder="Type a message…  (Enter to send, Shift + Enter for a new line)"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
          />
          <Button icon={Send} loading={sending} disabled={!input.trim()} onClick={() => send()} aria-label="Send message">
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
