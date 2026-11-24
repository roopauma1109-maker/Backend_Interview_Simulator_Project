import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertCircle, ClipboardList, Home as HomeIcon, ListChecks, RotateCcw, Target, ThumbsUp, TrendingUp } from 'lucide-react';
import { fetchResult } from '../services/api.js';
import { buildInsights, cap, scoreTone } from '../services/insights.js';
import ScoreCard from '../components/ScoreCard.jsx';
import Loading from '../components/Loading.jsx';

function Ring({ value, tone }) {
  const r = 54;
  const c = 2 * Math.PI * r;
  return (
    <svg viewBox="0 0 140 140" className={`ring tone-${tone}`} role="img" aria-label={`Overall score ${value}%`}>
      <circle cx="70" cy="70" r={r} className="ring-bg" />
      <g transform="rotate(-90 70 70)">
        <motion.circle
          cx="70"
          cy="70"
          r={r}
          className="ring-fg"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: c * (1 - value / 100) }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </g>
      <text x="70" y="77" textAnchor="middle" className="ring-text">{value}%</text>
    </svg>
  );
}

function InsightCard({ icon: Icon, title, items, tone, delay }) {
  return (
    <motion.div className={`card insight tone-${tone}`} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.4 }}>
      <h3><Icon size={18} /> {title}</h3>
      {items.length ? (
        <ul>{items.map((t) => <li key={t}>{t}</li>)}</ul>
      ) : (
        <p className="muted small">Nothing to report yet.</p>
      )}
    </motion.div>
  );
}

export default function Results() {
  const { sessionId } = useParams();
  const [state, setState] = useState({ loading: true, data: null, error: '' });

  useEffect(() => {
    let off = false;
    (async () => {
      try {
        let data;
        if (sessionId === 'resume') {
          // Resume interviews are scored locally and cached for this browser tab only.
          const raw = sessionStorage.getItem('ais_resume_result');
          if (!raw) throw new Error('No resume interview result found. Complete a resume interview first.');
          data = JSON.parse(raw);
        } else {
          data = await fetchResult(sessionId);
        }
        if (!off) setState({ loading: false, data, error: '' });
      } catch (err) {
        if (!off) setState({ loading: false, data: null, error: err.message });
      }
    })();
    return () => { off = true; };
  }, [sessionId]);

  if (state.loading) return <Loading label="Loading results…" />;

  if (state.error || !state.data) {
    return (
      <div className="card empty-state">
        <AlertCircle size={30} />
        <h2>Results unavailable</h2>
        <p className="muted">{state.error || 'We could not load these results.'}</p>
        <p className="muted small">Topic interview sessions are stored in server memory and disappear when the backend restarts.</p>
        <Link to="/interview" className="btn btn-primary">Start a new interview</Link>
      </div>
    );
  }

  const { data } = state;
  const answers = data.answers || [];
  const answered = answers.length;
  const average = data.average_score ?? 0;
  const tone = scoreTone(average);
  const isResume = sessionId === 'resume';
  const insights = buildInsights(answers, average, data.topic, data.difficulty);

  if (!answered) {
    return (
      <div className="card empty-state">
        <ClipboardList size={30} />
        <h2>No answers recorded</h2>
        <p className="muted">This session has no submitted answers, so there is nothing to score yet.</p>
        <Link to={isResume ? '/resume-interview' : '/interview'} className="btn btn-primary">Try again</Link>
      </div>
    );
  }

  return (
    <div className="stack-lg">
      <header className="row-between wrap">
        <div>
          <h1 className="page-title">Interview results</h1>
          <p className="muted">
            {data.topic}{data.difficulty ? ` · ${cap(data.difficulty)}` : ''}{data.filename ? ` · ${data.filename}` : ''}
          </p>
        </div>
        <Ring value={average} tone={tone} />
      </header>

      <div className="grid-3">
        <ScoreCard label="Questions answered" value={answered} icon={ListChecks} hint={`of ${data.total_questions} in this interview`} />
        <ScoreCard label="Total score" value={data.total_score} suffix={` / ${answered * 100}`} icon={Target} delay={0.08} />
        <ScoreCard label="Percentage" value={average} suffix="%" icon={TrendingUp} tone={tone} progress={average} delay={0.16} />
      </div>

      <div className="grid-3">
        <InsightCard icon={ThumbsUp} title="Strengths" items={insights.strengths} tone="success" delay={0.1} />
        <InsightCard icon={AlertCircle} title="Areas for improvement" items={insights.improvements} tone="warning" delay={0.18} />
        <InsightCard icon={ListChecks} title="Recommended next steps" items={insights.next} tone="primary" delay={0.26} />
      </div>
      <p className="muted small">Strengths and improvements are derived from keyword matching on your answers.</p>

      <section className="stack">
        <h2 className="section-title">Question breakdown</h2>
        {answers.map((a, i) => (
          <motion.article key={`${i}-${a.question}`} className="card answer-card" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i * 0.05, 0.4), duration: 0.35 }}>
            <div className="row-between">
              <span className="badge">Question {i + 1}</span>
              <span className={`score-pill tone-${scoreTone(a.score)}`}>{a.score}% · {a.grade}</span>
            </div>
            <h3 className="answer-q">{a.question}</h3>

            <div className="answer-block">
              <h4>Your answer</h4>
              <p>{a.user_answer}</p>
            </div>

            <div className="chips">
              {(a.matched_keywords || []).map((k) => <span key={`m-${k}`} className="chip chip-success">{k}</span>)}
              {(a.missed_keywords || []).map((k) => <span key={`x-${k}`} className="chip chip-warning">{k}</span>)}
            </div>

            <details className="model-answer">
              <summary>Model answer</summary>
              <p>{a.model_answer || 'No model answer is stored for this question.'}</p>
            </details>
          </motion.article>
        ))}
      </section>

      <div className="row-end">
        <Link to="/" className="btn btn-ghost"><HomeIcon size={16} /> Dashboard</Link>
        <Link to={isResume ? '/resume-interview' : '/interview'} className="btn btn-primary"><RotateCcw size={16} /> Practise again</Link>
      </div>
    </div>
  );
}
