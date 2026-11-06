import { Search } from 'lucide-react';
import { cn } from '../../lib/utils';

interface Props {
  icon?: React.ReactNode;
  message: string;
  className?: string;
}

export function EmptyCard({ icon, message, className }: Props) {
  return (
    <div
      className={cn(
        'rounded-xl border border-[#FDE0B8] bg-[#FEF4E6] p-10 flex flex-col items-center gap-4 text-center',
        className
      )}
    >
      <div className="text-[#7B515F] opacity-50">
        {icon ?? <Search size={32} strokeWidth={1.5} />}
      </div>
      <p className="text-[#7B515F] text-sm max-w-xs">{message}</p>
    </div>
  );
}
