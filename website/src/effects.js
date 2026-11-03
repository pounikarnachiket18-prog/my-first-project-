// =========================================================
// Motion-graphics effects for the page (HTML/CSS side)
// =========================================================
import { drawIcon } from './icons.js';
import { sound } from './sound.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const rand = (a, b) => a + Math.random() * (b - a);
const sign = () => (Math.random() < 0.5 ? -1 : 1);

// ---------------------------------------------------------
// 1. Kinetic type: letters (or words) fly in and assemble
// ---------------------------------------------------------
function splitKinetic(el) {
  const mode = el.dataset.split || 'chars';
  const far = el.hasAttribute('data-far');
  const units = [];

  const makeUnit = (text, inGrad) => {
    const u = document.createElement('span');
    u.className = 'u';
    u.textContent = text;
    if (inGrad) u.classList.add('g');
    units.push(u);
    return u;
  };

  const walk = (node, inGrad) => {
    [...node.childNodes].forEach((child) => {
      if (child.nodeType === Node.TEXT_NODE) {
        const frag = document.createDocumentFragment();
        child.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) {
            frag.appendChild(document.createTextNode(' '));
            return;
          }
          if (mode === 'words') {
            frag.appendChild(makeUnit(part, inGrad));
          } else {
            const w = document.createElement('span');
            w.className = 'w';
            [...part].forEach((ch) => w.appendChild(makeUnit(ch, inGrad)));
            frag.appendChild(w);
          }
        });
        child.replaceWith(frag);
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        if (child.classList.contains('no-split')) {
          child.classList.add('u');
          units.push(child);
        } else {
          walk(child, inGrad || child.classList.contains('grad'));
        }
      }
    });
  };
  walk(el, false);

  const vw = window.innerWidth;
  const vh = window.innerHeight;
  units.forEach((u, i) => {
    const dx = far ? rand(0.2, 0.5) * vw : rand(60, 240);
    const dy = far ? rand(0.2, 0.45) * vh : rand(30, 170);
    u.style.setProperty('--kx', `${sign() * dx}px`);
    u.style.setProperty('--ky', `${sign() * dy}px`);
    u.style.setProperty('--kr', `${sign() * rand(20, 120)}deg`);
    u.style.setProperty('--ks', rand(0.3, 1.8).toFixed(2));
    u.style.setProperty('--kd', `${(i * (mode === 'words' ? 70 : 32)) | 0}ms`);
  });
  return units;
}

// Gradient words stay one continuous gradient after splitting
function fixGradients() {
  document.querySelectorAll('.grad').forEach((grad) => {
    const parts = grad.querySelectorAll('.u.g');
    if (!parts.length) return;
    grad.classList.add('split');
    const left = Math.min(...[...parts].map((p) => p.offsetLeft));
    const right = Math.max(...[...parts].map((p) => p.offsetLeft + p.offsetWidth));
    parts.forEach((p) => {
      p.style.backgroundSize = `${right - left}px 100%`;
      p.style.backgroundPosition = `${left - p.offsetLeft}px 0`;
    });
  });
}

// ---------------------------------------------------------
// 2. Hand-drawn circles / underlines around words
// ---------------------------------------------------------
const MARK_PATHS = {
  circle: 'M 18 34 C 22 8, 172 2, 190 26 C 204 48, 70 64, 16 46 C -4 38, 28 12, 74 8',
  underline: 'M 4 34 C 40 22, 70 40, 104 30 S 160 22, 196 30',
};
function addMarks() {
  document.querySelectorAll('.mark').forEach((mark) => {
    const type = mark.classList.contains('mark-underline') ? 'underline' : 'circle';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 200 60');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('aria-hidden', 'true');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', MARK_PATHS[type]);
    path.setAttribute('pathLength', '1');
    svg.appendChild(path);
    mark.appendChild(svg);
  });
}

// ---------------------------------------------------------
// 3. Typewriter with a block cursor
// ---------------------------------------------------------
function typewriter(words) {
  const el = document.getElementById('typed');
  if (!el || reduceMotion) return;
  let wi = 0;
  let text = words[0];
  let deleting = true;
  const tick = () => {
    const word = words[wi];
    if (deleting) {
      text = text.slice(0, -1);
      el.textContent = text;
      if (!text) {
        deleting = false;
        wi = (wi + 1) % words.length;
      }
      setTimeout(tick, 45);
    } else {
      text = word.slice(0, text.length + 1);
      el.textContent = text;
      sound.play('type');
      if (text === word) {
        deleting = true;
        setTimeout(tick, 1700);
      } else {
        setTimeout(tick, 85);
      }
    }
  };
  setTimeout(tick, 2200);
}

