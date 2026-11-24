
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Layout from './components/Layout.jsx';

import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Home from './pages/Home.jsx';
import Interview from './pages/Interview.jsx';
import ResumeInterview from './pages/ResumeInterview.jsx';
import Results from './pages/Results.jsx';
import AICoach from './pages/AICoach.jsx';
import Analytics from './pages/Analytics.jsx';
import CodingArena from './pages/CodingArena';

function PublicOnly({ children }) {
  const { isAuthenticated } = useAuth();

  return isAuthenticated
    ? <Navigate to="/" replace />
    : children;
}

export default function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicOnly>
            <Login />
          </PublicOnly>
        }
      />

      <Route
        path="/register"
        element={
          <PublicOnly>
            <Register />
          </PublicOnly>
        }
      />

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/interview" element={<Interview />} />
          <Route path="/resume-interview" element={<ResumeInterview />} />
          <Route path="/results/:sessionId" element={<Results />} />
          <Route path="/coach" element={<AICoach />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/coding-arena" element={<CodingArena />} />
        </Route>
      </Route>

      {/* Fallback Route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
