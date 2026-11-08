"""Obsahová databáze e-booku „Ještě 5 minut“.

Všechno, z čeho Scripter skládá videa: bolesti (háčky), scénky, vysvětlení,
řešení a úkoly z každé z 8 kapitol. Texty jsou psané pro mluvené slovo.

Mini-syntaxe v textech (viz j5m/markup.py):
  *slovo*        klíčové slovo → v titulcích zvýrazněné barvou a větší
  [řekni|ukaž]   co hlas vysloví | co se ukáže v titulku, např. [pět|5]

Každý řádek je L(text, "broll tagy"). Tagy určují, jaký B-roll se pod větu
hodí (seznam a anglické dotazy pro Pexels jsou v BROLL_TAGS).
"""

from __future__ import annotations


def L(text: str, tags: str = "") -> dict:
    return {"text": text, "broll": tags.split()}


# Tag → dotaz pro Pexels (anglicky, protože tak se tam hledá nejlíp).
# Stejné názvy použij pro složky vlastních záběrů ve video/library/<tag>/.
BROLL_TAGS: dict[str, str] = {
    "library": "university library student studying",
    "laptop_night": "laptop typing at night dark room",
    "phone_scroll": "scrolling phone in bed night",
    "phone_down": "phone face down on desk",
    "notes": "handwriting notes notebook study",
    "desk": "study desk top view books",
    "clock": "clock ticking close up",
    "exam": "students writing exam",
    "stress": "stressed student head in hands",
    "coffee": "coffee cup desk morning study",
    "campus": "university campus students walking",
    "writing": "writing on laptop document",
    "timer": "timer countdown phone",
    "calendar": "planner calendar writing plan",
    "city_night": "city night window lights",
    "books": "stack of books library shelf",
    "sleep": "person sleeping bed morning light",
    "tram": "tram city commute window",
    "friends_study": "friends studying together table",
    "window_rain": "rain on window night",
    "tidy": "cleaning desk organizing room",
}