// ---------------------------------------------------------
// 4. Pixel icons drawn on <canvas class="px" data-icon="...">
// ---------------------------------------------------------
function drawPixelIcons(root = document) {
  root.querySelectorAll('canvas.px').forEach((c) => {
    drawIcon(c, c.dataset.icon, parseInt(c.dataset.scale || '4', 10));
  });
}

// ---------------------------------------------------------
// 5. Curved 3D film strip
// ---------------------------------------------------------
const FILM = [
  ['Mindset', 'bulb', '#ffd9b0'],
  ['Discipline', 'flame', '#f7f2ea'],
  ['Focus', 'camera', '#bff0cf'],
  ['Growth', 'star', '#cfe0ff'],
  ['Confidence', 'bubble', '#fff1b8'],
  ['Clarity', 'monitor', '#ffd9b0'],
  ['Habits', 'remote', '#f7f2ea'],
  ['Self-love', 'heart', '#bff0cf'],
];
function buildFilmStrip() {
  const ring = document.getElementById('filmRing');
  if (!ring) return;
  const items = [...FILM, ...FILM];
  const n = items.length;
  const frameW = window.innerWidth < 600 ? 132 : 172;
  const radius = Math.round((n * (frameW + 8)) / (2 * Math.PI));
  ring.style.setProperty('--R', `${radius}px`);
  ring.style.setProperty('--fw', `${frameW}px`);
  ring.innerHTML = '';
  items.forEach(([word, icon, bg], i) => {
    const f = document.createElement('div');
    f.className = 'frame';
    f.style.transform = `rotateY(${(i * 360) / n}deg) translateZ(${radius}px)`;
    f.innerHTML = `<div class="frame-in" style="background:${bg}"><canvas class="px" data-icon="${icon}" data-scale="${frameW < 150 ? 3 : 4}"></canvas><span>${word}</span></div>`;
    ring.appendChild(f);
  });
  drawPixelIcons(ring);
}

// ---------------------------------------------------------
// 6. Editing timeline waveform + little visualisers
// ---------------------------------------------------------
function buildWaves() {
  document.querySelectorAll('[data-wave]').forEach((wave) => {
    const count = parseInt(wave.dataset.wave, 10);
    for (let i = 0; i < count; i++) {
      const bar = document.createElement('i');
      const h = 20 + Math.abs(Math.sin(i * 0.55) * 55) + Math.random() * 25;
      bar.style.height = `${Math.min(100, h)}%`;
      bar.style.animationDelay = `${(-Math.random() * 1.2).toFixed(2)}s`;
      wave.appendChild(bar);
    }
  });
}

// ---------------------------------------------------------
// 7. Ink bleed: text seeps in like ink dropped in water
// ---------------------------------------------------------
const SVG_NS = 'http://www.w3.org/2000/svg';
function prepareInk() {
  const els = document.querySelectorAll('.ink');
  if (!els.length || reduceMotion) return;
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('width', '0');
  svg.setAttribute('height', '0');
  svg.setAttribute('aria-hidden', 'true');
  svg.style.position = 'absolute';
  const defs = document.createElementNS(SVG_NS, 'defs');
  svg.appendChild(defs);
  document.body.appendChild(svg);
  els.forEach((el, i) => {
    const f = document.createElementNS(SVG_NS, 'filter');
    f.id = `ink${i}`;
    ['x', 'y'].forEach((k) => f.setAttribute(k, '-20%'));
    ['width', 'height'].forEach((k) => f.setAttribute(k, '140%'));
    f.innerHTML =
      `<feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="3" seed="${i + 3}" result="n"/>` +
      `<feDisplacementMap in="SourceGraphic" in2="n" scale="70" xChannelSelector="R" yChannelSelector="G"/>`;
    defs.appendChild(f);
    el.style.filter = `url(#ink${i}) blur(2px)`;
    el._ink = f.querySelector('feDisplacementMap');
  });
}
function runInk(el) {
  const map = el._ink;
  if (!map) return;
  const delay = parseFloat(el.dataset.inkDelay || 0);
  const dur = 1900;
  let t0 = null;
  const step = (now) => {
    if (t0 === null) t0 = now + delay;
    const t = Math.min(1, Math.max(0, (now - t0) / dur));
    const e = 1 - Math.pow(1 - t, 3);
    map.setAttribute('scale', (70 * (1 - e)).toFixed(2));
    el.style.filter = t < 1 ? `url(#${map.parentNode.id}) blur(${(2 * (1 - e)).toFixed(2)}px)` : 'none';
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// ---------------------------------------------------------
// 8. Night-sky ending: moon rises, mountains sink (parallax)
// ---------------------------------------------------------
function outroParallax() {
  const outro = document.querySelector('.outro');
  if (!outro || reduceMotion) return;
  const update = () => {
    const r = outro.getBoundingClientRect();
    const vh = window.innerHeight;
    const p = Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height)));
    outro.style.setProperty('--p', p.toFixed(3));
  };
  window.addEventListener('scroll', update, { passive: true });
  update();
}

