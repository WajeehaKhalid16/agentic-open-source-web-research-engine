// ─── Colors ──────────────────────────────────────────────────────────────────

export const color = {
  pageBg:   '#FFF7EC',
  surface:  '#FFFFFF',
  cream:    '#FDE0B8',
  cream80:  '#FDE8C9',
  cream40:  '#FEF4E6',
  orange:   '#FC9A64',
  orange80: '#FDB486',
  orange20: '#FEE9DC',
  rose:     '#C17C75',
  rose20:   '#F0E0DF',
  mauve:    '#7B515F',
  mauve20:  '#E8DADE',
  plum:     '#23131E',
  plum60:   '#6B5068',
} as const;

// ─── Typography ───────────────────────────────────────────────────────────────

export const font = {
  heading: '"Playfair Display", Georgia, serif',
  body:    '"Inter", system-ui, sans-serif',
  mono:    '"JetBrains Mono", "Fira Code", monospace',
} as const;

export const fontSize = {
  xs:   '0.75rem',   //  12px
  sm:   '0.875rem',  //  14px
  base: '1rem',      //  16px
  lg:   '1.125rem',  //  18px
  xl:   '1.25rem',   //  20px
  '2xl':'1.5rem',    //  24px
  '3xl':'1.875rem',  //  30px
  '4xl':'2.25rem',   //  36px
} as const;

export const lineHeight = {
  tight:  1.25,
  normal: 1.5,
  report: 1.7,
} as const;

// ─── Layout ───────────────────────────────────────────────────────────────────

export const measure = {
  report: '65ch',
} as const;

export const space = {
  1:  '0.25rem',   //  4px
  2:  '0.5rem',    //  8px
  3:  '0.75rem',   // 12px
  4:  '1rem',      // 16px
  5:  '1.25rem',   // 20px
  6:  '1.5rem',    // 24px
  7:  '1.75rem',   // 28px
  8:  '2rem',      // 32px
  9:  '2.25rem',   // 36px
  10: '2.5rem',    // 40px
  11: '2.75rem',   // 44px
  12: '3rem',      // 48px
  14: '3.5rem',    // 56px
  16: '4rem',      // 64px
  18: '4.5rem',    // 72px
  20: '5rem',      // 80px
  22: '5.5rem',    // 88px
  24: '6rem',      // 96px
} as const;

export const radius = {
  sm:   '0.25rem',
  md:   '0.5rem',
  lg:   '0.75rem',
  xl:   '1rem',
  full: '9999px',
} as const;

export const shadow = {
  card:   '0 1px 3px rgba(35,19,30,0.07), 0 4px 16px rgba(35,19,30,0.05)',
  drawer: '-4px 0 24px rgba(35,19,30,0.10)',
  focus:  '0 0 0 3px rgba(252,154,100,0.40)',
} as const;

// ─── Motion ───────────────────────────────────────────────────────────────────

export const motionTokens = {
  fast:   150,
  normal: 280,
  slow:   480,
  ease:   [0.4, 0, 0.2, 1] as [number, number, number, number],
  spring: { type: 'spring', stiffness: 300, damping: 28 } as const,
  stagger: 0.08,
} as const;

// ─── Z-index ──────────────────────────────────────────────────────────────────

export const z = {
  base:    0,
  card:    10,
  drawer:  40,
  overlay: 50,
  toast:   60,
} as const;

// ─── Verdict ─────────────────────────────────────────────────────────────────

export const verdict = {
  'well-supported': {
    bg:     '#E6F4EA',
    text:   '#2E6B3E',
    border: '#A8D5B5',
  },
  'partial': {
    bg:     '#FEF3CD',
    text:   '#7B5700',
    border: '#F0D080',
  },
  'disputed': {
    bg:     '#F0E0DF',
    text:   '#7B2020',
    border: '#C17C75',
  },
  'insufficient': {
    bg:     '#E8DADE',
    text:   '#5A3A44',
    border: '#7B515F',
  },
} as const;

// ─── Pipeline Stages ──────────────────────────────────────────────────────────

export const stages = [
  { id: 'scope',   label: 'Scope'   },
  { id: 'plan',    label: 'Plan'    },
  { id: 'search',  label: 'Search'  },
  { id: 'fetch',   label: 'Fetch'   },
  { id: 'extract', label: 'Extract' },
  { id: 'rank',    label: 'Rank'    },
  { id: 'write',   label: 'Write'   },
  { id: 'verify',  label: 'Verify'  },
] as const;

// ─── Aggregated default export ────────────────────────────────────────────────

const tokens = {
  color,
  font,
  fontSize,
  lineHeight,
  measure,
  space,
  radius,
  shadow,
  motionTokens,
  z,
  verdict,
  stages,
} as const;

export default tokens;
