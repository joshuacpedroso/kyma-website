/* Kyma Empreendimentos — interações e animações */
(() => {
  const d = document;
  const root = d.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const store = {
    get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* sem storage */ } }
  };
  const $ = (s, c = d) => c.querySelector(s);
  const $$ = (s, c = d) => [...c.querySelectorAll(s)];

  /* ---------- Preloader ---------- */
  const pre = $('.preloader');
  const onReady = [];
  let isReady = false;
  const ready = () => {
    if (isReady) return;
    isReady = true;
    root.classList.add('is-ready');
    onReady.forEach(fn => fn());
  };
  if (pre && !store.get('kyma-intro') && !reduce) {
    store.set('kyma-intro', '1');
    root.classList.add('is-loading');
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      pre.classList.add('is-done');
      root.classList.remove('is-loading');
      setTimeout(ready, 280);
      setTimeout(() => pre.remove(), 1400);
    };
    setTimeout(finish, 2000);
  } else {
    if (pre) pre.remove();
    requestAnimationFrame(ready);
  }

  /* ---------- Split de palavras ---------- */
  $$('[data-split]').forEach(el => {
    el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    let i = 0;
    const base = parseFloat(el.dataset.split) || 0;
    const walk = node => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(' '); return; }
            const w = d.createElement('span');
            w.className = 'w';
            w.setAttribute('aria-hidden', 'true');
            const wi = d.createElement('span');
            wi.className = 'wi';
            wi.textContent = part;
            wi.style.transitionDelay = (base + i++ * 0.07).toFixed(2) + 's';
            w.append(wi);
            frag.append(w);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') {
          walk(n);
        }
      });
    };
    walk(el);
  });

  /* ---------- Revelação no scroll ---------- */
  $$('[data-stagger]').forEach(parent => {
    const step = parseFloat(parent.dataset.stagger) || 0.1;
    [...parent.children].forEach((c, i) => {
      if (!c.hasAttribute('data-reveal')) c.setAttribute('data-reveal', '');
      c.style.transitionDelay = (i * step).toFixed(2) + 's';
    });
  });

  const revealables = $$('[data-reveal], [data-split], .reveal-img');
  if ('IntersectionObserver' in window && !reduce) {
    // Elementos com clip-path fechado contam como invisíveis para o observer,
    // então .reveal-img é observado através do elemento pai.
    const targets = new Map();
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        (targets.get(e.target) || []).forEach(el => {
          const show = () => el.classList.add('is-in');
          if (el.closest('.hero')) (isReady ? show() : onReady.push(show)); else show();
        });
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.1 });
    revealables.forEach(el => {
      const t = el.classList.contains('reveal-img') ? el.parentElement : el;
      if (!targets.has(t)) targets.set(t, []);
      targets.get(t).push(el);
      io.observe(t);
    });
  } else {
    revealables.forEach(el => el.classList.add('is-in'));
  }

  /* ---------- Header, progresso, parallax, manifesto (loop de scroll) ---------- */
  const header = $('[data-header]');
  const progress = $('.progress');
  const parallax = $$('[data-parallax]');
  const manifesto = $$('[data-words]').map(el => {
    const words = [];
    const walk = node => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(' '); return; }
            const s = d.createElement('span');
            s.className = 'mw';
            s.textContent = part;
            words.push(s);
            frag.append(s);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
    return { el, words };
  });

  let lastY = scrollY;
  let ticking = false;
  const onScroll = () => {
    const y = scrollY;
    const vh = innerHeight;
    if (header) {
      header.classList.toggle('is-scrolled', y > 40);
      const hide = y > lastY && y > 480 && !root.classList.contains('menu-open');
      header.classList.toggle('is-hidden', hide);
    }
    if (progress) {
      const max = d.documentElement.scrollHeight - vh;
      progress.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
    }
    if (!reduce) {
      parallax.forEach(el => {
        const r = el.parentElement.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        const speed = parseFloat(el.dataset.parallax) || 0.15;
        const offset = (r.top + r.height / 2 - vh / 2) * speed;
        el.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`;
      });
    }
    manifesto.forEach(({ el, words }) => {
      const r = el.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
      const lit = Math.round(p * words.length);
      words.forEach((w, i) => w.classList.toggle('lit', i < lit));
    });
    lastY = y;
    ticking = false;
  };
  addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  addEventListener('resize', onScroll, { passive: true });
  onScroll();

  /* ---------- Menu mobile ---------- */
  const burger = $('.burger');
  const menu = $('#menu');
  const setMenu = open => {
    root.classList.toggle('menu-open', open);
    if (burger) {
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    }
    if (menu) menu.setAttribute('aria-hidden', String(!open));
  };
  if (burger) burger.addEventListener('click', () => setMenu(!root.classList.contains('menu-open')));
  if (menu) $$('a', menu).forEach(a => a.addEventListener('click', () => setMenu(false)));
  d.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

  /* ---------- Contadores ---------- */
  const counters = $$('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const el = e.target;
        const end = parseInt(el.dataset.count, 10);
        const pad = el.dataset.pad ? parseInt(el.dataset.pad, 10) : 0;
        const fmt = v => String(v).padStart(pad, '0');
        if (reduce) { el.textContent = fmt(end); cio.unobserve(el); return; }
        const t0 = performance.now();
        const dur = 1800;
        const tick = t => {
          const p = Math.min(1, (t - t0) / dur);
          const eased = 1 - Math.pow(1 - p, 4);
          el.textContent = fmt(Math.round(end * eased));
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        cio.unobserve(el);
      });
    }, { threshold: 0.6 });
    counters.forEach(c => cio.observe(c));
  }

  /* ---------- Slider do hero ---------- */
  const hero = $('[data-hero-slider]');
  if (hero) {
    const slides = $$('.hero__slide', hero);
    const dots = $$('.hero__dots button', hero);
    const count = $('.hero__count b', hero);
    const caption = $('.hero__caption', hero);
    const bar = $('.hero__bar span', hero);
    let idx = 0;
    let timer;
    const go = n => {
      slides[idx].classList.remove('is-active');
      dots[idx] && dots[idx].setAttribute('aria-current', 'false');
      idx = (n + slides.length) % slides.length;
      slides[idx].classList.add('is-active');
      dots[idx] && dots[idx].setAttribute('aria-current', 'true');
      if (count) count.textContent = String(idx + 1).padStart(2, '0');
      if (caption) {
        caption.style.opacity = 0;
        setTimeout(() => { caption.textContent = slides[idx].dataset.caption || ''; caption.style.opacity = 1; }, 300);
      }
      if (bar) { bar.classList.remove('run'); void bar.offsetWidth; bar.classList.add('run'); }
      clearTimeout(timer);
      if (!reduce) timer = setTimeout(() => go(idx + 1), 6000);
    };
    dots.forEach((b, i) => b.addEventListener('click', () => go(i)));
    const start = () => go(0);
    isReady ? start() : onReady.push(start);
  }

  /* ---------- Filtros ---------- */
  const filterWrap = $('[data-filters]');
  if (filterWrap) {
    const items = $$('[data-tags]');
    const countEl = $('[data-filter-count]');
    $$('[data-filter]', filterWrap).forEach(btn => {
      btn.addEventListener('click', () => {
        const f = btn.dataset.filter;
        $$('[data-filter]', filterWrap).forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
        let n = 0;
        items.forEach(it => {
          const show = f === 'todos' || it.dataset.tags.split(' ').includes(f);
          if (show) {
            n++;
            it.classList.remove('is-gone');
            requestAnimationFrame(() => requestAnimationFrame(() => it.classList.remove('is-hidden')));
          } else {
            it.classList.add('is-hidden');
            setTimeout(() => { if (it.classList.contains('is-hidden')) it.classList.add('is-gone'); }, 450);
          }
        });
        if (countEl) countEl.textContent = String(n).padStart(2, '0');
      });
    });
  }

  /* ---------- Lightbox ---------- */
  const lbLinks = $$('[data-lightbox]');
  if (lbLinks.length) {
    const lb = d.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Visualização de imagem');
    const arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
    lb.innerHTML = `<img class="lightbox__img" alt="">
      <p class="lightbox__cap"></p>
      <button class="lightbox__btn lightbox__close" aria-label="Fechar"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      <button class="lightbox__btn lightbox__prev" aria-label="Anterior">${arrow}</button>
      <button class="lightbox__btn lightbox__next" aria-label="Próxima">${arrow}</button>`;
    d.body.append(lb);
    const img = $('.lightbox__img', lb);
    const cap = $('.lightbox__cap', lb);
    let group = [];
    let cur = 0;
    let opener = null;
    const show = i => {
      cur = (i + group.length) % group.length;
      const a = group[cur];
      img.style.opacity = 0;
      img.onload = () => { img.style.opacity = 1; };
      img.src = a.href;
      img.alt = a.dataset.caption || '';
      cap.textContent = a.dataset.caption || '';
    };
    const open = a => {
      opener = a;
      group = lbLinks.filter(l => l.dataset.lightbox === a.dataset.lightbox);
      show(group.indexOf(a));
      lb.classList.add('is-open');
      $('.lightbox__prev', lb).hidden = $('.lightbox__next', lb).hidden = group.length < 2;
      $('.lightbox__close', lb).focus();
    };
    const close = () => { lb.classList.remove('is-open'); if (opener) opener.focus(); };
    lbLinks.forEach(a => a.addEventListener('click', e => { e.preventDefault(); open(a); }));
    $('.lightbox__close', lb).addEventListener('click', close);
    $('.lightbox__prev', lb).addEventListener('click', () => show(cur - 1));
    $('.lightbox__next', lb).addEventListener('click', () => show(cur + 1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    d.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(cur - 1);
      if (e.key === 'ArrowRight') show(cur + 1);
    });
  }

  /* ---------- Scroll horizontal arrastável ---------- */
  $$('.hscroll').forEach(el => {
    let down = false, sx = 0, sl = 0, moved = false;
    el.addEventListener('pointerdown', e => {
      if (e.pointerType !== 'mouse') return;
      down = true; moved = false; sx = e.clientX; sl = el.scrollLeft;
    });
    addEventListener('pointermove', e => {
      if (!down) return;
      const dx = e.clientX - sx;
      if (Math.abs(dx) > 5) { moved = true; el.classList.add('is-drag'); }
      el.scrollLeft = sl - dx;
    });
    addEventListener('pointerup', () => {
      if (!down) return;
      down = false;
      setTimeout(() => el.classList.remove('is-drag'), 0);
    });
    el.addEventListener('click', e => { if (moved) { e.preventDefault(); moved = false; } }, true);
  });

  /* ---------- Cursor, magnetismo, tilt (só desktop) ---------- */
  if (fine && !reduce) {
    const dot = d.createElement('div');
    const ring = d.createElement('div');
    dot.className = 'cursor is-hidden';
    ring.className = 'cursor-ring is-hidden';
    ring.innerHTML = '<span></span>';
    d.body.append(dot, ring);
    const label = $('span', ring);
    let mx = -100, my = -100, rx = -100, ry = -100;
    addEventListener('pointermove', e => {
      mx = e.clientX; my = e.clientY;
      dot.style.transform = `translate3d(${mx}px, ${my}px, 0)`;
      dot.classList.remove('is-hidden'); ring.classList.remove('is-hidden');
    }, { passive: true });
    d.addEventListener('pointerleave', () => { dot.classList.add('is-hidden'); ring.classList.add('is-hidden'); });
    const loop = () => {
      rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18;
      ring.style.transform = `translate3d(${rx}px, ${ry}px, 0)`;
      requestAnimationFrame(loop);
    };
    loop();
    d.addEventListener('pointerover', e => {
      const t = e.target.closest('[data-cursor], a, button, input, textarea, select, label');
      if (!t) { ring.classList.remove('is-hover', 'is-label'); return; }
      if (t.dataset.cursor) {
        label.textContent = t.dataset.cursor;
        ring.classList.add('is-label'); ring.classList.remove('is-hover');
      } else {
        ring.classList.add('is-hover'); ring.classList.remove('is-label');
      }
    });

    $$('[data-magnetic]').forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        el.style.transform = `translate(${x * 0.25}px, ${y * 0.35}px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });

    $$('[data-tilt]').forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(900px) rotateY(${px * 6}deg) rotateX(${-py * 6}deg)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------- Formulário de contato → WhatsApp ---------- */
  const form = $('#contact-form');
  const toast = msg => {
    let t = $('.toast');
    if (!t) { t = d.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); d.body.append(t); }
    t.textContent = msg;
    t.classList.add('is-show');
    setTimeout(() => t.classList.remove('is-show'), 3600);
  };
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      let ok = true;
      $$('[required]', form).forEach(inp => {
        const bad = !inp.value.trim() || (inp.type === 'email' && !/^\S+@\S+\.\S+$/.test(inp.value));
        inp.closest('.field').classList.toggle('is-error', bad);
        if (bad) ok = false;
      });
      if (!ok) { toast('Preencha os campos destacados, por favor.'); return; }
      const v = n => (form.elements[n] && form.elements[n].value.trim()) || '';
      const lines = [
        `Olá! Meu nome é ${v('nome')}.`,
        v('interesse') ? `Tenho interesse em: ${v('interesse')}.` : '',
        v('mensagem'),
        '',
        `Telefone: ${v('telefone')}`,
        v('email') ? `E-mail: ${v('email')}` : ''
      ].filter((l, i, a) => l || (i > 0 && a[i - 1]));
      const url = `https://wa.me/${form.dataset.wa}?text=${encodeURIComponent(lines.join('\n'))}`;
      window.open(url, '_blank', 'noopener');
      toast('Perfeito! Abrimos o WhatsApp com sua mensagem.');
      form.reset();
    });
  }

  /* ---------- Transição entre páginas ---------- */
  if (!reduce) {
    const wipe = d.createElement('div');
    wipe.className = 'page-wipe';
    d.body.append(wipe);
    d.addEventListener('click', e => {
      const a = e.target.closest('a');
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      if (a.target === '_blank' || a.hasAttribute('download') || a.dataset.lightbox !== undefined) return;
      const url = new URL(a.href, location.href);
      if (url.origin !== location.origin || (url.pathname === location.pathname && url.hash)) return;
      e.preventDefault();
      root.classList.add('is-leaving');
      setTimeout(() => { location.href = url.href; }, 520);
    });
    addEventListener('pageshow', () => root.classList.remove('is-leaving'));
  }

  /* ---------- Ano no rodapé ---------- */
  $$('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
})();
