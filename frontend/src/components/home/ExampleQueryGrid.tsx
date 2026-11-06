import { motion } from 'framer-motion';

interface Props {
  queries: string[];
  onSelect: (query: string) => void;
}

export function ExampleQueryGrid({ queries, onSelect }: Props) {
  if (!queries.length) return null;
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide text-center">Example queries</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {queries.map((q, i) => (
          <motion.button
            key={q}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.28 }}
            onClick={() => onSelect(q)}
            className="text-left px-4 py-3 rounded-xl border border-[#FDE0B8] bg-white text-sm text-[#23131E] hover:border-[#FC9A64] hover:bg-[#FEE9DC] transition-colors shadow-card"
          >
            {q}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
