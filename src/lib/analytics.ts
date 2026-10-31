import { analytics as cfg } from '../../site.config';

let loaded = false;

/** Načte analytiku (Plausible – bez cookies, takže bez souhlasové lišty). */
export function loadAnalytics() {
  if (loaded || !cfg.provider) return;
  loaded = true;
  const s = document.createElement('script');
  s.defer = true;
  s.src = cfg.plausibleSrc;
  s.dataset.domain = cfg.plausibleDomain;
  document.head.appendChild(s);
}

/** Vlastní událost (např. klik na checkout). */
export function track(event: string, props?: Record<string, string>) {
  const w = window as unknown as { plausible?: (e: string, o?: { props?: Record<string, string> }) => void };
  w.plausible?.(event, { props });
}
