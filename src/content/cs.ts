import type { SiteContent } from './types';

/**
 * VŠECHNY TEXTY WEBU (čeština).
 * Ceny a odkazy nejsou tady, ale v site.config.ts.
 * Mini-syntaxe: **tučně**, [odkaz](/url).
 * Jednopísmenné předložky (v, k, s, z, a, i, o, u) se nezlomí na konec řádku automaticky.
 */
export const cs: SiteContent = {
  meta: {
    title: 'Ještě 5 minut – e-book o tom, jak přestat odkládat učení',
    description:
      'E-book pro vysokoškoláky o tom, jak přestat odkládat učení a bakalářku. 70 stran, 8 kapitol, PDF pro mobil i počítač.',
    ogAlt: 'Ještě 5 minut – e-book o tom, jak přestat odkládat učení',
    productDescription:
      'E-book (PDF, 70 stran) o tom, jak přestat odkládat učení a bakalářskou práci. Balíček navíc obsahuje týdenní plánovač, šablonu do Notionu, SOS kartu na zkouškové a pracovní listy.',
  },

  nav: {
    links: [
      { label: 'Obsah', href: '#obsah' },
      { label: 'Cena', href: '#cena' },
      { label: 'Otázky', href: '#faq' },
    ],
    cta: 'Začnu teď',
    skip: 'Přeskočit na obsah',
    logoLabel: 'Ještě 5 minut – úvod',
    ariaLabel: 'Hlavní navigace',
  },

  hero: {
    lead: 'Začnu',
    excuses: ['zítra.', 'v pondělí.', 'po obědě.', 'večer.'],
    now: 'teď.',
    subtitle: 'Přestaň se učit noc před zkouškou.',
    points: [
      '8 kapitol, každá na 5 minut čtení',
      'Začneš, i když se ti nechce',
      'Mobil tě přestane rozhazovat',
      'Zkouškové i bakalářka po malých krocích',
    ],
    trust: ['14 dní na vrácení peněz'],
    buy: 'Začnu teď',
    regularLabel: 'běžně',
    discountLabel: 'launch sleva',
    ctaNote: 'PDF ti přijde do minuty',
    videoLabel: 'Video: na lísteček v diáři se píše „Done!“',
  },

  learn: {
    title: 'Co se změní',
    intro: 'Tohle si z e-booku odneseš.',
    beforeLabel: 'Místo:',
    items: [
      { before: 'Otevřu skripta a nic.', after: 'Začneš, i když se ti nechce.' },
      { before: 'Za tři minuty jsem na mobilu.', after: 'Učíš se, aniž bys sahal po telefonu.' },
      { before: 'Učím se až noc před zkouškou.', after: 'Zkouškové máš naplánované dopředu.' },
      { before: 'Bakalářka je v nedohlednu.', after: 'Píšeš ji po malých krocích.' },
      { before: 'Musí to být dokonalé.', after: 'Hotové je lepší než dokonalé.' },
      { before: 'Jeden špatný den a vzdám to.', after: 'Navážeš i po dni, kdy se nic nepovedlo.' },
    ],
  },

  contents: {
    title: 'Obsah',
    intro: 'Každá kapitola se dá přečíst zhruba za pět minut a končí jedním konkrétním úkolem.',
    chapters: [
      { title: 'Proč odkládáme', text: 'Co se děje v hlavě, když učení odsouváme, a proč to není lenost.' },
      { title: 'Pravidlo pěti minut', text: 'Jak začít nejmenším možným krokem.' },
      { title: 'Mobil', text: 'Jak omezit rozptylování bez úplného digitálního detoxu.' },
      { title: 'Zkouškové', text: 'Plán na čtrnáct dní před zkouškou a co dělat, když zbývají tři.' },
      { title: 'Bakalářská práce', text: 'Od prázdné stránky k první hotové kapitole.' },
      { title: 'Perfekcionismus', text: 'Proč je hotová práce lepší než dokonalá.' },
      { title: 'Když to nevyjde', text: 'Jak navázat po dni, kdy se nic neudělalo.' },
      { title: 'Tvůj plán', text: 'Sestavíš si plán na příští týden.' },
    ],
  },

  pricing: {
    title: 'Cena',
    regularLabel: 'běžně',
    eurLabel: 'Ze Slovenska',
    popular: 'Nejčastější volba',
    plans: {
      basic: {
        name: 'E-book',
        features: ['E-book v PDF, 70 stran', 'Aktualizace zdarma'],
        cta: 'Chci e-book',
      },
      bundle: {
        name: 'E-book + bonusy',
        features: [
          'E-book v PDF, 70 stran',
          'Týdenní plánovač k tisku',
          'Šablona do Notionu',
          'SOS karta na zkouškové',
          'Pracovní listy ke kapitolám',
          'Aktualizace zdarma',
        ],
        cta: 'Chci e-book i bonusy',
      },
    },
  },

  lead: {
    title: 'SOS karta zdarma',
    text: 'Jedna stránka s postupem na posledních dvanáct hodin před zkouškou. Pošleme ti ji e-mailem.',
    emailLabel: 'E-mail',
    emailPlaceholder: 'tvuj@email.cz',
    consent:
      'Souhlasím se zasíláním SOS karty a občasných tipů e-mailem. Odhlásit se můžu kdykoli. Více v [zásadách ochrany osobních údajů]({{privacy}}).',
    submit: 'Pošlete mi SOS kartu',
    sending: 'Posílám…',
    successTitle: 'Hotovo',
    successText: 'SOS karta je na cestě. Pokud nedorazí do pár minut, podívej se do složky Promo nebo Spam.',
    error: 'Odeslání se nepovedlo. Zkus to prosím za chvíli znovu.',
    invalidEmail: 'Zkontroluj prosím e-mailovou adresu.',
    consentRequired: 'Bez souhlasu ti nemůžeme nic poslat.',
  },

  faq: {
    title: 'Časté otázky',
    items: [
      {
        q: 'V jakém formátu e-book je?',
        a: 'V PDF. Otevřeš ho na mobilu, tabletu i v počítači a text je čitelný i na malém displeji. Šablonu do Notionu si zkopíruješ jedním kliknutím.',
      },
      {
        q: 'Jak dlouho trvá ho přečíst?',
        a: 'Celý zhruba dvě hodiny. Každá kapitola má asi pět minut čtení, takže ho můžeš číst postupně.',
      },
      {
        q: 'Pro koho je e-book?',
        a: 'Pro vysokoškoláky, kteří učení a bakalářku odkládají na poslední chvíli. Nemusíš mít žádný systém ani aplikace, stačí mobil nebo počítač.',
      },
      {
        q: 'Pomůže mi, i když mám zkoušku za pár dní?',
        a: 'Ano. Kapitola o zkouškovém má plán na čtrnáct dní i postup pro situaci, kdy zbývají jen tři.',
      },
    ],
  },

  footer: {
    policies: [
      { label: 'Obchodní podmínky', handle: 'terms-of-service' },
      { label: 'Ochrana osobních údajů', handle: 'privacy-policy' },
      { label: 'Vrácení peněz a reklamace', handle: 'refund-policy' },
      { label: 'Kontaktní údaje', handle: 'contact-information' },
    ],
  },

  notFound: {
    title: 'Stránka nenalezena',
    text: 'Tahle stránka neexistuje nebo byla přesunuta.',
    cta: 'Zpět na úvod',
  },
};

export default cs;
