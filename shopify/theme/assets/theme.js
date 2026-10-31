/* Ještě 5 minut – chování tématu (bez knihoven) */
(() => {
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const designMode = !!(window.Shopify && window.Shopify.designMode);

  // Lišta nahoře: po scrollu plovoucí pilulka (na podstránkách je pilulkou pořád)
  const nav = document.getElementById('nav');
  if (nav && !nav.classList.contains('is-solid')) {
    const onScroll = () => nav.classList.toggle('is-stuck', scrollY > 24);
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Jemné najíždění sekcí při scrollu (sourozenci postupně)
  const io =
    'IntersectionObserver' in window
      ? new IntersectionObserver(
          (entries) => {
            for (const e of entries) {
              if (e.isIntersecting) {
                e.target.classList.add('is-in');
                io.unobserve(e.target);
              }
            }
          },
          { rootMargin: '0px 0px -8% 0px', threshold: 0.12 },
        )
      : null;
  const reveal = (root) => {
    root.querySelectorAll('[data-reveal]').forEach((el) => {
      const sibs = [...(el.parentElement ? el.parentElement.children : [])].filter((c) => c.hasAttribute('data-reveal'));
      el.style.setProperty('--i', String(Math.min(sibs.indexOf(el), 8)));
      if (io && !designMode) io.observe(el);
      else el.classList.add('is-in');
    });
  };

  // Hero: výmluvy se postupně přeškrtnou a zůstane „teď.“
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const hero = (root) => {
    const swap = root.querySelector('[data-swap]');
    if (swap && !calm) {
      const words = [...swap.querySelectorAll('.w')];
      words[0].classList.add('is-active');
      (async () => {
        await wait(700);
        for (let i = 0; i < words.length - 1; i++) {
          const cur = words[i];
          const next = words[i + 1];
          cur.classList.add('is-struck');
          await wait(500);
          next.classList.add('is-entering');
          void next.offsetWidth;
          cur.classList.add('is-leaving');
          cur.classList.remove('is-active');
          next.classList.add('is-active');
          next.classList.remove('is-entering');
          await wait(i + 1 === words.length - 1 ? 0 : 750);
        }
      })();
    }
    // s omezeným pohybem video nehraje (zůstane první snímek)
    const video = root.querySelector('[data-hero-video]');
    if (video && calm) {
      video.removeAttribute('autoplay');
      video.pause();
    }
  };

  reveal(document);
  hero(document);

  // Editor tématu: znovu oživit sekci po úpravě
  document.addEventListener('shopify:section:load', (e) => {
    reveal(e.target);
    hero(e.target);
  });
})();
