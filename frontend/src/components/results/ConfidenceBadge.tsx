import { verdict } from '../../tokens/tokens';
import type { Confidence } from '../../types/api';

interface Props { value: Confidence }

const labels: Record<Confidence, string> = {
  'well-supported': 'Well Supported',
  'partial': 'Partially Supported',
  'disputed': 'Disputed',
  'insufficient': 'Insufficient Evidence',
};

export function ConfidenceBadge({ value }: Props) {
  const t = verdict[value];
  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold border"
      style={{ backgroundColor: t.bg, color: t.text, borderColor: t.border }}
    >
      {labels[value]}
    </span>
  );
}
