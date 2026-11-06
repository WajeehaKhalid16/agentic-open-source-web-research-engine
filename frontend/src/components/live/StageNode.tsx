import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import type { StageId, StageStatus } from '../../types/api';

interface Props {
  id: StageId;
  label: string;
  status: StageStatus;
  isLast?: boolean;
}

const statusConfig: Record<StageStatus, { icon: React.ReactNode; nodeClass: string; textClass: string }> = {
  idle: {
    icon: <span className="w-2 h-2 rounded-full bg-[#FDE0B8]" />,
    nodeClass: 'border-[#FDE0B8] bg-white',
    textClass: 'text-[#7B515F]',
  },
  running: {
    icon: <Loader2 size={14} className="animate-spin text-[#FC9A64]" />,
    nodeClass: 'border-[#FC9A64] bg-[#FEE9DC]',
    textClass: 'text-[#FC9A64]',
  },
  complete: {
    icon: <CheckCircle2 size={14} className="text-white" />,
    nodeClass: 'border-[#FC9A64] bg-[#FC9A64]',
    textClass: 'text-[#23131E] font-semibold',
  },
  error: {
    icon: <AlertCircle size={14} className="text-[#C17C75]" />,
    nodeClass: 'border-[#C17C75] bg-[#F0E0DF]',
    textClass: 'text-[#C17C75]',
  },
};

export function StageNode({ id: _id, label, status, isLast }: Props) {
  const cfg = statusConfig[status];
  return (
    <div className="flex items-center">
      {/* Node */}
      <div className="flex flex-col items-center gap-1.5">
        <motion.div
          layout
          animate={status === 'running' ? { boxShadow: ['0 0 0 0px rgba(252,154,100,0.4)', '0 0 0 6px rgba(252,154,100,0)', '0 0 0 0px rgba(252,154,100,0.4)'] } : { boxShadow: '0 0 0 0px rgba(252,154,100,0)' }}
          transition={{ duration: 1.4, repeat: status === 'running' ? Infinity : 0 }}
          className={`w-9 h-9 rounded-full border-2 flex items-center justify-center transition-colors duration-300 ${cfg.nodeClass}`}
        >
          {cfg.icon}
        </motion.div>
        <span className={`text-xs whitespace-nowrap ${cfg.textClass}`}>{label}</span>
      </div>

      {/* Connector */}
      {!isLast && (
        <div className="relative mx-1 w-8 h-0.5 bg-[#FDE0B8] rounded-full overflow-hidden mt-[-18px]">
          <motion.div
            className="absolute inset-y-0 left-0 bg-[#FC9A64] rounded-full"
            initial={{ width: '0%' }}
            animate={{ width: status === 'complete' ? '100%' : '0%' }}
            transition={{ duration: 0.4 }}
          />
        </div>
      )}
    </div>
  );
}
