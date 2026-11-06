interface Props {
  refId: number;
  onClick: (refId: number) => void;
}

export function InlineCitation({ refId, onClick }: Props) {
  return (
    <button
      onClick={() => onClick(refId)}
      aria-label={`Open evidence for citation ${refId}`}
      className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-[#FEE9DC] border border-[#FC9A64] text-[#FC9A64] font-mono font-bold hover:bg-[#FC9A64] hover:text-[#23131E] transition-colors ml-0.5 align-super leading-none focus-visible:shadow-focus"
      style={{ verticalAlign: 'super', fontSize: '0.65rem' }}
    >
      {refId}
    </button>
  );
}
