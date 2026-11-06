/**
 * mockData.ts
 * Realistic mock data for the research engine frontend.
 * Guarded by VITE_USE_MOCKS — import freely; tree-shaken in production.
 */

import type {
  Run,
  RunSummary,
  Source,
  Passage,
  Audit,
} from '../types/api';

// ─── Past Run Summaries ───────────────────────────────────────────────────────

export const mockRunSummaries: RunSummary[] = [
  {
    run_id:     'run-001',
    query:      'AI in disaster management and emergency response systems',
    mode:       'web',
    status:     'complete',
    created_at: '2026-10-28T09:14:32Z',
    elapsed_ms: 47320,
    stats: {
      sources_fetched:  8,
      claims_verified:  14,
      pct_verified:     77.8,
    },
  },
  {
    run_id:     'run-002',
    query:      'Large language model hallucination mitigation techniques 2024',
    mode:       'academic',
    status:     'complete',
    created_at: '2026-10-25T14:52:10Z',
    elapsed_ms: 61880,
    stats: {
      sources_fetched:  12,
      claims_verified:  21,
      pct_verified:     87.5,
    },
  },
  {
    run_id:     'run-003',
    query:      'Generative AI energy consumption and carbon footprint',
    mode:       'news',
    status:     'error',
    created_at: '2026-10-22T07:03:55Z',
    elapsed_ms: 12400,
    stats: {
      sources_fetched: 3,
      claims_verified: 0,
      pct_verified:    0,
    },
  },
];

// ─── Sources ──────────────────────────────────────────────────────────────────

export const mockSources: Source[] = [
  {
    source_id:         'src-001',
    url:               'https://www.un.org/en/disaster-risk-reduction/ai-emergency-response-report-2024',
    title:             'AI for Disaster Risk Reduction: 2024 Global Assessment',
    type:              'official',
    status:            'extracted',
    fetch_ms:          843,
    credibility_score: 0.94,
    snippet:
      'Artificial intelligence tools have been deployed in 47 countries for flood prediction, '
      + 'wildfire spread modelling, and post-disaster needs assessment. Early warning lead times '
      + 'improved by an average of 6.2 hours compared to conventional models.',
  },
  {
    source_id:         'src-002',
    url:               'https://www.reuters.com/technology/ai-disaster-response-wildfires-2024-09-12/',
    title:             'How AI Helped Emergency Teams Respond Faster During 2024 California Wildfires',
    type:              'news',
    status:            'extracted',
    fetch_ms:          612,
    credibility_score: 0.81,
    snippet:
      'Cal Fire officials credited machine-learning-driven satellite imagery analysis with '
      + 'identifying fire perimeter expansions up to 40 minutes earlier than ground observers, '
      + 'enabling more targeted evacuation orders.',
  },
  {
    source_id:         'src-003',
    url:               'https://arxiv.org/abs/2409.11234',
    title:             'Real-Time Flood Extent Mapping Using Multimodal Foundation Models',
    type:              'academic',
    status:            'extracted',
    fetch_ms:          1104,
    credibility_score: 0.89,
    snippet:
      'We present FloodFM, a multimodal foundation model fine-tuned on paired SAR and optical '
      + 'imagery from 230 historical flood events. FloodFM achieves an F1 of 0.91 on the '
      + 'WorldFloods benchmark, outperforming prior baselines by 7.3 percentage points.',
    academic: {
      venue:          'NeurIPS 2024',
      venue_type:     'conference',
      peer_reviewed:  true,
      authors:        ['Y. Chen', 'A. Kapoor', 'M. Rußwurm', 'D. Tuia'],
      year:           2024,
      doi:            '10.48550/arXiv.2409.11234',
      citation_count: 38,
      abstract:
        'Accurate and rapid flood extent mapping is critical for emergency response coordination. '
        + 'Existing methods rely on single-modality remote sensing and struggle in cloud-covered '
        + 'scenarios. We present FloodFM, a multimodal foundation model fine-tuned on paired SAR '
        + 'and optical imagery from 230 historical flood events across six continents. FloodFM '
        + 'achieves an F1 of 0.91 on the WorldFloods benchmark, outperforming prior baselines '
        + 'by 7.3 pp with a 2× faster inference time.',
      tldr:           'Foundation model for real-time flood mapping using SAR + optical fusion, reaching F1 0.91.',
      task:           'Flood extent mapping',
      domain:         'Remote sensing / Disaster management',
      method:         'Multimodal transformer fine-tuning',
      benchmarks:     ['WorldFloods', 'SEN1Floods11'],
      key_results: [
        { metric: 'F1 (WorldFloods)',   value: '0.91',  vendor_reported: false },
        { metric: 'F1 (SEN1Floods11)',  value: '0.88',  vendor_reported: false },
        { metric: 'Inference time (s)', value: '1.4',   vendor_reported: false },
      ],
      baselines:     ['U-Net', 'SegFormer', 'RaVÆN'],
      has_ablations: true,
      limitations:   'Validation limited to publicly available flood events; real-time satellite delivery latency not modelled.',
    },
  },
  {
    source_id:         'src-004',
    url:               'https://arxiv.org/abs/2311.07942',
    title:             'LLM-Assisted Crisis Communication: Accuracy and Misinformation Risks',
    type:              'academic',
    status:            'extracted',
    fetch_ms:          980,
    credibility_score: 0.76,
    snippet:
      'Large language models deployed for public crisis communication produced factually incorrect '
      + 'shelter-in-place guidance in 12% of test scenarios. Retrieval-augmented generation '
      + 'reduced this error rate to 3.1%, but introduced latency of 2.4 seconds per query.',
    academic: {
      venue:          'ACL 2024',
      venue_type:     'conference',
      peer_reviewed:  true,
      authors:        ['S. Patel', 'L. Zhao', 'R. Fernandez'],
      year:           2024,
      doi:            '10.18653/v1/2024.acl-long.312',
      citation_count: 19,
      abstract:
        'We evaluate seven open-weight and proprietary LLMs on a novel CrisisQA benchmark of '
        + '1,200 public safety queries derived from real emergency management transcripts. '
        + 'Without retrieval augmentation, models produced incorrect guidance in 12% of scenarios. '
        + 'RAG reduced this to 3.1% but introduced a 2.4 s median latency, raising usability '
        + 'concerns for time-critical deployments.',
      tldr:           'LLMs make crisis communication errors 12% of the time; RAG cuts this to 3.1% but adds latency.',
      task:           'Crisis communication QA',
      domain:         'NLP / Public safety',
      method:         'Benchmark evaluation + RAG ablation',
      benchmarks:     ['CrisisQA'],
      key_results: [
        { metric: 'Error rate (baseline)', value: '12%',  vendor_reported: false },
        { metric: 'Error rate (RAG)',       value: '3.1%', vendor_reported: false },
        { metric: 'RAG latency (median)',   value: '2.4s', vendor_reported: false },
      ],
      baselines:     ['GPT-4o', 'Llama-3-70B', 'Mistral-8x22B', 'Gemini 1.5 Pro', 'Claude 3 Opus'],
      has_ablations: true,
      limitations:
        'CrisisQA is English-only; multilingual performance not assessed. Latency measured on A100 GPU, not edge deployments.',
    },
  },
];

