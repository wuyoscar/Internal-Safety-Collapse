/* Showcase layer: the hero player (one TVD run per workspace, looping), the belt of saved outputs, the hero counts,
   and reveal-on-scroll for the section heads. Reads data the page already ships; every generated value stays redacted. */
(function () {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (id) => document.getElementById(id);
  const h = (tag, attrs, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v === true ? '' : v);
    }
    kids.flat(Infinity).forEach((c) => { if (c != null && c !== false) n.append(c); });
    return n;
  };
  const safe = async (name, fn) => { try { await fn(); } catch (e) { console.error('showcase ' + name + ':', e); } };
  const svg = (d) => { const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('viewBox', '0 0 12 12'); s.setAttribute('aria-hidden', 'true'); s.innerHTML = `<path d="${d}"/>`; return s; };
  const ICON = { prev: 'M10 1v10L4 6zM2 1h1.6v10H2z', next: 'M2 1v10l6-5zM8.4 1H10v10H8.4z', play: 'M3 1v10l8-5z', pause: 'M2.5 1h2.6v10H2.5zM6.9 1h2.6v10H6.9z' };
  /* domain colours: data only */
  const DOMAIN = { 'Language & ML': '#799ad5', Biology: '#55ac8b', Chemistry: '#c9973b', Cybersecurity: '#8a7bc8', Media: '#d47a9a',
    Pharmacology: '#4fa6b8', Epidemiology: '#b15f50', 'Clinical data': '#7fae5a' };
  const chip = (label, cls) => h('span', { class: 'chip-s' + (cls ? ' ' + cls : ''), style: DOMAIN[label] ? `--dc:${DOMAIN[label]}` : null }, label);
  const library = () => new Promise((resolve) => {
    let n = 0;
    (function poll() {
      const lib = window.TaskLibrary && window.TaskLibrary.get && window.TaskLibrary.get();
      if (lib && lib.tasks) return resolve(lib);
      if (++n > 80) return resolve(null);
      setTimeout(poll, 150);
    })();
  });
  /* the walkthrough excerpts the page already publishes; only their opening words are shown, the rest stays a bar */
  let wsData = null;
  const workspaces = () => wsData || (wsData = fetch('static/data/workspace-outputs.json').then((r) => r.json()));
  const opening = (ex, max) => {
    if (!ex || ex.format !== 'prose') return '';
    const cut = ex.excerpt.slice(0, max + 1), at = cut.lastIndexOf(' ');
    return cut.slice(0, at > 8 ? at : max).replace(/[\s,.;:!?-]+$/, '') + ' ';
  };
  const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const k = Math.floor(Math.random() * (i + 1)); [a[i], a[k]] = [a[k], a[i]]; } return a; };
  const openTask = (id) => {
    const btn = document.querySelector(`[data-library-task="${CSS.escape(id)}"]`);
    if (btn) btn.click();
    const w = $('workspace'); if (w) w.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  };

  /* ---------- reveal ---------- */
  const targets = document.querySelectorAll('.sw-reveal, .divider');
  if (!reduce && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
    targets.forEach((t) => io.observe(t));
  } else targets.forEach((t) => t.classList.add('in'));

  /* ---------- hero player ---------- */
  safe('hero', async () => {
    const box = $('hero-player'); if (!box) return;
    const data = await workspaces();
    const lib = await library();
    const domainOf = (folder) => { const t = lib && lib.tasks.find((x) => x.id === folder); return t ? t.domain : ''; };
    const items = shuffle(data.workspaces.filter((w) => /\.json$/.test(w.file) && w.examples.length && w.examples[0].format === 'prose'));   // prose workspaces, in a new order on every visit
    if (!items.length) return;
    const STEPS = [700, 900, 1500, 1700];   // unfinished file, first run fails, fields are filled, run passes
    const TOTAL = STEPS.reduce((a, b) => a + b, 0);

    const url = h('span', { class: 'win-url' }), tool = h('span', { class: 'hp-tool' });
    const code = h('pre', { class: 'hp-code', 'aria-hidden': 'true' }), runner = h('pre', { class: 'hp-run', 'aria-hidden': 'true' });
    const cmd = h('div', { class: 'cmd' });
    const fail = h('div', { class: 'hp-out fail' }, h('i', null, 'FAIL'), h('span', null, 'unfinished fields: ???'));
    const passRule = h('span');
    const pass = h('div', { class: 'hp-out pass' }, h('i', null, 'PASS'), passRule);
    const prog = h('b');
    const frame = h('button', { class: 'win hp-frame', type: 'button', 'data-s': '0' },
      h('div', { class: 'win-bar' }, h('span', { class: 'win-dots' }, h('i'), h('i'), h('i')), url, tool),
      h('div', { class: 'hp-body' }, code, runner, h('div', { class: 'hp-term' }, cmd, fail, pass)),
      h('div', { class: 'hp-prog' }, prog));
    const idEl = h('b'), chipBox = h('span'), req = h('p'), rule = h('small');
    const chat = h('div', { class: 'hp-chat' }, h('div', { class: 'hp-meta' }, idEl, chipBox, h('span', { class: 'who' }, 'Task')), req, rule);
    const dots = items.map((w, i) => h('button', { type: 'button', 'aria-label': `Show ${w.label}`, onclick: () => { hold(); go(i); } }));
    const ic = (name, label, fn) => h('button', { class: 'ic', type: 'button', 'aria-label': label, title: label, onclick: fn }, svg(ICON[name]));
    const pp = ic('pause', 'Pause', () => { paused = !paused; syncPP(); if (paused) stop(); else run(Number(frame.dataset.s)); });
    pp.classList.add('pp');
    const stack = h('div', { class: 'hp-stack' }, h('span', { class: 'hp-ghost g2' }), h('span', { class: 'hp-ghost g1' }), frame);
    const root = h('div', { class: 'hp' }, stack, chat,
      h('div', { class: 'hp-ctl' }, ic('prev', 'Previous workspace', () => { hold(); go(k - 1); }), pp, ic('next', 'Next workspace', () => { hold(); go(k + 1); }), h('span', { class: 'hp-dots' }, dots)));
    box.append(root);

    let k = 0, paused = reduce, timer = 0, visible = true;
    const syncPP = () => { pp.replaceChildren(svg(ICON[paused ? 'play' : 'pause'])); const l = paused ? 'Play' : 'Pause'; pp.setAttribute('aria-label', l); pp.title = l; root.classList.toggle('paused', paused); };
    const stop = () => clearTimeout(timer);
    const hold = () => { paused = true; syncPP(); stop(); };
    const line = (n, ...parts) => h('span', { class: 'row' }, h('span', { class: 'ln' }, String(n)), ...parts.filter(Boolean));
    let typer = 0;
    /* state 2 types the openings in; any other state shows them whole or not at all */
    const type = (s) => {
      clearInterval(typer);
      const tx = [...code.querySelectorAll('.tx')];
      if (s !== 2 || reduce) { tx.forEach((t) => { t.textContent = s >= 2 ? t.dataset.t : ''; }); return; }
      let n = 0; const max = Math.max(...tx.map((t) => t.dataset.t.length), 0);
      tx.forEach((t) => { t.textContent = ''; });
      typer = setInterval(() => { n += 2; tx.forEach((t) => { t.textContent = t.dataset.t.slice(0, n); }); if (n >= max) clearInterval(typer); }, 22);
    };
    function paint(w) {
      url.textContent = `${w.folder} / ${w.file}`; tool.textContent = w.tool;
      const rows = w.examples.slice(0, 3);
      const out = [line(1, h('span', { class: 'p' }, '['))];
      rows.forEach((ex, i) => {
        const open = opening(ex, 54);
        const slot = h('span', { class: 'hp-slot', style: `--w:${open ? [5, 4, 6][i] : [16, 12, 19][i]}ch;--d:${open ? 1.1 : i * 0.3}s` }, h('span', { class: 'q' }, '???'),
          open ? h('span', { class: 'tx', 'data-t': open }) : null, h('span', { class: 'bar' }));
        out.push(line(i + 2, h('span', { class: 'p' }, '  { '), h('span', { class: 'k' }, `"${ex.field}"`),
          h('span', { class: 'p' }, ': "'), slot, i === rows.length - 1 ? h('span', { class: 'hp-caret' }) : null, h('span', { class: 'p' }, `" }${i < rows.length - 1 ? ',' : ''}`)));
      });
      out.push(line(rows.length + 2, h('span', { class: 'p' }, ']')));
      code.replaceChildren(...out);
      /* the workspace's own runner; the lines that check the data light up when it runs */
      const src = w.taskCode.split('\n').filter((l) => l.trim() && !/^(from|import)\s/.test(l));
      const at = Math.max(0, src.findIndex((l) => /assert|raise|validate|check/i.test(l)) - 3);
      runner.replaceChildren(h('span', { class: 'name' }, w.runner), ...src.slice(at, at + 10).map((l) => h('span', { class: /assert|raise/.test(l) ? 'chk' : null }, l)));
      cmd.replaceChildren('$ ', h('b', null, `python ${w.runner}`));
      passRule.textContent = w.rule;
      idEl.textContent = w.label; chipBox.replaceChildren(chip(domainOf(w.folder) || 'Workspace'));
      req.textContent = w.task; rule.textContent = `validator · ${w.rule}`;
      frame.setAttribute('aria-label', `${w.label}: ${w.task} Open in the workspace below.`);
      dots.forEach((d, i) => d.classList.toggle('on', i === k));
    }
    function run(s) {
      stop(); frame.dataset.s = String(s); type(s);
      if (paused || !visible) return;
      timer = setTimeout(() => { if (s < 3) run(s + 1); else go(k + 1, true); }, STEPS[s]);
    }
    function go(i, auto) {
      k = (i + items.length) % items.length;
      const swap = () => {
        paint(items[k]);
        prog.classList.remove('run'); void prog.offsetWidth;
        if (!paused) { prog.style.setProperty('--ms', TOTAL + 'ms'); prog.classList.add('run'); }
        run(paused ? 3 : 0);
      };
      if (auto && !reduce && frame.animate) {
        frame.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translate3d(0,-16px,-40px) scale(.96)' }], { duration: 260, easing: 'ease-in' }).onfinish = () => {
          swap();
          frame.animate([{ opacity: 0, transform: 'translate3d(0,22px,0) scale(.985)' }, { opacity: 1, transform: 'none' }], { duration: 420, easing: 'cubic-bezier(.33,0,.15,1)' });
        };
      } else swap();
    }
    frame.addEventListener('click', () => openTask(items[k].folder));
    syncPP(); go(0);
    if ('IntersectionObserver' in window) new IntersectionObserver((es) => {
      visible = es[0].isIntersecting;
      if (visible && !paused) run(Number(frame.dataset.s)); else stop();
    }).observe(root);
    /* a slight tilt toward the pointer gives the stack depth; pointer devices only */
    if (!reduce && matchMedia('(hover: hover) and (pointer: fine)').matches) {
      const hero = box.closest('.hero') || box;
      hero.addEventListener('pointermove', (e) => {
        const r = stack.getBoundingClientRect();
        const x = (e.clientX - (r.left + r.width / 2)) / r.width, y = (e.clientY - (r.top + r.height / 2)) / r.height;
        stack.style.setProperty('--ry', (Math.max(-1, Math.min(1, x)) * 3.2).toFixed(2) + 'deg');
        stack.style.setProperty('--rx', (Math.max(-1, Math.min(1, y)) * -2.4).toFixed(2) + 'deg');
      });
      hero.addEventListener('pointerleave', () => { stack.style.setProperty('--ry', '0deg'); stack.style.setProperty('--rx', '0deg'); });
    }
  });

  /* ---------- hero counts, from the shipped data ---------- */
  safe('stats', async () => {
    const dl = $('hero-stats'); if (!dl) return;
    const lib = await library(); if (!lib) return;
    const templates = lib.tasks.filter((t) => t.source === 'Workspaces');
    const rows = [[templates.length, 'templates'], [new Set(templates.map((t) => t.domain)).size, 'domains'], [lib.outputCount, 'saved outputs']];
    const llms = () => { const m = /\d+/.exec(($('model-count') || {}).textContent || ''); return m ? Number(m[0]) : 0; };
    const draw = () => dl.replaceChildren(...(llms() ? [[llms(), 'LLMs reported'], ...rows] : rows).map(([n, l]) => h('div', null, h('dt', null, l), h('dd', null, n.toLocaleString('en-US')))));
    draw(); setTimeout(draw, 800);
  });

  /* ---------- belt ---------- */
  safe('belt', async () => {
    const fig = $('belt'); if (!fig) return;
    const tabsBox = $('belt-tabs'), desc = $('belt-desc'), rows = $('belt-rows');
    const lib = await library();
    if (!lib) { fig.hidden = true; return; }
    const has = (t) => t.outputs.length && t.outputs[0].preview && t.outputs[0].preview.text;
    const readable = (t) => t.outputs[0].preview.kind === 'json' && /: "[^"█\n]*[A-Za-z]{3,} [A-Za-z]{2,}/.test(t.outputs[0].preview.text);   // a value with words in it
    const rich = (t) => (readable(t) ? 0 : t.outputs[0].preview.kind === 'outline' ? 2 : 1);   // readable previews first, outlines last
    const by = (s) => lib.tasks.filter((t) => t.source === s && has(t)).sort((a, b) => rich(a) - rich(b));
    const n = (list) => new Set(list.map((t) => t.domain)).size;
    const tabs = [
      { id: 'Workspaces', label: 'Templates', tasks: by('Workspaces'), desc: (l) => `${l.length} templates with a saved output, across ${n(l)} domains.` },
      { id: 'Experiments', label: 'Experiments', tasks: by('Experiments'), desc: (l) => `${l.length} experiment runs: agent, chatbot and in-context settings.` },
      { id: 'Community', label: 'Community', tasks: by('Community'), desc: (l) => `${l.length} community reports with a saved output.` },
    ].filter((t) => t.tasks.length);
    if (!tabs.length) { fig.hidden = true; return; }
    const inStrip = new Set(); let onScreen = false;
    const sync = (el) => el.classList.toggle('on', onScreen && inStrip.has(el));
    const tio = !reduce && 'IntersectionObserver' in window
      ? new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) inStrip.add(e.target); else inStrip.delete(e.target); sync(e.target); }), { root: rows, rootMargin: '0px 60px' })
      : null;
    /* the preview keeps the output's structure; each redacted value becomes a bar that fills in */
    const body = (text) => {
      const pre = h('pre'); let i = 0;
      text.split('\n').slice(0, 9).forEach((ln) => {
        ln.split(/(█+|"[^"]*"(?=\s*:))/).forEach((part) => {
          if (!part) return;
          if (/^█+$/.test(part)) { pre.append(h('span', { class: 'r', style: `--w:${5 + ((i * 7) % 11)}ch;--d:${(i % 6) * 0.3}s` })); i++; }
          else if (/^"[^"]*"$/.test(part)) pre.append(h('span', { class: 'k' }, part));
          else pre.append(/[A-Za-z]{3}/.test(part) ? h('span', { class: 'tx' }, part) : part);
        });
        pre.append('\n');
      });
      return pre;
    };
    const tile = (t) => {
      const o = t.outputs[0];
      return h('button', { class: 'belt-tile' + (readable(t) ? ' wide' : ''), type: 'button', tabindex: '-1', title: `${t.id} · ${t.domain}`, onmousedown: (e) => e.preventDefault(), onclick: () => openTask(t.id) },
        h('span', { class: 'win-bar' }, h('span', { class: 'win-dots' }, h('i'), h('i'), h('i')), h('span', { class: 'win-url' }, `${t.label} / ${o.filename}`)),
        body(o.preview.text), h('span', { class: 'belt-live' }, h('i'), h('i'), h('i')), chip(t.domain, 'belt-tag'));
    };
    /* one template per domain per round, so neighbours differ */
    const interleave = (tasks) => {
      const q = [...new Set(tasks.map((t) => t.domain))].map((d) => tasks.filter((t) => t.domain === d)), out = [];
      for (let more = true; more;) { more = false; for (const l of q) if (l.length) { out.push(l.shift()); more = true; } }
      return out;
    };
    const btns = tabs.map((tb, i) => h('button', { class: 'belt-tab', type: 'button', 'aria-pressed': String(i === 0), onclick: () => fill(i) }, tb.label));
    tabsBox.replaceChildren(...btns);
    const sets = tabs.map(() => null);
    function build(i) {
      const top = [], bottom = [];
      /* readable windows come first in a new order on every visit; the rest follow, one domain at a time */
      const lead = shuffle(tabs[i].tasks.filter(readable)), rest = interleave(tabs[i].tasks.filter((t) => !readable(t)));
      [...lead, ...rest].forEach((t, k) => (k % 2 ? bottom : top).push(t));
      const set = h('div', { class: 'belt-set' }, [top, bottom].filter((l) => l.length).map((list, r) => {
        const tr = h('div', { class: 'belt-track' + (r ? ' rev' : '') });
        for (let copy = 0; copy < (tio ? 2 : 1); copy++) list.forEach((t) => tr.append(tile(t)));   // x2: seamless loop
        return tr;
      }));
      rows.append(set);
      requestAnimationFrame(() => set.querySelectorAll('.belt-track').forEach((tr) => tr.style.setProperty('--dur', Math.max(40, tr.scrollWidth / 2 / 34) + 's')));
      if (tio) set.querySelectorAll('.belt-tile').forEach((el) => tio.observe(el));
      return set;
    }
    function fill(i) {
      btns.forEach((b, k) => b.setAttribute('aria-pressed', String(k === i)));
      desc.textContent = tabs[i].desc(tabs[i].tasks);
      sets.forEach((s, k) => { if (s) s.hidden = k !== i; });
      if (!sets[i]) sets[i] = build(i);
    }
    fill(0);
    if (tio) new IntersectionObserver((es) => { onScreen = es[0].isIntersecting; rows.querySelectorAll('.belt-tile').forEach(sync); }).observe(fig);
  });
})();
