/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: false,
  theme: {
    extend: {
      colors: {
        'page-bg': '#FFF7EC',
        cream: { DEFAULT: '#FDE0B8', 80: '#FDE8C9', 40: '#FEF4E6' },
        orange: { DEFAULT: '#FC9A64', 80: '#FDB486', 20: '#FEE9DC' },
        rose: { DEFAULT: '#C17C75', 20: '#F0E0DF' },
        mauve: { DEFAULT: '#7B515F', 20: '#E8DADE' },
        plum: { DEFAULT: '#23131E', 60: '#6B5068' },
      },
      fontFamily: {
        heading: ['"Playfair Display"', 'Georgia', 'serif'],
        body: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      maxWidth: { report: '65ch' },
      boxShadow: {
        card: '0 1px 3px rgba(35,19,30,0.07), 0 4px 16px rgba(35,19,30,0.05)',
        drawer: '-4px 0 24px rgba(35,19,30,0.10)',
        focus: '0 0 0 3px rgba(252,154,100,0.40)',
      },
      borderRadius: {
        sm: '0.25rem', md: '0.5rem', lg: '0.75rem', xl: '1rem',
      },
    },
  },
  plugins: [],
};
