import { useState } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';

interface Props {
  label: string;
  chips: string[];
  onChange: (chips: string[]) => void;
  placeholder?: string;
}

export function KeywordChipEditor({ label, chips, onChange, placeholder = 'Add term…' }: Props) {
  const [input, setInput] = useState('');

  const add = (val: string) => {
    const v = val.trim().replace(/,$/, '');
    if (v && !chips.includes(v)) onChange([...chips, v]);
    setInput('');
  };

  const remove = (chip: string) => onChange(chips.filter((c) => c !== chip));

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      add(input);
    } else if (e.key === 'Backspace' && !input && chips.length) {
      remove(chips[chips.length - 1]);
    }
  };

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">{label}</label>
      <div
        className={cn(
          'flex flex-wrap gap-1.5 p-2.5 rounded-lg border border-[#FDE0B8] bg-white min-h-[42px]',
          'focus-within:shadow-focus transition-shadow'
        )}
      >
        {chips.map((chip) => (
          <span
            key={chip}
            className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#FEE9DC] text-[#23131E] text-sm font-medium border border-[#FC9A64]"
          >
            {chip}
            <button
              onClick={() => remove(chip)}
              aria-label={`Remove ${chip}`}
              className="hover:text-[#FC9A64] transition-colors"
            >
              <X size={12} />
            </button>
          </span>
        ))}
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          onBlur={() => input && add(input)}
          placeholder={chips.length === 0 ? placeholder : ''}
          className="flex-1 min-w-[100px] outline-none text-sm text-[#23131E] bg-transparent placeholder:text-[#7B515F]/50"
        />
      </div>
    </div>
  );
}
