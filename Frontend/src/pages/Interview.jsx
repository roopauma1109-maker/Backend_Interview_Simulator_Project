
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertCircle,
  BookOpen,
  Coffee,
  Code2,
  Cpu,
  Database,
  Globe,
  Play,
  Layers,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

import {
  fetchTopics,
  fetchIntermediateTopics,
  nextQuestion,
  startInterview,
  submitAnswer,
} from '../services/api.js';

import { useToast } from '../context/ToastContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';

import Button from '../components/Button.jsx';
import Loading from '../components/Loading.jsx';
import InterviewRunner from '../components/InterviewRunner.jsx';
import { cap } from '../services/insights.js';

const FALLBACK_TOPICS = [
  'Python',
  'Java',
  'DBMS',
  'REST API',
  'Operating Systems',
];

const INTERMEDIATE_LABELS = {
  java: 'Java',
  python: 'Python',
  dbms: 'DBMS',
  api: 'REST API',
  os: 'Operating Systems',
};

const ICONS = {
  python: Code2,
  java: Coffee,
  dbms: Database,
  'rest api': Globe,
  api: Globe,
  'operating systems': Cpu,
  os: Cpu,
};

const iconFor = (name) => {
  const key = Object.keys(ICONS).find((k) =>
    name.toLowerCase().includes(k)
  );

  return key ? ICONS[key] : BookOpen;
};

const DIFFICULTIES = ['easy', 'medium', 'hard'];

