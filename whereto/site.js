// 去處 Whereto｜官網互動：主題、導覽列、進場、首頁的照片卡示範與各章節的小互動。
// 文字都放在 HTML 的 data-* 屬性，這支腳本三種語言共用。
(() => {
  const root = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = (k, v) => { try { v === undefined ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} };

  // ---------- 主題 ----------
  const themeBtn = $('#themeBtn');
  const sysDark = matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : sysDark.matches;
  const paintTheme = () => themeBtn && themeBtn.setAttribute('aria-label', isDark() ? themeBtn.dataset.light : themeBtn.dataset.dark);
  paintTheme();
  sysDark.addEventListener('change', paintTheme);
  themeBtn && themeBtn.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    store('wt-theme', root.dataset.theme);
    paintTheme();
  });

  // 記住選過的語言，繁中首頁就不再自動轉址
  $$('.lang a').forEach(a => a.addEventListener('click', () => store('lang', a.dataset.lang)));

  // ---------- 導覽列與閱讀進度 ----------
  const nav = $('#nav'), bar = $('.progress');
  let ticking = false;
  const onScroll = () => {
    const h = root.scrollHeight - innerHeight;
    bar.style.setProperty('--p', h > 0 ? (scrollY / h).toFixed(4) : 0);
    nav.classList.toggle('is-stuck', scrollY > 8);
    ticking = false;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  // ---------- 進場 ----------
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { threshold: .15, rootMargin: '0px 0px -6% 0px' });
  $$('.rv, [data-in]').forEach(el => reduce ? el.classList.add('in') : io.observe(el));
  // 首屏標題不等捲動
  const display = $('.display');
  display && requestAnimationFrame(() => display.classList.add('in'));

  // 只在看得到時才做的事
  const whenSeen = (el, fn, threshold = .4) => {
    if (!el) return;
    new IntersectionObserver(([e], o) => { if (e.isIntersecting) { o.disconnect(); fn(); } }, { threshold }).observe(el);
  };

  // ---------- 光束跟著游標微微轉向 ----------
  if (!reduce && matchMedia('(pointer: fine)').matches) {
    let raf = 0;
    addEventListener('pointermove', e => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const t = ((e.clientX / innerWidth) - .5) * 8;
        $$('.beam').forEach(b => b.style.setProperty('--tilt', t.toFixed(2) + 'deg'));
        raf = 0;
      });
    }, { passive: true });
  }

  // ---------- 首頁：照片卡示範 ----------
  const deck = $('.deck');
  if (deck) {
    const screen = deck.closest('.screen');
    const L = deck.dataset;
    const live = $('[data-live]', screen);
    const nEl = $('.sort-n', screen);
    const barEl = $('.bar i', screen);
    const undoBtn = $('[data-act="undo"]', screen);
    const ctl = { del: $('[data-act="del"]', screen), keep: $('[data-act="keep"]', screen) };
    const counts = { del: 0, album: 0, keep: 0 };
    const countEls = Object.fromEntries($$('[data-count]').map(b => [b.dataset.count, b]));
    const edge = { del: 'var(--delete)', keep: 'var(--keep)', album: 'var(--accent)' };
    const templates = $$('.pcard', deck).map(c => { c.remove(); return c; });
    const total = templates.length;
    let stack = [], history = [];

    const setCount = (k, v) => {
      counts[k] = v;
      const b = countEls[k];
      if (!b) return;
      b.textContent = v;
      if (!reduce) { b.classList.remove('tick'); void b.offsetWidth; b.classList.add('tick'); }
    };
    const update = () => {
      const done = history.length;
      nEl.textContent = done;
      barEl.parentElement.style.setProperty('--done', done / total);
      barEl.style.width = (done / total * 100) + '%';
      undoBtn.disabled = done === 0;
    };
    const layout = () => stack.forEach((c, i) => {
      c.dataset.depth = Math.min(i, 3);
      c.style.zIndex = 20 - i;
      c.setAttribute('aria-hidden', i ? 'true' : 'false');
    });
    const deal = () => {
      $$('.pcard', deck).forEach(c => c.remove());
      stack = templates.map(t => {
        const c = t.cloneNode(true);
        c.setAttribute('role', 'img');
        for (const k of ['del', 'keep', 'album']) {
          const s = document.createElement('i');
          s.className = 'stamp ' + k; s.textContent = L[k]; s.setAttribute('aria-hidden', 'true');
          c.appendChild(s);
        }
        deck.appendChild(c);
        return c;
      });
      history = [];
      layout(); update();
    };
    const say = msg => { live.textContent = ''; setTimeout(() => { live.textContent = msg; }, 30); };

    // 拖曳中的視覺：卡片邊框朝方向亮起、對應印章浮現、底部按鈕同步填色
    const paint = (c, dx, dy) => {
      const dir = -dy > Math.abs(dx) && -dy > 16 ? 'album' : dx < 0 ? 'del' : 'keep';
      const dist = dir === 'album' ? -dy : Math.abs(dx);
      const p = Math.min(1, Math.max(0, (dist - 10) / 90));
      c.style.setProperty('--x', dx + 'px');
      c.style.setProperty('--y', dy + 'px');
      c.style.setProperty('--r', (dx * .06) + 'deg');
      c.style.setProperty('--edge', edge[dir]);
      c.style.setProperty('--o', p);
      $$('.stamp', c).forEach(s => {
        const on = s.classList.contains(dir) ? p : 0;
        s.style.opacity = on;
        s.style.transform = `scale(${.7 + on * .35}) rotate(var(--sr, 0deg))`;
      });
      ctl.del.classList.toggle('hot', dir === 'del' && p >= 1);
      ctl.keep.classList.toggle('hot', dir === 'keep' && p >= 1);
      return { dir, p };
    };
    const clearPaint = c => {
      for (const v of ['--x', '--y', '--r', '--o']) c.style.removeProperty(v);
      $$('.stamp', c).forEach(s => { s.style.opacity = ''; s.style.transform = ''; });
      ctl.del.classList.remove('hot'); ctl.keep.classList.remove('hot');
    };

    const fling = dir => {
      const c = stack[0];
      if (!c) return;
      const w = deck.clientWidth;
      paint(c, dir === 'del' ? -110 : dir === 'keep' ? 110 : 0, dir === 'album' ? -110 : 0);
      requestAnimationFrame(() => {
        c.classList.remove('dragging');
        c.classList.add('gone');
        c.style.setProperty('--x', dir === 'del' ? -w * 1.5 + 'px' : dir === 'keep' ? w * 1.5 + 'px' : '0px');
        c.style.setProperty('--y', dir === 'album' ? -deck.clientHeight * 1.2 + 'px' : '30px');
        c.style.setProperty('--r', dir === 'del' ? '-22deg' : dir === 'keep' ? '22deg' : '0deg');
        c.style.setProperty('--s', dir === 'album' ? '.7' : '1');
        ctl.del.classList.remove('hot'); ctl.keep.classList.remove('hot');
      });
      stack.shift();
      history.push({ c, dir });
      setCount(dir, counts[dir] + 1);
      layout(); update();
      const n = `${history.length} / ${total}`;
      say(L['said' + dir[0].toUpperCase() + dir.slice(1)] + (root.lang === 'en' ? ` (${n})` : `（${n}）`));
      if (navigator.vibrate) navigator.vibrate(dir === 'del' ? 18 : 10);
      if (!stack.length) setTimeout(() => {
        if (stack.length) return; // 等待期間按了復原
        say(L.saidAgain);
        for (const k in counts) setCount(k, 0);
        deal();
      }, 900);
    };
    const undo = () => {
      const h = history.pop();
      if (!h) return;
      const { c, dir } = h;
      setCount(dir, counts[dir] - 1);
      c.classList.remove('gone');
      c.style.removeProperty('--s');
      clearPaint(c);
      stack.unshift(c);
      layout(); update();
      say(L.saidUndo);
    };

    // 拖曳：只有最上面那張跟手
    let drag = null;
    deck.addEventListener('pointerdown', e => {
      const c = stack[0];
      if (!c || !c.contains(e.target) || e.button > 0) return;
      drag = { c, x: e.clientX, y: e.clientY, t: performance.now(), dir: null, p: 0, armed: false };
      c.classList.add('dragging');
      deck.setPointerCapture(e.pointerId);
    });
    deck.addEventListener('pointermove', e => {
      if (!drag) return;
      const r = paint(drag.c, e.clientX - drag.x, e.clientY - drag.y);
      if (r.p >= 1 && !drag.armed && navigator.vibrate) navigator.vibrate(6);
      drag.armed = r.p >= 1;
      Object.assign(drag, r);
    });
    const end = e => {
      if (!drag) return;
      const { c, x, y, t } = drag;
      const dx = e.clientX - x, dy = e.clientY - y;
      const v = Math.hypot(dx, dy) / Math.max(1, performance.now() - t);
      c.classList.remove('dragging');
      if (drag.p >= 1 || (v > .7 && Math.hypot(dx, dy) > 40)) fling(drag.dir);
      else clearPaint(c);
      drag = null;
    };
    deck.addEventListener('pointerup', end);
    deck.addEventListener('pointercancel', e => { if (drag) { drag.c.classList.remove('dragging'); clearPaint(drag.c); drag = null; } });

    $$('[data-act]', screen).forEach(b => b.addEventListener('click', () => {
      b.dataset.act === 'undo' ? undo() : fling(b.dataset.act);
    }));

    // 鍵盤：焦點在示範上，或首屏在畫面中且焦點沒在別的控制項上
    const hero = $('.hero');
    let heroVisible = true;
    new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting && e.intersectionRatio > .35; }, { threshold: [0, .35, .7] }).observe(hero);
    document.addEventListener('keydown', e => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const a = document.activeElement;
      const free = a === deck || ((a === document.body || !a) && heroVisible);
      if (!free) return;
      const map = { ArrowLeft: 'del', ArrowRight: 'keep', ArrowUp: 'album' };
      if (map[e.key]) { e.preventDefault(); fling(map[e.key]); }
      else if (e.key === 'Backspace' || e.key === 'z') { e.preventDefault(); undo(); }
    });

    deal();
  }

  // ---------- 01：照片牆 ----------
  const wall = $('.wall');
  if (wall) {
    const mosaic = $('.mosaic', wall);
    const nEl = $('.wall-n', wall);
    const btn = $('.toggle', wall);
    const keepers = ['#F9B075', '#E0682F', '#2F6F86', '#3E6B47', '#C9C3E6', '#9A3412', '#CBD8BF', '#F5C7C0', '#164B60', '#7C6A9E', '#FDE9C9', '#43385E', '#F28C5B', '#1F3B28'];
    let seed = 11;
    const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const N = 96;
    let kept = 0, prev = keepers[0];
    const frag = document.createDocumentFragment();
    for (let i = 0; i < N; i++) {
      const t = document.createElement('i');
      const r = rnd();
      if (r < .54) {
        const k = rnd();
        t.className = k < .38 ? 'x shot' : k < .72 ? 'x' : k < .88 ? 'x blur' : 'x';
        t.style.setProperty('--c', k < .72 ? prev : k < .88 ? keepers[(rnd() * keepers.length) | 0] : '#B9B2A8');
      } else {
        prev = keepers[(rnd() * keepers.length) | 0];
        t.style.setProperty('--c', prev);
        kept++;
      }
      t.style.setProperty('--d', ((rnd() * 700) | 0) + 'ms');
      frag.appendChild(t);
    }
    mosaic.appendChild(frag);
    let anim = 0;
    const countTo = to => {
      cancelAnimationFrame(anim);
      const from = +nEl.textContent, t0 = performance.now(), dur = reduce ? 1 : 900;
      const step = now => {
        const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        nEl.textContent = Math.round(from + (to - from) * e);
        if (k < 1) anim = requestAnimationFrame(step);
      };
      anim = requestAnimationFrame(step);
    };
    const set = on => {
      wall.classList.toggle('sorted', on);
      btn.setAttribute('aria-pressed', on);
      countTo(on ? kept : N);
    };
    let touched = false;
    btn.addEventListener('click', () => { touched = true; set(btn.getAttribute('aria-pressed') !== 'true'); });
    whenSeen(wall, () => setTimeout(() => { if (!touched) set(true); }, reduce ? 0 : 1400), .5);
  }

  // ---------- 02A：方向 ----------
  const compass = $('.compass');
  if (compass) {
    const dirs = ['del', 'album', 'keep', ''];
    let i = 0, timer = 0, stopped = false;
    const set = d => { compass.dataset.dir = d; };
    const stop = () => { stopped = true; clearInterval(timer); };
    $$('.dbtn', compass).forEach(b => {
      b.addEventListener('pointerenter', () => { stop(); set(b.dataset.dir); });
      b.addEventListener('focus', () => { stop(); set(b.dataset.dir); });
      b.addEventListener('click', () => { stop(); set(compass.dataset.dir === b.dataset.dir ? '' : b.dataset.dir); });
    });
    compass.addEventListener('pointerleave', () => { if (stopped) set(''); });
    if (!reduce) whenSeen(compass, () => { if (!stopped) timer = setInterval(() => set(dirs[i++ % dirs.length]), 1500); });
    $$('.months button', compass).forEach(b => b.addEventListener('click', () => {
      b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true');
    }));
  }

  // ---------- 02B：相似群組 ----------
  const group = $('.group');
  if (group) {
    const save = $('.save', group);
    const tiles = $$('.tile', group);
    const sum = () => {
      const mb = tiles.filter(t => t.getAttribute('aria-pressed') === 'true').reduce((a, t) => a + +t.dataset.mb, 0);
      save.textContent = group.dataset.save.replace('{n}', mb.toFixed(1));
    };
    tiles.forEach(t => t.addEventListener('click', () => {
      t.setAttribute('aria-pressed', t.getAttribute('aria-pressed') !== 'true');
      sum();
    }));
    sum();
  }

  // ---------- 02C：配對與下載 ----------
  const browser = $('.browser');
  if (browser) {
    const cells = $$('.code i', browser);
    const code = browser.dataset.code;
    let timers = [];
    const run = () => {
      timers.forEach(clearTimeout); timers = [];
      browser.classList.remove('paired');
      cells.forEach(c => { c.textContent = ''; c.className = ''; });
      if (reduce) { cells.forEach((c, i) => { c.textContent = code[i]; }); browser.classList.add('paired'); return; }
      cells[0].className = 'cur';
      [...code].forEach((d, i) => timers.push(setTimeout(() => {
        cells[i].textContent = d; cells[i].className = 'on';
        if (cells[i + 1]) cells[i + 1].className = 'cur';
      }, 700 + i * 260)));
      timers.push(setTimeout(() => browser.classList.add('paired'), 700 + code.length * 260 + 500));
    };
    $('.replay', browser).addEventListener('click', run);
    whenSeen(browser, run, .5);
  }

  // ---------- 05：名字 ----------
  const name = $('.name-story');
  name && (reduce ? name.classList.add('lit') : whenSeen($('.glyphs, .qmark', name), () => name.classList.add('lit'), .6));
})();
