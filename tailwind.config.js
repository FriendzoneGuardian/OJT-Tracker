/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/**/*.js"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        scarlet: {
          50: '#fff1f1',
          100: '#ffdfdf',
          200: '#ffc5c5',
          300: '#ff9d9d',
          400: '#ff6666',
          50: '#ff3333',
          600: '#ee1111',
          700: '#cc0000',
          800: '#990000',
          900: '#770000',
          950: '#440000',
        },
        amoled: {
          DEFAULT: '#000000',
          card: '#0a0a0a',
          border: '#1a1a1a',
        }
      },
    },
  },
  plugins: [],
}
