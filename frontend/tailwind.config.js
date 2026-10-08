/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        sidebar: 'var(--sidebar)',
        'sidebar-border': 'var(--sidebar-border)',
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: '#000000',
        },
        accent: 'var(--accent)',
        border: 'var(--border)',
        muted: 'var(--muted)',
        'muted-foreground': 'var(--muted-foreground)',
      },
    },
  },
  plugins: [],
}
