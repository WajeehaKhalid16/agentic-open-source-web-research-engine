import { verdict } from '../../tokens/tokens';
import type { VerdictType } from '../../types/api';
import { cn } from '../../lib/utils';

interface Props {
  value: VerdictType;
  className?: string;
}

export function VerdictBadge({ value, className }: Props) {
  const t = verdict[value];
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        className
      )}
      style={{ backgroundColor: t.bg, color: t.text, borderColor: t.border }}
    >
      {value.replace(/-/g, ' ')}
    </span>
  );
}
