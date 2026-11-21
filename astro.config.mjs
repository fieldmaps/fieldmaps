import svelte from "@astrojs/svelte";
import { defineConfig, fontProviders } from "astro/config";

const font = (name, cssVariable, fallback = "sans-serif") => ({
  provider: fontProviders.fontsource(),
  name,
  cssVariable,
  weights: [400, 600, 700],
  subsets: ["latin"],
  fallbacks: [fallback],
});

export default defineConfig({
  site: "https://fieldmaps.io",
  output: "static",
  integrations: [svelte()],
  fonts: [
    font("Public Sans", "--font-sans"),
    font("IBM Plex Mono", "--font-mono-face", "monospace"),
  ],
});