// ─── Passages ─────────────────────────────────────────────────────────────────

export const mockPassages: Passage[] = [
  {
    passage_id: 'pass-001',
    source_id:  'src-001',
    text:
      'AI tools have been deployed in 47 countries for flood prediction, wildfire spread modelling, '
      + 'and post-disaster needs assessment. Early warning lead times improved by an average of '
      + '6.2 hours compared to conventional meteorological models in the same evaluation period.',
    char_start: 0,
    char_end:   220,
    bm25_score: 14.72,
    rank:       1,
    entities:   ['47 countries', 'flood prediction', 'wildfire spread modelling'],
    numbers:    ['47', '6.2 hours'],
    key_terms:  ['AI tools', 'early warning', 'lead time', 'meteorological models'],
  },
  {
    passage_id: 'pass-002',
    source_id:  'src-002',
    text:
      'Machine-learning-driven satellite imagery analysis identified fire perimeter expansions '
      + 'up to 40 minutes earlier than ground observers, enabling more targeted and timely '
      + 'evacuation orders during the August 2024 Lake Tahoe complex fire.',
    char_start: 410,
    char_end:   623,
    bm25_score: 13.45,
    rank:       2,
    entities:   ['Lake Tahoe', 'Cal Fire', 'August 2024'],
    numbers:    ['40 minutes'],
    key_terms:  ['satellite imagery', 'fire perimeter', 'evacuation', 'lead time'],
  },
  {
    passage_id: 'pass-003',
    source_id:  'src-003',
    text:
      'FloodFM achieves an F1 of 0.91 on the WorldFloods benchmark, outperforming prior baselines '
      + 'including U-Net (F1 0.79), SegFormer (F1 0.83), and RaVÆN (F1 0.84) by between '
      + '7.3 and 12 percentage points, while running inference in 1.4 seconds on an A100 GPU.',
    char_start: 2104,
    char_end:   2342,
    bm25_score: 12.98,
    rank:       3,
    entities:   ['FloodFM', 'WorldFloods', 'U-Net', 'SegFormer', 'RaVÆN', 'A100'],
    numbers:    ['0.91', '0.79', '0.83', '0.84', '7.3', '12', '1.4 seconds'],
    key_terms:  ['F1 score', 'benchmark', 'flood extent', 'SAR imagery'],
  },
  {
    passage_id: 'pass-004',
    source_id:  'src-004',
    text:
      'Large language models produced factually incorrect shelter-in-place guidance in 12% of '
      + 'test scenarios drawn from the CrisisQA benchmark. Retrieval-augmented generation (RAG) '
      + 'reduced this error rate to 3.1%, a relative improvement of 74%, but introduced a '
      + 'median latency of 2.4 seconds per query on A100 hardware.',
    char_start: 880,
    char_end:   1116,
    bm25_score: 11.60,
    rank:       4,
    entities:   ['CrisisQA', 'RAG', 'A100'],
    numbers:    ['12%', '3.1%', '74%', '2.4 seconds'],
    key_terms:  ['LLM', 'crisis communication', 'RAG', 'shelter-in-place', 'error rate'],
  },
  {
    passage_id: 'pass-005',
    source_id:  'src-001',
    text:
      'Post-disaster damage assessment workflows using computer vision models reduced field '
      + 'survey time by 58% in three pilot programmes conducted in Türkiye, Morocco, and '
      + 'the Philippines following major seismic and storm events in 2023–2024.',
    char_start: 3020,
    char_end:   3230,
    bm25_score: 10.88,
    rank:       5,
    entities:   ['Türkiye', 'Morocco', 'Philippines'],
    numbers:    ['58%', '2023–2024'],
    key_terms:  ['damage assessment', 'computer vision', 'field survey', 'seismic'],
  },
];

