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
    text: '**Ještě 5 minut** je e-book pro vysokoškoláky. Osm kapitol po pěti minutách, které tě dostanou od odkládání k učení.',
    points: ['Začneš, i když se ti nechce', 'Mobil tě přestane rozhazovat', 'Zkouškové i bakalářka po malých krocích'],
    trust: ['14 dní na vrácení peněz', 'Jednorázově, žádné předplatné'],
    buy: 'Začnu teď',
    regularLabel: 'běžně',
    free: 'Nejdřív zkusit zdarma',
    ctaNote: 'PDF ti přijde do minuty',
    videoLabel: 'Video: na lísteček v diáři se píše „Done!“',
  },

  learn: {
    title: 'Co se změní',
    intro: 'Tohle si z e-booku odneseš.',
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
      'Souhlasím se zasíláním SOS karty a občasných tipů e-mailem. Odhlásit se můžu kdykoli. Více v [zásadách ochrany osobních údajů](/gdpr).',
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
        q: 'Jak můžu zaplatit?',
        a: 'Kartou nebo bankovním převodem přes platební bránu SimpleShop. Po zaplacení ti přijde e-mail s odkazem ke stažení.',
      },
      {
        q: 'Dostanu fakturu?',
        a: 'Ano, faktura přijde e-mailem automaticky po zaplacení. Pokud kupuješ na firmu, vyplň v objednávce IČO.',
      },
      {
        q: 'Můžu nakoupit ze Slovenska?',
        a: 'Ano, zaplatíš v eurech kartou nebo převodem. E-book je v češtině.',
      },
      {
        q: 'Dostanu aktualizace?',
        a: 'Ano, zdarma. Novou verzi ti pošleme na e-mail, který zadáš při nákupu.',
      },
      {
        q: 'Co když mi e-book nepomůže?',
        a: 'Napiš nám do 14 dnů od nákupu a vrátíme ti peníze.',
      },
    ],
  },

  footer: {
    legal: [
      { label: 'Obchodní podmínky', href: '/obchodni-podminky' },
      { label: 'Ochrana osobních údajů', href: '/gdpr' },
      { label: 'Reklamační řád', href: '/reklamacni-rad' },
    ],
    cookieSettings: 'Nastavení cookies',
  },

  cookies: {
    label: 'Souhlas s analytikou',
    text: 'Anonymní statistiky návštěvnosti zapneme, jen když souhlasíš.',
    decline: 'Jen nutné',
    accept: 'Povolit statistiky',
  },

  notFound: {
    title: 'Stránka nenalezena',
    text: 'Tahle stránka neexistuje nebo byla přesunuta.',
    cta: 'Zpět na úvod',
  },

  // TODO: právní texty jsou šablona. Před spuštěním je nech zkontrolovat (ideálně právníkem).
  legal: {
    placeholderNote: 'Šablona – před spuštěním doplň skutečné údaje a nech text zkontrolovat.',
    back: '← Zpět na úvod',
    updatedLabel: 'Aktualizováno',
    pages: {
      obchodniPodminky: {
        title: 'Obchodní podmínky',
        description: 'Obchodní podmínky prodeje e-booku Ještě 5 minut.',
        updated: '{{datum}}',
        sections: [
          {
            heading: '1. Prodávající',
            body: ['{{Jméno / firma}}, IČO {{IČO}}, se sídlem {{adresa}}. Kontakt: {{e-mail}}.', '{{Plátce / neplátce DPH}}.'],
          },
          {
            heading: '2. Předmět koupě',
            body: [
              'Předmětem koupě je digitální obsah – e-book ve formátu PDF, případně s bonusovými materiály podle zvoleného balíčku.',
            ],
          },
          {
            heading: '3. Objednávka a platba',
            body: [
              'Objednávka probíhá přes platební systém SimpleShop. Platit lze kartou nebo bankovním převodem (QR platbou).',
              'Po připsání platby obdrží kupující e-mail s odkazem ke stažení a daňový doklad.',
            ],
          },
          {
            heading: '4. Odstoupení od smlouvy',
            body: [
              '{{Doplnit: souhlas kupujícího s dodáním digitálního obsahu před uplynutím lhůty pro odstoupení a poučení o ztrátě práva na odstoupení (§ 1837 písm. l) občanského zákoníku).}}',
              '{{Doplnit: podmínky dobrovolné záruky vrácení peněz, pokud ji nabízíš.}}',
            ],
          },
          { heading: '5. Závěrečná ustanovení', body: ['{{Doplnit.}}'] },
        ],
      },
      gdpr: {
        title: 'Ochrana osobních údajů',
        description: 'Jak zpracováváme osobní údaje na webu Ještě 5 minut.',
        updated: '{{datum}}',
        sections: [
          { heading: 'Správce údajů', body: ['{{Jméno / firma}}, IČO {{IČO}}, {{adresa}}, {{e-mail}}.'] },
          {
            heading: 'Jaké údaje zpracováváme',
            body: [
              'Při stažení SOS karty: e-mail a nepovinně jméno. Účel: zaslání SOS karty a občasných tipů. Právní základ: souhlas, který můžeš kdykoli odvolat (odkaz v každém e-mailu).',
              'Při nákupu: údaje nutné k vyřízení objednávky a vystavení dokladu. Právní základ: plnění smlouvy a zákonné povinnosti.',
            ],
          },
          {
            heading: 'Zpracovatelé',
            body: ['{{Doplnit: e-mailingová služba (Ecomail / MailerLite), SimpleShop, hosting, případně analytika.}}'],
          },
          {
            heading: 'Cookies a statistiky',
            body: [
              'Bez tvého souhlasu nepoužíváme žádné analytické ani marketingové cookies. Souhlas můžeš kdykoli změnit odkazem „Nastavení cookies“ v patičce.',
            ],
          },
          {
            heading: 'Tvoje práva',
            body: [
              'Máš právo na přístup k údajům, opravu, výmaz, omezení zpracování, přenositelnost, odvolání souhlasu a podání stížnosti u ÚOOÚ (uoou.gov.cz).',
            ],
          },
        ],
      },
      reklamacniRad: {
        title: 'Reklamační řád',
        description: 'Jak reklamovat e-book Ještě 5 minut.',
        updated: '{{datum}}',
        sections: [
          {
            heading: 'Jak reklamovat',
            body: [
              'Nejde ti soubor stáhnout nebo otevřít? Napiš na {{e-mail}} a do předmětu dej „Reklamace“. Uveď číslo objednávky a popis problému.',
            ],
          },
          { heading: 'Lhůty', body: ['{{Doplnit: lhůta pro vyřízení reklamace (max. 30 dní).}}'] },
          { heading: 'Způsob vyřízení', body: ['{{Doplnit: zaslání nového odkazu / opravené verze, případně vrácení peněz.}}'] },
        ],
      },
    },
  },
};

export default cs;
