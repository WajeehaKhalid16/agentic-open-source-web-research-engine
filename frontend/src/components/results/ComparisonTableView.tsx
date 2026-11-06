import type { ComparisonTable } from '../../types/api';
import { InlineCitation } from './InlineCitation';

interface Props {
  table: ComparisonTable;
  onCitationClick: (refId: number) => void;
}

export function ComparisonTableView({ table, onCitationClick }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <h3 className="font-heading text-xl text-[#23131E]">Comparison</h3>
      <div className="overflow-x-auto rounded-xl border border-[#FDE0B8]">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#23131E] text-white text-left">
              {table.headers.map((h, i) => (
                <th key={i} className="px-4 py-3 font-semibold whitespace-nowrap">{h}</th>
              ))}
              <th className="px-4 py-3 font-semibold w-20">Sources</th>
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, ri) => (
              <tr key={ri} className={ri % 2 === 0 ? 'bg-white' : 'bg-[#FEF4E6]'}>
                {row.cells.map((cell, ci) => (
                  <td key={ci} className="px-4 py-3 text-[#23131E]">
                    {cell}
                    {row.vendor_reported[ci] && (
                      <span className="ml-1.5 inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-[#FEE9DC] text-[#7B3010] border border-[#FC9A64] font-medium">
                        vendor
                      </span>
                    )}
                  </td>
                ))}
                <td className="px-4 py-3">
                  {row.citations.map((ref) => (
                    <InlineCitation key={ref} refId={ref} onClick={onCitationClick} />
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
