import type { ReportFinding } from '../../types/api';
import { InlineCitation } from './InlineCitation';

interface Props {
  finding: ReportFinding;
  onCitationClick: (refId: number) => void;
}

export function ReportSection({ finding, onCitationClick }: Props) {
  return (
    <section className="flex flex-col gap-3">
      <h3 className="font-heading text-xl text-[#23131E]">{finding.theme}</h3>
      <p className="text-[#23131E] leading-[1.75] max-w-report">
        {finding.body}
        {finding.citations.map((ref) => (
          <InlineCitation key={ref} refId={ref} onClick={onCitationClick} />
        ))}
      </p>
    </section>
  );
}
