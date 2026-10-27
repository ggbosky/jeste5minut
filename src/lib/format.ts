const NBSP = '\u00a0';

export const czk = (n: number) => `${n.toLocaleString('cs-CZ').replace(/\s/g, NBSP)}${NBSP}Kč`;
export const eur = (n: number) => `${n.toLocaleString('cs-CZ')}${NBSP}€`;

/** Cena, za kterou se právě prodává (launch, pokud běží). */
export const currentPrice = (p: { regular: number; launch: number | null }) => p.launch ?? p.regular;
