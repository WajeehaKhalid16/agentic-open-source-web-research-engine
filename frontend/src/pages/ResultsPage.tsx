import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, AlertTriangle } from 'lucide-react';
import { getRun, getSources, getEvidence, getAudit } from '../api/client';
import type { Run, Source, Passage, Audit, AuditResult, SourceType } from '../types/api';
import { RootLayout } from '../components/layout/RootLayout';
import { StatStrip } from '../components/results/StatStrip';
import { ConfidenceBadge } from '../components/results/ConfidenceBadge';
import { ReportSection } from '../components/results/ReportSection';
import { ComparisonTableView } from '../components/results/ComparisonTableView';
import { EvidenceDrawer } from '../components/results/EvidenceDrawer';
import { EntityHighlighter } from '../components/results/EntityHighlighter';
import { AuditTable } from '../components/audit/AuditTable';
import { SourceCard } from '../components/live/SourceCard';
import { AcademicCard } from '../components/sources/AcademicCard';
import { SourceFacetBar } from '../components/sources/SourceFacetBar';
import { ExportPanel } from '../components/export/ExportPanel';
import { ErrorCard } from '../components/shared/ErrorCard';
import { SkeletonBlock } from '../components/shared/SkeletonBlock';
import { EmptyCard } from '../components/shared/EmptyCard';
import { ErrorBoundary } from '../components/shared/ErrorBoundary';

type TabId = 'report' | 'sources' | 'evidence' | 'audit' | 'log' | 'export';

const TABS: { id: TabId; label: string }[] = [
  { id: 'report',   label: 'Report'   },
  { id: 'sources',  label: 'Sources'  },
  { id: 'evidence', label: 'Evidence' },
  { id: 'audit',    label: 'Audit'    },
  { id: 'log',      label: 'Log'      },
  { id: 'export',   label: 'Export'   },
];

function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-6 p-8 max-w-4xl mx-auto">
      <SkeletonBlock lines={1} className="max-w-xs" />
      <div className="grid grid-cols-4 gap-3">
        {[...Array(4)].map((_, i) => <div key={i} className="h-20 rounded-xl bg-[#FDE0B8] animate-pulse" />)}
      </div>
      <SkeletonBlock lines={6} />
    </div>
  );
}

