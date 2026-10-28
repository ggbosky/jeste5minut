/**
 * Kontrakt pro jazykové verze. cs.ts (a později sk.ts) musí splnit tenhle typ –
 * TypeScript ti řekne, když nějaký text chybí.
 *
 * Mini-syntaxe v textech (viz src/lib/rich.ts):
 *   **tučně**      → tučně
 *   [text](/url)   → odkaz
 */

export type Link = { label: string; href: string };

export type LegalPage = {
  title: string;
  description: string;
  updated: string;
  sections: { heading: string; body: string[] }[];
};

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
    title: string;
    subtitle: string;
    text: string;
    buy: string;
    regularLabel: string;
    free: string;
    facts: { value: string; label: string }[];
    book: { title: string; subtitle: string };
  };
  learn: { title: string; items: string[] };
  contents: { title: string; intro: string; chapters: { title: string; text: string }[] };
  pricing: {
    title: string;
    regularLabel: string;
    eurLabel: string;
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
  footer: { legal: Link[]; cookieSettings: string };
  cookies: { text: string; decline: string; accept: string; label: string };
  notFound: { title: string; text: string; cta: string };
  legal: {
    placeholderNote: string;
    back: string;
    updatedLabel: string;
    pages: Record<'obchodniPodminky' | 'gdpr' | 'reklamacniRad', LegalPage>;
  };
};
