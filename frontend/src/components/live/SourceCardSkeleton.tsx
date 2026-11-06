import { SkeletonBlock } from '../shared/SkeletonBlock';

export function SourceCardSkeleton() {
  return (
    <div className="rounded-xl border border-[#FDE0B8] bg-white shadow-card p-4 flex flex-col gap-3 animate-pulse">
      <div className="flex items-center justify-between gap-3">
        <div className="h-4 w-2/3 rounded-md bg-[#FDE0B8]" />
        <div className="h-5 w-12 rounded-full bg-[#FDE0B8]" />
      </div>
      <div className="h-3 w-1/2 rounded-md bg-[#FDE0B8]" />
      <SkeletonBlock lines={2} />
    </div>
  );
}
