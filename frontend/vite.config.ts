import fs from "fs";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

const isDev = process.env.VITE_IS_DEV === "true";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "localhost",
    port: 5173,
    https: isDev
      ? {
          key: fs.readFileSync("./localhost-key.pem"),
          cert: fs.readFileSync("./localhost-cert.pem"),
        }
      : undefined,
    proxy: {
      "/api": {
        target: "https://back.cheap-bob.store",
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: "cheap-bob.store",
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@pages": path.resolve(__dirname, "src/pages"),
      "@constant": path.resolve(__dirname, "src/constant"),
      "@components": path.resolve(__dirname, "src/components"),
      "@interface": path.resolve(__dirname, "src/interface"),
      "@services": path.resolve(__dirname, "src/services"),
      "@styles": path.resolve(__dirname, "src/styles"),
      "@store": path.resolve(__dirname, "src/store"),
      "@utils": path.resolve(__dirname, "src/utils"),
      "@context": path.resolve(__dirname, "src/context"),
    },
  },
});
