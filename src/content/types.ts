/**
 * Kontrakt pro jazykové verze. cs.ts (a později sk.ts) musí splnit tenhle typ –
 * TypeScript ti řekne, když nějaký text chybí.
 *
 * Mini-syntaxe v textech (viz src/lib/rich.ts):
 *   ~~zítra~~      → přeškrtnuté
 *   ==slovo==      → podtržené zvýrazňovačem
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
    title: [string, string];
    subline: string;
    primaryCta: string;
    secondaryCta: string;
    trust: string;
    alarm: {
      time: string;
      day: string;
      label: string;
      snooze: string;
      stop: string;
      /** Texty tlačítka po každém kliknutí. Poslední = scroll na nabídku. */
      reactions: string[];
      counter: string;
      appTitle: string;
    };
    book: { title: string; subtitle: string; pages: string };
  };
  reframe: {
    title: [string, string];
    body: string;
    points: { title: string; text: string }[];
  };
  lead: {
    title: string;
    text: string;
    nameLabel: string;
    namePlaceholder: string;
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
    perks: string[];
    mockup: { title: string; rows: [string, string][]; stamp: string };
  };
  inside: {
    title: string;
    intro: string;
    chapterLabel: string;
    readTime: string;
    chapters: { title: string; text: string }[];
    bonusesTitle: string;
    bonuses: { kind: 'planner' | 'notion' | 'sos' | 'worksheets'; title: string; text: string }[];
  };
  how: {
    title: string;
    steps: { title: string; text: string }[];
  };
  testimonials: {
    title: string;
    note: string;
    placeholderBadge: string;
    items: { quote: string; author: string; role: string; placeholder: boolean }[];
  };
  pricing: {
    title: string;
    intro: string;
    launchBadge: string;
    popular: string;
    regularLabel: string;
    eurLabel: string;
    plans: Record<'basic' | 'bundle', { name: string; text: string; features: string[]; cta: string }>;
  };
  guarantee: { title: string; text: string };
  faq: { title: string; items: { q: string; a: string }[] };
  finalCta: { title: [string, string]; text: string; cta: string };
  footer: {
    tagline: string;
    legalTitle: string;
    legal: Link[];
    contactTitle: string;
    socialTitle: string;
    cookieSettings: string;
    rights: string;
    signoff: string;
    toTop: string;
  };
  miniTimer: { label: string; done: string; cta: string };
  cookies: { text: string; decline: string; accept: string; label: string };
  notFound: { title: string; text: string; cta: string };
  legal: {
    placeholderNote: string;
    back: string;
    updatedLabel: string;
    pages: Record<'obchodniPodminky' | 'gdpr' | 'reklamacniRad', LegalPage>;
  };
};