// ─── Full Run ─────────────────────────────────────────────────────────────────

export const mockRun: Run = {
  run_id:       'run-001',
  query:        'AI in disaster management and emergency response systems',
  mode:         'web',
  status:       'complete',
  created_at:   '2026-10-28T09:14:32Z',
  completed_at: '2026-10-28T09:15:19Z',
  elapsed_ms:   47320,
  warnings: [
    'Source src-002 (Reuters) paywalled; snippet extracted from Google AMP cache.',
  ],
  stats: {
    sources_found:   14,
    sources_fetched:  8,
    passages_total:  74,
    claims_total:    18,
    claims_verified: 14,
    claims_partial:   2,
    claims_disputed:  1,
    claims_missing:   1,
    pct_verified:    77.8,
  },
  plan: {
    scope: 'Survey current AI applications in disaster prediction, emergency response coordination, '
      + 'and post-disaster assessment, covering both peer-reviewed research and operational deployments.',
    query_variants: [
      'AI machine learning disaster risk reduction early warning systems 2024',
      'artificial intelligence wildfire flood emergency response real-time 2024',
      'LLM natural language processing crisis communication public safety',
    ],
  },
  report: {
    confidence:        'partial',
    executive_summary:
      'Artificial intelligence is increasingly embedded in disaster management workflows globally, '
      + 'with demonstrated gains in early warning lead times (averaging +6.2 hours for flood events), '
      + 'real-time hazard mapping (FloodFM F1 0.91), and post-disaster damage assessment (−58% field '
      + 'survey time). However, evidence quality is uneven: operational claims from UN and government '
      + 'sources lack peer-reviewed validation, and LLM-based crisis communication carries a residual '
      + 'error rate of 3.1% even with RAG, posing risks in time-critical contexts. Overall confidence '
      + 'is rated partial pending independent replication of the largest operational claims.',
    findings: [
      {
        theme:
          'Early warning systems powered by AI provide meaningful lead-time improvements',
        body:
          'UN-reported deployments across 47 countries show that AI-enhanced flood and wildfire '
          + 'prediction extended early warning lead times by an average of 6.2 hours relative to '
          + 'conventional meteorological baselines [1]. Satellite-driven fire perimeter detection '
          + 'during the 2024 California wildfire season provided an additional 40-minute advantage '
          + 'over ground observation [2]. These figures are operationally significant but derive '
          + 'from agency self-reporting rather than controlled experiments.',
        citations: [1, 2],
      },
      {
        theme: 'Foundation models advance automated hazard mapping with strong benchmark results',
        body:
          'FloodFM, a multimodal transformer trained on 230 historical flood events, achieves '
          + 'F1 0.91 on WorldFloods and 0.88 on SEN1Floods11, surpassing all evaluated baselines '
          + '(U-Net 0.79, SegFormer 0.83, RaVÆN 0.84) by 7–12 percentage points [3]. Inference '
          + 'runs in 1.4 s on a single A100 GPU, suggesting near-real-time operational viability. '
          + 'Ablations confirm that SAR–optical fusion is the primary driver of performance gains '
          + 'over single-modality approaches.',
        citations: [3],
      },
      {
        theme: 'LLM-based crisis communication reduces error rates but introduces latency trade-offs',
        body:
          'Evaluation across 1,200 real-world crisis scenarios shows baseline LLMs produce incorrect '
          + 'guidance in 12% of queries. Retrieval-augmented generation (RAG) cuts this to 3.1%, '
          + 'a 74% relative reduction [4]. However, RAG introduces 2.4 s median latency, which may '
          + 'be prohibitive for real-time dispatch systems. Multilingual and edge-deployment '
          + 'performance remains uncharacterised.',
        citations: [4],
      },
    ],
    comparison_table: {
      headers: ['System', 'Task', 'Key metric', 'Lead time / Accuracy', 'Validated?'],
      rows: [
        {
          cells:          ['UN AI Early Warning',   'Flood / wildfire prediction', 'Lead-time gain', '+6.2 h average', 'Agency-reported only'],
          citations:      [1],
          vendor_reported: [false, false, false, true, false],
        },
        {
          cells:          ['FloodFM (NeurIPS 2024)', 'Flood extent mapping',       'F1 (WorldFloods)', '0.91',         'Peer-reviewed'],
          citations:      [3],
          vendor_reported: [false, false, false, false, false],
        },
        {
          cells:          ['LLM + RAG (ACL 2024)',   'Crisis communication QA',    'Error rate',       '3.1%',         'Peer-reviewed'],
          citations:      [4],
          vendor_reported: [false, false, false, false, false],
        },
      ],
    },
    agreements: [
      'All sources agree that AI provides measurable lead-time advantages over conventional '
        + 'methods in both flood prediction and wildfire detection.',
      'Academic and operational sources consistently identify retrieval augmentation as the '
        + 'most effective mitigation for LLM hallucination in public safety contexts.',
    ],
    conflicts: [
      'UN operational figures (+6.2 h lead time) are agency self-reported and lack the '
        + 'controlled validation design of academic benchmarks, making direct comparison '
        + 'with peer-reviewed results methodologically uncertain.',
    ],
    timeline: null,
    limitations:
      'Primary evidence for operational deployments relies on UN and government agency reports '
      + 'rather than peer-reviewed studies. Academic benchmarks (WorldFloods, CrisisQA) may not '
      + 'reflect real-time infrastructure constraints. Geographical coverage skews toward North '
      + 'America and Europe. No evidence was located for AI use in SIDS (Small Island Developing '
      + 'States) or Sub-Saharan African contexts.',
    references: [
      {
        ref_id:  1,
        title:   'AI for Disaster Risk Reduction: 2024 Global Assessment',
        url:     'https://www.un.org/en/disaster-risk-reduction/ai-emergency-response-report-2024',
        authors: ['UN Office for Disaster Risk Reduction'],
        year:    2024,
        type:    'official',
      },
      {
        ref_id:  2,
        title:   'How AI Helped Emergency Teams Respond Faster During 2024 California Wildfires',
        url:     'https://www.reuters.com/technology/ai-disaster-response-wildfires-2024-09-12/',
        authors: ['J. Martinez', 'C. Webb'],
        year:    2024,
        type:    'news',
      },
      {
        ref_id:  3,
        title:   'Real-Time Flood Extent Mapping Using Multimodal Foundation Models',
        url:     'https://arxiv.org/abs/2409.11234',
        authors: ['Y. Chen', 'A. Kapoor', 'M. Rußwurm', 'D. Tuia'],
        year:    2024,
        type:    'academic',
      },
      {
        ref_id:  4,
        title:   'LLM-Assisted Crisis Communication: Accuracy and Misinformation Risks',
        url:     'https://arxiv.org/abs/2311.07942',
        authors: ['S. Patel', 'L. Zhao', 'R. Fernandez'],
        year:    2024,
        type:    'academic',
      },
    ],
  },
};

