// One feature of a code in one source; layer is the source id, name the tile property focus matches on.
export interface Part {
  s: string;
  id: string;
  layer: string;
  name: string;
  label: string | null;
  bbox: number[];
}

// bbox is [west, south, east, north]; east can pass 180 for codes across the antimeridian.
export interface AttributeRow {
  iso3: string;
  bbox: number[] | null;
  parts: Part[] | null;
  [column: string]: unknown;
}

// One box around all boxes; across the antimeridian, western boxes move east by 360 when that is narrower.
export function unionBox(boxes: number[][]): number[] {
  const union = (bs: number[][]) => [
    Math.min(...bs.map((b) => b[0])),
    Math.min(...bs.map((b) => b[1])),
    Math.max(...bs.map((b) => b[2])),
    Math.max(...bs.map((b) => b[3])),
  ];
  const plain = union(boxes);
  const east = union(boxes.map((b) => (b[2] <= 0 ? [b[0] + 360, b[1], b[2] + 360, b[3]] : b)));
  return plain[2] - plain[0] <= Math.max(180, east[2] - east[0]) ? plain : east;
}
