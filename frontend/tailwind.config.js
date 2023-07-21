/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.html', './src/**/*.tsx'],
  plugins: [require("tailwindcss"), require("autoprefixer")],
};
