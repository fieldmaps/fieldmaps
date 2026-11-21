export type Slot = "a" | "b";
export type View = "fade" | Slot;

// Listed from highest to lowest quality.
export const SOURCES = [
  { id: "fieldmaps", label: "FieldMaps" },
  { id: "wp", label: "US State Dept" },
] as const;
export type SourceId = (typeof SOURCES)[number]["id"];

export const VIEWS: { id: View; label: string }[] = [
  { id: "fade", label: "Fade" },
  { id: "a", label: "A" },
  { id: "b", label: "B" },
];
export const SLOTS: Slot[] = ["a", "b"];
export type Basemap = "map" | "satellite";
export const BASEMAPS: { id: Basemap; label: string }[] = [
  { id: "map", label: "Map" },
  { id: "satellite", label: "Satellite" },
];

const FADE_CYCLE_MS = 3000;
const KEY_STEP: Record<string, number> = { "[": -1, "]": 1 };

export class CompareState {
  pair = $state<Record<Slot, SourceId>>({ a: "fieldmaps", b: "wp" });
  view = $state<View>("fade");
  basemap = $state<Basemap>("map");
  sweep = $state(0);
  #frame = 0;

  opacities = $derived<Record<Slot, number>>(
    this.view === "fade"
      ? { a: 1 - this.sweep, b: this.sweep }
      : { a: Number(this.view === "a"), b: Number(this.view === "b") },
  );

  animate(on: boolean) {
    cancelAnimationFrame(this.#frame);
    if (!on) return;
    const start = performance.now();
    const tick = (now: number) => {
      this.sweep = (1 - Math.cos((2 * Math.PI * (now - start)) / FADE_CYCLE_MS)) / 2;
      this.#frame = requestAnimationFrame(tick);
    };
    this.#frame = requestAnimationFrame(tick);
  }

  // Picking the other slot's source swaps the two, so A and B always differ.
  pick(slot: Slot, id: SourceId) {
    const other = slot === "a" ? "b" : "a";
    if (this.pair[other] === id) this.pair[other] = this.pair[slot];
    this.pair[slot] = id;
  }

  keydown(e: KeyboardEvent) {
    if ((e.target as Element).closest?.("input:not([type=radio]), select, textarea")) return;
    const by = KEY_STEP[e.key];
    if (by === undefined) return;
    const next = VIEWS[VIEWS.findIndex((v) => v.id === this.view) + by];
    if (next) this.view = next.id;
  }
}
