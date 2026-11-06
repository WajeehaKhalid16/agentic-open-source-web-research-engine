import { cn } from '../../lib/utils';

interface Props {
  venue: string;
  venueType: 'conference' | 'journal' | 'preprint';
  peerReviewed: boolean;
  className?: string;
}

const typeColors: Record<
  'conference' | 'journal' | 'preprint',
  { bg: string; text: string; border: string }
> = {
  conference: { bg: '#FEE9DC', text: '#7B3010', border: '#FC9A64' },
  journal:    { bg: '#E8DADE', text: '#3A1A28', border: '#7B515F' },
  preprint:   { bg: '#FEF4E6', text: '#7B5700', border: '#FDE0B8' },
};

export function VenueBadge({ venue, venueType, peerReviewed, className }: Props) {
  const c = typeColors[venueType];
  return (
    <div className={cn('flex items-center gap-2 flex-wrap', className)}>
      <span
        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border"
        style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
      >
        {venue}
      </span>
      {peerReviewed && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs border border-green-300 bg-green-50 text-green-700">
          Peer-reviewed
        </span>
      )}
    </div>
  );
}
