/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#07070a',
        surface: '#13131a',
        primary: '#00e5ff',
        primaryDark: '#0088aa',
        danger: '#ff2e63',
        success: '#00e676',
        textMain: '#e0e0e0',
        textMuted: '#8a8a9a',
      },
      animation: {
        'glow-pulse': 'glow 3s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 10px rgba(0, 229, 255, 0.2)' },
          '100%': { boxShadow: '0 0 25px rgba(0, 229, 255, 0.6)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
