import svelte from "@astrojs/svelte";
import { defineConfig } from "astro/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  site: "https://fieldmaps.io",
  output: "static",
  integrations: [svelte()],
  vite: {
    resolve: {
      alias: { $lib: fileURLToPath(new URL("./src/lib", import.meta.url)) },
    },
  },
});
