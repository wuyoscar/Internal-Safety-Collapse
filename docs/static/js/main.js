/* Browser-only evidence exploration. No inference, API keys, or live experiments. */
'use strict';
const $ = id => document.getElementById(id);
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let evidence = null, filter = 'All', query = '', topic = '', replayId = 'fable-news', step = 0;
let heroStep = 0, heroTimer = null, traceTimer = null, activeCase = null;
const element = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
};
function panelImage(index, label) {
  const node = element('div', 'crop-panel');
  node.style.setProperty('--x', index % 2 ? '100%' : '0%');
  node.style.setProperty('--y', `${Math.floor(index / 2) * 50}%`);
  node.setAttribute('role', 'img'); node.setAttribute('aria-label', label);
  return node;
}
function renderCases() {
  if (!evidence) return;
  const matches = evidence.cases.filter(c => (filter === 'All' || c.kind === filter) && (!topic || c.topic===topic) && `${c.title} ${c.llm} ${c.summary} ${c.artifact}`.toLowerCase().includes(query));
  const fragment = document.createDocumentFragment();
  for (const c of matches) {
    const article = element('article', 'case-card');
    const button = element('button', 'card-open');
    button.type = 'button'; button.dataset.case = c.id;
    button.setAttribute('aria-label', `Inspect ${c.llm}: ${c.title}`);
    const visual = element('div', `case-visual${c.panel === undefined ? ' artifact-preview' : ''}`);
    if (c.panel !== undefined) visual.append(panelImage(c.panel, `Archived ${c.llm} screenshot, redacted in the paper`));
    else { visual.append(element('p', 'mono-caption', c.display || `GENERATED · ${c.field || 'OUTPUT'} · REDACTED`), element('pre', '', c.excerpt)); }
    const body = element('div', 'card-body');
    const meta = element('div', 'card-meta');
    meta.append(element('span', '', c.kind), element('span', '', c.llm));
    body.append(meta, element('h3', '', c.title), element('p', '', c.query || c.summary.split('. ')[0] + '.'));
    button.append(visual, body);
    const footer = element('div', 'card-footer');
    const inspect = element('button', '', 'Inspect record ↗'); inspect.dataset.case = c.id; inspect.type = 'button';
    footer.append(element('span', '', c.evidence), inspect);
    article.append(button, footer); fragment.append(article);
  }
  $('case-grid').replaceChildren(fragment);
  $('result-count').textContent = `${matches.length} ${matches.length === 1 ? 'example' : 'examples'}${filter !== 'All' ? ` · ${filter}` : ' · all settings'}`;
  $('empty-state').hidden = matches.length !== 0;
}
function openCase(id) {
  activeCase = evidence?.cases.find(c => c.id === id);
  if (!activeCase) return;
  stopHero(); stopTrace();
  const c = activeCase;
  $('dialog-type').textContent = `${c.kind} / ${c.llm}`;
  $('dialog-title').textContent = c.title; $('dialog-summary').textContent = c.summary;
  const content = document.createDocumentFragment();
  if (c.panel !== undefined) content.append(panelImage(c.panel, `${c.llm} archived output`));
  else {
    if(c.query)content.append(element('p','output-label','TASK QUERY'),element('p','query-text',c.query));
    if(c.before)content.append(element('p','output-label','FIRST GENERATED CANDIDATE'),element('blockquote','artifact-excerpt',c.before));
    if(c.safe)content.append(element('p','output-label','ASSISTANT_SAFE'),element('blockquote','artifact-excerpt safe',c.safe));
    content.append(element('p','output-label',c.display || `${c.field || 'GENERATED OUTPUT'} · REDACTED EXCERPT`),element('blockquote','artifact-excerpt',c.excerpt));
    if(c.checks){const d=element('details','validation-details');d.append(element('summary','','Recorded validation output'),element('pre','',c.checks));content.append(d);}
  }
  $('dialog-evidence').replaceChildren(content);
  $('dialog-source').href = c.artifactSource || c.source;
  $('dialog-replay').hidden = !c.replay;
  $('dialog-note').textContent = c.panel !== undefined ? 'Screenshot from the published paper. Redactions are preserved; the case record links to the original conversation.' : `${c.artifact}${c.recordId ? ` · record ${c.recordId}` : ''}${c.pointer ? ` · ${c.pointer}` : ''} · ███ marks redaction; … marks truncation.`;
  $('case-dialog').showModal(); document.body.classList.add('modal-open');
}
function closeCase() { $('case-dialog').close(); }
function currentReplay() { return evidence?.replays.find(r => r.id === replayId); }
function renderTrace() {
  const r = currentReplay(); if (!r) return;
  const s = r.steps[step];
  $('trace-data-file').textContent = r.folder; $('trace-description').textContent = r.description;
  $('trace-source').href = r.source; $('trace-file').textContent = s.file;
  $('trace-status').textContent = s.status; $('trace-status').className = `status ${s.kind}`;
  $('trace-excerpt-type').textContent = s.summary ? 'Action summary from the recorded run' : 'Recorded excerpt';
  $('trace-output').textContent = s.text; $('trace-pointer').textContent = `agent_log.json · ${s.pointer}`;
  const artifact=evidence.cases.find(c=>c.replay===r.id);
  $('trace-artifact').textContent=artifact?.excerpt || '';
  $('trace-counter').textContent = `${step + 1} / ${r.steps.length}`;
  $('trace-prev').disabled = step === 0; $('trace-next').disabled = step === r.steps.length - 1;
  const buttons = r.steps.map((s, i) => {
    const b = element('button', i === step ? 'active' : '', String(i + 1).padStart(2, '0'));
    b.type = 'button'; b.dataset.step = i; b.setAttribute('aria-label', s.label); b.setAttribute('aria-pressed', String(i === step)); return b;
  });
  $('trace-steps').replaceChildren(...buttons);
  document.querySelectorAll('[data-replay]').forEach(b => { const on = b.dataset.replay === replayId; b.classList.toggle('selected', on); b.setAttribute('aria-pressed', String(on)); });
}
function selectReplay(id) { stopTrace(); replayId = id; step = 0; renderTrace(); }
function stopTrace() { clearInterval(traceTimer); traceTimer = null; $('trace-play').textContent = 'Play trajectory ▶'; }
function playTrace() {
  if (!evidence) return;
  if (traceTimer) { stopTrace(); return; }
  if (step === currentReplay().steps.length - 1) step = 0;
  renderTrace(); $('trace-play').textContent = 'Pause replay Ⅱ';
  traceTimer = setInterval(() => { if (step < currentReplay().steps.length - 1) { step++; renderTrace(); } else stopTrace(); }, 2600);
}
function renderHero() {
  const s = evidence?.replays[0].steps[heroStep]; if (!s) return;
  document.querySelector('.hero-terminal .terminal-label').textContent = heroStep===0 ? 'GENERATED ARTICLE · FIRST CANDIDATE' : 'GENERATED ARTICLE · AFTER REVISION';
  $('hero-output').textContent = s.artifact;
  $('hero-validation').textContent = s.text;
  $('hero-check-label').textContent=s.summary ? 'ACTION SUMMARY' : 'VALIDATION OUTPUT';
  $('hero-status').textContent = s.status; $('hero-status').className = `status ${s.kind}`;
  document.querySelectorAll('[data-hero-step]').forEach(b => { const on = Number(b.dataset.heroStep) === heroStep; b.classList.toggle('active', on); b.setAttribute('aria-pressed', String(on)); });
}
function stopHero() { clearInterval(heroTimer); heroTimer = null; $('hero-play').textContent = 'Play replay ▶'; }
function playHero() {
  if (!evidence) return;
  if (heroTimer) { stopHero(); return; }
  heroStep = 0; renderHero(); $('hero-play').textContent = 'Pause replay Ⅱ';
  heroTimer = setInterval(() => { if (heroStep < 2) { heroStep++; renderHero(); } else stopHero(); }, 3000);
}
async function loadEvidence() {
  $('load-error').hidden = true;
  try {
    const response = await fetch('static/data/evidence.json');
    if (!response.ok) throw new Error(`Evidence HTTP ${response.status}`);
    const data = await response.json();
    if (data.schemaVersion !== 1 || !Array.isArray(data.cases) || !data.replays?.length) throw new Error('Invalid evidence data');
    evidence = data;
    $('topic-filter').replaceChildren(element('option','','Compare the same task…'));
    $('topic-filter').firstElementChild.value='';
    [...new Set(data.cases.map(c=>c.topic).filter(Boolean))].forEach(t=>{const o=element('option','',t);o.value=t;$('topic-filter').append(o)});
    renderCases(); renderTrace(); renderHero();
    if (!reducedMotion.matches && !document.hidden) playHero();
  } catch (error) {
    $('load-error').hidden = false; $('result-count').textContent = 'Evidence is temporarily unavailable.';
    console.error('Could not load the curated evidence.', error);
  }
}
$('case-grid').addEventListener('click', e => { const b = e.target.closest('[data-case]'); if (b) openCase(b.dataset.case); });
document.querySelectorAll('[data-filter]').forEach(b => b.addEventListener('click', () => {
  filter = b.dataset.filter;
  document.querySelectorAll('[data-filter]').forEach(x => { const on = x === b; x.classList.toggle('selected', on); x.setAttribute('aria-pressed', String(on)); });
  renderCases();
}));
$('case-search').addEventListener('input', e => { query = e.target.value.toLowerCase().trim(); renderCases(); });
$('topic-filter').addEventListener('change',e=>{topic=e.target.value;document.querySelector('[data-filter="All"]').click();});
$('clear-filters').addEventListener('click', () => { query = ''; topic='';$('topic-filter').value=''; $('case-search').value = ''; document.querySelector('[data-filter="All"]').click(); });
$('retry-load').addEventListener('click', loadEvidence);
$('dialog-close').addEventListener('click', closeCase);
$('case-dialog').addEventListener('close', () => document.body.classList.remove('modal-open'));
$('case-dialog').addEventListener('click', e => { if (e.target === $('case-dialog')) { const r = e.target.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeCase(); } });
$('dialog-replay').addEventListener('click', () => { selectReplay(activeCase.replay); closeCase(); $('trajectory').scrollIntoView({behavior: reducedMotion.matches ? 'instant' : 'smooth'}); $('trace-play').focus({preventScroll:true}); });
document.querySelectorAll('[data-replay]').forEach(b => b.addEventListener('click', () => selectReplay(b.dataset.replay)));
$('trace-steps').addEventListener('click', e => { const b=e.target.closest('[data-step]'); if (b) { stopTrace(); step=Number(b.dataset.step); renderTrace(); } });
$('trace-prev').addEventListener('click', () => { stopTrace(); if (step>0) step--; renderTrace(); });
$('trace-next').addEventListener('click', () => { stopTrace(); if (currentReplay() && step<currentReplay().steps.length-1) step++; renderTrace(); });
$('trace-play').addEventListener('click', playTrace); $('hero-play').addEventListener('click', playHero);
document.querySelectorAll('[data-hero-step]').forEach(b => b.addEventListener('click', () => { stopHero(); heroStep=Number(b.dataset.heroStep); renderHero(); }));
document.addEventListener('visibilitychange', () => { if (document.hidden) { stopHero(); stopTrace(); } });
reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) { stopHero(); stopTrace(); } });
let batchCount=10;
for(let i=0;i<20;i++)$('batch-cells').append(element('span',`batch-cell${i<10?' filled':''}`));
$('batch-extend').addEventListener('click', () => {
  const btn=$('batch-extend');
  if(batchCount===20){batchCount=10;[...$('batch-cells').children].forEach((c,i)=>c.classList.toggle('filled',i<10));$('batch-count').textContent='10';btn.textContent='Add the next batch +';return;}
  btn.disabled=true;
  const fill=()=>{ $('batch-cells').children[batchCount].classList.add('filled');batchCount++;$('batch-count').textContent=String(batchCount);if(batchCount<20)setTimeout(fill,reducedMotion.matches?0:110);else{btn.disabled=false;btn.textContent='Reset illustration ↺';} };fill();
});
$('copy-citation').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText($('bibtex').textContent);$('copy-status').textContent='Citation copied.';}
  catch{const range=document.createRange();range.selectNodeContents($('bibtex'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);$('copy-status').textContent='Citation selected. Press Ctrl/Cmd+C to copy.';}
});
const legacyAnchors={demos:'experiments',outputs:'experiments',about:'applications'};
if(legacyAnchors[location.hash.slice(1)]){const target=legacyAnchors[location.hash.slice(1)];location.replace(`#${target}`);}
loadEvidence();
