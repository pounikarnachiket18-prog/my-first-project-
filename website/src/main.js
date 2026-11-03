// =========================================================
// Nachiket · Mindset Mode India — 3D scene + page interactions
// Edit this file, then run `npm run build` to update app.js
// =========================================================
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

const COLORS = {
  bg: 0x07070d,
  saffron: new THREE.Color('#ff9933'),
  white: new THREE.Color('#fff4e6'),
  green: new THREE.Color('#22c55e'),
};

// Words that rotate in the hero line "I make videos about ___"
const ROTATING_WORDS = ['mindset', 'discipline', 'focus', 'self-growth', 'confidence', 'habits'];

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const isNarrow = () => window.innerWidth < 860;

document.body.classList.add('loading');

// ---------------------------------------------------------
// 3D WORLD
// ---------------------------------------------------------
function createWorld() {
  const canvas = document.getElementById('scene');
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  } catch (err) {
    return null;
  }
  if (!renderer.getContext()) return null;

  const pixelRatio = Math.min(window.devicePixelRatio || 1, isNarrow() ? 1.5 : 2);
  renderer.setPixelRatio(pixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(COLORS.bg, 1);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(COLORS.bg, 0.035);

  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 0, 7);

  // Everything that moves together as "the mind"
  const mind = new THREE.Group();
  scene.add(mind);

  // --- 1. The glowing, breathing core (custom shader) ---
  const coreUniforms = {
    uTime: { value: 0 },
    uAmp: { value: 0.18 },
    uPulse: { value: 0 },
    uColorA: { value: COLORS.saffron.clone() },
    uColorB: { value: COLORS.white.clone() },
    uColorC: { value: COLORS.green.clone() },
  };
  const core = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.15, isNarrow() ? 32 : 56),
    new THREE.ShaderMaterial({
      uniforms: coreUniforms,
      vertexShader: /* glsl */ `
        uniform float uTime;
        uniform float uAmp;
        uniform float uPulse;
        varying vec3 vNormal;
        varying vec3 vView;
        varying float vDisp;
        void main() {
          vec3 p = position;
          float t = uTime * 0.6;
          float d = sin(p.x * 2.4 + t) * sin(p.y * 2.6 + t * 1.3) * sin(p.z * 2.2 + t * 0.7);
          d += 0.5 * sin(p.x * 5.1 - t * 1.1) * sin(p.y * 4.7 + t * 0.9) * sin(p.z * 5.3 + t * 1.5);
          d += 0.25 * sin(length(p) * 9.0 - uTime * 4.0) * uPulse;
          vDisp = d;
          p += normal * d * (uAmp + uPulse * 0.35);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vView = normalize(-mv.xyz);
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * mv;
        }
      `,
      fragmentShader: /* glsl */ `
        uniform vec3 uColorA;
        uniform vec3 uColorB;
        uniform vec3 uColorC;
        uniform float uPulse;
        varying vec3 vNormal;
        varying vec3 vView;
        varying float vDisp;
        void main() {
          float fres = pow(1.0 - max(dot(vNormal, vView), 0.0), 2.4);
          // deep saffron body, green "thought" patches, bright white-hot rim
          vec3 col = uColorA * 0.55;
          col = mix(col, uColorC * 0.75, smoothstep(0.25, 0.85, vDisp));
          col = mix(col, uColorA * 0.25, smoothstep(-0.2, -0.9, vDisp));
          vec3 rim = mix(uColorA, uColorB, smoothstep(0.55, 1.0, fres));
          float glow = 0.35 + uPulse * 0.5;
          vec3 outCol = col * glow + rim * fres * (1.1 + uPulse);
          gl_FragColor = vec4(outCol, 1.0);
        }
      `,
    })
  );
  mind.add(core);

  // --- 2. Wireframe "thought shell" ---
  const shell = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.75, 1)),
    new THREE.LineBasicMaterial({ color: COLORS.saffron, transparent: true, opacity: 0.35 })
  );
  mind.add(shell);

  const shell2 = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.DodecahedronGeometry(2.05, 0)),
    new THREE.LineBasicMaterial({ color: COLORS.white, transparent: true, opacity: 0.12 })
  );
  mind.add(shell2);

  // --- 3. Tricolour orbit rings with little satellites ---
  const rings = [];
  const ringDefs = [
    { r: 2.45, color: COLORS.saffron, tilt: [1.2, 0.2, 0], speed: 0.5 },
    { r: 2.75, color: COLORS.white, tilt: [0.4, 1.0, 0.3], speed: -0.35 },
    { r: 3.05, color: COLORS.green, tilt: [-0.9, 0.5, 0.8], speed: 0.28 },
  ];
  ringDefs.forEach((def) => {
    const pivot = new THREE.Group();
    pivot.rotation.set(...def.tilt);
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(def.r, 0.009, 8, 220),
      new THREE.MeshBasicMaterial({ color: def.color, transparent: true, opacity: 0.75 })
    );
    pivot.add(ring);
    const sat = new THREE.Mesh(
      new THREE.SphereGeometry(0.075, 16, 16),
      new THREE.MeshBasicMaterial({ color: def.color.clone().multiplyScalar(1.6) })
    );
    sat.position.x = def.r;
    const satHolder = new THREE.Group();
    satHolder.add(sat);
    pivot.add(satHolder);
    mind.add(pivot);
    rings.push({ pivot, satHolder, speed: def.speed });
  });

  // --- 4. Floating geometric "ideas" around the mind ---
  const ideas = [];
  const ideaGeos = [
    new THREE.OctahedronGeometry(0.22, 0),
    new THREE.TetrahedronGeometry(0.24, 0),
    new THREE.BoxGeometry(0.28, 0.28, 0.28),
    new THREE.IcosahedronGeometry(0.2, 0),
  ];
  const palette = [COLORS.saffron, COLORS.white, COLORS.green];
  for (let i = 0; i < 14; i++) {
    const m = new THREE.LineSegments(
      new THREE.EdgesGeometry(ideaGeos[i % ideaGeos.length]),
      new THREE.LineBasicMaterial({ color: palette[i % 3], transparent: true, opacity: 0.55 })
    );
    const a = (i / 14) * Math.PI * 2;
    const radius = 3.6 + Math.random() * 2.4;
    m.userData = {
      a,
      radius,
      y: (Math.random() - 0.5) * 4,
      speed: 0.05 + Math.random() * 0.08,
      spin: 0.3 + Math.random() * 0.8,
      bob: Math.random() * Math.PI * 2,
    };
    scene.add(m);
    ideas.push(m);
  }

  // --- 5. Star dust / particles ---
  const dotTexture = (() => {
    const c = document.createElement('canvas');
    c.width = c.height = 64;
    const g = c.getContext('2d');
    const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, 'rgba(255,255,255,1)');
    grd.addColorStop(0.35, 'rgba(255,255,255,0.6)');
    grd.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grd;
    g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  })();

  const STAR_COUNT = isNarrow() ? 1400 : 2800;
  const starPos = new Float32Array(STAR_COUNT * 3);
  const starCol = new Float32Array(STAR_COUNT * 3);
  for (let i = 0; i < STAR_COUNT; i++) {
    const r = 6 + Math.random() * 34;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    starPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    starPos[i * 3 + 2] = r * Math.cos(phi);
    const roll = Math.random();
    const c = roll < 0.18 ? COLORS.saffron : roll < 0.3 ? COLORS.green : COLORS.white;
    starCol[i * 3] = c.r;
    starCol[i * 3 + 1] = c.g;
    starCol[i * 3 + 2] = c.b;
  }
  const starGeo = new THREE.BufferGeometry();
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute('color', new THREE.BufferAttribute(starCol, 3));
  const stars = new THREE.Points(
    starGeo,
    new THREE.PointsMaterial({
      size: 0.09,
      map: dotTexture,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })
  );
  scene.add(stars);

  // --- 6. Energy burst particles (on click / tap) ---
  const BURST = 260;
  const burstPos = new Float32Array(BURST * 3);
  const burstVel = [];
  for (let i = 0; i < BURST; i++) burstVel.push(new THREE.Vector3());
  const burstGeo = new THREE.BufferGeometry();
  burstGeo.setAttribute('position', new THREE.BufferAttribute(burstPos, 3));
  const burstMat = new THREE.PointsMaterial({
    size: 0.08,
    map: dotTexture,
    color: COLORS.saffron.clone().multiplyScalar(1.5),
    transparent: true,
    opacity: 0,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });
  const burst = new THREE.Points(burstGeo, burstMat);
  mind.add(burst);
  let burstLife = 0;

  function triggerBurst() {
    coreUniforms.uPulse.value = 1;
    burstLife = 1;
    for (let i = 0; i < BURST; i++) {
      const v = new THREE.Vector3().randomDirection();
      burstPos[i * 3] = v.x * 1.2;
      burstPos[i * 3 + 1] = v.y * 1.2;
      burstPos[i * 3 + 2] = v.z * 1.2;
      burstVel[i].copy(v).multiplyScalar(2 + Math.random() * 3.5);
    }
    burstGeo.attributes.position.needsUpdate = true;
  }

  // --- Post-processing: bloom glow ---
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(pixelRatio);
  composer.setSize(window.innerWidth, window.innerHeight);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.7, // strength
    0.45, // radius
    0.2 // threshold
  );
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  // ---------------------------------------------------------
  // Scroll choreography: each <section> has data-x/y/z/amp/s
  // telling the 3D mind where to be while that section is in view.
  // ---------------------------------------------------------
  const sections = [...document.querySelectorAll('main .section')].map((el) => ({
    el,
    x: parseFloat(el.dataset.x || 0),
    y: parseFloat(el.dataset.y || 0),
    z: parseFloat(el.dataset.z || 7),
    amp: parseFloat(el.dataset.amp || 0.2),
    s: parseFloat(el.dataset.s || 1),
    center: 0,
  }));
  function measure() {
    sections.forEach((s) => {
      const r = s.el.getBoundingClientRect();
      s.center = r.top + window.scrollY + r.height / 2;
    });
  }
  measure();

  const target = { x: 0, y: 0, z: 7, amp: 0.18, s: 1 };
  const current = { ...target };
  const smooth = (t) => t * t * (3 - 2 * t);

  function computeTarget() {
    const mid = window.scrollY + window.innerHeight / 2;
    let a = sections[0];
    let b = sections[0];
    let t = 0;
    if (mid >= sections[sections.length - 1].center) {
      a = b = sections[sections.length - 1];
    } else if (mid > sections[0].center) {
      for (let i = 0; i < sections.length - 1; i++) {
        if (mid >= sections[i].center && mid < sections[i + 1].center) {
          a = sections[i];
          b = sections[i + 1];
          t = smooth((mid - a.center) / (b.center - a.center));
          break;
        }
      }
    }
    const narrow = isNarrow();
    for (const k of ['x', 'y', 'z', 'amp', 's']) target[k] = a[k] + (b[k] - a[k]) * t;
    if (narrow) {
      // On phones the mind stays centred and sits a bit higher, behind the text
      target.x = 0;
      target.y = target.y * 0.5 + 1.4;
      target.z += 4.5;
    }
  }

  // ---------------------------------------------------------
  // Input: mouse parallax + click/tap energy burst
  // ---------------------------------------------------------
  const pointer = { x: 0, y: 0, sx: 0, sy: 0 };
  window.addEventListener('pointermove', (e) => {
    pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (e.clientY / window.innerHeight) * 2 - 1;
  });
  window.addEventListener('pointerdown', (e) => {
    if (e.target.closest('a, button, .tilt, input, textarea')) return;
    triggerBurst();
  });

  let lastScrollY = window.scrollY;
  let scrollVel = 0;

  function onResize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    composer.setSize(w, h);
    bloom.setSize(w, h);
    measure();
  }
  window.addEventListener('resize', onResize);
  window.addEventListener('load', measure);

  // ---------------------------------------------------------
  // Animation loop
  // ---------------------------------------------------------
  const clock = new THREE.Clock();
  const motion = reduceMotion ? 0.15 : 1;
  let firstFrameCb = null;

  function frame() {
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    computeTarget();
    const ease = 1 - Math.pow(0.0015, dt); // frame-rate independent smoothing
    for (const k in current) current[k] += (target[k] - current[k]) * ease;

    // scroll speed adds a little extra spin
    const sy = window.scrollY;
    scrollVel += ((sy - lastScrollY) * 0.002 - scrollVel) * 0.1;
    lastScrollY = sy;

    mind.position.set(current.x, current.y, 0);
    const breathe = 1 + Math.sin(time * 1.2) * 0.015 * motion;
    mind.scale.setScalar(current.s * breathe);

    core.rotation.y += dt * 0.25 * motion + scrollVel * 0.5;
    core.rotation.x += dt * 0.08 * motion;
    shell.rotation.y -= dt * 0.18 * motion + scrollVel * 0.6;
    shell.rotation.z += dt * 0.06 * motion;
    shell2.rotation.x += dt * 0.05 * motion;
    shell2.rotation.y += dt * 0.07 * motion - scrollVel * 0.3;

    rings.forEach((r, i) => {
      r.pivot.rotation.z += dt * r.speed * 0.4 * motion;
      r.satHolder.rotation.z += dt * r.speed * 2.2 * motion;
      r.pivot.rotation.x += Math.sin(time * 0.3 + i) * 0.0008 * motion;
    });

    ideas.forEach((m) => {
      const u = m.userData;
      u.a += dt * u.speed * motion;
      m.position.set(
        Math.cos(u.a) * u.radius + current.x * 0.4,
        u.y + Math.sin(time * 0.8 + u.bob) * 0.25,
        Math.sin(u.a) * u.radius - 3
      );
      m.rotation.x += dt * u.spin * motion;
      m.rotation.y += dt * u.spin * 0.7 * motion;
    });

    stars.rotation.y += dt * 0.012 * motion;
    stars.rotation.x = sy * 0.00008;

    coreUniforms.uTime.value += dt * motion;
    coreUniforms.uAmp.value = current.amp;
    coreUniforms.uPulse.value *= Math.pow(0.25, dt);

    if (burstLife > 0) {
      burstLife = Math.max(0, burstLife - dt * 0.7);
      for (let i = 0; i < BURST; i++) {
        burstPos[i * 3] += burstVel[i].x * dt;
        burstPos[i * 3 + 1] += burstVel[i].y * dt;
        burstPos[i * 3 + 2] += burstVel[i].z * dt;
        burstVel[i].multiplyScalar(0.97);
      }
      burstGeo.attributes.position.needsUpdate = true;
      burstMat.opacity = burstLife;
    }

    // camera drifts with the mouse for a parallax feel
    pointer.sx += (pointer.x - pointer.sx) * 0.05;
    pointer.sy += (pointer.y - pointer.sy) * 0.05;
    camera.position.x = pointer.sx * 0.7 * motion;
    camera.position.y = -pointer.sy * 0.45 * motion;
    camera.position.z = current.z;
    camera.lookAt(0, current.y * 0.3, 0);

    composer.render();

    if (firstFrameCb) {
      firstFrameCb();
      firstFrameCb = null;
    }
    requestAnimationFrame(frame);
  }

  return {
    start(onFirstFrame) {
      firstFrameCb = onFirstFrame;
      requestAnimationFrame(frame);
    },
    burst: triggerBurst,
  };
}

