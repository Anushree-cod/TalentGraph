/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['selector', 'html[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'landing-glow':
          'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,58,237,0.12), transparent)',
        'dashboard-glow':
          'radial-gradient(ellipse at center, rgba(124,58,237,0.18) 0%, rgba(99,102,241,0.08) 40%, transparent 70%)',
      },
      boxShadow: {
        'dashboard-window': '0 -20px 80px rgba(124,58,237,0.15)',
      },
    },
  },
  plugins: [],
};
