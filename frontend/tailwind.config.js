// tailwind.config.js
// 색은 여기 넷만 쓴다: 글자(ink), 보조 글자(zinc-500), 선(line), 포인트(brand).
// 웹 화면은 global.css -> output.css 로 컴파일한 것을 쓴다(클래스를 바꾸면 npm run css).
module.exports = {
  content: ["./App.{js,jsx,ts,tsx}", "./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18181B",
        line: "#E7E7E4",
        canvas: "#F6F6F4",
        brand: { DEFAULT: "#1F6F54", soft: "#E9F2EE" },
        danger: { DEFAULT: "#B42318", soft: "#FDF1F0" },
      },
    },
  },
  plugins: [],
}
