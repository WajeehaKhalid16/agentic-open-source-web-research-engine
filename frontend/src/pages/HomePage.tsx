import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, SlidersHorizontal, History } from 'lucide-react';
import { RootLayout } from '../components/layout/RootLayout';
import { AmbientBackground } from '../components/layout/AmbientBackground';
import { BackendStatusPill } from '../components/home/BackendStatusPill';
import { ModeToggle } from '../components/home/ModeToggle';
import { FilterPanel, type FilterValues } from '../components/home/FilterPanel';
import { ExampleQueryGrid } from '../components/home/ExampleQueryGrid';
import { PastRunsSlideOver } from '../components/home/PastRunsSlideOver';
import { createRun } from '../api/client';
import type { RunMode } from '../types/api';

const EXAMPLE_QUERIES = [
  'What are recent AI applications in disaster management?',
  'How do large language models perform on reasoning benchmarks?',
  'State of open-source multimodal models in 2024',
  'What methods reduce hallucination in RAG systems?',
];

const DEFAULT_FILTERS: FilterValues = {
  dateFrom: '', dateTo: '',
  depth: 2, maxSources: 8,
  language: 'en',
  sourceTypes: ['web', 'news', 'academic'],
  mustInclude: [], mustExclude: [],
};

export function HomePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<RunMode>('web');
  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState<FilterValues>(DEFAULT_FILTERS);
  const [showPastRuns, setShowPastRuns] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const { run_id } = await createRun({
        query: query.trim(),
        mode,
        max_sources: filters.maxSources,
        depth: filters.depth,
        date_range: { from: filters.dateFrom || null, to: filters.dateTo || null },
        language: filters.language,
        source_types: filters.sourceTypes,
        must_include: filters.mustInclude,
        must_exclude: filters.mustExclude,
      });
      navigate(`/runs/${run_id}/live`);
    } catch {
      setError('Could not start research. Is the API running at localhost:8000?');
      setSubmitting(false);
    }
  };

  return (
    <RootLayout>
      <AmbientBackground />

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4">
        <span className="font-heading text-xl text-[#23131E] font-semibold tracking-tight">Research Engine</span>
        <div className="flex items-center gap-3">
          <BackendStatusPill />
          <button
            onClick={() => setShowPastRuns(true)}
            className="flex items-center gap-1.5 text-sm text-[#7B515F] hover:text-[#23131E] transition-colors px-3 py-1.5 rounded-lg hover:bg-white/60"
          >
            <History size={15} />
            Past runs
          </button>
        </div>
      </header>

      {/* Main */}
      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.48 }}
        className="relative z-10 flex flex-col items-center px-6 py-16 gap-10 min-h-[calc(100vh-64px)]"
      >
        {/* Hero heading */}
        <div className="text-center max-w-2xl">
          <h1 className="font-heading text-4xl text-[#23131E] mb-3 text-balance">
            Agentic Web Research
          </h1>
          <p className="text-[#7B515F] text-lg leading-relaxed">
            Ask a question. Get a cited, evidence-backed report.
          </p>
        </div>

        {/* Search section */}
        <div className="w-full max-w-2xl flex flex-col gap-4">
          {/* Mode toggle */}
          <div className="flex justify-center">
            <ModeToggle value={mode} onChange={setMode} />
          </div>

          {/* Search form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What do you want to research?"
                aria-label="Research query"
                className="flex-1 py-4 px-5 rounded-2xl border border-[#FDE0B8] bg-white shadow-card text-[#23131E] placeholder:text-[#7B515F]/60 text-base focus:outline-none focus:shadow-focus transition-shadow"
              />
              <button
                type="submit"
                disabled={!query.trim() || submitting}
                className="flex items-center gap-2 px-6 py-4 rounded-2xl bg-[#FC9A64] text-[#23131E] font-semibold hover:bg-[#FDB486] transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-card"
              >
                <Search size={18} />
                {submitting ? 'Starting…' : 'Research'}
              </button>
            </div>

            {error && (
              <p className="text-sm text-[#C17C75] px-1">{error}</p>
            )}

            {/* Filter toggle */}
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setFilterOpen((v) => !v)}
                className="flex items-center gap-1.5 text-sm text-[#7B515F] hover:text-[#23131E] transition-colors px-3 py-1.5 rounded-lg hover:bg-white/60"
                aria-expanded={filterOpen}
                aria-controls="filter-panel"
              >
                <SlidersHorizontal size={14} />
                {filterOpen ? 'Hide filters' : 'Filters'}
                {(filters.mustInclude.length + filters.mustExclude.length > 0) && (
                  <span className="ml-1 w-4 h-4 rounded-full bg-[#FC9A64] text-[#23131E] text-[10px] flex items-center justify-center font-bold">
                    {filters.mustInclude.length + filters.mustExclude.length}
                  </span>
                )}
              </button>
            </div>

            <div id="filter-panel">
              <FilterPanel open={filterOpen} values={filters} onChange={setFilters} />
            </div>
          </form>

          <ExampleQueryGrid queries={EXAMPLE_QUERIES} onSelect={(q) => setQuery(q)} />
        </div>
      </motion.main>

      <PastRunsSlideOver open={showPastRuns} onClose={() => setShowPastRuns(false)} />
    </RootLayout>
  );
}
