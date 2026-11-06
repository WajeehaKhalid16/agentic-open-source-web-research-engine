import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, ExternalLink, Clock } from 'lucide-react';
import { listRuns } from '../../api/client';
import type { RunSummary } from '../../types/api';
import { SkeletonBlock } from '../shared/SkeletonBlock';
import { EmptyCard } from '../shared/EmptyCard';
import { ErrorCard } from '../shared/ErrorCard';

interface Props {
  open: boolean;
  onClose: () => void;
}

function RunStatusBadge({ status }: { status: RunSummary['status'] }) {
  const cfg = {
    pending:  { label: 'Pending',  cls: 'bg-[#FEF3CD] text-[#7B5700] border-[#F0D080]' },
    running:  { label: 'Running',  cls: 'bg-[#FEE9DC] text-[#7B3010] border-[#FC9A64]' },
    complete: { label: 'Complete', cls: 'bg-[#E6F4EA] text-[#2E6B3E] border-[#A8D5B5]' },
    error:    { label: 'Error',    cls: 'bg-[#F0E0DF] text-[#7B2020] border-[#C17C75]' },
  }[status];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${cfg.cls}`}>
      {cfg.label}
    </span>
  );
}

export function PastRunsSlideOver({ open, onClose }: Props) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError(null);
    listRuns()
      .then(setRuns)
      .catch(() => setError('Could not load run history.'))
      .finally(() => setLoading(false));
    setTimeout(() => closeRef.current?.focus(), 50);
  }, [open]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (open) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-[#FFF7EC]/70 backdrop-blur-sm z-40"
            onClick={onClose}
            aria-hidden="true"
          />
          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
            transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
            className="fixed right-0 top-0 h-full w-96 max-w-full bg-white shadow-drawer z-50 flex flex-col"
            role="dialog"
            aria-modal="true"
            aria-label="Past research runs"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#FDE0B8]">
              <h2 className="font-heading text-xl text-[#23131E]">Past Runs</h2>
              <button
                ref={closeRef}
                onClick={onClose}
                className="text-[#7B515F] hover:text-[#23131E] transition-colors p-1 rounded-lg hover:bg-[#FDE0B8]"
                aria-label="Close past runs"
              >
                <X size={18} />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-3 scrollbar-thin">
              {loading && (
                <div className="flex flex-col gap-4">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="rounded-xl border border-[#FDE0B8] p-4 flex flex-col gap-2">
                      <SkeletonBlock lines={2} />
                    </div>
                  ))}
                </div>
              )}
              {error && <ErrorCard message={error} onRetry={() => { setError(null); setLoading(true); listRuns().then(setRuns).catch(() => setError('Could not load run history.')).finally(() => setLoading(false)); }} />}
              {!loading && !error && runs.length === 0 && (
                <EmptyCard message="No past runs yet. Start a research query to see results here." />
              )}
              {!loading && runs.map((run) => (
                <div key={run.run_id} className="rounded-xl border border-[#FDE0B8] bg-white p-4 flex flex-col gap-2 shadow-card">
                  <p className="text-sm text-[#23131E] font-medium line-clamp-2">{run.query}</p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <RunStatusBadge status={run.status} />
                    <span className="flex items-center gap-1 text-xs text-[#7B515F]">
                      <Clock size={11} />
                      {new Date(run.created_at).toLocaleDateString()}
                    </span>
                    {run.stats.pct_verified != null && (
                      <span className="text-xs text-[#7B515F]">{Math.round(run.stats.pct_verified)}% verified</span>
                    )}
                  </div>
                  <a
                    href={`/runs/${run.run_id}`}
                    className="flex items-center gap-1 text-xs font-semibold text-[#FC9A64] hover:text-[#FDB486] transition-colors w-fit"
                  >
                    Open <ExternalLink size={11} />
                  </a>
                </div>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
