import { email as cfg } from '../../site.config';

export type SubscribePayload = {
  email: string;
  name?: string;
  consent: boolean;
  /** odkud formulář přišel: 'sos-karta' | … */
  source: string;
  /** volitelný štítek, např. výsledek kvízu */
  tag?: string;
};

export const isValidEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim());

/**
 * Jediné místo, které posílá e-mail do Ecomailu / MailerLite / vlastního endpointu.
 * Chceš změnit službu? Uprav jen site.config.ts (endpoint, format, fields), případně tuhle funkci.
 */
export async function subscribe(data: SubscribePayload): Promise<void> {
  if (!isValidEmail(data.email)) throw new Error('invalid-email');
  if (!data.consent) throw new Error('consent-required');

  const f = cfg.fields;
  const body: Record<string, string> = {
    [f.email]: data.email.trim(),
    [f.consent]: 'yes',
    [f.source]: data.source,
  };
  if (data.name?.trim()) body[f.name] = data.name.trim();
  if (data.tag) body[f.tag] = data.tag;

  if (cfg.endpoint.includes('{{')) {
    // Endpoint ještě není nastavený. Ve vývoji předstíráme úspěch, ať jde UI otestovat.
    if (import.meta.env.DEV) {
      console.info('[subscribe] EMAIL_ENDPOINT není nastavený – simuluji úspěch.', body);
      await new Promise((r) => setTimeout(r, 700));
      return;
    }
    throw new Error('endpoint-not-configured');
  }

  const res = await fetch(cfg.endpoint, {
    method: 'POST',
    headers:
      cfg.format === 'json'
        ? { 'Content-Type': 'application/json', Accept: 'application/json' }
        : { 'Content-Type': 'application/x-www-form-urlencoded', Accept: 'application/json' },
    body: cfg.format === 'json' ? JSON.stringify(body) : new URLSearchParams(body).toString(),
  });
  if (!res.ok) throw new Error(`http-${res.status}`);
}
