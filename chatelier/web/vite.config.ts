import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/**
 * The dev server binds loopback only. The browser tool talks to a `mekaneck`
 * binary on the same machine, so exposing this server on a LAN interface
 * would contradict the guarantee the tool makes about where data goes.
 */
export default defineConfig({
  plugins: [react()],
  server: { host: "127.0.0.1", port: 5173, strictPort: true },
  build: { outDir: "dist", sourcemap: true },
});
