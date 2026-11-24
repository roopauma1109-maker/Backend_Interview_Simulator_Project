
import { NavLink } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Bot,
  BookOpen,
  FileText,
  LayoutDashboard,
  Sparkles,
  X,
  ChartNoAxesCombined,
  Code2
} from 'lucide-react';

const ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/interview', label: 'Topic Practice', icon: BookOpen },
  { to: '/resume-interview', label: 'Resume Interview', icon: FileText },
  { to: '/coach', label: 'AI Coach', icon: Bot },
  { to: '/analytics', label: 'Performance Analytics', icon: ChartNoAxesCombined },
  { to: '/coding-arena', label: 'Coding Arena', icon: Code2 },
];

function Brand() {
  return (
    <div className="brand">
      <span className="brand-mark">
        <Sparkles size={18} />
      </span>
      <span>Interview Simulator</span>
    </div>
  );
}

function NavList({ onNavigate }) {
  return (
    <nav className="nav-list" aria-label="Main">
      {ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            `nav-link${isActive ? ' active' : ''}`
          }
        >
          <Icon size={18} />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export default function Sidebar({ open, onClose }) {
  return (
    <>
      <aside className="sidebar">
        <Brand />
        <NavList />
      </aside>

      <AnimatePresence>
        {open && (
          <motion.div
            key="overlay"
            className="drawer-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
        )}

        {open && (
          <motion.aside
            key="drawer"
            className="drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Navigation menu"
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 300 }}
          >
            <div className="drawer-head">
              <Brand />

              <button
                type="button"
                className="icon-btn"
                onClick={onClose}
                aria-label="Close menu"
              >
                <X size={20} />
              </button>
            </div>

            <NavList onNavigate={onClose} />
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
