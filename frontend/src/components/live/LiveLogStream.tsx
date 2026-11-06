import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Terminal, ChevronDown, ChevronUp } from 'lucide-react';
import type { StageId } from '../../types/api';

interface LogEntry {
  stage: StageId;
  level: 'info' | 'warn' | 'error';
  message: string;
  ts: string;
}

interface Props {
  logs: LogEntry[];
}

const levelColor = { info: '#6B5068', warn: '#FC9A64', error: '#C17C75' };

function formatTime(ts: string): string {
  try { return new Date(ts).toLocaleTimeString('en-US', { hour12: false }); } catch { return ts; }
}

export function LiveLogStream({ logs }: Props) {
  const [open, setOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs, open]);

  return (
    <div className="rounded-xl border border-[#FDE0B8] bg-white overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-3 text-sm font-semibold text-[#7B515F] hover:bg-[#FEF4E6] transition-colors"
        aria-expanded={open}
      >
        <span className="flex items-center gap-2">
          <Terminal size={15} />
          Run Log
          {logs.length > 0 && (
            <span className="text-xs font-mono bg-[#FDE0B8] text-[#7B515F] px-2 py-0.5 rounded-full">{logs.length}</span>
          )}
        </span>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
            transition={{ duration: 0.24 }}
            className="overflow-hidden"
          >
            <pre className="text-xs font-mono px-5 py-3 max-h-48 overflow-y-auto scrollbar-thin bg-[#FFF7EC] leading-relaxed">
              {logs.length === 0 ? (
                <span className="text-[#7B515F]">No log entries yet…</span>
              ) : (
                logs.map((entry, i) => (
                  <div key={i} style={{ color: levelColor[entry.level] }}>
                    [{formatTime(entry.ts)}] [{entry.stage.toUpperCase()}] {entry.message}
                  </div>
                ))
              )}
              <div ref={bottomRef} />
            </pre>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
