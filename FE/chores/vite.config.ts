import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'
import fs from 'fs';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'local_cert','local.app.com-key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname,  'local_cert','local.app.com.pem')),
    },
    host: 'local.app.com',  // important so Vite binds to your domain
    port: 5173,             // default Vite port, change if needed
  },
});