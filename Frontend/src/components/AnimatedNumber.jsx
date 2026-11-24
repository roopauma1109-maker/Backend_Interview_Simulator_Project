import { useEffect, useState } from 'react';
import { animate, useReducedMotion } from 'framer-motion';

export default function AnimatedNumber({ value, duration = 0.9, suffix = '' }) {
  const reduce = useReducedMotion();
  const [display, setDisplay] = useState(reduce ? value : 0);

  useEffect(() => {
    if (reduce) {
      setDisplay(value);
      return undefined;
    }
    const controls = animate(0, value, {
      duration,
      ease: 'easeOut',
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => controls.stop();
  }, [value, duration, reduce]);

  return <span>{display}{suffix}</span>;
}
