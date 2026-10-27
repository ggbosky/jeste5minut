import { analytics as cfg } from '../../site.config';

const KEY = 'j5m-consent';
export type Consent = 'granted' | 'denied';

export const analyticsEnabled = () => cfg.provider !== null;

export function getConsent(): Consent | null {
  try {
    const v = localStorage.getItem(KEY);
    return v === 'granted' || v === 'denied' ? v : null;
  } catch {
    return null;
  }
}

export function setConsent(v: Consent) {
  try {
    localStorage.setItem(KEY, v);
  } catch {
    /* privátní okno – nevadí, zeptáme se příště znovu */
  }
  if (v === 'granted') loadAnalytics();
}

let loaded = false;

/** Načte analytiku. Volá se jen po výslovném souhlasu. */
export function loadAnalytics() {
  if (loaded || !cfg.provider) return;
  loaded = true;
  const s = document.createElement('script');
  s.defer = true;
  if (cfg.provider === 'plausible') {
    s.src = cfg.plausibleSrc;
    s.dataset.domain = cfg.plausibleDomain;
  } else {
    s.src = `https://www.googletagmanager.com/gtag/js?id=${cfg.ga4Id}`;
    const w = window as unknown as { dataLayer: unknown[]; gtag: (...a: unknown[]) => void };
    w.dataLayer = w.dataLayer || [];
    w.gtag = function gtag() {
      // eslint-disable-next-line prefer-rest-params
      w.dataLayer.push(arguments);
    };
    w.gtag('js', new Date());
    w.gtag('config', cfg.ga4Id, { anonymize_ip: true });
  }
  document.head.appendChild(s);
}

/** Vlastní událost (např. klik na checkout). Bez souhlasu nedělá nic. */
export function track(event: string, props?: Record<string, string>) {
  if (!loaded) return;
  const w = window as unknown as {
    plausible?: (e: string, o?: { props?: Record<string, string> }) => void;
    gtag?: (...a: unknown[]) => void;
  };
  if (cfg.provider === 'plausible') w.plausible?.(event, { props });
  else w.gtag?.('event', event, props);
}
