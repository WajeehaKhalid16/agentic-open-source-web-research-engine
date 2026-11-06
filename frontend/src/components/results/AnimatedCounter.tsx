import { useEffect, useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform, useReducedMotion } from 'framer-motion';

interface Props {
  value: number;
  label: string;
  suffix?: string;
  decimals?: number;
}

export function AnimatedCounter({ value, label, suffix = '', decimals = 0 }: Props) {
  const reduced = useReducedMotion();
  const motionVal = useMotionValue(0);
  const spring = useSpring(motionVal, { stiffness: 80, damping: 20 });
  const display = useTransform(spring, (v) => v.toFixed(decimals) + suffix);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (reduced) {
      motionVal.set(value);
    } else {
      motionVal.set(value);
    }
  }, [value, reduced, motionVal]);

  if (reduced) {
    return (
      <div className="flex flex-col items-center gap-1">
        <span className="font-heading text-2xl font-bold text-[#23131E]">
          {value.toFixed(decimals)}{suffix}
        </span>
        <span className="text-xs text-[#7B515F] font-medium">{label}</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-1">
      <motion.span ref={ref} className="font-heading text-2xl font-bold text-[#23131E]">
        {display}
      </motion.span>
      <span className="text-xs text-[#7B515F] font-medium">{label}</span>
    </div>
  );
}
