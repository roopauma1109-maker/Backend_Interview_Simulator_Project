
import { useState } from 'react';
import {
  Link,
  useLocation,
  useNavigate,
} from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn } from 'lucide-react';

import AuthShell, {
  formVariants,
  itemVariants,
} from '../components/AuthShell.jsx';

import PasswordField from '../components/PasswordField.jsx';
import Button from '../components/Button.jsx';

import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';
import { loginUser } from '../services/api.js';

export default function Login() {
  const { login: saveUser } = useAuth();

  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [form, setForm] = useState({
    username: location.state?.username || '',
    password: '',
  });

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (key) => (e) => {
    setForm((f) => ({
      ...f,
      [key]: e.target.value,
    }));

    setErrors((er) => ({
      ...er,
      [key]: '',
    }));

    setServerError('');
  };

  const submit = async (e) => {
    e.preventDefault();

    if (loading) return;

    const next = {};

    if (!form.username.trim()) {
      next.username = 'Enter your username.';
    }

    if (!form.password) {
      next.password = 'Enter your password.';
    }

    setErrors(next);

    if (Object.keys(next).length > 0) return;

    setLoading(true);

    try {
      // Call backend login API
      const res = await loginUser(
        form.username.trim(),
        form.password
      );

      // Validate backend response
      if (
        !res ||
        res.status !== 'success' ||
        res.user_id === undefined ||
        res.user_id === null ||
        !res.username
      ) {
        throw new Error(
          'Invalid login response. User details are missing.'
        );
      }

      // Save authenticated user in AuthContext
      saveUser({
        user_id: res.user_id,
        username: res.username,
      });

      toast.success(`Welcome back, ${res.username}!`);

      navigate(
        location.state?.from?.pathname || '/',
        { replace: true }
      );

    } catch (err) {
      console.error('Login error:', err);

      setServerError(
        err.message || 'Login failed. Please try again.'
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to continue your interview practice."
      footer={
        <>
          New here? <Link to="/register">Create an account</Link>
        </>
      }
    >
      <motion.form
        className="auth-form"
        onSubmit={submit}
        noValidate
        variants={formVariants}
        initial="hidden"
        animate="show"
      >
        {serverError && (
          <motion.div
            variants={itemVariants}
            className="banner banner-error"
            role="alert"
          >
            {serverError}
          </motion.div>
        )}

        <motion.div
          variants={itemVariants}
          className="field"
        >
          <label htmlFor="username" className="label">
            Username
          </label>

          <input
            id="username"
            className={`input${errors.username ? ' invalid' : ''}`}
            value={form.username}
            onChange={set('username')}
            autoComplete="username"
            disabled={loading}
            aria-invalid={Boolean(errors.username)}
          />

          {errors.username && (
            <p className="field-error" role="alert">
              {errors.username}
            </p>
          )}
        </motion.div>

        <motion.div variants={itemVariants}>
          <PasswordField
            id="password"
            label="Password"
            value={form.password}
            onChange={set('password')}
            error={errors.password}
            autoComplete="current-password"
            disabled={loading}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Button
            type="submit"
            icon={LogIn}
            loading={loading}
            className="btn-block"
          >
            {loading ? 'Signing in…' : 'Login'}
          </Button>
        </motion.div>
      </motion.form>
    </AuthShell>
  );
}
