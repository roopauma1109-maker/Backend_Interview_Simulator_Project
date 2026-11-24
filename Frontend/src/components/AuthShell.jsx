import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

export const formVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.15 } },
};
export const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="auth-wrap">
      <motion.div
        className="auth-card card"
        initial={{ opacity: 0, y: 24, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
      >
        <div className="brand brand-center">
          <span className="brand-mark"><Sparkles size={18} /></span>
          <span>Interview Simulator</span>
        </div>
        <h1 className="auth-title">{title}</h1>
        <p className="muted center">{subtitle}</p>
        {children}
        <p className="auth-footer muted">{footer}</p>
      </motion.div>
    </div>
  );
}