// ---------------------------------------------------------
// 9. Photo that assembles from big pixels into a sharp image
// ---------------------------------------------------------
function setupPixelReveal() {
  document.querySelectorAll('.pixel-reveal').forEach((fig) => {
    const img = fig.querySelector('img');
    const c = fig.querySelector('canvas');
    if (!img || !c) return;
    if (reduceMotion) {
      c.remove();
      return;
    }
    const g = c.getContext('2d');
    const tiny = document.createElement('canvas');
    const tg = tiny.getContext('2d');
    const drawAt = (cols) => {
      const w = fig.clientWidth;
      const h = fig.clientHeight;
      if (!w || !h || !img.naturalWidth) return;
      c.width = w;
      c.height = h;
      const rows = Math.max(1, Math.round((cols * h) / w));
      tiny.width = cols;
      tiny.height = rows;
      // "cover" crop, focused a little above centre (the face)
      const ir = img.naturalWidth / img.naturalHeight;
      const fr = w / h;
      let sw = img.naturalWidth;
      let sh = img.naturalHeight;
      if (ir > fr) sw = sh * fr;
      else sh = sw / fr;
      const sx = (img.naturalWidth - sw) / 2;
      const sy = (img.naturalHeight - sh) * 0.3;
      tg.imageSmoothingEnabled = true;
      tg.drawImage(img, sx, sy, sw, sh, 0, 0, cols, rows);
      g.imageSmoothingEnabled = false;
      g.drawImage(tiny, 0, 0, cols, rows, 0, 0, w, h);
    };
    const ready = img.complete ? Promise.resolve() : new Promise((r) => img.addEventListener('load', r, { once: true }));
    ready.then(() => drawAt(7));
    fig._reveal = () =>
      ready.then(() => {
        const steps = [7, 10, 14, 20, 28, 40, 58, 84, 130];
        steps.forEach((n, i) => setTimeout(() => drawAt(n), 350 + i * 130));
        setTimeout(() => c.classList.add('done'), 350 + steps.length * 130);
        setTimeout(() => sound.play('blips'), 300);
      });
  });
}

// ---------------------------------------------------------
// Public API
// ---------------------------------------------------------
export function setupEffects({ words }) {
  if (!reduceMotion) document.documentElement.classList.add('fx');

  document.querySelectorAll('.kinetic').forEach(splitKinetic);
  document.querySelectorAll('.slice').forEach((el) => {
    const inner = document.createElement('span');
    inner.className = 'slice-text';
    while (el.firstChild) inner.appendChild(el.firstChild);
    el.appendChild(inner);
  });
  addMarks();
  drawPixelIcons();
  document.querySelectorAll('section, .band').forEach((section) => {
    section.querySelectorAll('.reveal').forEach((el, i) => {
      el.style.transitionDelay = `${Math.min(i * 90, 540)}ms`;
    });
  });
  buildFilmStrip();
  buildWaves();
  prepareInk();
  setupPixelReveal();
  outroParallax();

  fixGradients();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fixGradients);
  let rt;
  window.addEventListener('resize', () => {
    clearTimeout(rt);
    rt = setTimeout(() => {
      fixGradients();
      buildFilmStrip();
    }, 200);
  });

  // film strip spins a little extra as you scroll
  const tilt = document.querySelector('.film-tilt');
  if (tilt && !reduceMotion) {
    window.addEventListener(
      'scroll',
      () => tilt.style.setProperty('--scrollSpin', `${(window.scrollY * -0.06).toFixed(2)}deg`),
      { passive: true }
    );
  }

  return {
    // Called once the intro loader is gone, so the hero animation is seen
    start() {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (!e.isIntersecting) return;
            e.target.classList.add('in');
            const c = e.target.classList;
            if (c.contains('ink')) runInk(e.target);
            if (e.target._reveal) e.target._reveal();
            if (c.contains('ink') && e.target.tagName === 'H2') sound.play('rumble');
            if (c.contains('kinetic')) sound.play('swoosh');
            if (c.contains('mark')) sound.play('scribble', 0.9);
            if (c.contains('edit-timeline')) {
              sound.play('snip', 1.8);
              setTimeout(() => sound.play('snip'), 2150);
            }
            if (c.contains('outro')) sound.play('bell', 0.9);
            io.unobserve(e.target);
          });
        },
        { threshold: 0.2 }
      );
      document
        .querySelectorAll('.reveal, .kinetic, .mark, .slice, .edit-timeline, .outro, .film-band, .ink, .signature, .pixel-reveal')
        .forEach((el) => io.observe(el));
      typewriter(words);
    },
  };
}
