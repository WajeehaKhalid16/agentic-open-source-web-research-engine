import { AnimatePresence, motion } from 'framer-motion';
import type { SourceType } from '../../types/api';
import { KeywordChipEditor } from './KeywordChipEditor';

export interface FilterValues {
  dateFrom: string;
  dateTo: string;
  depth: number;
  maxSources: number;
  language: string;
  sourceTypes: SourceType[];
  mustInclude: string[];
  mustExclude: string[];
}

interface Props {
  open: boolean;
  values: FilterValues;
  onChange: (values: FilterValues) => void;
}

const SOURCE_TYPE_OPTIONS: { id: SourceType; label: string }[] = [
  { id: 'web', label: 'Web' },
  { id: 'news', label: 'News' },
  { id: 'academic', label: 'Academic' },
  { id: 'official', label: 'Official docs' },
  { id: 'code', label: 'Code repos' },
  { id: 'benchmark', label: 'Benchmarks' },
];

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'es', label: 'Spanish' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ar', label: 'Arabic' },
];

function set<K extends keyof FilterValues>(values: FilterValues, key: K, val: FilterValues[K]): FilterValues {
  return { ...values, [key]: val };
}

function toggleSourceType(values: FilterValues, type: SourceType): FilterValues {
  const has = values.sourceTypes.includes(type);
  return set(values, 'sourceTypes', has ? values.sourceTypes.filter((t) => t !== type) : [...values.sourceTypes, type]);
}

export function FilterPanel({ open, values, onChange }: Props) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
          className="overflow-hidden"
        >
          <div className="border border-[#FDE0B8] rounded-xl bg-white p-5 flex flex-col gap-5 mt-2">
            {/* Date range */}
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">From</label>
                <input
                  type="date"
                  value={values.dateFrom}
                  onChange={(e) => onChange(set(values, 'dateFrom', e.target.value))}
                  className="border border-[#FDE0B8] rounded-lg px-3 py-2 text-sm text-[#23131E] bg-white focus:outline-none focus:shadow-focus"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">To</label>
                <input
                  type="date"
                  value={values.dateTo}
                  onChange={(e) => onChange(set(values, 'dateTo', e.target.value))}
                  className="border border-[#FDE0B8] rounded-lg px-3 py-2 text-sm text-[#23131E] bg-white focus:outline-none focus:shadow-focus"
                />
              </div>
            </div>

            {/* Depth & Max sources */}
            <div className="grid grid-cols-2 gap-5">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">
                  Search depth <span className="text-[#FC9A64] font-bold">{values.depth}</span>
                </label>
                <input
                  type="range" min={1} max={3} step={1}
                  value={values.depth}
                  onChange={(e) => onChange(set(values, 'depth', Number(e.target.value)))}
                  className="accent-[#FC9A64] h-1.5 rounded-full"
                />
                <div className="flex justify-between text-xs text-[#7B515F]">
                  <span>Shallow</span><span>Deep</span>
                </div>
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Max sources</label>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onChange(set(values, 'maxSources', Math.max(3, values.maxSources - 1)))}
                    className="w-8 h-8 rounded-lg border border-[#FDE0B8] flex items-center justify-center text-[#7B515F] hover:border-[#FC9A64] hover:text-[#FC9A64] transition-colors"
                  >−</button>
                  <span className="w-8 text-center font-semibold text-[#23131E]">{values.maxSources}</span>
                  <button
                    onClick={() => onChange(set(values, 'maxSources', Math.min(20, values.maxSources + 1)))}
                    className="w-8 h-8 rounded-lg border border-[#FDE0B8] flex items-center justify-center text-[#7B515F] hover:border-[#FC9A64] hover:text-[#FC9A64] transition-colors"
                  >+</button>
                </div>
              </div>
            </div>

            {/* Language */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Language</label>
              <select
                value={values.language}
                onChange={(e) => onChange(set(values, 'language', e.target.value))}
                className="border border-[#FDE0B8] rounded-lg px-3 py-2 text-sm text-[#23131E] bg-white focus:outline-none focus:shadow-focus w-full max-w-xs"
              >
                {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
            </div>

            {/* Source types */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Source types</label>
              <div className="flex flex-wrap gap-2">
                {SOURCE_TYPE_OPTIONS.map((opt) => {
                  const checked = values.sourceTypes.includes(opt.id);
                  return (
                    <label key={opt.id} className="flex items-center gap-1.5 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => onChange(toggleSourceType(values, opt.id))}
                        className="accent-[#FC9A64] rounded"
                      />
                      <span className="text-sm text-[#23131E]">{opt.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Keywords */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <KeywordChipEditor
                label="Must include"
                chips={values.mustInclude}
                onChange={(chips) => onChange(set(values, 'mustInclude', chips))}
                placeholder="e.g. real-time, LLM"
              />
              <KeywordChipEditor
                label="Must exclude"
                chips={values.mustExclude}
                onChange={(chips) => onChange(set(values, 'mustExclude', chips))}
                placeholder="e.g. cryptocurrency"
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
