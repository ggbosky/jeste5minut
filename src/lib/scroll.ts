/**
 * Plynulý scroll na sekci. Sekce pod ohybem mají content-visibility: auto, takže se jejich
 * výška upřesní až během scrollu – po doběhnutí proto pozici (max. 3×) dorovnáme.
 */
export function scrollToId(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const offset = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
  const started = Date.now();
  let tries = 0;

  const go = () => {
    if ('onscrollend' in window) addEventListener('scrollend', settle, { once: true });
    el.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'start' });
  };
  const settle = () => {
    const off = Math.abs(el.getBoundingClientRect().top - offset) > 4;
    // po 4 s už nic nedorovnáváme, ať nebojujeme s uživatelem, který mezitím scrolluje sám
    if (off && tries++ < 3 && Date.now() - started < 4000) go();
  };
  go();
}
