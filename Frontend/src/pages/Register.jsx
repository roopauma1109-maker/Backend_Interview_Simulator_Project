
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus } from 'lucide-react';

import AuthShell, {
  formVariants,
  itemVariants,
} from '../components/AuthShell.jsx';

import PasswordField from '../components/PasswordField.jsx';
import Button from '../components/Button.jsx';

import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';
import { registerUser } from '../services/api.js';

export default function Register() {
  const toast = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: '',
    password: '',
    confirm: '',
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
      next.username = 'Choose a username.';
    }

    if (form.password.length < 8) {
      next.password =
        'Password must contain at least 8 characters.';
    }

    if (form.confirm !== form.password) {
      next.confirm = 'Passwords do not match.';
    }

    setErrors(next);

    if (Object.keys(next).length > 0) return;

    setLoading(true);

    try {
      // Call backend registration API
      const res = await registerUser(
        form.username.trim(),
        form.password
      );

      if (!res || res.status !== 'success') {
        throw new Error(
          res?.message || 'Registration failed.'
        );
      }

      toast.success('Account created. Please sign in.');

      navigate('/login', {
        replace: true,
        state: {
          username: form.username.trim(),
        },
      });

    } catch (err) {
      console.error('Registration error:', err);

      setServerError(
        err.message || 'Registration failed. Please try again.'
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell
      title="Create your account"
      subtitle="Start practising for your next interview."
      footer={
        <>
          Already registered? <Link to="/login">Sign in</Link>
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
            autoComplete="new-password"
            disabled={loading}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <PasswordField
            id="confirm"
            label="Confirm password"
            value={form.confirm}
            onChange={set('confirm')}
            error={errors.confirm}
            autoComplete="new-password"
            disabled={loading}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Button
            type="submit"
            icon={UserPlus}
            loading={loading}
            className="btn-block"
          >
            {loading ? 'Creating account…' : 'Register'}
          </Button>
        </motion.div>
      </motion.form>
    </AuthShell>
  );
}
