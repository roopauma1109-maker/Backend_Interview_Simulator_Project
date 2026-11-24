import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export default function PasswordField({ id, label, value, onChange, error, autoComplete, disabled }) {
  const [show, setShow] = useState(false);
  return (
    <div className="field">
      <label htmlFor={id} className="label">{label}</label>
      <div className="input-wrap">
        <input
          id={id}
          type={show ? 'text' : 'password'}
          className={`input${error ? ' invalid' : ''}`}
          value={value}
          onChange={onChange}
          autoComplete={autoComplete}
          disabled={disabled}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${id}-err` : undefined}
        />
        <button
          type="button"
          className="input-toggle"
          onClick={() => setShow((s) => !s)}
          aria-label={show ? 'Hide password' : 'Show password'}
        >
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
      {error && <p id={`${id}-err`} className="field-error" role="alert">{error}</p>}
    </div>
  );
}
