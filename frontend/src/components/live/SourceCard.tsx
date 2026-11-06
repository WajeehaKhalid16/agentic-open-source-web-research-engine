import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, AlertCircle, XCircle } from 'lucide-react';
import type { Source } from '../../types/api';

interface Props {
  source: Source;
  index?: number;
}

function getDomain(url: string): string {
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; }
}

function CredibilityBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.7 ? '#FC9A64' : score >= 0.4 ? '#C17C75' : '#E8DADE';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 rounded-full bg-[#FDE0B8] overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs text-[#7B515F] w-7 text-right">{pct}%</span>
    </div>
  );
}

const statusIcon: Record<Source['status'], React.ReactNode> = {
  fetching:  <Loader2 size={12} className="animate-spin text-[#FC9A64]" />,
  extracted: <CheckCircle2 size={12} className="text-green-600" />,
  failed:    <AlertCircle size={12} className="text-[#C17C75]" />,
  blocked:   <XCircle size={12} className="text-[#7B515F]" />,
};

const typeBadge: Record<string, string> = {
  web:       'bg-[#FEE9DC] text-[#7B3010] border-[#FC9A64]',
  news:      'bg-[#E8DADE] text-[#3A1A28] border-[#7B515F]',
  academic:  'bg-[#FEF4E6] text-[#7B5700] border-[#FDE0B8]',
  official:  'bg-[#E6F4EA] text-[#2E6B3E] border-[#A8D5B5]',
  code:      'bg-[#F0E0DF] text-[#7B2020] border-[#C17C75]',
  benchmark: 'bg-[#E8DADE] text-[#3A1A28] border-[#7B515F]',
};

export function SourceCard({ source, index = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.28 }}
      className="rounded-xl border border-[#FDE0B8] bg-white shadow-card p-4 flex flex-col gap-2.5 hover:border-[#FC9A64] transition-colors"
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-semibold text-[#23131E] line-clamp-2 flex-1 leading-snug">
          {source.title || getDomain(source.url)}
        </p>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${typeBadge[source.type] || typeBadge.web}`}>
            {source.type}
          </span>
          {statusIcon[source.status]}
        </div>
      </div>

      {/* Domain */}
      <span className="font-mono text-xs text-[#7B515F] truncate">{getDomain(source.url)}</span>

      {/* Snippet */}
      {source.snippet && (
        <p className="text-xs text-[#6B5068] line-clamp-2 leading-relaxed">{source.snippet}</p>
      )}

      {/* Credibility */}
      {source.credibility_score != null && (
        <div className="flex flex-col gap-1">
          <span className="text-xs text-[#7B515F] font-medium">Credibility</span>
          <CredibilityBar score={source.credibility_score} />
        </div>
      )}
    </motion.div>
  );
}
