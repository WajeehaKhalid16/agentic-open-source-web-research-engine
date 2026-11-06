import { verdict } from '../../tokens/tokens';
import type { AuditSummary } from '../../types/api';

interface Props { summary: AuditSummary }

export function AuditSummaryStrip({ summary }: Props) {
  const items = [
    { label: 'Verified',    value: summary.verified,  key: 'well-supported' as const },
    { label: 'Partial',     value: summary.partial,   key: 'partial' as const },
    { label: 'Disputed',    value: summary.disputed,  key: 'disputed' as const },
    { label: 'Missing',     value: summary.missing,   key: 'insufficient' as const },
  ];
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {items.map((item) => {
        const t = verdict[item.key];
        return (
          <div
            key={item.label}
            className="rounded-xl border p-4 flex flex-col gap-1 text-center"
            style={{ backgroundColor: t.bg, borderColor: t.border }}
          >
            <span className="font-heading text-2xl font-bold" style={{ color: t.text }}>{item.value}</span>
            <span className="text-xs font-medium" style={{ color: t.text }}>{item.label}</span>
          </div>
        );
      })}
    </div>
  );
}
