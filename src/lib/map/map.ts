import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import { Protocol } from "pmtiles";

export const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
export const FADE_MS = 600;
export const color = (name: string) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();
export const GLOBE = {
  projection: { type: "globe" },
  sky: { "atmosphere-blend": 0 },
} satisfies Partial<maplibregl.StyleSpecification>;

// The pmtiles protocol is global, so it stays registered while any map is mounted.
let mounted = 0;

export function createMap(
  options: maplibregl.MapOptions & { container: HTMLElement },
  onResize?: (map: maplibregl.Map) => void,
) {
  if (mounted++ === 0) {
    maplibregl.setWorkerUrl(workerUrl);
    maplibregl.addProtocol("pmtiles", new Protocol().tile);
  }
  const map = new maplibregl.Map(options);
  const resize = new ResizeObserver(() => {
    map.resize();
    onResize?.(map);
  });
  resize.observe(options.container);
  const destroy = () => {
    resize.disconnect();
    map.remove();
    if (--mounted === 0) maplibregl.removeProtocol("pmtiles");
  };
  return { map, destroy };
}
