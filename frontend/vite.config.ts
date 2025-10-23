import mkcert from "vite-plugin-mkcert";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss(), mkcert()],
  server: {
    https: {},
    host: "localhost",
    port: 5173,
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
