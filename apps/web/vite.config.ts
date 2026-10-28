/// <reference types="vitest/config" />
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// The dev server proxies the API, admin and media so the browser only ever talks
// to one origin, exactly like production behind nginx (no CORS in either setup).
export default defineConfig(({ mode, isSsrBuild }) => {
  const env = loadEnv(mode, new URL("../..", import.meta.url).pathname, "");
  const apiTarget = env.VITE_DEV_API_PROXY ?? "http://localhost:8000";
  const proxied = Object.fromEntries(
    ["/api", "/media", "/admin", "/static"].map((prefix) => [
      prefix,
      { target: apiTarget, changeOrigin: false },
    ]),
  );

  return {
    envDir: "../..",
    plugins: [react(), tailwindcss()],
    server: { host: true, port: 5173, proxy: proxied },
    preview: { port: 4173, proxy: proxied },
    build: {
      target: "es2022",
      cssCodeSplit: true,
      sourcemap: !isSsrBuild,
      // The pre-render bundle only needs code; public/ files are already in dist/.
      copyPublicDir: !isSsrBuild,
      assetsInlineLimit: 2048,
    },
    ssr: {
      // Bundle everything into the pre-render script so the runtime image needs no node_modules.
      noExternal: true,
      target: "node",
    },
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test/setup.ts"],
      css: false,
      restoreMocks: true,
    },
  };
});
