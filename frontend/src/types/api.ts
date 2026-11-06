// ─── Run Status & Mode ────────────────────────────────────────────────────────

export type RunStatus  = 'pending' | 'running' | 'complete' | 'error';
export type RunMode    = 'web' | 'news' | 'academic';
export type SourceType = 'web' | 'news' | 'academic' | 'official' | 'code' | 'benchmark';
export type VerdictType = 'well-supported' | 'partial' | 'disputed' | 'insufficient';
export type Confidence  = 'well-supported' | 'partial' | 'disputed' | 'insufficient';
export type StageId     = 'scope' | 'plan' | 'search' | 'fetch' | 'extract' | 'rank' | 'write' | 'verify';
export type StageStatus = 'idle' | 'running' | 'complete' | 'error';

// ─── Run Plan ─────────────────────────────────────────────────────────────────

export interface RunPlan {
  scope: string;
  query_variants: string[];
}

// ─── Run Stats ────────────────────────────────────────────────────────────────

export interface RunStats {
  sources_found:    number;
  sources_fetched:  number;
  passages_total:   number;
  claims_total:     number;
  claims_verified:  number;
  claims_partial:   number;
  claims_disputed:  number;
  claims_missing:   number;
  pct_verified:     number;
}

// ─── Report Shapes ────────────────────────────────────────────────────────────

export interface ReportReference {
  ref_id:  number;
  title:   string;
  url:     string;
  authors: string[];
  year:    number;
  type:    SourceType;
}

export interface ReportFinding {
  theme:     string;
  body:      string;
  citations: number[];
}

export interface ComparisonCell {
  cells:          string[];
  citations:      number[];
  vendor_reported: boolean[];
}

export interface ComparisonTable {
  headers: string[];
  rows:    ComparisonCell[];
}

export interface TimelineEvent {
  date:      string;
  headline:  string;
  citations: number[];
}

export interface Report {
  confidence:        Confidence;
  executive_summary: string;
  findings:          ReportFinding[];
  comparison_table:  ComparisonTable | null;
  agreements:        string[];
  conflicts:         string[];
  timeline:          TimelineEvent[] | null;
  limitations:       string;
  references:        ReportReference[];
}

// ─── Run ──────────────────────────────────────────────────────────────────────

export interface Run {
  run_id:       string;
  query:        string;
  mode:         RunMode;
  status:       RunStatus;
  created_at:   string;
  completed_at: string | null;
  elapsed_ms:   number;
  stats:        RunStats;
  plan:         RunPlan | null;
  report:       Report | null;
  warnings:     string[];
}

export interface RunSummary {
  run_id:     string;
  query:      string;
  mode:       RunMode;
  status:     RunStatus;
  created_at: string;
  elapsed_ms: number;
  stats: Pick<RunStats, 'sources_fetched' | 'claims_verified' | 'pct_verified'>;
}

// ─── Academic Metadata ────────────────────────────────────────────────────────

export interface AcademicMeta {
  venue:          string;
  venue_type:     'conference' | 'journal' | 'preprint';
  peer_reviewed:  boolean;
  authors:        string[];
  year:           number;
  doi:            string | null;
  citation_count: number | null;
  abstract:       string;
  tldr:           string;
  task:           string;
  domain:         string;
  method:         string;
  benchmarks:     string[];
  key_results:    { metric: string; value: string; vendor_reported: boolean }[];
  baselines:      string[];
  has_ablations:  boolean;
  limitations:    string;
}

// ─── Source ───────────────────────────────────────────────────────────────────

export interface Source {
  source_id:         string;
  url:               string;
  title:             string;
  type:              SourceType;
  status:            'fetching' | 'extracted' | 'failed' | 'blocked';
  fetch_ms:          number | null;
  credibility_score: number | null;
  snippet:           string | null;
  academic?:         AcademicMeta;
}

// ─── Passage ──────────────────────────────────────────────────────────────────

export interface Passage {
  passage_id: string;
  source_id:  string;
  text:       string;
  char_start: number;
  char_end:   number;
  bm25_score: number;
  rank:       number;
  entities:   string[];
  numbers:    string[];
  key_terms:  string[];
}

// ─── Audit ────────────────────────────────────────────────────────────────────

export interface AuditResult {
  claim_id:    string;
  claim_text:  string;
  verdict:     VerdictType;
  ref_id:      number;
  passage_id:  string | null;
  support_span: string | null;
  source_url:  string | null;
  note?:       string;
}

export interface AuditSummary {
  total:        number;
  verified:     number;
  partial:      number;
  disputed:     number;
  missing:      number;
  pct_verified: number;
}

export interface Audit {
  run_id:  string;
  summary: AuditSummary;
  results: AuditResult[];
}

// ─── SSE Events ───────────────────────────────────────────────────────────────

export type SSEEvent =
  | { event: 'stage';         stage: StageId; status: StageStatus; ts: string }
  | { event: 'plan_ready';    plan: RunPlan }
  | { event: 'source';        source: Source }
  | { event: 'source_update'; source_id: string; status: Source['status']; snippet?: string; credibility_score?: number }
  | { event: 'log';           stage: StageId; level: 'info' | 'warn' | 'error'; message: string; ts: string }
  | { event: 'complete';      run_id: string; redirect: string }
  | { event: 'error';         stage: StageId; message: string; recoverable: boolean };

// ─── API Request Shapes ───────────────────────────────────────────────────────

export interface CreateRunRequest {
  query:        string;
  mode:         RunMode;
  max_sources:  number;
  depth:        number;
  date_range:   { from: string | null; to: string | null };
  language:     string;
  source_types: SourceType[];
  must_include: string[];
  must_exclude: string[];
}
