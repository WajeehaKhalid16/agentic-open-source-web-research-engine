import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, ClipboardList } from 'lucide-react';
import { RootLayout } from '../components/layout/RootLayout';
import { AmbientBackground } from '../components/layout/AmbientBackground';
import { StagePipeline } from '../components/live/StagePipeline';
import { LiveSourceFeed } from '../components/live/LiveSourceFeed';
import { LiveLogStream } from '../components/live/LiveLogStream';
import { useRunEvents } from '../hooks/useRunEvents';
import type { StageId } from '../types/api';

export function LiveRunPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const events = useRunEvents(id ?? null, !!id);
  const [planDismissed, setPlanDismissed] = useState(false);
  const [planVariants, setPlanVariants] = useState<string[]>([]);

  // Sync variants from plan
  useEffect(() => {
    if (events.plan) setPlanVariants(events.plan.query_variants);
  }, [events.plan]);

  // Navigate to results when complete
  useEffect(() => {
    if (events.complete && id) {
      const timer = setTimeout(() => navigate(`/runs/${id}`), 500);
      return () => clearTimeout(timer);
    }
  }, [events.complete, id, navigate]);

  const isSearching = events.stages.search === 'running' || events.stages.search === 'complete';
  const showPlan = events.plan && !planDismissed && events.stages.search === 'idle';

  return (
    <RootLayout>
      <AmbientBackground />

      {/* Header */}
      <header className="relative z-10 flex items-center px-6 py-4 border-b border-[#FDE0B8]/60">
        <span className="font-heading text-xl text-[#23131E] font-semibold tracking-tight">Research Engine</span>
        {events.complete && (
          <span className="ml-auto text-sm text-green-600 font-medium flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Complete — loading results…
          </span>
        )}
      </header>

      <main className="relative z-10 max-w-4xl mx-auto px-6 py-10 flex flex-col gap-10">
        {/* Stage pipeline */}
        <section className="bg-white/80 backdrop-blur-sm rounded-2xl border border-[#FDE0B8] p-6 shadow-card">
          <StagePipeline stageStates={events.stages} />
        </section>

        {/* Plan approval */}
        {showPlan && events.plan && (
          <motion.section
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 28 }}
            className="bg-white rounded-2xl border border-[#FDE0B8] p-6 shadow-card flex flex-col gap-4"
          >
            <div className="flex items-center gap-2">
              <ClipboardList size={18} className="text-[#FC9A64]" />
              <h2 className="font-heading text-xl text-[#23131E]">Research Plan</h2>
            </div>
            <p className="text-sm italic text-[#7B515F]">{events.plan.scope}</p>

            {/* Editable variants */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide">Query variants</span>
              <div className="flex flex-wrap gap-2">
                {planVariants.map((v, i) => (
                  <div key={i} className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-[#FEE9DC] border border-[#FC9A64] text-sm text-[#23131E]">
                    {v}
                    <button
                      onClick={() => setPlanVariants((vs) => vs.filter((_, idx) => idx !== i))}
                      className="ml-1 text-[#7B515F] hover:text-[#FC9A64]"
                      aria-label={`Remove variant: ${v}`}
                    >×</button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setPlanDismissed(true)}
                className="px-4 py-2 rounded-xl border border-[#FDE0B8] text-sm text-[#7B515F] hover:border-[#FC9A64] hover:text-[#23131E] transition-colors"
              >
                Edit later
              </button>
              <button
                onClick={() => setPlanDismissed(true)}
                className="flex items-center gap-2 px-5 py-2 rounded-xl bg-[#FC9A64] text-[#23131E] font-semibold text-sm hover:bg-[#FDB486] transition-colors"
              >
                Approve & Continue <ArrowRight size={15} />
              </button>
            </div>
          </motion.section>
        )}

        {/* Live source feed */}
        <LiveSourceFeed sources={events.sources} isSearching={isSearching} />

        {/* Log stream */}
        <LiveLogStream logs={events.logs as Array<{ stage: StageId; level: 'info' | 'warn' | 'error'; message: string; ts: string }>} />
      </main>
    </RootLayout>
  );
}
