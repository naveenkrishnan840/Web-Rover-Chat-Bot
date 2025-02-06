// import { Config } from "tailwindcss";

export default {
  content: [
    "./src/components/*/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
}
