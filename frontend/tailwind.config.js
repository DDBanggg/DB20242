// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#1e60d9", // Royal Blue từ prompt cũ của bạn
        background: "#f3f4f6",
      },
    },
  },
  plugins: [],
};