/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  safelist: [
    "bg-gradient-light",
    "dark:bg-gradient-dark-purple",
    "text-text-light-mode",
    "dark:text-text-dark-mode",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-light': 'linear-gradient(135deg, #eef2ff, #e2e8f0)',
        'gradient-dark-purple': 'linear-gradient(135deg, #3b0764, #1b192f)',
      },
      colors: {
        'text-light-mode': '#111827',
        'text-dark-mode': '#d8b4fe',
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};