// ─── Audit ────────────────────────────────────────────────────────────────────

export const mockAudit: Audit = {
  run_id: 'run-001',
  summary: {
    total:        18,
    verified:     14,
    partial:       2,
    disputed:      1,
    missing:       1,
    pct_verified: 77.8,
  },
  results: [
    {
      claim_id:     'clm-001',
      claim_text:
        'AI tools have been deployed in 47 countries for flood prediction and wildfire modelling.',
      verdict:      'well-supported',
      ref_id:       1,
      passage_id:   'pass-001',
      support_span:
        'AI tools have been deployed in 47 countries for flood prediction, wildfire spread modelling, '
        + 'and post-disaster needs assessment.',
      source_url:
        'https://www.un.org/en/disaster-risk-reduction/ai-emergency-response-report-2024',
    },
    {
      claim_id:     'clm-002',
      claim_text:
        'AI improved early warning lead times by an average of 6.2 hours over conventional models.',
      verdict:      'partial',
      ref_id:       1,
      passage_id:   'pass-001',
      support_span:
        'Early warning lead times improved by an average of 6.2 hours compared to conventional '
        + 'meteorological models.',
      source_url:
        'https://www.un.org/en/disaster-risk-reduction/ai-emergency-response-report-2024',
      note:
        'Figure is agency self-reported; no independent peer-reviewed replication found.',
    },
    {
      claim_id:     'clm-003',
      claim_text:
        'Satellite ML analysis identified fire perimeter expansions 40 minutes before ground observers.',
      verdict:      'well-supported',
      ref_id:       2,
      passage_id:   'pass-002',
      support_span:
        'identified fire perimeter expansions up to 40 minutes earlier than ground observers',
      source_url:
        'https://www.reuters.com/technology/ai-disaster-response-wildfires-2024-09-12/',
    },
    {
      claim_id:     'clm-004',
      claim_text:   'FloodFM achieves F1 of 0.91 on the WorldFloods benchmark.',
      verdict:      'well-supported',
      ref_id:       3,
      passage_id:   'pass-003',
      support_span: 'FloodFM achieves an F1 of 0.91 on the WorldFloods benchmark',
      source_url:   'https://arxiv.org/abs/2409.11234',
    },
    {
      claim_id:     'clm-005',
      claim_text:
        'RAG reduces LLM crisis communication error rate from 12% to 3.1%.',
      verdict:      'well-supported',
      ref_id:       4,
      passage_id:   'pass-004',
      support_span:
        'produced factually incorrect shelter-in-place guidance in 12% of test scenarios … '
        + 'Retrieval-augmented generation (RAG) reduced this error rate to 3.1%',
      source_url:   'https://arxiv.org/abs/2311.07942',
    },
    {
      claim_id:     'clm-006',
      claim_text:
        'AI damage assessment reduced field survey time by 58% across three pilot programmes.',
      verdict:      'partial',
      ref_id:       1,
      passage_id:   'pass-005',
      support_span:
        'reduced field survey time by 58% in three pilot programmes conducted in Türkiye, Morocco, '
        + 'and the Philippines',
      source_url:
        'https://www.un.org/en/disaster-risk-reduction/ai-emergency-response-report-2024',
      note:
        'Agency-reported; pilot scope and methodology not independently verified.',
    },
    {
      claim_id:     'clm-007',
      claim_text:   'FloodFM outperforms U-Net by more than 15 percentage points on F1.',
      verdict:      'disputed',
      ref_id:       3,
      passage_id:   'pass-003',
      support_span: null,
      source_url:   'https://arxiv.org/abs/2409.11234',
      note:
        'Paper reports 7.3–12 pp improvement over U-Net (F1 0.79 vs 0.91). The 15 pp claim '
        + 'overstates the finding.',
    },
    {
      claim_id:     'clm-008',
      claim_text:
        'AI early warning systems have been validated in every OECD member country.',
      verdict:      'insufficient',
      ref_id:       1,
      passage_id:   null,
      support_span: null,
      source_url:   null,
      note:
        'No source in the retrieved corpus substantiates OECD-wide validation. '
        + 'The UN report mentions 47 countries without mapping to OECD membership.',
    },
  ],
};
