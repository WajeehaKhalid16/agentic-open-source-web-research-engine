import { useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, ExternalLink } from 'lucide-react';
import type { Passage, Source, AuditResult } from '../../types/api';
import { EntityHighlighter } from './EntityHighlighter';
import { VerdictBadge } from '../shared/VerdictBadge';

interface Props {
  passage: Passage | null;
  source: Source | null;
  auditResult: AuditResult | null;
  onClose: () => void;
}

function getDomain(url: string): string {
  try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return url; }
}

export function EvidenceDrawer({ passage, source, auditResult, onClose }: Props) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const isOpen = !!passage;

  useEffect(() => {
    if (isOpen) setTimeout(() => closeRef.current?.focus(), 50);
  }, [isOpen]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (isOpen) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && passage && (
        <motion.aside
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', stiffness: 300, damping: 28 }}
          className="fixed right-0 top-0 h-full w-[400px] max-w-full bg-white shadow-drawer z-40 flex flex-col overflow-hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Evidence passage"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#FDE0B8] shrink-0">
            <div className="flex items-center gap-2">
              <h3 className="font-heading text-lg text-[#23131E]">Evidence</h3>
              <span className="font-mono text-xs bg-[#FDE0B8] text-[#7B515F] px-2 py-0.5 rounded-full">
                #{passage.rank}
              </span>
            </div>
            <button
              ref={closeRef}
              onClick={onClose}
              className="text-[#7B515F] hover:text-[#23131E] transition-colors p-1 rounded-lg hover:bg-[#FDE0B8]"
              aria-label="Close evidence drawer"
            >
              <X size={18} />
            </button>
          </div>

          {/* Scrollable body */}
          <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-5 flex flex-col gap-5">
            {/* Verdict + claim */}
            {auditResult && (
              <div className="flex flex-col gap-2 p-4 rounded-xl bg-[#FEF4E6] border border-[#FDE0B8]">
                <VerdictBadge value={auditResult.verdict} />
                <p className="text-sm italic text-[#6B5068] leading-relaxed">{auditResult.claim_text}</p>
              </div>
            )}

            {/* Passage text */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Supporting passage</span>
              <p className="text-sm text-[#23131E] leading-relaxed bg-[#FFF7EC] rounded-xl p-4 border border-[#FDE0B8]">
                <EntityHighlighter
                  text={passage.text}
                  entities={passage.entities}
                  keyTerms={passage.key_terms}
                  numbers={passage.numbers}
                  strongSpan={auditResult?.support_span ?? undefined}
                />
              </p>
            </div>

            {/* Source mini-card */}
            {source && (
              <div className="flex flex-col gap-2">
                <span className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Source</span>
                <div className="rounded-xl border border-[#FDE0B8] bg-white p-4 flex flex-col gap-2">
                  <p className="text-sm font-semibold text-[#23131E] line-clamp-2">{source.title}</p>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 font-mono text-xs text-[#FC9A64] hover:underline"
                  >
                    {getDomain(source.url)} <ExternalLink size={10} />
                  </a>
                  {source.credibility_score != null && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1 rounded-full bg-[#FDE0B8] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-[#FC9A64]"
                          style={{ width: `${Math.round(source.credibility_score * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-[#7B515F]">{Math.round(source.credibility_score * 100)}%</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* BM25 score */}
            <div className="flex items-center gap-2 text-xs text-[#7B515F]">
              <span className="font-mono bg-[#FDE0B8] px-2 py-0.5 rounded-full">BM25 {passage.bm25_score.toFixed(2)}</span>
              <span>Passage {passage.char_start}–{passage.char_end}</span>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
