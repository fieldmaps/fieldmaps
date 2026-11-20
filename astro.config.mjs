import svelte from "@astrojs/svelte";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://fieldmaps.io",
  output: "static",
  integrations: [svelte()],
});
