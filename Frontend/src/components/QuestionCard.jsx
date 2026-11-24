import { AnimatePresence, motion } from 'framer-motion';
import { ProgressBar } from './ScoreCard.jsx';
import { cap } from '../services/insights.js';

export default function QuestionCard({ number, total, topic, difficulty, question, progress, children }) {
  return (
    <section className="card question-card">
      <div className="question-meta">
        <span className="badge">Question {number} of {total}</span>
        {topic && <span className="badge badge-soft">{topic}</span>}
        {difficulty && <span className="badge badge-soft">{cap(difficulty)}</span>}
      </div>
      <ProgressBar value={progress} label="Interview progress" />
      <AnimatePresence mode="wait">
        <motion.h2
          key={number}
          className="question-text"
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -24 }}
          transition={{ duration: 0.25 }}
        >
          {question}
        </motion.h2>
      </AnimatePresence>
      {children}
    </section>
  );
}
