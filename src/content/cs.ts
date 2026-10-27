import type { SiteContent } from './types';

/**
 * VŠECHNY TEXTY WEBU (čeština).
 * Ceny a odkazy nejsou tady, ale v site.config.ts.
 * Mini-syntaxe: ~~přeškrtnuté~~, ==zvýrazňovač==, **tučně**, [odkaz](/url).
 * Jednopísmenné předložky (v, k, s, z, a, i, o, u) se nezlomí na konec řádku automaticky.
 */
export const cs: SiteContent = {
  meta: {
    title: 'Ještě 5 minut – e-book o prokrastinaci pro studenty',
    description:
      'E-book, který tě dostane od „ještě chvilku“ k první větě. Zkouškové, bakalářka i mobil v ruce. Kapitoly na 5 minut, plánovač, Notion šablona a SOS karta zkouškového.',
    ogAlt: 'Ještě 5 minut. A pak už fakt začneš. – e-book o prokrastinaci pro studenty',
    productDescription:
      'E-book (PDF, cca 70 stran) o tom, jak přestat odkládat učení a bakalářku. Bonusy: týdenní plánovač, Notion šablona, SOS karta zkouškového a pracovní listy.',
  },

  nav: {
    links: [
      { label: 'Co v tom je', href: '#obsah' },
      { label: 'Recenze', href: '#recenze' },
      { label: 'FAQ', href: '#faq' },
    ],
    cta: 'Chci to',
    skip: 'Přeskočit na obsah',
    logoLabel: 'Ještě 5 minut – úvod',
    ariaLabel: 'Hlavní navigace',
  },

  hero: {
    eyebrow: 'E-book pro studenty, co začnou ~~zítra~~ teď',
    title: ['Ještě 5 minut.', 'A pak už fakt začneš.'],
    subline:
      'Zkouškové za dveřmi, bakalářka v nedohlednu a mobil v ruce. Tenhle e-book tě dostane od „ještě chvilku“ k první větě. Za 5 minut, ne za semestr.',
    primaryCta: 'Chci e-book',
    secondaryCta: 'SOS karta zdarma',
    trust: 'Pro studenty, co se učí noc před zkouškou. Bez kázání, bez motivačních citátů.',
    alarm: {
      time: '23:55',
      day: 'úterý 14. ledna',
      label: 'Zkouška z makra · 8:00',
      snooze: 'Odložit (5 min)',
      stop: 'Vstávám',
      reactions: ['Fakt? Zase?', 'Ještě jednou a dost…', 'Ok, tak začneme.'],
      counter: 'Odloženo',
      appTitle: 'Budík',
      notifications: [
        { app: 'Mamka', text: 'Učíš se? Zítra ti držím palce!', ago: 'před 2 h' },
        { app: 'Studijní systém', text: 'Odevzdání bakalářské práce: zbývá 12 dní', ago: 'včera' },
        { app: 'Čas u obrazovky', text: 'Dnes 6 h 47 min. O 2 h víc než minulý týden.', ago: 'teď' },
      ],
      battery: '12 %',
      lockLabel: 'Ukázka zamčeného telefonu s budíkem',
    },
    book: { title: 'Ještě 5 minut', subtitle: 'Jak přestat odkládat a fakt začít', pages: 'PDF · 70 stran' },
  },

  marquee: [
    '„Otevřu skripta a za 3 minuty jsem na TikToku“',
    '„Bakalářku odkládám půl roku“',
    '„Učím se až noc před zkouškou“',
    '„Uklidím si stůl. Pak pokoj. Pak celý byt.“',
    '„Ještě jedno video a jdu na to“',
    '„Začnu v pondělí. Tohle pondělí ne.“',
    '„Mám 47 záložek s motivačníma videama“',
    '„Než začnu, musím si udělat hezký poznámky“',
  ],

  marqueeLabel: 'Co si říkají studenti',

  reframe: {
    kicker: 'Malé tajemství',
    title: ['Nejsi ~~líný~~.', 'Tvůj mozek jen miluje ==okamžitou odměnu==.'],
    body:
      'TikTok ti dá odměnu hned. Kapitola ze statistiky? Možná za tři týdny u zkoušky. Není divu, že mozek volí telefon. Nepotřebuješ víc vůle. Stačí ho trochu přechytračit.',
    points: [
      {
        title: 'Odkládání není lenost',
        text: 'Je to útěk před nepříjemným pocitem. Nuda, strach, že to pokazíš, chaos v hlavě.',
      },
      {
        title: 'Motivace přijde až po startu',
        text: 'Ne před ním. Proto stačí 5 minut. Zbytek se rozjede sám.',
      },
      {
        title: 'Systém porazí vůli',
        text: 'Vůle dojde ve tři odpoledne. Systém funguje i v půlce zkouškového.',
      },
    ],
  },

  quiz: {
    kicker: 'Kvíz · 30 sekund',
    title: 'Jaký jsi odkladač?',
    intro: 'Čtyři typy, čtyři otázky. Žádná špatná odpověď (kromě „udělám to zítra“).',
    start: 'Spustit kvíz',
    progress: 'Otázka',
    back: 'Zpět',
    restart: 'Zkusit znovu',
    resultKicker: 'Tvůj typ',
    resultCta: 'Pošli mi tipy pro můj typ',
    tipLabel: 'Tip na prvních 5 minut',
    types: {
      perfekcionista: {
        name: 'Perfekcionista',
        text: 'Nezačneš, dokud nemáš dokonalý plán, dokonalé poznámky a dokonalou náladu. Takže nezačneš.',
        tip: 'Napiš schválně blbou první verzi. Má být špatně. Máš na to 5 minut.',
      },
      mobil: {
        name: 'Utíkač k mobilu',
        text: 'Otevřeš skripta, mozek zavolá o pomoc a ruka sama sáhne po telefonu. Je to reflex, ne slabost.',
        tip: 'Telefon do jiné místnosti. Ne do šuplíku. Do jiné místnosti.',
      },
      zahlceny: {
        name: 'Zahlcený',
        text: 'Máš toho tolik, že nevíš, kde začít. Tak nezačneš nikde a cítíš se ještě hůř.',
        tip: 'Vyber jednu věc, která zabere 5 minut. Jen jednu. Zbytek počká.',
      },
      posledni: {
        name: 'Na poslední chvíli',
        text: 'Funguješ jen pod tlakem. Adrenalin ve tři ráno je tvůj nejlepší kamarád i nepřítel.',
        tip: 'Udělej si falešný deadline o 3 dny dřív a řekni ho nahlas kamarádovi.',
      },
    },
    questions: [
      {
        q: 'Je 20:00, zítra máš zkoušku. Co děláš?',
        answers: [
          { text: 'Přepisuju poznámky načisto, ať jsou hezký.', type: 'perfekcionista' },
          { text: 'Jen mrknu na TikTok… a je 23:40.', type: 'mobil' },
          { text: 'Koukám na 400 slajdů a nevím, kde začít.', type: 'zahlceny' },
          { text: 'V klidu. Pravá práce začíná o půlnoci.', type: 'posledni' },
        ],
      },
      {
        q: 'Bakalářka. Jak to vypadá?',
        answers: [
          { text: 'Mám 14 verzí úvodu. Žádná není dost dobrá.', type: 'perfekcionista' },
          { text: 'Otevřu Word, pak YouTube, pak lednici.', type: 'mobil' },
          { text: 'Rešerše, data, citace… radši na to nemyslím.', type: 'zahlceny' },
          { text: 'Odevzdání je v květnu. Je březen. Pohoda.', type: 'posledni' },
        ],
      },
      {
        q: 'Co tě nejvíc vystihuje?',
        answers: [
          { text: 'Buď to udělám pořádně, nebo vůbec.', type: 'perfekcionista' },
          { text: 'Mám „jen na chvilku“ otevřených 23 appek.', type: 'mobil' },
          { text: 'Můj to-do list má vlastní to-do list.', type: 'zahlceny' },
          { text: 'Deadline je můj osobní trenér.', type: 'posledni' },
        ],
      },
      {
        q: 'Kdy se ti nejlíp pracuje?',
        answers: [
          { text: 'Až budu mít ideální podmínky. (Nikdy.)', type: 'perfekcionista' },
          { text: 'Když mám vybitý telefon.', type: 'mobil' },
          { text: 'Když mi někdo řekne, čím začít.', type: 'zahlceny' },
          { text: 'Když už fakt hoří.', type: 'posledni' },
        ],
      },
    ],
  },

  lead: {
    kicker: 'Zdarma',
    title: 'SOS karta zkouškového',
    text: 'Jedna stránka, která tě vytáhne z paniky noc před zkouškou. Co dělat v jakém pořadí, když zbývá 12 hodin. Pošleme ti ji do mailu.',
    quizTitle: 'Pošleme ti SOS kartu + tipy pro tvůj typ',
    quizText: 'Do mailu ti dorazí SOS karta zkouškového a pár krátkých tipů přesně pro tvůj typ odkladače.',
    nameLabel: 'Jméno (nepovinné)',
    namePlaceholder: 'Jak ti máme říkat?',
    emailLabel: 'E-mail',
    emailPlaceholder: 'tvuj@email.cz',
    consent:
      'Souhlasím se zasíláním SOS karty a občasných tipů na e-mail. Odhlásit se můžu jedním klikem. Víc v [zásadách ochrany osobních údajů](/gdpr).',
    submit: 'Pošlete mi ji',
    sending: 'Posílám…',
    successTitle: 'Hotovo. Mrkni do mailu.',
    successText: 'SOS karta je na cestě. Kdyby nedorazila do pár minut, zkontroluj složku Promo nebo Spam.',
    error: 'Něco se pokazilo a nebylo to tebou. Zkus to prosím za chvíli znovu.',
    invalidEmail: 'Tenhle e-mail nevypadá úplně dobře. Zkontroluješ ho?',
    consentRequired: 'Bez souhlasu ti nemůžeme nic poslat. Zaškrtni ho prosím.',
    perks: ['1 stránka A4', 'Plán na posledních 12 hodin', 'Funguje i ve 2 ráno'],
    mockup: {
      title: 'SOS karta zkouškového',
      stamp: 'SOS',
      rows: [
        ['T−12 h', 'Telefon do jiné místnosti'],
        ['T−11 h', 'Vyber 3 největší témata'],
        ['T−10 h', 'Bloky 25 min + 5 min pauza'],
        ['T−4 h', 'Shrnutí na 1 stránku'],
        ['T−3 h', 'Spát. Fakt.'],
        ['T−0', 'Snídaně a jdeš na to'],
      ],
    },
  },

  inside: {
    kicker: 'Co v tom je',
    title: '8 kapitol. Každá na 5 minut.',
    intro:
      'Žádná vata, žádné „věř si a dokážeš to“. Jedna kapitola = jedna technika, kterou hned vyzkoušíš. Celé to přečteš za dvě odpoledne.',
    chapters: [
      { time: '0:00', title: 'Proč odkládáš', text: 'A proč to vůbec není lenost. Co se ti děje v hlavě, když otevřeš skripta.' },
      { time: '0:45', title: 'Pravidlo 5 minut', text: 'Jak začít, když se ti fakt nechce. Nejmenší možný krok, který rozjede celý den.' },
      { time: '1:30', title: 'Mobil vs. ty', text: 'Jak vyhrát nad TikTokem bez digitálního detoxu v klášteře.' },
      { time: '2:15', title: 'Zkouškové bez paniky', text: 'Plán na 14 dní před zkouškou. A plán B, když ti zbývají tři.' },
      { time: '3:00', title: 'Bakalářka po kouscích', text: 'Od prázdné stránky k první kapitole. Malé kroky místo jednoho obřího strašáka.' },
      { time: '3:45', title: 'Hotové > dokonalé', text: 'Jak umlčet perfekcionistu, který ti ve 14 verzích maže úvod.' },
      { time: '4:30', title: 'Když to nevyjde', text: 'Restart bez výčitek. Jeden propadák neznamená, že jsi propadák.' },
      { time: '5:00', title: 'Teď', text: 'Tvůj osobní plán na příští týden. Hotový za 5 minut.' },
    ],
    bonusesKicker: 'Bonusy v balíčku',
    bonusesTitle: 'A k tomu nářadí',
    bonuses: [
      { kind: 'planner', title: 'Týdenní plánovač', text: 'PDF k tisku i do tabletu. Týden na jedné stránce, bez 40 kolonek.' },
      { kind: 'notion', title: 'Notion šablona', text: 'Zkouškové, bakalářka a deadliny na jednom místě. Duplikuješ jedním klikem.' },
      { kind: 'sos', title: 'SOS karta zkouškového', text: 'Co dělat, když je noc před zkouškou a ty máš přečtenou polovinu.' },
      { kind: 'worksheets', title: 'Pracovní listy', text: 'Ke každé kapitole jeden list. Vyplníš za 5 minut, výsledek vidíš hned.' },
    ],
  },

  how: {
    kicker: 'Jak to funguje',
    title: 'Tři kroky. Žádný z nich není „zítra“.',
    steps: [
      { title: 'Stáhni', text: 'Zaplatíš a do minuty máš PDF v mailu. Žádná registrace, žádná appka.' },
      { title: 'Přečti kapitolu za 5 minut', text: 'Jedna kapitola, jedna technika. Krátce, konkrétně, bez keců.' },
      { title: 'Začni', text: 'Na konci každé kapitoly je úkol na 5 minut. Pustíš časovač a jedeš.' },
    ],
  },

  // TODO: real testimonials – až budou skutečné recenze od čtenářů, nahraď texty
  // a nastav placeholder: false (zmizí štítek „ukázka“). Nevymýšlej jména.
  testimonials: {
    kicker: 'Recenze',
    title: 'Co říkají betačtenáři',
    note: 'E-book právě vychází. Sem dáme první skutečné recenze. Zatím tu jsou ukázky.',
    placeholderBadge: 'Ukázka',
    items: [
      {
        quote: 'Tady bude recenze od prvního čtenáře. Třeba o tom, jak konečně napsal úvod bakalářky.',
        author: 'Betačtenář/ka',
        role: 'Obor, ročník',
        placeholder: true,
      },
      {
        quote: 'Tady bude recenze o zkouškovém, které nebylo jedna velká noc před zkouškou.',
        author: 'Betačtenář/ka',
        role: 'Obor, ročník',
        placeholder: true,
      },
      {
        quote: 'Tady bude recenze o tom, kolik času šetří telefon v jiné místnosti.',
        author: 'Betačtenář/ka',
        role: 'Obor, ročník',
        placeholder: true,
      },
    ],
  },

  pricing: {
    kicker: 'Cena',
    title: 'Míň než jedna pizza s kamarády.',
    intro: 'Jednorázově. Žádné předplatné, žádné háčky. Stáhneš a máš navždy.',
    launchBadge: 'Launch cena',
    popular: 'Nejoblíbenější',
    regularLabel: 'Běžná cena',
    eurLabel: 'Ze Slovenska',
    paymentNote: 'Platba kartou nebo QR převodem přes SimpleShop. Faktura a odkaz ke stažení ti přijdou hned do mailu.',
    plans: {
      basic: {
        name: 'E-book',
        text: 'Všechno, co potřebuješ, abys dneska začal(a).',
        features: ['E-book PDF, cca 70 stran', '8 kapitol na 5 minut čtení', 'Čte se dobře i na mobilu', 'Aktualizace zdarma'],
        cta: 'Chci e-book',
      },
      bundle: {
        name: 'E-book + bonusy',
        text: 'E-book a k tomu nářadí na celé zkouškové i bakalářku.',
        features: [
          'Všechno z e-booku',
          'Týdenní plánovač (PDF)',
          'Notion šablona',
          'SOS karta zkouškového',
          'Pracovní listy ke kapitolám',
        ],
        cta: 'Chci všechno',
      },
    },
  },

  // TODO: záruku musí potvrdit majitel – upravit podmínky (lhůtu, postup) podle skutečnosti.
  guarantee: {
    kicker: 'Férová záruka',
    title: 'Nepomohlo? Vrátíme peníze.',
    text:
      'Když ti e-book nepomůže začít, napiš nám do 14 dnů od nákupu na e-mail a vrátíme ti peníze. Bez dotazníku a bez „a proč?“.',
  },

  faq: {
    kicker: 'FAQ',
    title: 'Otázky, které si klademe místo učení',
    items: [
      {
        q: 'V jakém formátu e-book je? Přečtu ho na mobilu?',
        a: 'Je to PDF. Otevřeš ho na mobilu, tabletu i v počítači. Sazba je dělaná tak, aby se dala číst i na malém displeji, takže žádné zoomování. Notion šablonu si jedním klikem zkopíruješ do svého Notionu.',
      },
      {
        q: 'Jak dlouho trvá to přečíst?',
        a: 'Celé zhruba dvě hodiny. Ale nemusíš najednou. Každá kapitola je na 5 minut. Jedna kapitola, jeden krok, hotovo.',
      },
      {
        q: 'Jak můžu zaplatit?',
        a: 'Kartou nebo QR platbou (převodem). Platba probíhá přes zabezpečenou bránu SimpleShop. Hned po zaplacení ti přijde e-mail s odkazem ke stažení.',
      },
      {
        q: 'Dostanu fakturu?',
        a: 'Jo. Fakturu ti systém pošle automaticky e-mailem hned po zaplacení. Kupuješ na firmu? Vyplň v objednávce IČO.',
      },
      {
        q: 'Funguje to i na Slovensku?',
        a: 'Jasně. Zaplatíš v eurech kartou i převodem. E-book je zatím v češtině, ale přečteš ho bez problémů. Slovenská verze se chystá.',
      },
      {
        q: 'Dostanu aktualizace?',
        a: 'Ano, zdarma. Když e-book vylepšíme nebo přidáme kapitolu, pošleme ti novou verzi na e-mail, který zadáš při nákupu.',
      },
      {
        q: 'Co když mi to nepomůže?',
        a: 'Napiš nám do 14 dnů od nákupu a vrátíme ti peníze. Víc nahoře v sekci Férová záruka.',
      },
    ],
  },

  finalCta: {
    title: ['Žádných dalších 5 minut.', 'Začni ==teď==.'],
    text: 'Odpočet běží. Ty můžeš taky.',
    cta: 'Chci to',
    timerLabel: 'Do startu zbývá',
    timerDone: 'Start!',
  },

  footer: {
    tagline: 'Pro všechny, co tohle čtou místo učení. To je v pohodě. Ale teď už jdi na to.',
    legalTitle: 'Právní věci',
    legal: [
      { label: 'Obchodní podmínky', href: '/obchodni-podminky' },
      { label: 'Ochrana osobních údajů', href: '/gdpr' },
      { label: 'Reklamační řád', href: '/reklamacni-rad' },
    ],
    contactTitle: 'Kontakt',
    socialTitle: 'Sleduj nás',
    cookieSettings: 'Nastavení cookies',
    rights: 'Všechna práva vyhrazena.',
    signoff: '~~zítra~~ teď.',
    toTop: 'Ještě 5 minut – zpět nahoru',
  },

  miniTimer: { label: 'Do startu', done: 'Čas začít', cta: 'Chci to' },

  cookies: {
    label: 'Souhlas s analytikou',
    text: 'Používáme jen to nutné. Anonymní statistiky návštěvnosti zapneme, jen když řekneš. Žádná reklama, žádné sledování napříč webem.',
    decline: 'Jen nutné',
    accept: 'Povolit statistiky',
  },

  notFound: {
    title: 'Tahle stránka si dala ještě 5 minut.',
    text: 'A pak dalších 5. A pak zmizela. Zkus to od začátku.',
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
