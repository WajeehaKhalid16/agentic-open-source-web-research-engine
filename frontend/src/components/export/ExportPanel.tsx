import { useState } from 'react';
import { FileText, Code, FileDown } from 'lucide-react';
import { downloadExport } from '../../api/client';
import { ErrorCard } from '../shared/ErrorCard';

interface Props { runId: string }

export function ExportPanel({ runId }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const download = async (format: 'md' | 'html' | 'json') => {
    setLoading(format);
    setError(null);
    try {
      const blob = await downloadExport(runId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `research-${runId.slice(0, 8)}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError('Download failed. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const formats = [
    { id: 'md' as const,   label: 'Markdown Report',  icon: <FileText size={16} />,  desc: 'Clean Markdown for notes or docs' },
    { id: 'html' as const, label: 'HTML Report',       icon: <Code size={16} />,      desc: 'Styled, shareable HTML file' },
    { id: 'json' as const, label: 'JSON Data',         icon: <FileDown size={16} />,  desc: 'Full structured data for analysis' },
  ];

  return (
    <div className="flex flex-col gap-6 max-w-md">
      <div>
        <h3 className="font-heading text-2xl text-[#23131E] mb-1">Export Research</h3>
        <p className="text-sm text-[#7B515F]">Download the complete report and all supporting data.</p>
      </div>

      {error && <ErrorCard message={error} onRetry={() => setError(null)} />}

      <div className="flex flex-col gap-3">
        {formats.map((f) => (
          <button
            key={f.id}
            onClick={() => download(f.id)}
            disabled={!!loading}
            className="flex items-center gap-4 px-5 py-4 rounded-xl border border-[#FDE0B8] bg-white shadow-card hover:border-[#FC9A64] hover:bg-[#FEE9DC] transition-colors text-left disabled:opacity-60 group"
          >
            <span className="text-[#FC9A64] group-hover:scale-110 transition-transform">{f.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-semibold text-[#23131E]">{f.label}</p>
              <p className="text-xs text-[#7B515F]">{f.desc}</p>
            </div>
            {loading === f.id && (
              <span className="text-xs text-[#7B515F] animate-pulse">Preparing…</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
