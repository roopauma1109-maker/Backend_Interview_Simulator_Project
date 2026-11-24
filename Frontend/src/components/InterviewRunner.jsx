import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, Flag, Send } from 'lucide-react';
import QuestionCard from './QuestionCard.jsx';
import Button from './Button.jsx';
import AnimatedNumber from './AnimatedNumber.jsx';
import { ProgressBar } from './ScoreCard.jsx';
import { useToast } from '../context/ToastContext.jsx';
import { scoreTone } from '../services/insights.js';

/**
 * Shared question → answer → feedback UI used by BOTH interview types.
 * The parent supplies the behaviour:
 *   onSubmit(answer) -> Promise<{score, grade, matched_keywords, missed_keywords, model_answer} | null>
 *   onNext()         -> Promise  (advance to the next question)
 *   onFinish()       -> Promise  (leave for the results page)
 * The parent should give this component key={questionNumber} so state resets per question.
 */
export default function InterviewRunner({ number, total, question, isLast, answeredCount, onSubmit, onNext, onFinish }) {
  const toast = useToast();
  const [answer, setAnswer] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [busy, setBusy] = useState('');
  const [fieldError, setFieldError] = useState('');
  const lock = useRef(false); // blocks duplicate submits / double-clicks
  const textRef = useRef(null);

  useEffect(() => {
    textRef.current?.focus();
  }, []);

  const guarded = async (kind, fn) => {
    if (lock.current) return null;
    lock.current = true;
    setBusy(kind);
    try {
      return await fn();
    } catch (err) {
      toast.error(err.message || 'Something went wrong.');
      return null;
    } finally {
      lock.current = false;
      setBusy('');
    }
  };

  const submit = async () => {
    if (evaluation || lock.current) return;
    if (!answer.trim()) {
      setFieldError('Please write an answer before submitting.');
      return;
    }
    setFieldError('');
    const result = await guarded('submit', () => onSubmit(answer.trim()));
    if (result) setEvaluation(result);
  };

  const progress = ((number - 1 + (evaluation ? 1 : 0)) / total) * 100;
  const matched = evaluation?.matched_keywords || [];
  const missed = evaluation?.missed_keywords || [];

  return (
    <div className="runner">
      <QuestionCard
        number={number}
        total={total}
        topic={question.topic}
        difficulty={question.difficulty}
        question={question.question}
        progress={progress}
      >
        <label htmlFor="answer" className="sr-only">Your answer</label>
        <textarea
          id="answer"
          ref={textRef}
          className={`textarea${fieldError ? ' invalid' : ''}`}
          rows={7}
          value={answer}
          disabled={Boolean(evaluation) || busy === 'submit'}
          placeholder="Type your answer here…  (Ctrl + Enter to submit)"
          onChange={(e) => {
            setAnswer(e.target.value);
            if (fieldError) setFieldError('');
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) submit();
          }}
        />
        {fieldError && <p className="field-error" role="alert">{fieldError}</p>}

        {!evaluation && (
          <div className="row-between">
            <span className="muted small">{answer.trim().length} characters</span>
            <div className="row-gap">
              {answeredCount > 0 && (
                <Button variant="ghost" icon={Flag} disabled={Boolean(busy)} onClick={() => guarded('finish', onFinish)}>
                  Finish now
                </Button>
              )}
              <Button
                icon={Send}
                loading={busy === 'submit'}
                disabled={!answer.trim() || Boolean(busy)}
                onClick={submit}
              >
                {busy === 'submit' ? 'Evaluating…' : 'Submit Answer'}
              </Button>
            </div>
          </div>
        )}
      </QuestionCard>

      <AnimatePresence>
        {evaluation && (
          <motion.div
            key="feedback"
            className="card feedback"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
          >
            <div className="feedback-head">
              <div className={`score-badge tone-${scoreTone(evaluation.score)}`}>
                <AnimatedNumber value={evaluation.score} suffix="%" />
              </div>
              <div>
                <h3>{evaluation.grade}</h3>
                <p className="muted small">Score for this answer</p>
              </div>
            </div>
            <ProgressBar value={evaluation.score} tone={scoreTone(evaluation.score)} label="Answer score" />

            <div className="kw-group">
              <h4>Concepts you covered</h4>
              {matched.length ? (
                <div className="chips">{matched.map((k) => <span key={k} className="chip chip-success">{k}</span>)}</div>
              ) : (
                <p className="muted small">No expected concepts were detected.</p>
              )}
            </div>
            <div className="kw-group">
              <h4>Concepts to add</h4>
              {missed.length ? (
                <div className="chips">{missed.map((k) => <span key={k} className="chip chip-warning">{k}</span>)}</div>
              ) : (
                <p className="muted small">Nothing missing – great coverage.</p>
              )}
            </div>
            <div className="model-answer">
              <h4>Model answer</h4>
              <p>{evaluation.model_answer || 'No model answer is stored for this question.'}</p>
            </div>

            <div className="row-end">
              {!isLast && (
                <Button variant="ghost" icon={Flag} disabled={Boolean(busy)} onClick={() => guarded('finish', onFinish)}>
                  Finish Interview
                </Button>
              )}
              {isLast ? (
                <Button icon={Flag} loading={busy === 'finish'} disabled={Boolean(busy)} onClick={() => guarded('finish', onFinish)}>
                  Finish Interview
                </Button>
              ) : (
                <Button icon={ArrowRight} loading={busy === 'next'} disabled={Boolean(busy)} onClick={() => guarded('next', onNext)}>
                  Next Question
                </Button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
