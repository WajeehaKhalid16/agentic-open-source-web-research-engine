import { ShieldCheck } from 'lucide-react';
import type { Audit } from '../../types/api';
import { AuditSummaryStrip } from './AuditSummaryStrip';
import { AuditRow } from './AuditRow';
import { EmptyCard } from '../shared/EmptyCard';

interface Props {
  audit: Audit;
  onViewEvidence: (passageId: string) => void;
}

export function AuditTable({ audit, onViewEvidence }: Props) {
  return (
    <div className="flex flex-col gap-6">
      <AuditSummaryStrip summary={audit.summary} />
      {audit.results.length === 0 ? (
        <EmptyCard icon={<ShieldCheck size={28} strokeWidth={1.5} />} message="No claims to audit." />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-[#FDE0B8]">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#23131E] text-white text-left">
                <th className="px-4 py-3 font-semibold w-28">Verdict</th>
                <th className="px-4 py-3 font-semibold">Claim</th>
                <th className="px-4 py-3 font-semibold">Supporting span</th>
                <th className="px-4 py-3 font-semibold w-32">Source</th>
                <th className="px-4 py-3 w-16" />
              </tr>
            </thead>
            <tbody>
              {audit.results.map((r) => (
                <AuditRow key={r.claim_id} result={r} onViewEvidence={onViewEvidence} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
