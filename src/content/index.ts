import { cs } from './cs';
import type { SiteContent } from './types';

// Slovenská verze: vytvoř sk.ts (export const sk: SiteContent = { … }) a přidej ji sem.
export const locales = { cs } satisfies Record<string, SiteContent>;
export type Locale = keyof typeof locales;
export const defaultLocale: Locale = 'cs';

export function getContent(locale: Locale = defaultLocale): SiteContent {
  return locales[locale];
}

export type { SiteContent } from './types';
