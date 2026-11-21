import svelte from "@astrojs/svelte";
import { defineConfig, fontProviders } from "astro/config";
import { createReadStream, statSync } from "node:fs";
import { resolve, sep } from "node:path";

const font = (name, cssVariable, fallback = "sans-serif") => ({
  provider: fontProviders.fontsource(),
  name,
  cssVariable,
  weights: [400, 600, 700],
  subsets: ["latin"],
  fallbacks: [fallback],
});

const CATALOG = resolve("catalog");

// Dev only: serves catalog/ at /site-data/ with HTTP range requests, which PMTiles needs.
const siteData = {
  name: "site-data",
  apply: "serve",
  configureServer(server) {
    server.middlewares.use("/site-data", (req, res, next) => {
      const path = resolve(CATALOG, "." + decodeURIComponent(req.url.split("?")[0]));
      if (!path.startsWith(CATALOG + sep)) return next();
      const stat = statSync(path, { throwIfNoEntry: false });
      if (!stat?.isFile()) return next();
      const { size } = stat;
      const range = /bytes=(\d+)-(\d*)/.exec(req.headers.range ?? "");
      const start = range ? Number(range[1]) : 0;
      const end = range?.[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
      if (start > end) {
        res.writeHead(416, { "Content-Range": `bytes */${size}` });
        return res.end();
      }
      res.writeHead(range ? 206 : 200, {
        "Accept-Ranges": "bytes",
        "Content-Length": end - start + 1,
        ...(range && { "Content-Range": `bytes ${start}-${end}/${size}` }),
      });
      createReadStream(path, { start, end }).on("error", next).pipe(res);
    });
  },
};

export default defineConfig({
  site: "https://fieldmaps.io",
  output: "static",
  integrations: [svelte()],
  vite: { plugins: [siteData] },
  fonts: [
    font("Public Sans", "--font-sans"),
    font("IBM Plex Mono", "--font-mono-face", "monospace"),
  ],
});