CHAPTERS: list[dict] = [
    # ------------------------------------------------------------------ 1
    {
        "id": 1,
        "title": "Proč odkládáme",
        "task": "Mapa odkládání",
        "headline": "Proč odkládáš učení (a není to lenost)",
        "hashtags": ["prokrastinace", "odkladani", "studium"],
        "pov_hooks": [
            L("POV: zkouška je za týden a ty právě *uklízíš šuplík*.", "tidy desk"),
            L("POV: otevřeš skripta a za tři minuty jsi na *mobilu*.", "phone_scroll"),
        ],
        "myth_hooks": [
            L("Myslíš si, že odkládáš, protože jsi *línej*. Nejsi.", "stress"),
            L("Odkládání není problém s časem. Je to problém s *pocitem*.", "window_rain"),
        ],
        "mistake_hooks": [
            L("Největší chyba? Myslet si, že ti chybí *silná vůle*.", "stress"),
        ],
        "list_hook": L("[Tři|3] věci, co ti o odkládání nikdo neřekl.", "desk"),
        "scenes": [
            L("Sedíš nad skripty, víš, co by bylo rozumný, a o deset minut později koukáš na *videa*.", "laptop_night phone_scroll"),
            L("Najednou je strašně důležitý vyluxovat, odepsat mámě a *zkontrolovat Instagram*.", "phone_scroll tidy"),
        ],
        "insights": [
            L("Úkol v tobě vyvolá nepříjemnej pocit. *Nejistotu*, nudu nebo strach, že to nebude dobrý.", "stress notes"),
            L("Mozek chce ten pocit hned vypnout. A mobil ti nabídne *úlevu za dvě sekundy*.", "phone_scroll"),
            L("Úleva přijde hned, *výčitky až potom*. A tak se ta smyčka točí pořád dokola.", "city_night clock"),
            L("Odkládají lidi chytrý, pilný i zodpovědný. Nejsi rozbitej, jen bojuješ na *špatným místě*.", "campus library"),
        ],
        "fixes": [
            L("*Zmenši úkol*. Čím menší úkol, tím menší odpor. A tím míň důvodů utíkat.", "notes desk"),
            L("*Ztiž si útěk*. Když mobil není po ruce, odpor často přejde dřív, než k němu dojdeš.", "phone_down"),
        ],
        "list_items": [
            L("Jedna: není to lenost. Je to útěk před *nepříjemným pocitem*.", "stress"),
            L("Dvě: úleva přijde hned, ale výčitky *až potom*. Proto se to opakuje.", "phone_scroll"),
            L("Tři: silou vůle to nevyhraješ. *Zmenši úkol* a ztiž si útěk.", "notes"),
        ],
        "task_intro": L("Úkol na dnešek. Zabere [pět|5] minut.", "notes"),
        "task_steps": [
            L("Vypiš *všechno*, co teď odkládáš. Nehodnoť, jen piš.", "notes"),
            L("Vyber *jednu věc*. Tu, která tě nejvíc tíží.", "desk"),
            L("A přepiš ji *konkrétně*. Ne učit se na statistiku, ale projít příklady [jedna až deset|1–10].", "writing notes"),
        ],
        "punches": [
            L("Není to lenost. Je to *smyčka*. A smyčka se dá přerušit.", "clock"),
            L("Odkládání není povaha. Je to *zvyk*. A zvyky se dají přepsat.", "coffee"),
        ],
    },
    # ------------------------------------------------------------------ 2
    {
        "id": 2,
        "title": "Pravidlo pěti minut",
        "task": "Prvních pět minut",
        "headline": "Pravidlo 5 minut",
        "hashtags": ["pravidlo5minut", "motivace", "studium"],
        "pov_hooks": [
            L("POV: celý odpoledne se ti nechce otevřít *seminárku*.", "laptop_night"),
            L("POV: už hodinu plánuješ, jak *začneš* psát seminárku.", "calendar writing"),
        ],
        "myth_hooks": [
            L("Myslíš si, že na začátek potřebuješ *motivaci*. Je to přesně naopak.", "coffee"),
        ],
        "mistake_hooks": [
            L("Největší chyba? Dát si úkol učit se na zkoušku. To není úkol, to je *mlha*.", "window_rain"),
        ],
        "list_hook": L("[Tři|3] triky, jak začít, když se ti *fakt nechce*.", "desk"),
        "scenes": [
            L("Největší odpor cítíš *před začátkem*, ne během práce.", "stress"),
            L("A když to konečně otevřeš, po deseti minutách zjistíš, že to vlastně *jde*.", "writing"),
        ],
        "insights": [
            L("[Pět|5] minut je tak málo, že se proti nim těžko hledá *výmluva*.", "timer"),
            L("Mozek se nebrání, protože se nezavazuje k *celýmu odpoledni*.", "clock"),
            L("Jakmile se rozjedeš, nepříjemnej pocit často *sám povolí*.", "writing"),
        ],
        "fixes": [
            L("Domluv se sám se sebou: budu na tom pracovat [pět|5] minut. *Pak smím přestat.*", "timer"),
            L("Ale mysli to vážně. Po pěti minutách *fakt smíš skončit*. Jinak mozek ten trik prokoukne.", "clock"),
            L("Ne učit se na makro. Ale otevřít skripta a přečíst *dvě strany*.", "books notes"),
            L("Ne napsat seminárku. Ale otevřít dokument a napsat *nadpis a jednu větu*.", "writing"),
            L("Nejde ani [pět|5] minut? Zmenši to na *dvě*. Cílem dneška není postoupit, ale *začít*.", "desk"),
        ],
        "list_items": [
            L("Jedna: dej si jen [pět|5] minut. A pak *fakt smíš přestat*.", "timer"),
            L("Dvě: z mlhy udělej krok. Ne napsat seminárku, ale *napsat nadpis*.", "writing"),
            L("Tři: rozhodni předem, kdy začneš. Ne odpoledne, ale *ve dvě u stolu*.", "clock desk"),
        ],
        "task_intro": L("Zkus to hned teď.", "timer"),
        "task_steps": [
            L("Napiš si první krok, kterej zvládneš do *pěti minut*.", "notes"),
            L("Rozhodni, kdy přesně začneš. Ne odpoledne, ale *ve dvě po obědě u stolu*.", "clock desk"),
            L("Nastav *časovač na [pět|5] minut* a jeď. Pak se rozhodni, jestli pokračuješ.", "timer"),
        ],
        "punches": [
            L("Začínat je *dovednost*. A trénuje se jako cokoli jinýho.", "coffee"),
            L("[Pět|5] minut práce je pořád o pět víc *než včera*.", "timer"),
        ],
    },
    # ------------------------------------------------------------------ 3
    {
        "id": 3,
        "title": "Mobil",
        "task": "Telefon z dosahu",
        "headline": "Jak tě mobil krade o učení",
        "hashtags": ["screentime", "mobil", "soustredeni"],
        "pov_hooks": [
            L("POV: jen na chvilku Instagram. A najednou je o *hodinu víc*.", "phone_scroll clock"),
            L("POV: učíš se a mobil leží *hned vedle skript*.", "phone_scroll desk"),
        ],
        "myth_hooks": [
            L("Mobil není tvůj nepřítel. Jen by neměl bejt *první volba*.", "phone_down"),
        ],
        "mistake_hooks": [
            L("Největší chyba? Snažit se mobil porazit *silou vůle*.", "phone_scroll"),
        ],
        "list_hook": L("[Tři|3] úpravy mobilu, který ti zachrání *zkouškový*.", "phone_down"),
        "scenes": [
            L("Vytáhneš ho za *dvě sekundy*. A než se naděješ, je o půl hodiny později.", "phone_scroll clock"),
            L("Každý zaváhání u úkolu skončí v telefonu, když leží *na stole*.", "phone_scroll desk"),
        ],
        "insights": [
            L("Aplikace jsou navržený tak, aby tě udržely *co nejdýl*. Vůle proti tomu prohrává. Vyhrává *vzdálenost*.", "phone_scroll"),
            L("Když je mobil v jiný místnosti, musel by ses zvednout a dojít pro něj. A ten malej odpor *většinou stačí*.", "phone_down"),
        ],
        "fixes": [
            L("*Vypni upozornění* u aplikací, který tě vytrhávají.", "phone_scroll"),
            L("Při učení dej telefon *mimo dosah*. Do tašky, do šuplíku, klidně spolubydlícímu.", "phone_down"),
            L("Zapni *režim soustředění* na dobu učení.", "phone_down timer"),
            L("*Odhlas se* z aplikace, kde trávíš nejvíc času. Zadávat znova heslo je přesně ten malej odpor, co potřebuješ.", "phone_scroll"),
            L("Rozhodni se předem: když sáhnu po mobilu bez důvodu, *položím ho displejem dolů* a dokončím větu.", "phone_down notes"),
        ],
        "list_items": [
            L("Jedna: *vypni upozornění* u aplikací, který tě vytrhávají.", "phone_scroll"),
            L("Dvě: při učení dej mobil *do jiný místnosti*.", "phone_down"),
            L("Tři: *odhlas se* z appky, kde trávíš nejvíc času.", "phone_scroll"),
        ],
        "task_intro": L("Úkol na [pět|5] minut. *Teď hned.*", "timer"),
        "task_steps": [
            L("Vypni upozornění aspoň u *tří aplikací*.", "phone_scroll"),
            L("Dej telefon do *jiný místnosti* a pět minut pracuj.", "phone_down desk"),
            L("A čárkuj, kolikrát tě to k mobilu táhlo. *Nehodnoť, jen počítej.*", "notes"),
        ],
        "punches": [
            L("Co je daleko, to se *nedělá*.", "phone_down"),
            L("Nejde o to, že bys byl slabej. Jde o to, že mobil je *moc blízko*.", "phone_scroll"),
        ],
    },
    # ------------------------------------------------------------------ 4
    {
        "id": 4,
        "title": "Zkouškové",
        "task": "Rozpis zkouškového",
        "headline": "Plán na zkouškové za 14 dní",
        "hashtags": ["zkouskove", "zkouska", "uceni"],
        "pov_hooks": [
            L("POV: zkouška je ráno a ty se to učíš *noc předtím*. Zase.", "laptop_night city_night"),
            L("POV: zbývají ti *tři dny* a umíš z toho tak půlku.", "stress calendar"),
        ],
        "myth_hooks": [
            L("Učení noc před zkouškou má jednu výhodu. Strach přebije odpor. Jinak má *samý nevýhody*.", "laptop_night"),
        ],
        "mistake_hooks": [
            L("Největší chyba ve zkouškovým? Pořád dokola *číst poznámky*.", "notes books"),
        ],
        "list_hook": L("Jak se naučit na zkoušku za [čtrnáct dní|14 dní] *bez panikaření*.", "calendar"),
        "scenes": [
            L("Látku si pamatuješ pár dní, umíš jí málo a jdeš na zkoušku *nevyspalej*.", "sleep exam"),
            L("Čteš to potřetí a pořád máš pocit, že to *neumíš*.", "notes stress"),
        ],
        "insights": [
            L("Stejná látka *třikrát po hodině* s odstupem vydrží v hlavě mnohem dýl než tři hodiny v kuse.", "clock books"),
            L("Zakryj text a zkus odpovědět *zpaměti*. Je to nepříjemný, protože hned vidíš, co nevíš. A přesně proto to funguje.", "notes"),
        ],
        "fixes": [
            L("Zbývají tři dny? Roztřiď okruhy na *umím, trochu a vůbec*.", "notes"),
            L("Začni tím, co je u zkoušky často a co *trochu umíš*. Tam získáš nejvíc za nejmíň času.", "exam notes"),
            L("Uč se *vybavováním*, ne čtením. Ke každýmu okruhu tři otázky a odpovídej zpaměti.", "notes"),
            L("A *spi*. Noc bez spánku ti vezme víc, než kolik se za ni naučíš.", "sleep"),
        ],
        "list_items": [
            L("[Dny čtrnáct až dvanáct|Dny 14–12]: *zmapuj*. Sylabus, okruhy, slajdy a starý otázky.", "calendar notes"),
            L("[Dny jedenáct až čtyři|Dny 11–4]: *projdi a vybav si*. Dva až čtyři bloky denně.", "library notes"),
            L("Poslední tři dny: *žádná nová látka*. Jen opakuj a dej si zkoušku nanečisto.", "exam"),
        ],
        "task_intro": L("Udělej si rozpis *ještě dneska*.", "calendar"),
        "task_steps": [
            L("Napiš datum nejbližší zkoušky a spočítej, kolik dní *zbývá*.", "calendar"),
            L("Sepiš *všechny okruhy* a rozděl je do dnů.", "notes"),
            L("A dnešní celek otevři a *pět minut* na něm pracuj.", "timer desk"),
        ],
        "punches": [
            L("Panika je normální. Ale i tři dny jsou pořád *patnáct až dvacet bloků* práce.", "clock"),
            L("Pustit okruh, na kterej se skoro neptají, je *rozhodnutí*. Ne selhání.", "exam"),
        ],
    },
    # ------------------------------------------------------------------ 5
    {
        "id": 5,
        "title": "Bakalářská práce",
        "task": "První kousek",
        "headline": "Jak konečně začít bakalářku",
        "hashtags": ["bakalarka", "bakalarskaprace", "diplomka"],
        "pov_hooks": [
            L("POV: bakalářka je pořád *až po zkouškovým*.", "calendar"),
            L("POV: otevřeš dokument s bakalářkou a koukáš na *prázdnou stránku*.", "writing laptop_night"),
        ],
        "myth_hooks": [
            L("Bakalářka se nepíše. Bakalářka se *skládá z malých kroků*.", "writing"),
        ],
        "mistake_hooks": [
            L("Největší chyba u bakalářky? Začínat *textem*. A ne osnovou.", "writing"),
        ],
        "list_hook": L("[Tři|3] pravidla, díky kterým bakalářku *fakt dopíšeš*.", "library"),
        "scenes": [
            L("Je velká, termín je daleko, nikdo tě nehlídá a nic podobnýho jsi nikdy nepsal. Dohromady z toho je *hora*.", "library books"),
            L("A schůzku s vedoucím odkládáš, protože *zatím nemáš co ukázat*.", "campus"),
        ],
        "insights": [
            L("Každej z těch důvodů by stačil sám. Dohromady je bakalářka *ideální úkol na odkládání*.", "books"),
            L("Hora se neleze najednou. Rozlož ji na kroky, který zvládneš za *patnáct až pětadvacet minut*.", "notes"),
        ],
        "fixes": [
            L("*Začni osnovou*, ne textem. Jen nadpisy kapitol a pod každou dvě tři odrážky.", "notes writing"),
            L("Piš *ošklivej první draft*. Nech si v textu poznámky jako doplnit a jeď dál.", "writing"),
            L("Ne napsat teorii. Ale *napsat první odstavec* podkapitoly [dva jedna|2.1].", "writing"),
            L("Vedoucí není soudce. Domluv si *pravidelnej kontakt* a posílej i nehotový kusy.", "campus"),
        ],
        "list_items": [
            L("Jedna: *začni osnovou*. Prázdná stránka děsí, osnova ne.", "notes"),
            L("Dvě: piš *ošklivej první draft*. Upravovat jde jen to, co je napsaný.", "writing"),
            L("Tři: *krátce, ale často*. Pětadvacet minut denně je víc než celej víkend jednou za měsíc.", "library timer"),
        ],
        "task_intro": L("Tohle zvládneš *ještě dneska*.", "desk"),
        "task_steps": [
            L("Sepiš *hlavní části* svý práce.", "notes"),
            L("Vyber tu, na který teď pracuješ, a rozlož ji na *pět až osm kroků*.", "notes writing"),
            L("První krok musí jít udělat do *pěti minut*. A udělej ho *dneska*.", "timer"),
        ],
        "punches": [
            L("Prázdná stránka děsí. *Osnova ne.*", "writing"),
            L("Termín schůzky s vedoucím je ten nejlepší *malej deadline*.", "calendar"),
        ],
    },
    # ------------------------------------------------------------------ 6
    {
        "id": 6,
        "title": "Perfekcionismus",
        "task": "Definice hotovo",
        "headline": "Perfekcionismus tě brzdí",
        "hashtags": ["perfekcionismus", "seminarka", "studium"],
        "pov_hooks": [
            L("POV: přepisuješ první větu seminárky *už počtvrtý*.", "writing laptop_night"),
        ],
        "myth_hooks": [
            L("Musí to bejt dokonalý zní jako vysoký nároky. V praxi to znamená, že *nezačneš vůbec*.", "writing"),
        ],
        "mistake_hooks": [
            L("Největší chyba? Psát a *opravovat zároveň*.", "writing"),
        ],
        "list_hook": L("[Tři|3] otázky, který si polož, *než začneš psát*.", "notes"),
        "scenes": [
            L("Když má bejt výsledek bezchybnej, každej začátek je *riziko*.", "stress"),
            L("A nejjistější způsob, jak neudělat chybu, je *nedělat nic*.", "window_rain"),
        ],
        "insights": [
            L("Odkládáš, protože se bojíš, že to nebude dobrý. Pak máš málo času, takže to dobrý *opravdu není*.", "clock stress"),
            L("Seminárka nemusí bejt nejlepší v ročníku. Musí *splnit zadání*.", "writing"),
            L("Většina zaseknutí vzniká tím, že se snažíš napsat první větu rovnou *dokonale*.", "writing"),
        ],
        "fixes": [
            L("Řekni si předem, co znamená *hotovo*. A až toho dosáhneš, skonči.", "notes"),
            L("Rozděl práci na dvě fáze. Když píšeš, *nepiluješ*. Když upravuješ, nepíšeš nový.", "writing"),
        ],
        "list_items": [
            L("Jedna: co přesně musí výsledek *splňovat*? Zadání, rozsah, kritéria. Nic navíc.", "notes"),
            L("Dvě: jakej výsledek ti *stačí*? Známka, počet stran, úroveň.", "writing"),
            L("Tři: kolik času tomu *dáš*? Až vyprší, odevzdáš, co máš.", "timer"),
        ],
        "task_intro": L("Mini úkol na [pět|5] minut.", "timer"),
        "task_steps": [
            L("Vezmi svůj úkol a napiš, co přesně musí *splňovat*.", "notes"),
            L("Napiš, jakej výsledek ti *stačí*, a urči *časovej limit*.", "notes timer"),
            L("A pět minut pracuj na verzi *dost dobrá*. Rychleji, než je ti příjemný.", "writing"),
        ],
        "punches": [
            L("Hotový se dá vylepšit. *Nezačatý ne.*", "writing"),
            L("Dost dobrý je *cíl*. Ne kompromis.", "coffee"),
        ],
    },
    # ------------------------------------------------------------------ 7
    {
        "id": 7,
        "title": "Když to nevyjde",
        "task": "Plán návratu",
        "headline": "Co dělat, když to nevyjde",
        "hashtags": ["motivace", "restart", "studium"],
        "pov_hooks": [
            L("POV: tři dny za sebou a skripta *ani neotevřený*.", "books window_rain"),
        ],
        "myth_hooks": [
            L("Jeden vynechanej den nic nezkazí. Zkazí to až myšlenka, že *už je to stejně jedno*.", "window_rain"),
        ],
        "mistake_hooks": [
            L("Největší chyba po špatným dni? Snažit se *všechno dohnat*.", "stress"),
        ],
        "list_hook": L("[Tři|3] kroky, jak se vrátit po dni, kdy se *nic neudělalo*.", "coffee"),
        "scenes": [
            L("Přijde to. Den, kdy se nic neudělá. Možná *tři takový za sebou*.", "sleep window_rain"),
            L("A teď se rozhoduje, jestli se vrátíš, nebo to celý odepíšeš se slovy *stejně mi to nejde*.", "stress"),
        ],
        "insights": [
            L("Z plánu na hodinu jsou najednou tři. Úkol vyroste, odpor taky a smyčka se roztočí *znovu*.", "clock"),
            L("Výčitky jsou nepříjemnej pocit. A víš, kam takový pocity vedou. K *dalšímu útěku*.", "phone_scroll"),
        ],
        "fixes": [
            L("*Nedoháněj.* Pokračuj tam, kde jsi skončil, a plán prostě posuň.", "calendar"),
            L("Udělej *dvouminutovou verzi*. Otevři úkol a udělej jeden krok. I jedna věta se počítá.", "writing timer"),
        ],
        "list_items": [
            L("Jedna: *neodsuzuj*. Řekni si, jeden den nevyšel. To se stává.", "coffee"),
            L("Dvě: *zmenši to*. Nedělej dneska dvojnásobek. Udělej dvouminutovou verzi.", "timer"),
            L("Tři: *naplánuj*. Kdy a co uděláš zítra. Čas, místo a první krok.", "calendar"),
        ],
        "task_intro": L("Napiš si tohle, *ještě než to přijde*.", "notes"),
        "task_steps": [
            L("Vzpomeň si na poslední den, kdy plán *nevyšel*, a najdi důvod.", "notes"),
            L("Napiš řešení, který na něj *příště použiješ*.", "notes"),
            L("A napiš si větu na návrat. Třeba: zítra [v devět|v 9:00] udělám *jeden krok*.", "clock notes"),
        ],
        "punches": [
            L("Nezáleží na tom, kolikrát vynecháš. Záleží na tom, *kolikrát se vrátíš*.", "campus"),
        ],
    },
    # ------------------------------------------------------------------ 8
    {
        "id": 8,
        "title": "Tvůj plán",
        "task": "Plán na příští týden",
        "headline": "Týdenní plán, který vydrží",
        "hashtags": ["planovani", "produktivita", "studium"],
        "pov_hooks": [
            L("POV: v neděli večer si slibuješ, že od pondělka *fakt začneš*.", "calendar city_night"),
        ],
        "myth_hooks": [
            L("Plán nestav na hodinách. Stav ho na *blocích*.", "timer calendar"),
        ],
        "mistake_hooks": [
            L("Největší chyba v plánování? Dát si na tejden *pět hlavních úkolů*.", "calendar"),
        ],
        "list_hook": L("Jak si za [deset|10] minut naplánovat *celej tejden*.", "calendar"),
        "scenes": [
            L("Barevná tabulka na celej tejden. A ve středu je to *celý pryč*.", "calendar"),
            L("Slibuješ si osm hodin učení denně a pak neuděláš *ani jednu*.", "stress clock"),
        ],
        "insights": [
            L("Blok je [pětadvacet|25] minut práce na jedný věci a pak [pět|5] minut pauza. Začíná se snáz, protože *konec je vidět*.", "timer"),
            L("Lepší málo *každej den* než hodně jednou.", "coffee desk"),
        ],
        "fixes": [
            L("Vyber *jeden až dva* hlavní úkoly. Ne pět.", "notes"),
            L("Každýmu bloku dej *čas a místo*. Ideálně pořád stejný.", "library clock"),
            L("Ke každýmu bloku napiš *první krok*, ať nemusíš ráno vymýšlet, co dělat.", "notes"),
            L("Když tě během bloku něco napadne, *zapiš si to* na papír a vrať se k práci.", "notes"),
            L("Nezvládneš [pětadvacet|25] minut? Začni s *patnácti*. Důležitý je blok dokončit, ne jeho délka.", "timer"),
        ],
        "list_items": [
            L("Jedna: vyber *jeden až dva* hlavní úkoly. Ne pět.", "notes"),
            L("Dvě: každýmu bloku dej *čas, místo a první krok*.", "calendar"),
            L("Tři: v neděli *deset minut revize*. Co fungovalo, to nech.", "coffee"),
        ],
        "task_intro": L("Udělej to hned, *dokud to máš v hlavě*.", "calendar"),
        "task_steps": [
            L("Napiš *hlavní úkol* na příští tejden.", "notes"),
            L("Vyber dny a časy bloků a ke každýmu *první krok*.", "calendar"),
            L("A první blok si zapiš *do kalendáře v mobilu*. Jo, i telefon se někdy hodí.", "phone_down calendar"),
        ],
        "punches": [
            L("Neexistuje univerzální systém. Existuje ten, *kterej funguje tobě*.", "coffee"),
            L("Každej tejden přidej jen trochu. Za měsíc budeš *úplně jinde*.", "campus"),
        ],
    },
]