export function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<Run | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [passages, setPassages] = useState<Passage[]>([]);
  const [audit, setAudit] = useState<Audit | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<TabId>('report');
  const [sourceFacet, setSourceFacet] = useState<SourceType | 'all'>('all');

  // Evidence drawer state
  const [drawerPassageId, setDrawerPassageId] = useState<string | null>(null);
  const [drawerAuditResult, setDrawerAuditResult] = useState<AuditResult | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([getRun(id), getSources(id), getEvidence(id), getAudit(id)])
      .then(([r, s, p, a]) => {
        setRun(r); setSources(s); setPassages(p); setAudit(a);
      })
      .catch(() => setFetchError('Could not load research results. The run may not exist.'))
      .finally(() => setLoading(false));
  }, [id]);

  const openEvidence = (passageId: string, auditResult?: AuditResult) => {
    setDrawerPassageId(passageId);
    setDrawerAuditResult(auditResult ?? null);
    setActiveTab('report'); // keep report tab visible
  };

  const openCitation = (refId: number) => {
    // Find passage associated with this ref
    const auditMatch = audit?.results.find((r) => r.ref_id === refId && r.passage_id);
    if (auditMatch?.passage_id) {
      openEvidence(auditMatch.passage_id, auditMatch);
    }
  };

  const drawerPassage = passages.find((p) => p.passage_id === drawerPassageId) ?? null;
  const drawerSource = drawerPassage ? sources.find((s) => s.source_id === drawerPassage.source_id) ?? null : null;

  if (loading) return <RootLayout><LoadingSkeleton /></RootLayout>;
  if (fetchError) return <RootLayout><div className="p-8 max-w-xl mx-auto"><ErrorCard message={fetchError} /></div></RootLayout>;
  if (!run || !run.report) return <RootLayout><div className="p-8 max-w-xl mx-auto"><EmptyCard message="No report found for this run." /></div></RootLayout>;

  const report = run.report;

  // Source facet filtering
  const facetCounts: Partial<Record<SourceType | 'all', number>> = { all: sources.length };
  for (const s of sources) facetCounts[s.type] = (facetCounts[s.type] ?? 0) + 1;
  const filteredSources = sourceFacet === 'all' ? sources : sources.filter((s) => s.type === sourceFacet);

  return (
    <RootLayout>
      {/* Header */}
      <header className="border-b border-[#FDE0B8] bg-white px-6 py-4 flex items-center gap-4">
        <Link to="/" className="text-[#7B515F] hover:text-[#23131E] transition-colors p-1">
          <ArrowLeft size={18} />
        </Link>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-[#7B515F] uppercase tracking-wide mb-0.5">Research run</p>
          <h1 className="font-heading text-xl text-[#23131E] truncate">{run.query}</h1>
        </div>
        <span className="font-mono text-xs text-[#7B515F] hidden sm:block">{run.run_id.slice(0, 8)}</span>
      </header>

      {/* Stats strip */}
      <div className="px-6 py-4 max-w-5xl mx-auto w-full">
        <StatStrip stats={run.stats} elapsedMs={run.elapsed_ms} />
      </div>

      {/* Tabs */}
      <div className="border-b border-[#FDE0B8] bg-white">
        <div className="max-w-5xl mx-auto px-6 flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-[#FC9A64] text-[#23131E]'
                  : 'border-transparent text-[#7B515F] hover:text-[#23131E] hover:border-[#FDE0B8]'
              }`}
              aria-selected={activeTab === tab.id}
              role="tab"
            >
              {tab.label}
              {tab.id === 'audit' && audit && (
                <span className="ml-1.5 text-xs font-mono bg-[#FDE0B8] text-[#7B515F] px-1.5 py-0.5 rounded-full">
                  {Math.round(audit.summary.pct_verified)}%
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      <div className="max-w-5xl mx-auto px-6 py-8 w-full">
        <ErrorBoundary label={activeTab}>

          {/* REPORT TAB */}
          {activeTab === 'report' && (
            <div className="flex flex-col gap-8 max-w-report">
              {/* Executive summary */}
              <section className="flex flex-col gap-3">
                <div className="flex items-center gap-3 flex-wrap">
                  <h2 className="font-heading text-2xl text-[#23131E]">Executive Summary</h2>
                  <ConfidenceBadge value={report.confidence} />
                </div>
                <p className="text-[#23131E] leading-[1.75]">{report.executive_summary}</p>
              </section>

              {/* Warnings */}
              {run.warnings.length > 0 && (
                <div className="flex flex-col gap-2 p-4 rounded-xl bg-[#FEF3CD] border border-[#F0D080]">
                  <div className="flex items-center gap-2 text-[#7B5700]">
                    <AlertTriangle size={15} />
                    <span className="text-sm font-semibold">Warnings</span>
                  </div>
                  {run.warnings.map((w, i) => (
                    <p key={i} className="text-sm text-[#7B5700]">{w}</p>
                  ))}
                </div>
              )}

              {/* Findings */}
              {report.findings.map((f, i) => (
                <ReportSection key={i} finding={f} onCitationClick={openCitation} />
              ))}

              {/* Comparison table */}
              {report.comparison_table && (
                <ComparisonTableView table={report.comparison_table} onCitationClick={openCitation} />
              )}

              {/* Agreements & Conflicts */}
              {(report.agreements.length > 0 || report.conflicts.length > 0) && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {report.agreements.length > 0 && (
                    <div className="flex flex-col gap-2">
                      <h3 className="font-heading text-lg text-[#23131E]">Agreements</h3>
                      <ul className="flex flex-col gap-2">
                        {report.agreements.map((a, i) => (
                          <li key={i} className="text-sm text-[#23131E] leading-relaxed pl-3 border-l-2 border-[#FC9A64]">{a}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {report.conflicts.length > 0 && (
                    <div className="flex flex-col gap-2">
                      <h3 className="font-heading text-lg text-[#23131E]">Conflicts</h3>
                      <ul className="flex flex-col gap-2">
                        {report.conflicts.map((c, i) => (
                          <li key={i} className="text-sm text-[#23131E] leading-relaxed pl-3 border-l-2 border-[#C17C75]">{c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Limitations */}
              {report.limitations && (
                <section className="flex flex-col gap-2">
                  <h3 className="font-heading text-lg text-[#23131E]">Limitations</h3>
                  <p className="text-sm text-[#7B515F] leading-relaxed">{report.limitations}</p>
                </section>
              )}

              {/* References */}
              {report.references.length > 0 && (
                <section className="flex flex-col gap-3">
                  <h3 className="font-heading text-lg text-[#23131E]">References</h3>
                  <ol className="flex flex-col gap-2 list-none">
                    {report.references.map((ref) => (
                      <li key={ref.ref_id} className="flex gap-3 text-sm">
                        <span className="font-mono text-[#FC9A64] shrink-0 w-5">[{ref.ref_id}]</span>
                        <span className="text-[#23131E]">
                          {ref.authors.join(', ')} ({ref.year}).{' '}
                          <a
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#FC9A64] hover:underline inline-flex items-center gap-0.5"
                          >
                            {ref.title} <ExternalLink size={11} />
                          </a>
                        </span>
                      </li>
                    ))}
                  </ol>
                </section>
              )}
            </div>
          )}

          {/* SOURCES TAB */}
          {activeTab === 'sources' && (
            <div className="flex flex-col gap-5">
              <SourceFacetBar selected={sourceFacet} onChange={setSourceFacet} counts={facetCounts} />
              {filteredSources.length === 0 ? (
                <EmptyCard message="No sources match this filter." />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredSources.map((s, i) =>
                    s.type === 'academic' ? (
                      <AcademicCard key={s.source_id} source={s} />
                    ) : (
                      <SourceCard key={s.source_id} source={s} index={i} />
                    )
                  )}
                </div>
              )}
            </div>
          )}

          {/* EVIDENCE TAB */}
          {activeTab === 'evidence' && (
            <div className="flex flex-col gap-4">
              {passages.length === 0 ? (
                <EmptyCard message="No evidence passages found for this run." />
              ) : (
                passages.map((p) => {
                  const src = sources.find((s) => s.source_id === p.source_id);
                  return (
                    <div key={p.passage_id} className="rounded-xl border border-[#FDE0B8] bg-white p-5 flex flex-col gap-3 shadow-card">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-xs bg-[#FDE0B8] text-[#7B515F] px-2 py-0.5 rounded-full">#{p.rank}</span>
                        {src && <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#E8DADE] text-[#3A1A28] border border-[#7B515F]/20">{src.title?.slice(0, 40) ?? 'Unknown source'}</span>}
                        <span className="ml-auto font-mono text-xs text-[#7B515F]">BM25 {p.bm25_score.toFixed(2)}</span>
                      </div>
                      <p className="text-sm text-[#23131E] leading-relaxed">
                        <EntityHighlighter text={p.text} entities={p.entities} keyTerms={p.key_terms} numbers={p.numbers} />
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* AUDIT TAB */}
          {activeTab === 'audit' && (
            audit ? (
              <AuditTable
                audit={audit}
                onViewEvidence={(passageId) => {
                  const ar = audit.results.find((r) => r.passage_id === passageId);
                  openEvidence(passageId, ar);
                }}
              />
            ) : (
              <EmptyCard message="Audit data not available for this run." />
            )
          )}

          {/* LOG TAB */}
          {activeTab === 'log' && (
            <div className="flex flex-col gap-4">
              {run.warnings.length > 0 && (
                <div className="rounded-xl border border-[#FDE0B8] bg-white p-5">
                  <h3 className="font-heading text-lg text-[#23131E] mb-3">Run Warnings</h3>
                  <pre className="font-mono text-xs text-[#7B515F] whitespace-pre-wrap leading-relaxed">
                    {run.warnings.join('\n')}
                  </pre>
                </div>
              )}
              <div className="rounded-xl border border-[#FDE0B8] bg-[#FFF7EC] p-5">
                <p className="text-sm text-[#7B515F] italic">Full run log is streamed in real-time on the live run page. Only warnings are persisted here.</p>
              </div>
            </div>
          )}

          {/* EXPORT TAB */}
          {activeTab === 'export' && id && <ExportPanel runId={id} />}

        </ErrorBoundary>
      </div>

      {/* Evidence drawer */}
      <EvidenceDrawer
        passage={drawerPassage}
        source={drawerSource}
        auditResult={drawerAuditResult}
        onClose={() => { setDrawerPassageId(null); setDrawerAuditResult(null); }}
      />
    </RootLayout>
  );
}
