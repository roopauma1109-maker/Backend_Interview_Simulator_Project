import { motion } from 'framer-motion';
import AnimatedNumber from './AnimatedNumber.jsx';

export function ProgressBar({ value, tone = 'primary', label }) {
  const pct = Math.max(0, Math.min(100, value || 0));
  return (
    <div
      className="progress"
      role="progressbar"
      aria-valuenow={Math.round(pct)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <motion.div
        className={`progress-fill tone-${tone}`}
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      />
    </div>
  );
}

export default function ScoreCard({ label, value, suffix = '', icon: Icon, tone = 'primary', progress, hint, delay = 0 }) {
  return (
    <motion.div
      className={`card stat-card tone-${tone}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <div className="stat-top">
        {Icon && (
          <span className="stat-icon">
            <Icon size={18} />
          </span>
        )}
        <span className="stat-label">{label}</span>
      </div>
      <div className="stat-value">
        <AnimatedNumber value={value} suffix={suffix} />
      </div>
      {progress != null && <ProgressBar value={progress} tone={tone} label={label} />}
      {hint && <p className="muted small">{hint}</p>}
    </motion.div>
  );
}
