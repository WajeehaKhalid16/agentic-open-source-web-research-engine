import { AlertTriangle, RefreshCw } from 'lucide-react';
import { cn } from '../../lib/utils';

interface Props {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorCard({ title = 'Something went wrong', message, onRetry, className }: Props) {
  return (
    <div className={cn('rounded-xl border border-[#F0E0DF] bg-[#F0E0DF] p-6 flex flex-col gap-3', className)}>
      <div className="flex items-center gap-2 text-[#C17C75]">
        <AlertTriangle size={18} strokeWidth={2} />
        <span className="font-semibold text-sm" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
          {title}
        </span>
      </div>
      <p className="text-[#6B5068] text-sm leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 text-sm font-medium text-[#FC9A64] hover:text-[#FDB486] transition-colors w-fit"
        >
          <RefreshCw size={14} />
          Try again
        </button>
      )}
    </div>
  );
}
