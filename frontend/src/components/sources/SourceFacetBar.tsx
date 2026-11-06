import { Globe, Newspaper, GraduationCap, FileText, Code2, BarChart3 } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { SourceType } from '../../types/api';

interface Props {
  selected: SourceType | 'all';
  onChange: (type: SourceType | 'all') => void;
  counts: Partial<Record<SourceType | 'all', number>>;
}

const facets: { id: SourceType | 'all'; label: string; icon?: React.ReactNode }[] = [
  { id: 'all',       label: 'All' },
  { id: 'web',       label: 'Web',        icon: <Globe size={13} /> },
  { id: 'news',      label: 'News',       icon: <Newspaper size={13} /> },
  { id: 'academic',  label: 'Academic',   icon: <GraduationCap size={13} /> },
  { id: 'official',  label: 'Official',   icon: <FileText size={13} /> },
  { id: 'code',      label: 'Code',       icon: <Code2 size={13} /> },
  { id: 'benchmark', label: 'Benchmarks', icon: <BarChart3 size={13} /> },
];

export function SourceFacetBar({ selected, onChange, counts }: Props) {
  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label="Filter sources by type">
      {facets.map((f) => (
        <button
          key={f.id}
          onClick={() => onChange(f.id)}
          aria-pressed={selected === f.id}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-colors',
            selected === f.id
              ? 'bg-[#FC9A64] border-[#FC9A64] text-[#23131E] font-semibold'
              : 'bg-white border-[#FDE0B8] text-[#7B515F] hover:border-[#FC9A64] hover:text-[#23131E]'
          )}
        >
          {f.icon}
          {f.label}
          {counts[f.id] !== undefined && (
            <span className={cn('ml-0.5 text-xs', selected === f.id ? 'text-[#23131E]' : 'text-[#7B515F]/70')}>
              {counts[f.id]}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