export default function Interview() {
  const toast = useToast();
  const navigate = useNavigate();
  const { user } = useAuth();

  const userId = user?.user_id ?? user?.id;

  const [topics, setTopics] = useState(null);
  const [intermediateTopics, setIntermediateTopics] = useState(null);

  const [topicsError, setTopicsError] = useState('');
  const [intermediateError, setIntermediateError] = useState('');

  const [loadingTopics, setLoadingTopics] = useState(true);

  const [form, setForm] = useState({
    level: 'basic',
    topic: '',
    difficulty: 'easy',
    count: 5,
  });

  const [starting, setStarting] = useState(false);
  const [session, setSession] = useState(null);

  // Load both question banks
  useEffect(() => {
    let off = false;

    const loadTopics = async () => {
      try {
        const [basicResult, intermediateResult] =
          await Promise.allSettled([
            fetchTopics(),
            fetchIntermediateTopics(),
          ]);

        if (off) return;

        if (basicResult.status === 'fulfilled') {
          setTopics(basicResult.value.topics || {});
        } else {
          setTopicsError(basicResult.reason.message);
        }

        if (intermediateResult.status === 'fulfilled') {
          setIntermediateTopics(
            intermediateResult.value.topics || {}
          );
        } else {
          setIntermediateError(
            intermediateResult.reason.message
          );
        }
      } finally {
        if (!off) setLoadingTopics(false);
      }
    };

    loadTopics();

    return () => {
      off = true;
    };
  }, []);

  // Get topics according to selected level
  const topicList = useMemo(() => {
    if (form.level === 'intermediate') {
      return intermediateTopics
        ? Object.keys(intermediateTopics)
        : [];
    }

    const names = topics ? Object.keys(topics) : [];
    return names.length ? names : FALLBACK_TOPICS;
  }, [topics, intermediateTopics, form.level]);

  // Reset topic when level changes
  useEffect(() => {
    if (topicList.length) {
      setForm((f) => ({
        ...f,
        topic: topicList.includes(f.topic)
          ? f.topic
          : topicList[0],
      }));
    } else {
      setForm((f) => ({ ...f, topic: '' }));
    }
  }, [topicList]);

  const effectiveDifficulty =
    form.level === 'intermediate'
      ? 'intermediate'
      : form.difficulty;

  const available =
    form.level === 'intermediate'
      ? intermediateTopics?.[form.topic]
      : topics?.[form.topic]?.[form.difficulty];

  const noQuestions = available === 0;

  const selectedTopicLabel =
    form.level === 'intermediate'
      ? INTERMEDIATE_LABELS[form.topic] || cap(form.topic)
      : form.topic;

  const lastSession = (() => {
    try {
      return JSON.parse(
        sessionStorage.getItem('ais_last_session') || 'null'
      );
    } catch {
      return null;
    }
  })();

  const resetToSetup = (message) => {
    setSession(null);
    if (message) toast.error(message);
  };

  // Start interview
  const start = async () => {
    if (starting || !form.topic) return;

    if (!userId) {
      toast.error('User ID not found. Please login again.');
      return;
    }

    if (noQuestions) {
      toast.error('No questions available for this selection.');
      return;
    }

    setStarting(true);

    try {
      const res = await startInterview({
        topic: form.topic,
        difficulty: effectiveDifficulty,
        numQuestions: form.count,
        userId,
        questionLevel: form.level,
      });

      sessionStorage.setItem(
        'ais_last_session',
        JSON.stringify({
          id: res.session_id,
          topic: selectedTopicLabel,
          difficulty: effectiveDifficulty,
          level: form.level,
        })
      );

      setSession({
        id: res.session_id,
        total: res.total_questions,
        number: res.question_number,
        question: res.question,
        answered: 0,
      });

      if (res.total_questions < form.count) {
        toast.info(
          `Only ${res.total_questions} question(s) available for this combination.`
        );
      }
    } catch (err) {
      toast.error(err.message);
    } finally {
      setStarting(false);
    }
  };

  const sessionGone = (err) =>
    /invalid session/i.test(err.message || '');

  const handleSubmit = async (answer) => {
    try {
      const res = await submitAnswer(session.id, answer);

      setSession((s) => ({
        ...s,
        answered: res.questions_answered,
      }));

      return res;
    } catch (err) {
      if (sessionGone(err)) {
        resetToSetup(
          'This interview session no longer exists on the server. Please start again.'
        );
        return null;
      }

      throw err;
    }
  };

  const handleNext = async () => {
    try {
      const res = await nextQuestion(session.id);

      if (res.status === 'completed') {
        navigate(`/results/${session.id}`);
        return;
      }

      setSession((s) => ({
        ...s,
        number: res.question_number,
        total: res.total_questions,
        question: res.question,
      }));
    } catch (err) {
      if (sessionGone(err)) {
        resetToSetup(
          'This interview session no longer exists on the server. Please start again.'
        );
        return;
      }

      throw err;
    }
  };

  const handleFinish = () => {
    navigate(`/results/${session.id}`);
  };

  // Interview screen
  if (session) {
    return (
      <InterviewRunner
        key={session.number}
        number={session.number}
        total={session.total}
        question={session.question}
        isLast={session.number >= session.total}
        answeredCount={session.answered}
        onSubmit={handleSubmit}
        onNext={handleNext}
        onFinish={handleFinish}
      />
    );
  }

  return (
    <div className="stack-lg">

      {/* Page Header */}
      <header>
        <div className="row-between">
          <div>
            <h1 className="page-title">Topic Practice</h1>
            <p className="muted">
              Build your technical knowledge with structured practice.
            </p>
          </div>

          <div className="banner banner-info">
            <BookOpen size={17} />
            <span>Practice Zone</span>
          </div>
        </div>
      </header>

      {/* Last Session */}
      {lastSession?.id && (
        <div className="banner banner-info">
          <CheckCircle2 size={18} />

          <span>
            Last session: {lastSession.topic} (
            {cap(lastSession.difficulty)}).{' '}
            <Link to={`/results/${lastSession.id}`}>
              View results
            </Link>
          </span>
        </div>
      )}

      {loadingTopics ? (
        <Loading label="Loading topics..." />
      ) : (
        <motion.div
          className="card stack-lg"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
        >

          {/* Level Selection */}
          <div className="stack-sm">
            <div className="row-between">
              <div>
                <h2 className="section-title">
                  <Layers size={19} /> Choose Practice Level
                </h2>
                <p className="muted small">
                  Select the question bank you want to practice.
                </p>
              </div>
            </div>

            <div className="grid grid-2" style={{ gap: 12 }}>

              <motion.button
                type="button"
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.98 }}
                className={`topic-btn ${
                  form.level === 'basic' ? 'active' : ''
                }`}
                onClick={() =>
                  setForm((f) => ({
                    ...f,
                    level: 'basic',
                    topic: '',
                  }))
                }
              >
                <BookOpen size={24} />

                <span className="topic-name">Basic Practice</span>

                <span className="muted small">
                  Easy · Medium · Hard
                </span>

                <span className="muted small">
                  Fundamental interview questions
                </span>
              </motion.button>

              <motion.button
                type="button"
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.98 }}
                className={`topic-btn ${
                  form.level === 'intermediate' ? 'active' : ''
                }`}
                onClick={() =>
                  setForm((f) => ({
                    ...f,
                    level: 'intermediate',
                    topic: '',
                    difficulty: 'intermediate',
                  }))
                }
              >
                <Sparkles size={24} />

                <span className="topic-name">
                  Intermediate Practice
                </span>

                <span className="muted small">
                  Scenario-based questions
                </span>

                <span className="muted small">
                  Apply concepts to real situations
                </span>
              </motion.button>

            </div>
          </div>

          {/* Basic / Intermediate Error */}
          {form.level === 'basic' && topicsError && (
            <div className="banner banner-warning" role="alert">
              <AlertCircle size={18} />
              Could not load basic topics. Showing default topics.
            </div>
          )}

          {form.level === 'intermediate' && intermediateError && (
            <div className="banner banner-warning" role="alert">
              <AlertCircle size={18} />
              Could not load intermediate topics: {intermediateError}
            </div>
          )}

          {/* Topic Selection */}
          <div className="stack-sm">

            <div className="row-between">
              <div>
                <h2 className="section-title">
                  1. Select Topic
                </h2>
                <p className="muted small">
                  Choose a subject to begin practicing.
                </p>
              </div>

              <span className="badge">
                {topicList.length} Topics
              </span>
            </div>

            {topicList.length === 0 ? (
              <div className="banner banner-warning">
                No topics available for this level.
                Check the backend question bank.
              </div>
            ) : (
              <div
                className="topic-grid"
                role="radiogroup"
                aria-label="Topic"
              >
                {topicList.map((name) => {
                  const label =
                    form.level === 'intermediate'
                      ? INTERMEDIATE_LABELS[name] || cap(name)
                      : name;

                  const Icon = iconFor(label);

                  const count =
                    form.level === 'intermediate'
                      ? intermediateTopics?.[name]
                      : topics?.[name]?.[form.difficulty];

                  const active = form.topic === name;

                  return (
                    <motion.button
                      key={name}
                      type="button"
                      role="radio"
                      aria-checked={active}
                      whileHover={{ y: -3 }}
                      whileTap={{ scale: 0.97 }}
                      className={`topic-btn${active ? ' active' : ''}`}
                      onClick={() =>
                        setForm((f) => ({
                          ...f,
                          topic: name,
                        }))
                      }
                    >
                      <Icon size={22} />

                      <span className="topic-name">
                        {label}
                      </span>

                      <span className="muted small">
                        {count ?? 0} questions
                      </span>

                      {active && (
                        <CheckCircle2 size={17} />
                      )}
                    </motion.button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Difficulty - Basic Only */}
          {form.level === 'basic' && (
            <div className="stack-sm">
              <h2 className="section-title">
                2. Select Difficulty
              </h2>

              <div
                className="seg"
                role="radiogroup"
                aria-label="Difficulty"
              >
                {DIFFICULTIES.map((d) => (
                  <button
                    key={d}
                    type="button"
                    role="radio"
                    aria-checked={form.difficulty === d}
                    className={`seg-btn${
                      form.difficulty === d ? ' active' : ''
                    }`}
                    onClick={() =>
                      setForm((f) => ({
                        ...f,
                        difficulty: d,
                      }))
                    }
                  >
                    {cap(d)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Intermediate Info */}
          {form.level === 'intermediate' && (
            <div className="banner banner-info">
              <Sparkles size={18} />
              <span>
                Intermediate questions are scenario-based.
                Difficulty is automatically set to Intermediate.
              </span>
            </div>
          )}

          {/* Question Count */}
          <div className="stack-sm">
            <h2 className="section-title">
              {form.level === 'basic' ? '3.' : '2.'}{' '}
              Number of Questions:{' '}
              <span className="accent">{form.count}</span>
            </h2>

            <input
              type="range"
              min={1}
              max={10}
              value={form.count}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  count: Number(e.target.value),
                }))
              }
              className="range"
              aria-label="Number of questions"
            />

            <div className="row-between muted small">
              <span>1 question</span>
              <span>10 questions</span>
            </div>

            {noQuestions && (
              <p className="field-error">
                No questions available for {selectedTopicLabel}.
                Try another topic.
              </p>
            )}

            {available > 0 && available < form.count && (
              <p className="muted small">
                Only {available} question(s) available.
                Your session will contain {available} questions.
              </p>
            )}
          </div>

          {/* Start Button */}
          <div className="row-between">
            <div className="muted small">
              Selected: <strong>{selectedTopicLabel || 'None'}</strong>
              {' · '}
              <strong>{cap(effectiveDifficulty)}</strong>
            </div>

            <Button
              icon={Play}
              loading={starting}
              disabled={!form.topic || noQuestions || topicList.length === 0}
              onClick={start}
            >
              {starting ? 'Starting...' : 'Start Practice'}
            </Button>
          </div>

        </motion.div>
      )}
    </div>
  );
}
