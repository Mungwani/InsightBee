/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // ✅ src 내부 파일 전부 스캔
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
