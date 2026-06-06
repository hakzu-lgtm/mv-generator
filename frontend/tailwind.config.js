/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#2C1A0A',
        card: '#4A2C14',
        elevated: '#5A3820',
        brand: {
          orange: '#F97316',
          amber: '#F59E0B',
          gold: '#D97706',
          green: '#10B981',
          red:   '#EF4444',
        },
        text: {
          primary:   '#FEF3E2',
          secondary: '#C9A882',
        },
        border: {
          DEFAULT: '#6B3E22',
          active:  '#F97316',
          chorus:  '#F59E0B',
        },
      },
      fontFamily: {
        sans: ['Pretendard', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'app-bg':     "radial-gradient(ellipse 80% 50% at 50% -10%, #F9731622, transparent)",
        'btn-primary':'linear-gradient(135deg, #F97316, #EA580C)',
      },
      animation: {
        'fade-in':    'fadeIn 0.3s ease-in-out',
        'slide-up':   'slideUp 0.4s ease-out',
        'wave':       'wave 1.5s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        wave: {
          '0%, 100%': { transform: 'scaleY(0.5)' },
          '50%':      { transform: 'scaleY(1.5)' },
        },
      },
    },
  },
  plugins: [],
}