# Univerzální háček pro formát „challenge“ (úkol na 5 minut).
CHALLENGE_HOOKS = [
    L("Jestli tohle sleduješ *místo učení*, udělej se mnou jednu věc.", "phone_scroll"),
    L("Dej mi [pět|5] minut. *Jen [pět|5].*", "timer"),
    L("Nechce se ti? V pohodě. *Tohle zvládneš i tak.*", "desk"),
]

# Závěrečné výzvy. {ord} = řadová číslovka kapitoly.
CTAS = [
    L("Celej postup najdeš v [íbuku|e-booku] *Ještě [pět|5] minut*. Odkaz máš v biu.", "cover"),
    L("Tohle je [{ord_say}|{ord_show}] kapitola z [íbuku|e-booku] *Ještě [pět|5] minut*. Zbytek najdeš v biu.", "cover"),
    L("Osm kapitol, každá na [pět|5] minut čtení. *Ještě [pět|5] minut*, odkaz v biu.", "cover"),
    L("Jestli se v tom vidíš, mrkni na *Ještě [pět|5] minut*. Odkaz je v biu.", "cover"),
]

ORDINALS = {1: "první", 2: "druhá", 3: "třetí", 4: "čtvrtá", 5: "pátá", 6: "šestá", 7: "sedmá", 8: "osmá"}

# Mluvené vsuvky pro přirozenost. „lower“ = přilepí se před větu a ta začne
# malým písmenem; „alone“ = samostatná věta před další větou.
FILLERS = {
    "lower": ["Hele,", "Upřímně,"],
    "alone": ["Víš co?", "A teď pozor.", "Fakt.", "Vážně."],
}

BASE_HASHTAGS = ["vysoka", "vysokaskola", "student", "jeste5minut"]

CTA_STICKER = "Odkaz na e-book je v biu"


def chapter(chapter_id: int) -> dict:
    for ch in CHAPTERS:
        if ch["id"] == chapter_id:
            return ch
    raise KeyError(f"Kapitola {chapter_id} neexistuje (1–8).")
