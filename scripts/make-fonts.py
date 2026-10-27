"""
Vyrobí statický řez Archivo pro nadpisy (šířka 72 %, váha 800) jen se znaky pro češtinu a slovenštinu.
Variabilní soubor s osou šířky má ~90 kB, tenhle ~15 kB → rychlejší první vykreslení na mobilu.

Použití:  pip install fonttools brotli  &&  python3 scripts/make-fonts.py
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

SRC = Path('node_modules/@fontsource-variable/archivo/files')
OUT = Path('src/assets/fonts')
OUT.mkdir(parents=True, exist_ok=True)

# základní latinka + interpunkce + čeština/slovenština (vč. velkých písmen)
TEXT = (
    ''.join(chr(c) for c in range(0x20, 0x7F))
    + '„“‚‘’–—…·×€°%‰ '
    + 'áäčďéěíĺľňóôŕřšťúůýžÁÄČĎÉĚÍĹĽŇÓÔŔŘŠŤÚŮÝŽ'
)

font = TTFont(SRC / 'archivo-latin-ext-wdth-normal.woff2')
latin = TTFont(SRC / 'archivo-latin-wdth-normal.woff2')
for f, name in ((latin, 'latin'), (font, 'latin-ext')):
    inst = instancer.instantiateVariableFont(f, {'wdth': 72, 'wght': 800})
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['kern', 'liga', 'tnum', 'lnum']
    sub = subset.Subsetter(opts)
    sub.populate(text=TEXT)
    sub.subset(inst)
    path = OUT / f'archivo-display-800-{name}.woff2'
    inst.flavor = 'woff2'
    inst.save(path)
    print(path, path.stat().st_size, 'B')
