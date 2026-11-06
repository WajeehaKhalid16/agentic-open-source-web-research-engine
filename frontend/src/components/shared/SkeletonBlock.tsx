import { cn } from '../../lib/utils';

interface Props {
  className?: string;
  lines?: number;
}

export function SkeletonBlock({ className, lines = 1 }: Props) {
  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'h-4 rounded-md bg-[#FDE0B8] animate-pulse',
            i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'
          )}
        />
      ))}
    </div>
  );
}
