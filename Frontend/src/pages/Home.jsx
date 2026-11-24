
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertCircle,
  ArrowRight,
  Bot,
  BookOpen,
  FileText,
  History,
  Layers,
  Sparkles,
  Code2,
  TrendingUp,
} from 'lucide-react';

import { useAuth } from '../context/AuthContext.jsx';
import {
  fetchHealth,
  fetchResult,
  fetchTopics,
  fetchIntermediateTopics,
} from '../services/api.js';

import ScoreCard from '../components/ScoreCard.jsx';
import Loading from '../components/Loading.jsx';
import { cap, scoreTone } from '../services/insights.js';

const ACTIONS = [
  {
    to: '/interview',
    icon: BookOpen,
    title: 'Topic Practice',
    text: 'Practise technical questions topic-wise with different difficulty levels.',
    tag: 'Basic & Intermediate',
  },
  {
    to: '/resume-interview',
    icon: FileText,
    title: 'Resume-Based Interview',
    text: 'Upload your resume and practise questions based on your skills and projects.',
    tag: 'Personalized',
  },
  {
    to: '/coach',
    icon: Bot,
    title: 'AI Coach',
    text: 'Improve your answers with AI-powered interview guidance and tips.',
    tag: 'AI Powered',
  },
];

const cardVariants = {
  hidden: { opacity: 0, y: 18 },
  show: (i) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.4 },
  }),
};

const topicLabels = {
  java: 'Java',
  python: 'Python',
  dbms: 'DBMS',
  api: 'REST API',
  os: 'Operating Systems',
};

