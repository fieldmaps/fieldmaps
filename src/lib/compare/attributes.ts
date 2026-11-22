// Columns in attributes.json from scripts/compare_attributes.py are `${group}_${source}`.
export interface AttributeGroup {
  key: string;
  label: string;
  sources: string[];
}

const GROUP_LABELS = [
  { key: "name", label: "Name" },
  { key: "mapname", label: "Label" },
  { key: "sovereign", label: "Sovereign" },
  { key: "status", label: "Status" },
  { key: "region", label: "Region" },
];

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

// Each group covers the sources the pipeline wrote a column for.
export function attributeGroups(
  row: AttributeRow | undefined,
  sources: string[],
): AttributeGroup[] {
  return GROUP_LABELS.map((g) => ({
    ...g,
    sources: row ? sources.filter((s) => `${g.key}_${s}` in row) : [],
  }));
}

export function value(row: AttributeRow, group: string, source: string): string {
  return String(row[`${group}_${source}`] ?? "").trim();
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

// Sources whose value differs from ref's, when both have one.
export function marked(
  row: AttributeRow,
  group: string,
  sources: string[],
  ref: string,
): Set<string> {
  const base = value(row, group, ref);
  return new Set(
    sources.filter((s) => {
      const v = value(row, group, s);
      return s !== ref && v && base && v !== base;
    }),
  );
}

// Rows are loaded once and never mutated, so the search text is cached per row.
const haystacks = new WeakMap<AttributeRow, string>();

export function matches(row: AttributeRow, group: string, pair: string[], query: string): boolean {
  if (!marked(row, group, pair, pair[0]).size) return false;
  const q = query.trim().toLowerCase();
  if (!q) return true;
  let text = haystacks.get(row);
  if (text === undefined) {
    text = Object.values(row)
      .map((v) => String(v ?? "").toLowerCase())
      .join("\n");
    haystacks.set(row, text);
  }
  return text.includes(q);
}
