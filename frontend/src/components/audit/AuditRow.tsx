import { ExternalLink, Eye } from 'lucide-react';
import type { AuditResult } from '../../types/api';
import { VerdictBadge } from '../shared/VerdictBadge';

interface Props {
  result: AuditResult;
  onViewEvidence: (passageId: string) => void;
}

function getDomain(url: string): string {
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; }
}

export function AuditRow({ result, onViewEvidence }: Props) {
  return (
    <tr className="border-t border-[#FDE0B8] hover:bg-[#FEF4E6] transition-colors">
      <td className="px-4 py-3">
        <VerdictBadge value={result.verdict} />
      </td>
      <td className="px-4 py-3 text-sm text-[#23131E] max-w-xs">
        {result.claim_text}
      </td>
      <td className="px-4 py-3 font-mono text-xs text-[#6B5068] max-w-[200px]">
        {result.support_span ? (
          <span className="line-clamp-2 bg-[#FEE9DC] px-1.5 py-0.5 rounded">
            {result.support_span}
          </span>
        ) : (
          <span className="text-[#C17C75]">—</span>
        )}
      </td>
      <td className="px-4 py-3">
        {result.source_url ? (
          <a
            href={result.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 font-mono text-xs text-[#FC9A64] hover:underline"
          >
            {getDomain(result.source_url)} <ExternalLink size={10} />
          </a>
        ) : <span className="text-xs text-[#7B515F]">—</span>}
      </td>
      <td className="px-4 py-3">
        {result.passage_id && (
          <button
            onClick={() => onViewEvidence(result.passage_id!)}
            className="flex items-center gap-1 text-xs text-[#FC9A64] hover:text-[#FDB486] font-medium"
            aria-label="View evidence passage"
          >
            <Eye size={13} /> View
          </button>
        )}
      </td>
    </tr>
  );
}
