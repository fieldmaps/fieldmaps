import type { AddProtocolAction, RasterSourceSpecification } from "maplibre-gl";

export const SATELLITE_PROTOCOL = "esri";
const TILE = 256;
const MAX_STEPS = 8;

export const SATELLITE: RasterSourceSpecification = {
  type: "raster",
  tiles: [`${SATELLITE_PROTOCOL}://{z}/{x}/{y}`],
  tileSize: TILE,
  maxzoom: 19,
  attribution: "Powered by Esri | Esri, Vantor, Earthstar Geographics, and the GIS User Community",
};

// Missing tiles 404 without CORS headers, so the browser can't cache them; remembered here instead.
const missing = new Set<string>();

// Any failed fetch counts as no imagery.
async function fetchTile(z: number, x: number, y: number, signal: AbortSignal) {
  const key = `${z}/${y}/${x}`;
  if (missing.has(key)) return null;
  try {
    const res = await fetch(
      `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${key}?blankTile=false`,
      { signal },
    );
    if (res.ok) return await res.blob();
  } catch (e) {
    if (signal.aborted) throw e;
  }
  missing.add(key);
  return null;
}

// Imagery depth varies by place, so a missing tile is cropped and enlarged from the nearest ancestor.
export const satelliteTile: AddProtocolAction = async (params, abort) => {
  const [z, x, y] = params.url.slice(`${SATELLITE_PROTOCOL}://`.length).split("/").map(Number);
  for (let d = 0; d <= Math.min(z, MAX_STEPS); d++) {
    const blob = await fetchTile(z - d, x >> d, y >> d, abort.signal);
    if (!blob) continue;
    if (d === 0) return { data: await blob.arrayBuffer() };
    const size = TILE >> d;
    const mask = (1 << d) - 1;
    const data = await createImageBitmap(blob, (x & mask) * size, (y & mask) * size, size, size, {
      resizeWidth: TILE,
      resizeHeight: TILE,
      resizeQuality: "high",
    });
    return { data };
  }
  throw new Error(`No satellite imagery for ${z}/${x}/${y}`);
};
