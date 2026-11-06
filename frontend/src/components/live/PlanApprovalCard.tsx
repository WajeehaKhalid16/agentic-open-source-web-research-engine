// ─── PlanApprovalCard ─────────────────────────────────────────────────────────
// Shows the AI-generated research plan and allows the user to approve or edit it
// before the engine proceeds with searches.

import { useState, useRef, type KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
import { ClipboardList, ArrowRight, X, Plus } from 'lucide-react';
import { color } from '../../tokens/tokens';

interface Props {
  plan: { scope: string; query_variants: string[] };
  onApprove: () => void;
  onEdit: (variants: string[]) => void;
}

// ─── Component ────────────────────────────────────────────────────────────────

export function PlanApprovalCard({ plan, onApprove, onEdit }: Props) {
  const [variants, setVariants]   = useState<string[]>(plan.query_variants);
  const [inputVal, setInputVal]   = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function removeVariant(index: number) {
    const next = variants.filter((_, i) => i !== index);
    setVariants(next);
    onEdit(next);
  }

  function addVariant() {
    const trimmed = inputVal.trim();
    if (!trimmed || variants.includes(trimmed)) return;
    const next = [...variants, trimmed];
    setVariants(next);
    setInputVal('');
    onEdit(next);
  }

  function handleInputKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') { e.preventDefault(); addVariant(); }
    if (e.key === 'Escape') { setInputVal(''); setIsEditing(false); }
  }

  function handleEditToggle() {
    setIsEditing(prev => !prev);
    setTimeout(() => inputRef.current?.focus(), 50);
  }

  return (
    <motion.div
      initial={{ scale: 0.96, opacity: 0 }}
      animate={{ scale: 1,    opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 28 }}
      className="rounded-2xl border border-cream bg-white shadow-card p-6 flex flex-col gap-5 w-full max-w-2xl mx-auto"
      role="region"
      aria-label="Research Plan"
    >
      {/* ── Header ── */}
      <div className="flex items-center gap-2.5">
        <ClipboardList size={20} color={color.orange} strokeWidth={1.75} />
        <h2
          className="font-heading text-xl leading-tight"
          style={{ color: color.plum }}
        >
          Research Plan
        </h2>
      </div>

      {/* ── Scope ── */}
      <div className="flex flex-col gap-1">
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: color.mauve }}>
          Scope
        </span>
        <p className="text-sm italic leading-relaxed" style={{ color: color.mauve }}>
          {plan.scope}
        </p>
      </div>

      {/* ── Query variants ── */}
      <div className="flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: color.mauve }}>
          Query Variants
        </span>

        <div className="flex flex-wrap gap-2" role="list" aria-label="Query variants">
          {variants.map((v, i) => (
            <span
              key={i}
              role="listitem"
              className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium border"
              style={{
                backgroundColor: color.orange20,
                borderColor:     color.cream,
                color:           color.plum,
              }}
            >
              {v}
              {isEditing && (
                <button
                  type="button"
                  onClick={() => removeVariant(i)}
                  aria-label={`Remove query variant: ${v}`}
                  className="rounded-full hover:bg-orange/20 transition-colors p-0.5"
                  style={{ color: color.mauve }}
                >
                  <X size={12} />
                </button>
              )}
            </span>
          ))}

          {/* Inline input to add new variant */}
          {isEditing && (
            <div
              className="inline-flex items-center gap-1 rounded-full border px-2 py-1"
              style={{ borderColor: color.orange, backgroundColor: color.surface }}
            >
              <input
                ref={inputRef}
                value={inputVal}
                onChange={e => setInputVal(e.target.value)}
                onKeyDown={handleInputKeyDown}
                placeholder="Add variant…"
                className="text-sm bg-transparent outline-none w-32 placeholder:text-mauve/50"
                style={{ color: color.plum }}
                aria-label="New query variant"
              />
              <button
                type="button"
                onClick={addVariant}
                aria-label="Add variant"
                disabled={!inputVal.trim()}
                className="text-orange hover:text-plum disabled:opacity-30 transition-colors"
              >
                <Plus size={14} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── Actions ── */}
      <div className="flex items-center gap-3 pt-1">
        {/* Edit toggle */}
        <button
          type="button"
          onClick={handleEditToggle}
          className="rounded-lg border px-4 py-2 text-sm font-medium transition-colors"
          style={{
            borderColor:     color.cream,
            color:           isEditing ? color.orange : color.mauve,
            backgroundColor: 'transparent',
          }}
          aria-pressed={isEditing}
        >
          {isEditing ? 'Done Editing' : 'Edit'}
        </button>

        {/* Approve */}
        <motion.button
          type="button"
          onClick={onApprove}
          whileHover={{ scale: 1.02 }}
          whileTap={  { scale: 0.98 }}
          className="inline-flex items-center gap-2 rounded-lg px-5 py-2 text-sm font-semibold transition-colors"
          style={{
            backgroundColor: color.orange,
            color:           color.plum,
          }}
        >
          Approve &amp; Continue
          <ArrowRight size={15} strokeWidth={2} />
        </motion.button>
      </div>
    </motion.div>
  );
}
