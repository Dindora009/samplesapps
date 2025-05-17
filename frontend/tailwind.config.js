/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5B21B6', // Deep purple
          light: '#7C3AED',
          dark: '#4C1D95',
        },
        secondary: {
          DEFAULT: '#1E3A8A', // Navy blue
          light: '#2563EB',
          dark: '#1E3A8A',
        },
        accent: {
          DEFAULT: '#F59E0B', // Gold accent
          light: '#FBBF24',
          dark: '#D97706',
        },
        background: {
          DEFAULT: '#0F0F10',
          light: '#1F2937',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
        heading: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
};