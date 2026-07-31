/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ds: {
          'bg-0': '#080809',
          'bg-1': '#0F0F12',
          'bg-2': '#16161A',
          'bg-3': '#1E1E24',
          'bg-4': '#26262E',
          'primary': '#6366F1',
          'secondary': '#8B5CF6',
          'success': '#10B981',
          'warning': '#F59E0B',
          'danger': '#EF4444',
          'info': '#3B82F6',
          'text-primary': '#F8FAFC',
          'text-secondary': '#CBD5E1',
          'text-muted': '#64748B',
          'border': 'rgba(255,255,255,0.06)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'h1': ['48px', { lineHeight: '1.2', letterSpacing: '-0.02em', fontWeight: '700' }],
        'h2': ['32px', { lineHeight: '1.3', letterSpacing: '-0.02em', fontWeight: '600' }],
        'h3': ['24px', { lineHeight: '1.4', letterSpacing: '-0.02em', fontWeight: '600' }],
        'h4': ['20px', { lineHeight: '1.5', letterSpacing: '-0.02em', fontWeight: '500' }],
        'h5': ['16px', { lineHeight: '1.6', letterSpacing: '-0.01em', fontWeight: '500' }],
        'body': ['14px', { lineHeight: '1.7' }],
        'small': ['12px', { lineHeight: '1.7' }],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'spin-slow': 'spin 8s linear infinite',
        'radar': 'radar 2s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(59,130,246,0.2), 0 0 20px rgba(59,130,246,0.1)' },
          '100%': { boxShadow: '0 0 20px rgba(59,130,246,0.4), 0 0 60px rgba(59,130,246,0.2)' },
        },
        radar: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
