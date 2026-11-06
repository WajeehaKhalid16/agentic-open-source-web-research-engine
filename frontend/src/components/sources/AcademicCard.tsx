import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import type { Source } from '../../types/api';
import { VenueBadge } from '../shared/VenueBadge';

interface Props { source: Source }

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);
  const doCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <button
      onClick={doCopy}
      className="flex items-center gap-1 text-xs text-[#FC9A64] hover:text-[#FDB486] font-medium"
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? 'Copied' : label}
    </button>
  );
}

function Collapsible({ label, children }: { label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-[#FDE0B8] rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium text-[#7B515F] bg-[#FEF4E6] hover:bg-[#FDE0B8] transition-colors"
        aria-expanded={open}
      >
        {label}
        <span className="text-[#FC9A64]">{open ? '−' : '+'}</span>
      </button>
      {open && <div className="px-4 py-3 text-sm text-[#23131E] leading-relaxed bg-white">{children}</div>}
    </div>
  );
}

export function AcademicCard({ source }: Props) {
  const a = source.academic;
  if (!a) return null;

  const bibtex = `@article{${source.source_id},\n  title={${source.title}},\n  author={${a.authors.join(' and ')}},\n  year={${a.year}},\n  url={${source.url}}${a.doi ? `,\n  doi={${a.doi}}` : ''}\n}`;
  const apa = `${a.authors.join(', ')} (${a.year}). ${source.title}. ${a.venue}. ${a.doi ? `https://doi.org/${a.doi}` : source.url}`;

  return (
    <div className="rounded-xl border border-[#FDE0B8] bg-white shadow-card p-5 flex flex-col gap-4">
      {/* Title + venue */}
      <div className="flex flex-col gap-2">
        <VenueBadge venue={a.venue} venueType={a.venue_type} peerReviewed={a.peer_reviewed} />
        <h3 className="font-heading text-lg text-[#23131E] leading-snug">{source.title}</h3>
        <p className="text-sm text-[#7B515F]">
          {a.authors.join(', ')} · {a.year}
          {a.doi && <> · <a href={`https://doi.org/${a.doi}`} target="_blank" rel="noopener noreferrer" className="text-[#FC9A64] hover:underline">{a.doi}</a></>}
          {a.citation_count != null && <> · {a.citation_count} citations</>}
        </p>
      </div>

      {/* TL;DR */}
      <div className="bg-[#FEF4E6] rounded-lg px-4 py-3 border border-[#FDE0B8]">
        <span className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Cited TL;DR</span>
        <p className="text-sm text-[#23131E] mt-1 leading-relaxed">{a.tldr}</p>
      </div>

      {/* Meta pills */}
      <div className="flex flex-wrap gap-2">
        {[
          { label: 'Task', value: a.task },
          { label: 'Domain', value: a.domain },
          { label: 'Method', value: a.method },
        ].map(({ label, value }) => value && (
          <span key={label} className="text-xs px-2.5 py-1 rounded-full bg-[#E8DADE] text-[#3A1A28] border border-[#7B515F]/20">
            <span className="font-semibold">{label}:</span> {value}
          </span>
        ))}
      </div>

      {/* Key results table */}
      {a.key_results.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-[#FDE0B8]">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-[#23131E] text-white">
                <th className="px-3 py-2 text-left font-semibold">Metric</th>
                <th className="px-3 py-2 text-left font-semibold">Value</th>
              </tr>
            </thead>
            <tbody>
              {a.key_results.map((r, i) => (
                <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-[#FEF4E6]'}>
                  <td className="px-3 py-2 text-[#23131E]">{r.metric}</td>
                  <td className="px-3 py-2 text-[#23131E]">
                    {r.value}
                    {r.vendor_reported && (
                      <span className="ml-1.5 text-[10px] bg-[#FEE9DC] text-[#7B3010] border border-[#FC9A64] px-1 py-0.5 rounded font-medium">vendor</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Baselines */}
      {a.baselines.length > 0 && (
        <p className="text-xs text-[#7B515F]">
          <span className="font-semibold">Baselines:</span> {a.baselines.join(', ')}
        </p>
      )}

      {/* Collapsibles */}
      <div className="flex flex-col gap-2">
        <Collapsible label="Abstract">{a.abstract}</Collapsible>
        {a.limitations && <Collapsible label="Limitations">{a.limitations}</Collapsible>}
        {a.has_ablations && <Collapsible label="Experiments & Ablations">See source for full experimental details and ablation study results.</Collapsible>}
      </div>

      {/* Export buttons */}
      <div className="flex gap-3 pt-1">
        <CopyButton text={bibtex} label="Copy BibTeX" />
        <CopyButton text={apa} label="Copy APA" />
      </div>
    </div>
  );
}
