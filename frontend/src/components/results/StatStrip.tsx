import type { RunStats } from '../../types/api';
import { AnimatedCounter } from './AnimatedCounter';

interface Props {
  stats: RunStats;
  elapsedMs: number;
}

export function StatStrip({ stats, elapsedMs }: Props) {
  const items = [
    { value: stats.sources_fetched, label: 'Sources' },
    { value: stats.passages_total, label: 'Passages' },
    { value: stats.pct_verified, label: 'Claims Verified', suffix: '%', decimals: 1 },
    { value: elapsedMs / 1000, label: 'Seconds', suffix: 's', decimals: 1 },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-[#FDE0B8] rounded-xl overflow-hidden border border-[#FDE0B8]">
      {items.map((s) => (
        <div key={s.label} className="bg-white px-6 py-5 flex flex-col items-center gap-1">
          <AnimatedCounter value={s.value} label={s.label} suffix={s.suffix} decimals={s.decimals} />
        </div>
      ))}
    </div>
  );
}
