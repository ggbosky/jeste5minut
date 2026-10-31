/**
 * Kontrakt pro jazykové verze. cs.ts (a později sk.ts) musí splnit tenhle typ –
 * TypeScript ti řekne, když nějaký text chybí.
 *
 * Mini-syntaxe v textech (viz src/lib/rich.ts):
 *   **tučně**      → tučně
 *   [text](/url)   → odkaz
 */

export type Link = { label: string; href: string };

export type SiteContent = {
  meta: {
    title: string;
    description: string;
    ogAlt: string;
    productDescription: string;
  };
  nav: {
    links: Link[];
    cta: string;
    skip: string;
    logoLabel: string;
    ariaLabel: string;
  };
  hero: {
    /** Nadpis: „Začnu“ + výmluvy, které se postupně přeškrtnou, a nakonec „teď.“ */
    lead: string;
    excuses: string[];
    now: string;
    subtitle: string;
    points: string[];
    buy: string;
    trust: string[];
    regularLabel: string;
    discountLabel: string;
    /** malý text pod hlavním tlačítkem */
    ctaNote: string;
    videoLabel: string;
  };
  learn: { title: string; intro: string; beforeLabel: string; items: { before: string; after: string }[] };
  contents: { title: string; intro: string; chapters: { title: string; text: string }[] };
  pricing: {
    title: string;
    regularLabel: string;
    eurLabel: string;
    popular: string;
    plans: Record<'basic' | 'bundle', { name: string; features: string[]; cta: string }>;
  };
  lead: {
    title: string;
    text: string;
    emailLabel: string;
    emailPlaceholder: string;
    consent: string;
    submit: string;
    sending: string;
    successTitle: string;
    successText: string;
    error: string;
    invalidEmail: string;
    consentRequired: string;
  };
  faq: { title: string; items: { q: string; a: string }[] };
  /** handle = adresa zásady v Shopify: /policies/<handle> */
  footer: { policies: { label: string; handle: string }[] };
  notFound: { title: string; text: string; cta: string };
};