// ---------------------------------------------------------
// PAGE UI
// ---------------------------------------------------------
function setupUI(world) {
  // Footer year
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  // Nav background + scroll progress + active link
  const nav = document.getElementById('nav');
  const progress = document.getElementById('progress');
  const links = [...document.querySelectorAll('.nav-links a')];
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const p = max > 0 ? window.scrollY / max : 0;
    progress.style.transform = `scaleX(${p})`;
    nav.classList.toggle('scrolled', window.scrollY > 30);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const activeObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = entry.target.id;
        links.forEach((a) => a.classList.toggle('active', a.getAttribute('href') === `#${id}`));
      });
    },
    { rootMargin: '-45% 0px -45% 0px' }
  );
  document.querySelectorAll('main .section').forEach((s) => activeObserver.observe(s));

  // Reveal-on-scroll, with a small stagger inside each section
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('in');
        revealObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.15 }
  );
  document.querySelectorAll('.section').forEach((section) => {
    section.querySelectorAll('.reveal').forEach((el, i) => {
      el.style.transitionDelay = `${Math.min(i * 90, 540)}ms`;
      revealObserver.observe(el);
    });
  });

  // Rotating words in the hero
  const rotator = document.getElementById('rotator');
  if (rotator && !reduceMotion) {
    let i = 0;
    setInterval(() => {
      rotator.classList.add('out');
      setTimeout(() => {
        i = (i + 1) % ROTATING_WORDS.length;
        rotator.textContent = ROTATING_WORDS[i];
        rotator.classList.remove('out');
      }, 350);
    }, 2200);
  }

  // 3D tilt cards
  const canHover = window.matchMedia('(hover: hover)').matches;
  if (canHover && !reduceMotion) {
    document.querySelectorAll('.tilt').forEach((card) => {
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        card.classList.add('tilting');
        card.style.setProperty('--ry', `${(px - 0.5) * 14}deg`);
        card.style.setProperty('--rx', `${(0.5 - py) * 12}deg`);
        card.style.setProperty('--mx', `${px * 100}%`);
        card.style.setProperty('--my', `${py * 100}%`);
      });
      card.addEventListener('pointerleave', () => {
        card.classList.remove('tilting');
        card.style.setProperty('--rx', '0deg');
        card.style.setProperty('--ry', '0deg');
      });
    });
  }

  // Cursor glow
  const glow = document.getElementById('cursorGlow');
  if (glow && canHover) {
    window.addEventListener('pointermove', (e) => {
      glow.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
    });
  }

  // Placeholder social links (until real links are added in index.html)
  const toast = document.getElementById('toast');
  let toastTimer;
  document.querySelectorAll('[data-placeholder]').forEach((a) => {
    a.addEventListener('click', (e) => {
      if (a.getAttribute('href') !== '#') return;
      e.preventDefault();
      toast.textContent = `${a.dataset.placeholder} link coming soon.`;
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
      if (world) world.burst();
    });
  });
}

// ---------------------------------------------------------
// BOOT
// ---------------------------------------------------------
function hideLoader() {
  const loader = document.getElementById('loader');
  loader.classList.add('done');
  document.body.classList.remove('loading');
  document.body.classList.add('ready');
}

const startedAt = performance.now();
const world = createWorld();
setupUI(world);

const finish = () => {
  const wait = Math.max(0, 900 - (performance.now() - startedAt));
  setTimeout(hideLoader, wait);
};

if (world) {
  world.start(finish);
} else {
  document.body.classList.add('no-webgl');
  finish();
}
