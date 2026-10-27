/**
 * Jediné místo pro ceny, odkazy a napojení služeb.
 * Texty webu jsou v src/content/cs.ts.
 *
 * Hodnoty v {{ }} jsou placeholdery – nahraď je tady, nebo je nastav
 * jako proměnné prostředí (PUBLIC_…) na Vercelu / Netlify.
 */

const env = import.meta.env ?? {};

export const site = {
  name: 'Ještě 5 minut',
  // TODO: finální doména (používá se pro canonical, sitemap, OG obrázek)
  url: 'https://jeste5minut.cz',
  locale: 'cs_CZ',
  author: 'Ještě 5 minut',
};

export const pricing = {
  currency: 'CZK',
  basic: {
    id: 'basic',
    // Běžná cena a launch cena. Když launch skončí, nastav launch: null.
    regular: 299,
    launch: 199 as number | null,
    eur: 12,
    checkoutUrl: env.PUBLIC_CHECKOUT_URL_BASIC || '{{CHECKOUT_URL_BASIC}}',
  },
  bundle: {
    id: 'bundle',
    regular: 499,
    launch: null as number | null,
    eur: 20,
    checkoutUrl: env.PUBLIC_CHECKOUT_URL_BUNDLE || '{{CHECKOUT_URL_BUNDLE}}',
  },
};

export const email = {
  /**
   * Kam se posílá formulář „SOS karta zdarma“.
   * Nikdy sem nedávej API klíč – endpoint musí být veřejný
   * (formulářová URL z Ecomailu / MailerLite, nebo vlastní serverless funkce).
   * Viz README → „E-mailový formulář“.
   */
  endpoint: env.PUBLIC_EMAIL_ENDPOINT || '{{EMAIL_ENDPOINT}}',
  /** 'json' = application/json, 'form' = application/x-www-form-urlencoded */
  format: 'json' as 'json' | 'form',
  /** Názvy polí, jak je čeká tvoje služba */
  fields: { email: 'email', name: 'name', consent: 'gdpr_consent', source: 'source', tag: 'tag' },
};

export const analytics = {
  /** 'plausible' | 'ga4' | null (null = žádná analytika, žádná cookie lišta) */
  provider: 'plausible' as 'plausible' | 'ga4' | null,
  plausibleDomain: 'jeste5minut.cz',
  plausibleSrc: 'https://plausible.io/js/script.js',
  ga4Id: 'G-XXXXXXXXXX',
};

export const contact = {
  // TODO: doplnit
  email: 'ahoj@jeste5minut.cz',
  company: '{{Jméno / firma}}',
  ico: '{{IČO}}',
  address: '{{Adresa}}',
};

export const socials = {
  tiktok: 'https://www.tiktok.com/@jeste5minut',
  instagram: 'https://www.instagram.com/jeste5minut',
};

export const config = { site, pricing, email, analytics, contact, socials };
export default config;
