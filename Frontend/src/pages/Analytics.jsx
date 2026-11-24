
import { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import {
  BarChart3,
  Trophy,
  Target,
  ClipboardCheck,
  Clock3,
  RefreshCw,
  TrendingUp,
  Sparkles,
} from "lucide-react";

const Analytics = () => {
  const { user } = useAuth();

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async () => {
    const userId = user?.user_id ?? user?.id;

    if (!userId) {
      setError("User ID not found. Please login again.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `http://127.0.0.1:8000/interview/history/${userId}`
      );

      if (!response.ok) {
        throw new Error(`Failed to load analytics (${response.status})`);
      }

      const data = await response.json();
      setHistory(data.history || []);
    } catch (err) {
      setError(err.message || "Unable to load analytics.");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const totalInterviews = history.length;

  const completedInterviews = history.filter(
    (item) => item.completed_at
  ).length;

  const averageScore =
    totalInterviews > 0
      ? (
          history.reduce(
            (sum, item) => sum + Number(item.average_score || 0),
            0
          ) / totalInterviews
        ).toFixed(1)
      : "0";

  const totalQuestions = history.reduce(
    (sum, item) => sum + Number(item.questions_answered || 0),
    0
  );

  const chartData = useMemo(() => {
    const grouped = {};

    history.forEach((item) => {
      const topic = item.topic || "Other";

      if (!grouped[topic]) {
        grouped[topic] = {
          topic,
          totalScore: 0,
          count: 0,
        };
      }

      grouped[topic].totalScore += Number(item.average_score || 0);
      grouped[topic].count += 1;
    });

    return Object.values(grouped).map((item) => ({
      topic: item.topic,
      score: Number((item.totalScore / item.count).toFixed(1)),
    }));
  }, [history]);

  const formatDate = (date) => {
    if (!date) return "—";

    const parsed = new Date(date);

    if (Number.isNaN(parsed.getTime())) return "—";

    return parsed.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner" />
        <p>Loading your performance...</p>
      </div>
    );
  }

  return (
    <div className="analytics-page">

      {/* Header */}

      <div className="analytics-header">
        <div>
          <div className="analytics-eyebrow">
            <Sparkles size={15} />
            YOUR LEARNING OVERVIEW
          </div>

          <h1 className="analytics-title">
            Performance Analytics
          </h1>

          <p className="analytics-subtitle">
            Track your interview preparation, monitor your scores,
            and measure your progress over time.
          </p>
        </div>

        <button
          className="analytics-refresh"
          onClick={fetchHistory}
          title="Refresh analytics"
        >
          <RefreshCw size={17} />
          Refresh
        </button>
      </div>

      {/* Error */}

      {error && (
        <div className="analytics-error">
          {error}
        </div>
      )}

      {/* Statistics */}

      <div className="analytics-stats">

        <div className="analytics-stat-card tone-primary">
          <div className="analytics-stat-top">
            <span className="analytics-stat-label">
              Total Interviews
            </span>
            <span className="analytics-stat-icon">
              <BarChart3 size={21} />
            </span>
          </div>

          <h2>{totalInterviews}</h2>
          <p>All practice sessions</p>
        </div>

        <div className="analytics-stat-card tone-success">
          <div className="analytics-stat-top">
            <span className="analytics-stat-label">
              Completed Interviews
            </span>
            <span className="analytics-stat-icon">
              <Trophy size={21} />
            </span>
          </div>

          <h2>{completedInterviews}</h2>
          <p>Successfully completed</p>
        </div>

        <div className="analytics-stat-card tone-warning">
          <div className="analytics-stat-top">
            <span className="analytics-stat-label">
              Average Score
            </span>
            <span className="analytics-stat-icon">
              <Target size={21} />
            </span>
          </div>

          <h2>{averageScore}%</h2>
          <p>Across all interviews</p>
        </div>

        <div className="analytics-stat-card tone-error">
          <div className="analytics-stat-top">
            <span className="analytics-stat-label">
              Questions Answered
            </span>
            <span className="analytics-stat-icon">
              <ClipboardCheck size={21} />
            </span>
          </div>

          <h2>{totalQuestions}</h2>
          <p>Total answers submitted</p>
        </div>

      </div>

      {/* Chart */}

      <section className="analytics-panel">

        <div className="analytics-panel-heading">
          <div>
            <h2>
              <TrendingUp size={20} />
              Topic-wise Performance
            </h2>
            <p>Your average interview scores by topic</p>
          </div>
        </div>

        {chartData.length === 0 ? (
          <div className="analytics-empty">
            <BarChart3 size={42} />
            <h3>No performance data yet</h3>
            <p>
              Complete an interview to see your topic-wise
              performance here.
            </p>
          </div>
        ) : (
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{
                  top: 15,
                  right: 20,
                  left: 0,
                  bottom: 10,
                }}
              >
                <CartesianGrid
                  strokeDasharray="4 4"
                  vertical={false}
                  stroke="#E2E8F0"
                />

                <XAxis
                  dataKey="topic"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#64748B", fontSize: 12 }}
                />

                <YAxis
                  domain={[0, 100]}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#64748B", fontSize: 12 }}
                  tickFormatter={(value) => `${value}%`}
                />

                <Tooltip
                  cursor={{ fill: "#EEF2FF" }}
                  formatter={(value) => [`${value}%`, "Average Score"]}
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid #E2E8F0",
                    boxShadow: "0 5px 20px rgba(15,23,42,0.08)",
                  }}
                />

                <Bar
                  dataKey="score"
                  fill="#4F46E5"
                  radius={[8, 8, 0, 0]}
                  maxBarSize={55}
                  animationDuration={900}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

      </section>

      {/* Interview History */}

      <section className="analytics-panel">

        <div className="analytics-panel-heading">
          <div>
            <h2>
              <Clock3 size={20} />
              Interview History
            </h2>
            <p>Review your previous practice sessions</p>
          </div>

          <span className="analytics-count">
            {totalInterviews} Sessions
          </span>
        </div>

        {history.length === 0 ? (
          <div className="analytics-empty">
            <ClipboardCheck size={42} />
            <h3>No interviews found</h3>
            <p>Start your first interview to build your history.</p>
          </div>
        ) : (
          <div className="analytics-table-wrap">
            <table className="analytics-table">

              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Difficulty</th>
                  <th>Score</th>
                  <th>Questions</th>
                  <th>Time</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr key={item.session_id}>

                    <td>
                      <span className="analytics-topic">
                        {item.topic}
                      </span>
                    </td>

                    <td>
                      <span className={`difficulty-badge ${String(item.difficulty || "easy").toLowerCase()}`}>
                        {item.difficulty || "Easy"}
                      </span>
                    </td>

                    <td>
                      <span className="analytics-score">
                        {Number(item.average_score || 0)}%
                      </span>
                    </td>

                    <td>
                      {item.questions_answered || 0}/
                      {item.total_questions || 0}
                    </td>

                    <td>
                      {item.time_taken || 0}s
                    </td>

                    <td>
                      <span
                        className={`status-badge ${
                          item.completed_at ? "completed" : "progress"
                        }`}
                      >
                        {item.completed_at ? "Completed" : "In Progress"}
                      </span>
                    </td>

                    <td>
                      {formatDate(item.started_at)}
                    </td>

                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}

      </section>

    </div>
  );
};

export default Analytics;
