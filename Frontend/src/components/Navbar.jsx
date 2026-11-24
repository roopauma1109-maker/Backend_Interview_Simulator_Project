import { useNavigate } from 'react-router-dom';
import { LogOut, Menu } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';

export default function Navbar({ onMenu }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleLogout = () => {
    logout();
    toast.info('You have been signed out.');
    navigate('/login', { replace: true });
  };

  return (
    <header className="navbar">
      <button type="button" className="icon-btn menu-btn" onClick={onMenu} aria-label="Open menu">
        <Menu size={22} />
      </button>
      <div className="navbar-title">AI Interview Simulator</div>
      <div className="navbar-user">
        <span className="avatar" aria-hidden="true">{user?.username?.[0]?.toUpperCase() || '?'}</span>
        <span className="navbar-name">{user?.username}</span>
        <button type="button" className="btn btn-ghost btn-sm" onClick={handleLogout}>
          <LogOut size={16} />
          <span className="hide-sm">Logout</span>
        </button>
      </div>
    </header>
  );
}
