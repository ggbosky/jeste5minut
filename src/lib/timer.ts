/**
 * Sdílený 5minutový odpočet (motiv „5 minut na start“).
 * Nejde o žádnou časově omezenou nabídku – jen vizuální motiv, cena se po doběhnutí nemění.
 */
export const DURATION = 5 * 60 * 1000;
const KEY = 'j5m-timer-start';

let start: number | null = null;

function getStart(): number {
  if (start !== null) return start;
  try {
    const saved = Number(sessionStorage.getItem(KEY));
    if (saved && Date.now() - saved < DURATION) start = saved;
  } catch {
    /* ignore */
  }
  if (start === null) {
    start = Date.now();
    try {
      sessionStorage.setItem(KEY, String(start));
    } catch {
      /* ignore */
    }
  }
  return start;
}

export const remaining = () => Math.max(0, DURATION - (Date.now() - getStart()));

export const fmt = (ms: number) => {
  const s = Math.ceil(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
};

type Listener = (ms: number) => void;
const listeners = new Set<Listener>();
let raf = 0;

function tick() {
  const ms = remaining();
  listeners.forEach((l) => l(ms));
  if (ms > 0) raf = window.setTimeout(tick, 250);
}

/** Zavolá callback ~4× za sekundu se zbývajícím časem v ms. */
export function onTick(cb: Listener) {
  listeners.add(cb);
  cb(remaining());
  if (!raf) tick();
  return () => listeners.delete(cb);
}
