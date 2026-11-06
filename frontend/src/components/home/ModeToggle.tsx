import { Globe, Newspaper, GraduationCap } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { RunMode } from '../../types/api';

interface Props {
  value: RunMode;
  onChange: (mode: RunMode) => void;
}

const modes: { id: RunMode; label: string; icon: React.ReactNode }[] = [
  { id: 'web',      label: 'Web',      icon: <Globe size={15} /> },
  { id: 'news',     label: 'News',     icon: <Newspaper size={15} /> },
  { id: 'academic', label: 'Academic', icon: <GraduationCap size={15} /> },
];

export function ModeToggle({ value, onChange }: Props) {
  return (
    <div
      className="inline-flex rounded-full border border-[#FDE0B8] bg-white shadow-[0_1px_3px_rgba(35,19,30,0.07),_0_4px_16px_rgba(35,19,30,0.05)] p-1"
      role="group"
      aria-label="Research mode"
    >
      {modes.map((m) => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          aria-pressed={value === m.id}
          className={cn(
            'flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
            value === m.id
              ? 'bg-[#FC9A64] text-[#23131E] shadow-sm'
              : 'text-[#7B515F] hover:text-[#23131E] hover:bg-[#FEF4E6]'
          )}
        >
          {m.icon}
          {m.label}
        </button>
      ))}
    </div>
  );
}
