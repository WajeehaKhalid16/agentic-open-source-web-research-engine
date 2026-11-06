const STOPWORDS = new Set(['the','a','an','in','on','at','is','are','was','were','of','and','or','to','for','with','by','from','as','it','its','this','that','be','been','has','have','had','do','does','did','will','would','could','should','may','might','shall','can','not','but','so','yet','both','either','neither','nor','just','than','then','too','very','also','about','after','before','between','into','through','during','above','below','each','every','all','any','few','more','most','other','some','such','no','only','same','own']);

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

interface Props {
  text: string;
  entities?: string[];
  keyTerms?: string[];
  numbers?: string[];
  strongSpan?: string;
}

export function EntityHighlighter({ text, entities = [], keyTerms = [], numbers = [], strongSpan }: Props) {
  if (!text) return null;

  // If we have a strong span, highlight that one span strongly
  if (strongSpan && text.includes(strongSpan)) {
    const idx = text.indexOf(strongSpan);
    return (
      <span>
        {text.slice(0, idx)}
        <mark className="bg-[#FC9A64] text-[#23131E] font-semibold rounded-sm px-0.5 not-italic">
          {strongSpan}
        </mark>
        {text.slice(idx + strongSpan.length)}
      </span>
    );
  }

  // Soft highlights for entities, keyTerms, numbers (skip stopwords)
  const terms = [...entities, ...keyTerms, ...numbers]
    .filter((t) => t.length > 2 && !STOPWORDS.has(t.toLowerCase()))
    .sort((a, b) => b.length - a.length); // longest first

  if (!terms.length) return <span>{text}</span>;

  const pattern = new RegExp(`(${terms.map(escapeRegex).join('|')})`, 'gi');
  const parts = text.split(pattern);

  return (
    <span>
      {parts.map((part, i) =>
        pattern.test(part) ? (
          <mark key={i} className="bg-[#FEE9DC] text-[#23131E] rounded-sm px-0.5 not-italic">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
}
