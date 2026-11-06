import { AnimatePresence } from 'framer-motion';
import { Search } from 'lucide-react';
import type { Source } from '../../types/api';
import { SourceCard } from './SourceCard';
import { SourceCardSkeleton } from './SourceCardSkeleton';
import { EmptyCard } from '../shared/EmptyCard';

interface Props {
  sources: Source[];
  isSearching: boolean;
}

export function LiveSourceFeed({ sources, isSearching }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-heading text-lg text-[#23131E]">Sources</h2>
      {sources.length === 0 && isSearching && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[...Array(4)].map((_, i) => <SourceCardSkeleton key={i} />)}
        </div>
      )}
      {sources.length === 0 && !isSearching && (
        <EmptyCard icon={<Search size={28} strokeWidth={1.5} />} message="Waiting for search to begin…" />
      )}
      <AnimatePresence>
        {sources.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {sources.map((s, i) => (
              <SourceCard key={s.source_id} source={s} index={i} />
            ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
