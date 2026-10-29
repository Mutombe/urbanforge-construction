/* Urban Forge Construction — site interactions (vanilla, no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = { get(k) { try { return sessionStorage.getItem(k); } catch { return null; } }, set(k, v) { try { sessionStorage.setItem(k, v); } catch { /* private mode */ } } };

  /* ---------- preloader ---------- */
  const pre = $('.preloader');
  const startPage = () => document.documentElement.classList.add('is-ready');
  if (pre) {
    const bar = $('.preloader__bar span', pre), count = $('.preloader__count', pre);
    const quick = store.get('uf-visited') || reduce;
    let p = 0, loaded = false;
    window.addEventListener('load', () => { loaded = true; });
    const tick = () => {
      p = Math.min(100, p + (loaded ? 6 : Math.random() * 3.2) * (quick ? 4 : 1));
      if (!loaded && p > 88) p = 88;
      bar.style.width = p + '%'; count.textContent = String(Math.round(p)).padStart(3, '0');
      if (p >= 100) { pre.classList.add('is-done'); store.set('uf-visited', 1); startPage(); }
      else requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    setTimeout(() => { loaded = true; }, 3500);
  } else startPage();

  /* ---------- header ---------- */
  const header = $('.header');
  let lastY = scrollY;
  const onScroll = () => {
    const y = scrollY;
    if (header) {
      header.classList.toggle('is-solid', y > 60);
      header.classList.toggle('is-hidden', y > 500 && y > lastY && !document.body.classList.contains('drawer-open'));
    }
    lastY = y;
    const top = $('.to-top');
    if (top) {
      const max = document.documentElement.scrollHeight - innerHeight;
      top.style.setProperty('--p', max > 0 ? (y / max).toFixed(3) : 0);
      top.classList.toggle('is-visible', y > 600);
    }
  };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  $('.to-top')?.addEventListener('click', () => scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }));

  /* ---------- drawer ---------- */
  const drawer = $('.drawer');
  const setDrawer = open => {
    if (!drawer) return;
    drawer.classList.toggle('is-open', open);
    document.body.classList.toggle('drawer-open', open);
    drawer.setAttribute('aria-hidden', String(!open));
    $$('[data-drawer-open]').forEach(b => b.setAttribute('aria-expanded', String(open)));
    if (open) $('.drawer__close', drawer)?.focus();
  };
  $$('[data-drawer-open]').forEach(b => b.addEventListener('click', () => setDrawer(true)));
  $$('[data-drawer-close]').forEach(b => b.addEventListener('click', () => setDrawer(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape') { setDrawer(false); closeLightbox(); } });

  /* ---------- split headings into animated lines ---------- */
  $$('[data-split]').forEach(el => {
    el.innerHTML = el.innerHTML.split(/<br\s*\/?>/i)
      .map((line, i) => `<span class="split-line"><span style="--i:${i}">${line.trim()}</span></span>`).join('');
  });

  /* ---------- reveal on scroll ---------- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    });
  }, { threshold: .15, rootMargin: '0px 0px -6% 0px' });
  const watch = () => $$('[data-reveal], [data-split], .img-reveal, [data-chart]').forEach(el => io.observe(el));
  if (document.documentElement.classList.contains('is-ready')) watch();
  else new MutationObserver((_, o) => { if (document.documentElement.classList.contains('is-ready')) { o.disconnect(); setTimeout(watch, 250); } })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

  /* ---------- counters ---------- */
  const cio = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    cio.unobserve(e.target);
    const el = e.target, to = parseFloat(el.dataset.count), dec = (el.dataset.count.split('.')[1] || '').length;
    const dur = reduce ? 1 : 1800, t0 = performance.now();
    const step = t => {
      const k = Math.min(1, (t - t0) / dur), v = to * (1 - Math.pow(1 - k, 4));
      el.textContent = v.toFixed(dec);
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }), { threshold: .6 });
  $$('[data-count]').forEach(el => cio.observe(el));

  /* ---------- hero slider + typed services ---------- */
  const slides = $$('.hero__slide'), dots = $$('.hero__dots button');
  if (slides.length > 1) {
    let cur = 0, timer;
    const go = i => {
      slides[cur].classList.remove('is-active'); dots[cur]?.classList.remove('is-active');
      cur = (i + slides.length) % slides.length;
      slides[cur].classList.add('is-active'); dots[cur]?.classList.add('is-active');
      clearInterval(timer); timer = setInterval(() => go(cur + 1), 6500);
    };
    dots.forEach((d, i) => d.addEventListener('click', () => go(i)));
    timer = setInterval(() => go(cur + 1), 6500);
  }
  const typed = $('[data-typed]');
  if (typed) {
    const words = JSON.parse(typed.dataset.typed), out = $('.txt', typed);
    let w = 0, c = 0, del = false;
    const loop = () => {
      const word = words[w];
      c += del ? -1 : 1;
      out.textContent = word.slice(0, c);
      let wait = del ? 38 : 72;
      if (!del && c === word.length) { del = true; wait = 2200; }
      else if (del && c === 0) { del = false; w = (w + 1) % words.length; wait = 380; }
      setTimeout(loop, wait);
    };
    if (reduce) out.textContent = words[0]; else setTimeout(loop, 1600);
  }

  /* ---------- parallax ---------- */
  const par = $$('[data-parallax]');
  if (par.length && !reduce) {
    let ticking = false;
    const run = () => {
      par.forEach(el => {
        const r = el.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight) return;
        const k = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
        el.style.transform = `translate3d(0, ${(k * parseFloat(el.dataset.parallax) * 100).toFixed(1)}px, 0)`;
      });
      ticking = false;
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(run); } }, { passive: true });
    run();
  }

  /* ---------- seamless marquees (duplicate content once) ---------- */
  $$('[data-marquee]').forEach(t => { t.innerHTML += t.innerHTML; $$(':scope > *', t).slice(t.children.length / 2).forEach(n => n.setAttribute('aria-hidden', 'true')); });

  /* ---------- services slider ---------- */
  $$('[data-slider]').forEach(wrap => {
    const track = $('.svc-track', wrap);
    const by = dir => track.scrollBy({ left: dir * (track.firstElementChild.offsetWidth + 22), behavior: 'smooth' });
    $('[data-prev]', wrap)?.addEventListener('click', () => by(-1));
    $('[data-next]', wrap)?.addEventListener('click', () => by(1));
  });

  /* ---------- testimonials ---------- */
  $$('[data-testi]').forEach(box => {
    const s = $$('.testi-slide', box), nav = $('.testi-nav', box);
    if (s.length < 2) return;
    let i = 0, t;
    const btns = s.map((_, k) => {
      const b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', `Show testimonial ${k + 1}`);
      b.addEventListener('click', () => show(k)); nav.appendChild(b); return b;
    });
    const show = k => {
      s[i].classList.remove('is-active'); btns[i].classList.remove('is-active');
      i = k; s[i].classList.add('is-active'); btns[i].classList.add('is-active');
      clearInterval(t); t = setInterval(() => show((i + 1) % s.length), 7000);
    };
    show(0);
  });

  /* ---------- tilt on hover (fine pointers only) ---------- */
  if (matchMedia('(hover: hover) and (pointer: fine)').matches && !reduce) {
    $$('[data-tilt]').forEach(el => {
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = `perspective(900px) rotateX(${(-y * 6).toFixed(2)}deg) rotateY(${(x * 8).toFixed(2)}deg) translateY(-8px)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------- touch: every desktop hover effect plays when its element crosses the middle of the screen ----------
     Reads each :hover rule in our stylesheet, re-emits it with .is-inview in place of :hover, and toggles
     .is-inview on the hovered element (the part of the selector before :hover) while it is in the centre band. */
  if (matchMedia('(hover: none)').matches) {
    const SKIP = /logo-marquee:hover|drawer|menu-btn|to-top|\.nav a/;
    const css = [], targets = new Set();
    const walk = rules => [...rules].forEach(r => {
      if (r.media) { if (matchMedia(r.media.mediaText).matches) walk(r.cssRules); return; }
      if (!r.selectorText || !r.selectorText.includes(':hover')) return;
      const sels = r.selectorText.split(',').map(s => s.trim()).filter(s => s.includes(':hover') && !SKIP.test(s));
      if (!sels.length) return;
      css.push(`${sels.map(s => s.replace(/:hover/g, '.is-inview')).join(', ')} { ${r.style.cssText} }`);
      sels.forEach(s => targets.add(s.split(':hover')[0].trim().replace(/[>+~]$/, '').trim()));
    });
    [...document.styleSheets].forEach(sh => { try { walk(sh.cssRules); } catch { /* cross-origin (fonts) */ } });
    const style = document.createElement('style'); style.textContent = css.join('\n'); document.head.appendChild(style);
    const vio = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle('is-inview', e.isIntersecting)), { rootMargin: '-35% 0px -35% 0px' });
    targets.forEach(sel => { try { $$(sel).forEach(el => vio.observe(el)); } catch { /* selector not queryable */ } });
  }

  /* ---------- project filters ---------- */
  $$('[data-filters]').forEach(bar => {
    const grid = $(bar.dataset.filters);
    bar.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      $$('button', bar).forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      const f = b.dataset.filter;
      $$('[data-cat]', grid).forEach(card => {
        const show = f === 'all' || card.dataset.cat === f;
        card.classList.toggle('is-hidden', !show);
        if (show && !reduce) card.animate([{ opacity: 0, transform: 'translateY(20px)' }, { opacity: 1, transform: 'none' }], { duration: 600, easing: 'cubic-bezier(.16,1,.3,1)' });
      });
    });
  });

  /* ---------- lightbox ---------- */
  const lb = $('.lightbox');
  function closeLightbox() { lb?.classList.remove('is-open'); }
  if (lb) {
    $$('[data-lightbox] figure').forEach(f => {
      f.tabIndex = 0;
      const open = () => {
        const img = $('img', f);
        $('img', lb).src = img.currentSrc || img.src; $('img', lb).alt = img.alt;
        $('p', lb).textContent = $('figcaption', f)?.textContent || '';
        lb.classList.add('is-open'); $('button', lb).focus();
      };
      f.addEventListener('click', open);
      f.addEventListener('keydown', e => { if (e.key === 'Enter') open(); });
    });
    lb.addEventListener('click', e => { if (e.target === lb || e.target.closest('button')) closeLightbox(); });
  }

  /* ---------- chart tooltips ---------- */
  const tip = document.createElement('div'); tip.className = 'tooltip'; tip.setAttribute('role', 'status'); document.body.appendChild(tip);
  $$('[data-tip]').forEach(el => {
    const [title, val] = el.dataset.tip.split('|');
    const show = e => {
      tip.innerHTML = `<strong>${title}</strong>${val || ''}`;
      const r = el.getBoundingClientRect();
      tip.style.left = (e?.clientX ?? r.left + r.width / 2) + 'px';
      tip.style.top = (e?.clientY ?? r.top) + 'px';
      tip.classList.add('is-on');
    };
    el.addEventListener('mousemove', show);
    el.addEventListener('focus', () => show());
    el.addEventListener('mouseleave', () => tip.classList.remove('is-on'));
    el.addEventListener('blur', () => tip.classList.remove('is-on'));
  });
  $$('[data-table-toggle]').forEach(b => b.addEventListener('click', () => {
    const t = $(b.dataset.tableToggle); t.hidden = !t.hidden;
    b.textContent = t.hidden ? 'Show data table' : 'Hide data table';
    b.setAttribute('aria-expanded', String(!t.hidden));
  }));

  /* ---------- map pins <-> city list ---------- */
  $$('[data-city]').forEach(el => {
    const key = el.dataset.city;
    const peers = () => $$(`[data-city="${key}"]`);
    el.addEventListener('mouseenter', () => peers().forEach(p => p.classList.add('is-active')));
    el.addEventListener('mouseleave', () => peers().forEach(p => p.classList.remove('is-active')));
  });

  /* ---------- forms: compose an email to the project desk ---------- */
  $$('form[data-mailto]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const d = new FormData(form), status = $('.form__status', form);
      if (form.dataset.mailto === 'newsletter') {
        location.href = `mailto:info@urbanforge.co.zw?subject=${encodeURIComponent('Newsletter subscription')}&body=${encodeURIComponent('Please add ' + d.get('email') + ' to the Urban Forge mailing list.')}`;
        form.reset(); return;
      }
      const body = [...d.entries()].filter(([k]) => k !== 'message').map(([k, v]) => `${k[0].toUpperCase() + k.slice(1)}: ${v}`).join('\n') + '\n\n' + (d.get('message') || '');
      location.href = `mailto:info@urbanforge.co.zw?subject=${encodeURIComponent('Project enquiry — ' + (d.get('service') || 'General'))}&body=${encodeURIComponent(body)}`;
      if (status) status.textContent = 'Thank you — your email app is opening with your enquiry ready to send.';
    });
  });

  /* ---------- footer year ---------- */
  $$('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
})();
