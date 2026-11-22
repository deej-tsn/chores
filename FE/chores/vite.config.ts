import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import fs from "fs";

// `local_cert/` is gitignored, so the certs exist on a dev machine but not in CI or a fresh clone.
// Reading them unconditionally made `npm run build` (and therefore CI) fail with ENOENT, even though
// a production build has no use for the dev server's TLS. Only enable HTTPS when both files are there.
const keyPath = path.resolve(__dirname, "local_cert", "local.app.com-key.pem");
const certPath = path.resolve(__dirname, "local_cert", "local.app.com.pem");
const hasLocalCerts = fs.existsSync(keyPath) && fs.existsSync(certPath);

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    https: hasLocalCerts
      ? {
          key: fs.readFileSync(keyPath),
          cert: fs.readFileSync(certPath),
        }
      : undefined,
    host: "0.0.0.0", // important so Vite binds to your domain
    port: 5173, // default Vite port, change if needed
  },
});