export default function Home() {
  const { user } = useAuth();

  const [stats, setStats] = useState({
    loading: true,
    error: '',
    health: null,
    topics: null,
    intermediate: null,
  });

  const [recent, setRecent] = useState([]);

  useEffect(() => {
    let off = false;

    (async () => {
      const [h, t, intermediate] = await Promise.allSettled([
        fetchHealth(),
        fetchTopics(),
        fetchIntermediateTopics(),
      ]);

      if (off) return;

      setStats({
        loading: false,
        error: h.status === 'rejected' ? h.reason?.message || 'Unable to connect to backend.' : '',
        health: h.status === 'fulfilled' ? h.value : null,
        topics: t.status === 'fulfilled' ? t.value?.topics : null,
        intermediate:
          intermediate.status === 'fulfilled'
            ? intermediate.value
            : null,
      });
    })();

    return () => {
      off = true;
    };
  }, []);

  useEffect(() => {
    let off = false;

    (async () => {
      const items = [];

      try {
        const raw = sessionStorage.getItem('ais_last_session');

        if (raw) {
          const { id } = JSON.parse(raw);
          const r = await fetchResult(id);

          if (r.answers?.length) {
            items.push({
              key: `s-${id}`,
              to: `/results/${id}`,
              title: r.topic,
              sub: `${cap(r.difficulty)} · ${r.answers.length} answered`,
              avg: r.average_score,
            });
          }
        }
      } catch {
        // Session may no longer exist.
      }

      try {
        const raw = sessionStorage.getItem('ais_resume_result');

        if (raw) {
          const r = JSON.parse(raw);

          items.push({
            key: 'resume',
            to: '/results/resume',
            title: 'Resume interview',
            sub: `${r.answers?.length || 0} answered`,
            avg: r.average_score,
          });
        }
      } catch {
        // Ignore invalid stored data.
      }

      if (!off) setRecent(items);
    })();

    return () => {
      off = true;
    };
  }, []);

  const topicEntries = stats.topics
    ? Object.entries(stats.topics)
    : [];

  const intermediateTopics = stats.intermediate?.topics || {};

  const intermediateCount =
    stats.intermediate?.total_questions ??
    Object.values(intermediateTopics).reduce(
      (sum, count) => sum + Number(count || 0),
      0
    );

  const basicCount = stats.health?.questions_loaded ?? 0;
  const totalQuestions = basicCount + intermediateCount;

  return (
    <div className="stack-lg home-page">

      {/* Welcome Hero */}
      <motion.section
        className="home-hero"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
      >
        <div className="home-hero-content">
          <span className="home-eyebrow">
            <Sparkles size={15} />
            YOUR INTERVIEW PREPARATION SPACE
          </span>

          <h1>
            Welcome back, {user?.username || 'Learner'}!
          </h1>

          <p>
            Build confidence, strengthen your technical skills and get
            interview-ready one question at a time.
          </p>

          <Link to="/interview" className="home-hero-button">
            Start Practising
            <ArrowRight size={17} />
          </Link>
        </div>

        <div className="home-hero-decoration">
          <div className="hero-icon-circle">
            <Code2 size={42} />
          </div>
          <div className="hero-floating-icon hero-float-one">
            <BookOpen size={20} />
          </div>
          <div className="hero-floating-icon hero-float-two">
            <Bot size={20} />
          </div>
        </div>
      </motion.section>

      {/* Quick Statistics */}
      <section className="stack">
        <div className="home-section-heading">
          <div>
            <h2 className="section-title">Your Question Bank</h2>
            <p className="muted small">
              Explore questions and improve your preparation.
            </p>
          </div>
          <span className="home-section-icon">
            <TrendingUp size={19} />
          </span>
        </div>

        {stats.loading && (
          <Loading inline label="Loading statistics..." />
        )}

        {!stats.loading && stats.error && (
          <div className="banner banner-warning" role="alert">
            <AlertCircle size={18} />
            {stats.error}
          </div>
        )}

        {!stats.loading && (
          <div className="grid-3">
            <ScoreCard
              label="Basic Questions"
              value={basicCount}
              icon={BookOpen}
            />

            <ScoreCard
              label="Intermediate Questions"
              value={intermediateCount}
              icon={Layers}
              delay={0.08}
            />

            <ScoreCard
              label="Total Questions"
              value={totalQuestions}
              icon={Code2}
              delay={0.16}
            />
          </div>
        )}

        {!stats.loading && topicEntries.length > 0 && (
          <motion.div
            className="card home-topic-card"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="home-card-heading">
              <div>
                <h3>Basic Questions by Topic</h3>
                <p className="muted small">
                  Available questions in each subject.
                </p>
              </div>
              <BookOpen size={20} />
            </div>

            <div className="chips mt">
              {topicEntries.map(([name, counts]) => {
                const count =
                  typeof counts === 'number'
                    ? counts
                    : (counts?.easy || 0) +
                      (counts?.medium || 0) +
                      (counts?.hard || 0);

                return (
                  <span key={name} className="chip">
                    {name} · {count}
                  </span>
                );
              })}
            </div>
          </motion.div>
        )}

        {!stats.loading && Object.keys(intermediateTopics).length > 0 && (
          <motion.div
            className="card home-topic-card"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <div className="home-card-heading">
              <div>
                <h3>Intermediate Questions by Topic</h3>
                <p className="muted small">
                  Scenario-based practice questions.
                </p>
              </div>
              <Layers size={20} />
            </div>

            <div className="chips mt">
              {Object.entries(intermediateTopics).map(([name, count]) => (
                <span key={name} className="chip">
                  {topicLabels[name] || cap(name)} · {count}
                </span>
              ))}
            </div>
          </motion.div>
        )}
      </section>

      {/* Practice Actions */}
      <section className="stack">
        <div className="home-section-heading">
          <div>
            <h2 className="section-title">Practice & Improve</h2>
            <p className="muted small">
              Choose the preparation method you want to focus on.
            </p>
          </div>
          <span className="home-section-icon">
            <Sparkles size={19} />
          </span>
        </div>

        <div className="grid-3">
          {ACTIONS.map(({ to, icon: Icon, title, text, tag }, i) => (
            <motion.div
              key={to}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              animate="show"
              whileHover={{ y: -5 }}
            >
              <Link to={to} className="card action-card home-action-card">
                <div className="home-action-top">
                  <span className="action-icon">
                    <Icon size={23} />
                  </span>
                  <span className="home-action-tag">{tag}</span>
                </div>

                <h3>{title}</h3>
                <p className="muted">{text}</p>

                <span className="action-cta">
                  Explore
                  <ArrowRight size={16} />
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Recent Results */}
      <section className="stack">
        <div className="home-section-heading">
          <div>
            <h2 className="section-title">Recent Results</h2>
            <p className="muted small">
              Review your latest interview performance.
            </p>
          </div>
          <span className="home-section-icon">
            <History size={19} />
          </span>
        </div>

        {recent.length === 0 ? (
          <div className="card empty-state home-empty-state">
            <History size={32} />
            <h3>No recent results yet</h3>
            <p className="muted">
              Complete a practice interview to see your performance here.
            </p>
            <Link to="/interview" className="btn btn-primary">
              Start your first interview
              <ArrowRight size={16} />
            </Link>
          </div>
        ) : (
          <div className="stack-sm">
            {recent.map((r, i) => (
              <motion.div
                key={r.key}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                whileHover={{ x: 3 }}
              >
                <Link to={r.to} className="card result-row home-result-row">
                  <div className="home-result-icon">
                    <FileText size={20} />
                  </div>

                  <div className="home-result-info">
                    <h3>{r.title}</h3>
                    <p className="muted small">{r.sub}</p>
                  </div>

                  <span className={`score-pill tone-${scoreTone(r.avg)}`}>
                    {Number(r.avg || 0)}%
                  </span>

                  <ArrowRight
                    size={17}
                    className="home-result-arrow"
                  />
                </Link>
              </motion.div>
            ))}
          </div>
        )}

        <p className="muted small">
          Interview sessions are stored in the backend's memory and are not
          linked to user accounts. Only your latest session from this
          browser can be listed.
        </p>
      </section>
    </div>
  );
}
