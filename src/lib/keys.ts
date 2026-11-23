const DIRECTIONS: Record<string, -1 | 1> = {
  ArrowUp: -1,
  ArrowLeft: -1,
  ArrowDown: 1,
  ArrowRight: 1,
};

export const direction = (e: KeyboardEvent) => {
  if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return undefined;
  if ((e.target as Element).closest?.("input, textarea, select, [contenteditable]"))
    return undefined;
  return DIRECTIONS[e.key];
};

export const stepper = (steps: HTMLElement[], active: () => number, reduced: boolean) => {
  // Repeated presses build on the step still being scrolled to, not the stale active one.
  let pending = -1;
  let pendingAt = 0;
  const to = (next: number) => {
    if (next < -1 || next >= steps.length) return false;
    pending = next;
    pendingAt = performance.now();
    const behavior: ScrollBehavior = reduced ? "instant" : "smooth";
    if (next < 0) scrollTo({ top: 0, behavior });
    else steps[next].scrollIntoView({ block: "center", behavior });
    return true;
  };
  const go = (d: -1 | 1) => to((performance.now() - pendingAt < 1000 ? pending : active()) + d);
  return { go, to };
};

// Left and right go to `sideways` when given, else they step like up and down.
export const stepKeys = (go: (d: -1 | 1) => boolean, sideways?: (d: -1 | 1) => void) => {
  const onKey = (e: KeyboardEvent) => {
    const d = direction(e);
    if (!d) return;
    if (sideways && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
      e.preventDefault();
      sideways(d);
    } else if (go(d)) e.preventDefault();
  };
  addEventListener("keydown", onKey);
  return () => removeEventListener("keydown", onKey);
};
