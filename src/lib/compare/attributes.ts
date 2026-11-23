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
    text = Object.entries(row)
      .filter(([k]) => k === "iso3" || /^(map)?name_/.test(k))
      .map(([, v]) => String(v ?? "").toLowerCase())
      .join("\n");
    haystacks.set(row, text);
  }
  return text.includes(q);
}

export type ItemType = "island" | "land" | "no_land";
// The Geometry pane's lists: differences split by kind.
export type GeometryList = "islands" | "land";

// A geometry difference from items.json; title is its smallest entity's name, pairs the source pairs it
// has patches in, drawn the source whose islands they are, and items the differences merged into it.
export interface ItemRow {
  item: string;
  items?: string[];
  title: string | null;
  type: ItemType;
  drawn: string | null;
  missing: string[] | null;
  islands: number | null;
  km2: number | null;
  bbox: number[] | null;
  pairs: string[] | null;
  list?: GeometryList;
  entities?: Record<string, [unknown, unknown][]>;
  [column: string]: unknown;
}

// A source's own text: the title, else the first code for items no source names.
export function itemTitle(row: ItemRow, sources: string[]): string {
  const code = sources.map((s) => row[`code_${s}`]).find(Boolean);
  return row.title?.trim() || String(code ?? row.item);
}

// All of a and b's differences between the same two entities, either way round, share one cause, so
// they merge into one row in one list, land over islands.
export function mergeItems(items: ItemRow[], a: string, b: string): ItemRow[] {
  const pair = [a, b].sort().join("|");
  const rows = new Map<string, ItemRow>();
  const entity = (it: ItemRow, s: string) => [it[`code_${s}`], it[`name_${s}`]].join("|");
  const own = (it: ItemRow) =>
    Object.fromEntries(
      [a, b].map((s) => [s, [[it[`code_${s}`], it[`name_${s}`]] as [unknown, unknown]]]),
    );
  // A no_land entity exists in one source only, so it counts when A or B holds it.
  const relevant = items.filter((it) =>
    it.type === "no_land"
      ? [a, b].some((s) => it[`code_${s}`] || it[`name_${s}`])
      : it.pairs?.includes(pair) && (it.type !== "island" || it.drawn === a),
  );
  for (const it of relevant) {
    const key = [entity(it, a), entity(it, b)].sort().join("||");
    const list: GeometryList = it.type === "island" ? "islands" : "land";
    const row = rows.get(key);
    if (!row) {
      rows.set(key, { ...it, items: [it.item], list, entities: own(it) });
      continue;
    }
    row.items!.push(it.item);
    const boxes = [row.bbox, it.bbox].filter((x): x is number[] => !!x);
    row.bbox = boxes.length ? unionBox(boxes) : null;
    row.pairs = [...new Set([...(row.pairs ?? []), ...(it.pairs ?? [])])];
    row.km2 = (row.km2 ?? 0) + (it.km2 ?? 0);
    row.islands = (row.islands ?? 0) + (it.islands ?? 0) || null;
    for (const s of [a, b]) {
      const ents = row.entities![s];
      if (!ents.some(([c, n]) => c === it[`code_${s}`] && n === it[`name_${s}`]))
        ents.push([it[`code_${s}`], it[`name_${s}`]]);
    }
    if (list === "land" && row.list !== "land") row.type = it.type;
    if (list === "land") row.list = list;
  }
  // Merged rows show each source's territories together.
  for (const row of rows.values()) {
    for (const s of [a, b]) {
      const ents = row.entities![s];
      if (ents.length < 2) continue;
      const join = (vs: unknown[]) => [...new Set(vs.filter(Boolean))].join(", ");
      row[`code_${s}`] = join(ents.map(([c]) => c));
      row[`name_${s}`] = join(ents.map(([, n]) => n));
    }
  }
  return [...rows.values()];
}

export function itemMatches(row: ItemRow, pair: string[], query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return pair.some((s) =>
    [row[`code_${s}`], row[`name_${s}`]].some((v) =>
      String(v ?? "")
        .toLowerCase()
        .includes(q),
    ),
  );
}
