/* Decorative cues for recorded playback. No inference, runtime metrics, or timers. */
(function () {
  'use strict';
  if (window.WorkspaceMotion) window.WorkspaceMotion.destroy();
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const phases = {
    inspect: { label: 'Reading code', cue: 'read', glyph: '↳' },
    write: { label: 'Editing data', cue: 'edit', glyph: '✎' },
    probe: { label: 'Running checks', cue: 'check', glyph: '›_' },
    fail: { label: 'Revision needed', cue: 'revise', glyph: '↺' },
    complete: { label: 'Checks complete', cue: 'end', glyph: '✓' },
    timeout: { label: 'Timed out', cue: 'end', glyph: '—' },
    archive: { label: 'Example', cue: '', glyph: '≡' }
  };
  const animations = new Set();
  let root, strip, icon, label, position, rail;
  let previous = null, paused = false, destroyed = false;

  function mount() {
    if (root && root.isConnected) return true;
    root = document.getElementById('ide-window');
    if (!root) return false;
    strip = document.createElement('div');
    strip.className = 'wm-strip';
    strip.setAttribute('aria-label', 'Playback phase');
    icon = document.createElement('span');
    icon.className = 'wm-icon';
    icon.setAttribute('aria-hidden', 'true');
    const context = document.createElement('span');
    context.className = 'wm-context';
    context.textContent = 'PLAYBACK';
    label = document.createElement('span');
    label.className = 'wm-label';
    rail = document.createElement('span');
    rail.className = 'wm-rail';
    rail.setAttribute('aria-hidden', 'true');
    for (const [key, text] of [['read', 'Read'], ['edit', 'Edit'], ['check', 'Check'], ['revise', 'Revise'], ['end', 'End']]) {
      const item = document.createElement('span');
      item.dataset.cue = key;
      item.textContent = text;
      rail.append(item);
    }
    position = document.createElement('span');
    position.className = 'wm-position';
    strip.append(icon, context, label, rail, position);
    const titlebar = root.querySelector('.ide-titlebar');
    if (titlebar) titlebar.after(strip);
    else root.prepend(strip);
    root.classList.add('wm-enabled');
    return true;
  }

  function clear() {
    for (const animation of animations) animation.cancel();
    animations.clear();
  }

  function move(element, frames, duration, delay) {
    if (!element || typeof element.animate !== 'function') return;
    const animation = element.animate(frames, {
      duration: duration || 480, delay: delay || 0,
      easing: 'cubic-bezier(.2,.7,.25,1)', iterations: 1, fill: 'none'
    });
    animations.add(animation);
    const dispose = () => animations.delete(animation);
    animation.onfinish = dispose;
    animation.oncancel = dispose;
  }

  function transition(input) {
    if (destroyed || !mount()) return;
    const state = input || {};
    const phase = Object.hasOwn(phases, state.phase) ? state.phase : 'inspect';
    const detail = phases[phase];
    const current = { phase, file: String(state.file || ''), step: state.step, total: state.total, mode: state.mode };
    const changed = !previous || Object.keys(current).some(key => current[key] !== previous[key]);
    const fileChanged = previous && current.file !== previous.file;
    previous = current;
    root.dataset.motionPhase = phase;
    root.dataset.motionPaused = String(paused || document.hidden);
    strip.dataset.archive = String(state.mode === 'outputs' || phase === 'archive');
    icon.textContent = detail.glyph;
    label.textContent = detail.label;
    const validPosition = Number.isInteger(state.step) && Number.isInteger(state.total) && state.total > 0 && state.step >= 0 && state.step < state.total;
    position.textContent = validPosition ? `${state.step + 1} / ${state.total}` : '';
    position.setAttribute('aria-label', validPosition ? `Playback item ${state.step + 1} of ${state.total}` : '');
    for (const item of rail.children) item.classList.toggle('wm-current', item.dataset.cue === detail.cue);
    if (!changed) return;
    clear();
    if (state.animate === false || paused || document.hidden || preference.matches) return;
    const editor = root.querySelector('.workspace-editor');
    const terminal = document.getElementById('ide-terminal');
    const feedback = root.querySelector('.workspace-feedback');
    const color = { fail: '225, 153, 130', complete: '143, 194, 159', timeout: '210, 182, 126' }[phase] || '217, 154, 114';
    const activePane = ['probe', 'timeout'].includes(phase) ? terminal : phase === 'fail' || phase === 'complete' ? feedback : editor;
    move(activePane, [
      { boxShadow: `inset 0 0 0 1px rgba(${color}, 0)` },
      { boxShadow: `inset 0 0 0 1px rgba(${color}, .65)`, offset: .28 },
      { boxShadow: `inset 0 0 0 1px rgba(${color}, 0)` }
    ], 850);
    move(icon, [{ opacity: .45, transform: 'translateY(2px)' }, { opacity: 1, transform: 'translateY(0)' }], 360);
    if (fileChanged) {
      move(document.getElementById('editor-file'), [{ opacity: .4, transform: 'translateX(5px)' }, { opacity: 1, transform: 'translateX(0)' }], 320);
      move(root.querySelector('.file-row.current'), [{ backgroundColor: '#635044' }, { backgroundColor: '#37373d' }], 650);
    }
    if (phase === 'write') {
      move(root.querySelector('.workspace-editor > .pane-title'), [{ backgroundColor: '#493b30' }, { backgroundColor: '#252526' }], 720);
    }
    if (phase === 'probe') {
      move(root.querySelector('.terminal-dot'), [{ opacity: .45, transform: 'scale(.8)' }, { opacity: 1, transform: 'scale(1.5)', offset: .4 }, { opacity: 1, transform: 'scale(1)' }], 800);
    }
    move(root.querySelector('.timeline-step.active'), [{ borderTopColor: `rgb(${color})`, backgroundColor: `rgba(${color}, .12)` }, { borderTopColor: '#d99a72', backgroundColor: 'transparent' }], 700);
  }

  function sync() {
    const stopped = paused || document.hidden || preference.matches;
    if (root) root.dataset.motionPaused = String(paused || document.hidden);
    if (preference.matches) { clear(); return; }
    for (const animation of animations) {
      if (stopped) animation.pause();
      else animation.play();
    }
  }
  function pause() { if (!destroyed) { paused = true; sync(); } }
  function resume() { if (!destroyed) { paused = false; sync(); } }
  function destroy() {
    destroyed = true;
    clear();
    document.removeEventListener('visibilitychange', sync);
    if (preference.removeEventListener) preference.removeEventListener('change', sync);
    else preference.removeListener(sync);
    if (strip) strip.remove();
    if (root) {
      root.classList.remove('wm-enabled');
      delete root.dataset.motionPhase;
      delete root.dataset.motionPaused;
    }
    previous = null;
  }
  document.addEventListener('visibilitychange', sync);
  if (preference.addEventListener) preference.addEventListener('change', sync);
  else preference.addListener(sync);
  window.WorkspaceMotion = { transition, pause, resume, destroy };
}());
