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

export type QuizTypeId = 'perfekcionista' | 'mobil' | 'zahlceny' | 'posledni';

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
    eyebrow: string;
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
      hint: string;
    };
    book: { title: string; subtitle: string; pages: string };
  };
  marquee: string[];
  marqueeLabel: string;
  reframe: {
    kicker: string;
    title: [string, string];
    body: string;
    points: { title: string; text: string }[];
  };
  quiz: {
    kicker: string;
    title: string;
    intro: string;
    start: string;
    progress: string;
    back: string;
    restart: string;
    resultKicker: string;
    resultCta: string;
    tipLabel: string;
    types: Record<QuizTypeId, { name: string; text: string; tip: string }>;
    questions: { q: string; answers: { text: string; type: QuizTypeId }[] }[];
  };
  lead: {
    kicker: string;
    title: string;
    text: string;
    quizTitle: string;
    quizText: string;
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
    kicker: string;
    title: string;
    intro: string;
    chapters: { time: string; title: string; text: string }[];
    bonusesKicker: string;
    bonusesTitle: string;
    bonuses: { kind: 'planner' | 'notion' | 'sos' | 'worksheets'; title: string; text: string }[];
  };
  how: {
    kicker: string;
    title: string;
    steps: { title: string; text: string }[];
  };
  testimonials: {
    kicker: string;
    title: string;
    note: string;
    placeholderBadge: string;
    items: { quote: string; author: string; role: string; placeholder: boolean }[];
  };
  pricing: {
    kicker: string;
    title: string;
    intro: string;
    launchBadge: string;
    popular: string;
    regularLabel: string;
    eurLabel: string;
    paymentNote: string;
    plans: Record<'basic' | 'bundle', { name: string; text: string; features: string[]; cta: string }>;
  };
  guarantee: { kicker: string; title: string; text: string };
  faq: { kicker: string; title: string; items: { q: string; a: string }[] };
  finalCta: { title: [string, string]; text: string; cta: string; timerLabel: string; timerDone: string };
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
