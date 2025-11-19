import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  resolve: {
  alias: {
    "@": path.resolve(__dirname, "./src"),
  },
  },
  server: {
    host: '0.0.0.0',  // important so Vite binds to your domain
    port: 5173,             // default Vite port, change if needed
  },
});