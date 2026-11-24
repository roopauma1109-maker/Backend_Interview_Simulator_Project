import { motion } from 'framer-motion';

export default function Loading({ label = 'Loading…', fullscreen = false, inline = false }) {
  const cls = `loading${fullscreen ? ' loading-full' : ''}${inline ? ' loading-inline' : ''}`;
  return (
    <motion.div
      className={cls}
      role="status"
      aria-live="polite"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <span className="spinner" aria-hidden="true" />
      {label && <span className="loading-label">{label}</span>}
    </motion.div>
  );
}
