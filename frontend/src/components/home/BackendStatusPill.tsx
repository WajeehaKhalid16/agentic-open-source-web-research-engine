import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { useHealthCheck } from '../../hooks/useHealthCheck';

export function BackendStatusPill() {
  const status = useHealthCheck();

  const config = {
    checking: {
      icon: <Loader2 size={12} className="animate-spin" />,
      label: 'Connecting',
      color: 'text-[#7B515F]',
    },
    ok: {
      icon: <CheckCircle2 size={12} />,
      label: 'API Ready',
      color: 'text-green-600',
    },
    error: {
      icon: <AlertCircle size={12} />,
      label: 'API Offline',
      color: 'text-[#C17C75]',
    },
  }[status];

  return (
    <div
      className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-white border border-[#FDE0B8] shadow-[0_1px_3px_rgba(35,19,30,0.07),_0_4px_16px_rgba(35,19,30,0.05)] ${config.color}`}
    >
      {config.icon}
      {config.label}
    </div>
  );
}
