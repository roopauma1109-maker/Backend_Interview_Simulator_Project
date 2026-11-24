import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export default function Button({
  variant = 'primary',
  loading = false,
  icon: Icon,
  disabled = false,
  className = '',
  children,
  ...rest
}) {
  const inactive = disabled || loading;
  return (
    <motion.button
      type="button"
      whileHover={inactive ? undefined : { scale: 1.03 }}
      whileTap={inactive ? undefined : { scale: 0.97 }}
      className={`btn btn-${variant} ${className}`.trim()}
      disabled={inactive}
      {...rest}
    >
      {loading ? <Loader2 size={16} className="spin" /> : Icon && <Icon size={16} />}
      {children}
    </motion.button>
  );
}
