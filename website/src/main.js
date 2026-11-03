// =========================================================
// Nachiket · Mindset Mode India — 3D scene + page interactions
// Edit the files in src/, then run `npm run build` to update app.js
// =========================================================
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { iconPixels } from './icons.js';
import { setupEffects } from './effects.js';
import { createSky, createFireRing, createArrow } from './cinematic.js';
import { sound } from './sound.js';

const COLORS = {
  bg: new THREE.Color('#07070d'),
  saffron: new THREE.Color('#ff9933'),
  white: new THREE.Color('#fff4e6'),
  green: new THREE.Color('#22c55e'),
};

// Words typed in the hero line "I make videos about ___"
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
  scene.fog = new THREE.FogExp2(COLORS.bg.clone(), 0.035);
  scene.add(new THREE.AmbientLight(0xffffff, 1.2));
  const sun = new THREE.DirectionalLight(0xffffff, 2.2);
  sun.position.set(-3, 4, 5);
  scene.add(sun);

  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 0, 7);

  // Watercolour ink-smoke sky behind everything
  const sky = createSky(isNarrow() ? 3 : 4);
  scene.add(sky.mesh);
  const pointScale = () =>
    (window.innerHeight * pixelRatio * 0.5) / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));

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

  // --- 2. Wireframe "thought shells" ---
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
  [
    { r: 2.45, color: COLORS.saffron, tilt: [1.2, 0.2, 0], speed: 0.5 },
    { r: 2.75, color: COLORS.white, tilt: [0.4, 1.0, 0.3], speed: -0.35 },
    { r: 3.05, color: COLORS.green, tilt: [-0.9, 0.5, 0.8], speed: 0.28 },
  ].forEach((def) => {
    const pivot = new THREE.Group();
    pivot.rotation.set(...def.tilt);
    pivot.add(
      new THREE.Mesh(
        new THREE.TorusGeometry(def.r, 0.009, 8, 220),
        new THREE.MeshBasicMaterial({ color: def.color, transparent: true, opacity: 0.75 })
      )
    );
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

  // --- 3b. Ring of fire (lit by the flaming arrow) ---
  const fire = createFireRing(isNarrow() ? 700 : 1200, 2.25);
  fire.uniforms.uScale.value = pointScale();
  mind.add(fire.points);
  let fireOn = false;
  let fireLevel = 0;

  // --- 3c. Flaming arrow ---
  const arrowFx = createArrow(520);
  arrowFx.uniforms.uScale.value = pointScale();
  scene.add(arrowFx.arrow, arrowFx.trail);
  let arrowT = -1; // -1 = not flying
  const arrowStart = new THREE.Vector3();
  const arrowEnd = new THREE.Vector3();
  const arrowDir = new THREE.Vector3();
  const arrowHead = new THREE.Vector3();

  // --- 4. Floating wireframe "ideas" ---
  const ideas = [];
  const ideaGeos = [
    new THREE.OctahedronGeometry(0.22, 0),
    new THREE.TetrahedronGeometry(0.24, 0),
    new THREE.BoxGeometry(0.28, 0.28, 0.28),
    new THREE.IcosahedronGeometry(0.2, 0),
  ];
  const palette = [COLORS.saffron, COLORS.white, COLORS.green];
  for (let i = 0; i < 12; i++) {
    const m = new THREE.LineSegments(
      new THREE.EdgesGeometry(ideaGeos[i % ideaGeos.length]),
      new THREE.LineBasicMaterial({ color: palette[i % 3], transparent: true, opacity: 0.55 })
    );
    m.userData = {
      a: (i / 12) * Math.PI * 2,
      radius: 3.6 + Math.random() * 2.4,
      y: (Math.random() - 0.5) * 4,
      speed: 0.05 + Math.random() * 0.08,
      spin: 0.3 + Math.random() * 0.8,
      bob: Math.random() * Math.PI * 2,
    };
    scene.add(m);
    ideas.push(m);
  }

  // --- 5. Confetti cubes drifting through the scene ---
  const CONFETTI = isNarrow() ? 26 : 44;
  const confettiColors = ['#ff9933', '#f7f2ea', '#22c55e', '#3b82f6', '#ffd23f', '#ef4444'];
  const confetti = new THREE.InstancedMesh(
    new THREE.BoxGeometry(0.12, 0.12, 0.12),
    new THREE.MeshLambertMaterial(),
    CONFETTI
  );
  const confettiData = [];
  const tmpObj = new THREE.Object3D();
  const tmpColor = new THREE.Color();
  for (let i = 0; i < CONFETTI; i++) {
    confettiData.push({
      x: (Math.random() - 0.5) * 18,
      y: (Math.random() - 0.5) * 14,
      z: -7 + Math.random() * 7,
      rx: Math.random() * 6,
      ry: Math.random() * 6,
      spin: 0.4 + Math.random() * 1.2,
      fall: 0.05 + Math.random() * 0.15,
      s: 0.5 + Math.random() * 1.1,
    });
    confetti.setColorAt(i, tmpColor.set(confettiColors[i % confettiColors.length]));
  }
  scene.add(confetti);

  // --- 6. Star dust ---
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
    starCol.set([c.r, c.g, c.b], i * 3);
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

  // --- 7. Energy burst particles (on click / tap) ---
  const BURST = 260;
  const burstPos = new Float32Array(BURST * 3);
  const burstVel = Array.from({ length: BURST }, () => new THREE.Vector3());
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
  mind.add(new THREE.Points(burstGeo, burstMat));
  let burstLife = 0;

  // ---------------------------------------------------------
  // 8. VOXEL ICONS: pixel-art icons built from little cubes.
  // When the section changes, the cubes fly apart and rebuild
  // themselves as the next icon. They live in their own scene,
  // drawn after the glow, so they stay crisp.
  // ---------------------------------------------------------
  const iconScene = new THREE.Scene();
  iconScene.add(new THREE.AmbientLight(0xffffff, 1.5));
  const iconSun = new THREE.DirectionalLight(0xffffff, 2.4);
  iconSun.position.set(-2, 3, 4);
  iconScene.add(iconSun);
  const iconGroup = new THREE.Group();
  iconScene.add(iconGroup);

  const VOX = 0.1;
  const POOL = 220;
  const vox = new THREE.InstancedMesh(
    new THREE.BoxGeometry(VOX * 0.94, VOX * 0.94, VOX * 2.2),
    new THREE.MeshLambertMaterial(),
    POOL
  );
  vox.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  iconGroup.add(vox);

  const V = {
    pos: [], from: [], mid: [], to: [],
    col: [], fromC: [], toC: [],
    scl: new Float32Array(POOL), fromS: new Float32Array(POOL), toS: new Float32Array(POOL),
    delay: new Float32Array(POOL), axis: [],
  };
  for (let i = 0; i < POOL; i++) {
    const p = new THREE.Vector3().randomDirection().multiplyScalar(2 + Math.random() * 3);
    V.pos.push(p);
    V.from.push(p.clone());
    V.mid.push(new THREE.Vector3());
    V.to.push(p.clone());
    V.col.push(new THREE.Color('#ff9933'));
    V.fromC.push(new THREE.Color());
    V.toC.push(new THREE.Color());
    V.axis.push(new THREE.Vector3().randomDirection());
  }
  let morphT = 2;
  let currentIcon = null;
  const shuffle = (arr) => {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  };

  function morphTo(name, explode = false) {
    const px = shuffle(iconPixels(name));
    for (let i = 0; i < POOL; i++) {
      V.from[i].copy(V.pos[i]);
      V.fromC[i].copy(V.col[i]);
      V.fromS[i] = V.scl[i];
      if (i < px.length) {
        V.to[i].set(px[i].x * VOX, px[i].y * VOX, 0);
        V.toC[i].set(px[i].color);
        V.toS[i] = 1;
      } else {
        V.to[i].copy(V.from[i]).add(new THREE.Vector3().randomDirection().multiplyScalar(2));
        V.toC[i].copy(V.fromC[i]);
        V.toS[i] = 0;
      }
      const spread = explode ? 2.6 + Math.random() * 2.2 : 0.8 + Math.random() * 1.6;
      V.mid[i]
        .copy(V.from[i])
        .lerp(V.to[i], 0.5)
        .add(new THREE.Vector3().randomDirection().multiplyScalar(spread));
      V.delay[i] = Math.random() * 0.35;
    }
    currentIcon = name;
    morphT = 0;
  }

  const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const q = new THREE.Quaternion();
  const m4 = new THREE.Matrix4();
  const sv = new THREE.Vector3();
  const a1 = new THREE.Vector3();
  const a2 = new THREE.Vector3();

  function updateVoxels(dt) {
    if (morphT > 1.05) return;
    morphT += dt / (reduceMotion ? 0.4 : 1.5);
    for (let i = 0; i < POOL; i++) {
      const lt = Math.min(1, Math.max(0, (morphT - V.delay[i]) / 0.65));
      const e = easeInOut(lt);
      // curved flight path: from -> scattered midpoint -> target
      a1.copy(V.from[i]).lerp(V.mid[i], e);
      a2.copy(V.mid[i]).lerp(V.to[i], e);
      V.pos[i].copy(a1).lerp(a2, e);
      V.col[i].copy(V.fromC[i]).lerp(V.toC[i], e);
      V.scl[i] = V.fromS[i] + (V.toS[i] - V.fromS[i]) * e;
      q.setFromAxisAngle(V.axis[i], Math.sin(e * Math.PI) * Math.PI);
      sv.setScalar(Math.max(V.scl[i], 0.0001));
      m4.compose(V.pos[i], q, sv);
      vox.setMatrixAt(i, m4);
      vox.setColorAt(i, V.col[i]);
    }
    vox.instanceMatrix.needsUpdate = true;
    vox.instanceColor.needsUpdate = true;
  }
  // start with every cube hidden, scattered
  for (let i = 0; i < POOL; i++) {
    vox.setMatrixAt(i, m4.makeScale(0.0001, 0.0001, 0.0001));
    vox.setColorAt(i, V.col[i]);
  }

  function triggerBurst() {
    coreUniforms.uPulse.value = 1;
    burstLife = 1;
    for (let i = 0; i < BURST; i++) {
      const v = new THREE.Vector3().randomDirection();
      burstPos.set([v.x * 1.2, v.y * 1.2, v.z * 1.2], i * 3);
      burstVel[i].copy(v).multiplyScalar(2 + Math.random() * 3.5);
    }
    burstGeo.attributes.position.needsUpdate = true;
    if (currentIcon) morphTo(currentIcon, true);
  }

  // --- Post-processing: bloom glow, then the crisp voxel icon on top ---
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(pixelRatio);
  composer.setSize(window.innerWidth, window.innerHeight);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.7, 0.45, 0.2);
  composer.addPass(bloom);
  const iconPass = new RenderPass(iconScene, camera);
  iconPass.clear = false;
  iconPass.clearDepth = true;
  composer.addPass(iconPass);
  composer.addPass(new OutputPass());

  // ---------------------------------------------------------
  // Scroll choreography: each <section> has data-x/y/z/amp/s/icon/bg
  // telling the 3D scene what to do while that section is in view.
  // ---------------------------------------------------------
  const sections = [...document.querySelectorAll('main .section')].map((el) => ({
    el,
    x: parseFloat(el.dataset.x || 0),
    y: parseFloat(el.dataset.y || 0),
    z: parseFloat(el.dataset.z || 7),
    amp: parseFloat(el.dataset.amp || 0.2),
    s: parseFloat(el.dataset.s || 1),
    icon: el.dataset.icon || 'bubble',
    // optional offset/scale of the pixel icon (desktop only)
    ix: parseFloat(el.dataset.ix || 0),
    iy: parseFloat(el.dataset.iy || 0),
    is: parseFloat(el.dataset.is || 1),
    bg: new THREE.Color(el.dataset.bg || '#07070d'),
    // watercolour sky: "colourA,colourB,amount"
    skyA: new THREE.Color((el.dataset.sky || '#3b1d5c,#ff9933,0.3').split(',')[0]),
    skyB: new THREE.Color((el.dataset.sky || '#3b1d5c,#ff9933,0.3').split(',')[1]),
    skyAmt: parseFloat((el.dataset.sky || '#3b1d5c,#ff9933,0.3').split(',')[2]),
    core: new THREE.Color(el.dataset.core || '#ff9933'),
    spin: parseFloat(el.dataset.spin || 1),
    fire: parseFloat(el.dataset.fire || 0),
    center: 0,
  }));
  function measure() {
    sections.forEach((s) => {
      const r = s.el.getBoundingClientRect();
      s.center = r.top + window.scrollY + r.height / 2;
    });
  }
  measure();

  const target = { x: 0, y: 0, z: 7, amp: 0.18, s: 1, ix: 0, iy: 0, is: 1, spin: 1, skyAmt: 0.3 };
  const current = { ...target };
  const targetBg = COLORS.bg.clone();
  const currentBg = COLORS.bg.clone();
  const look = {
    skyA: new THREE.Color(), skyB: new THREE.Color(), core: new THREE.Color(),
    tSkyA: new THREE.Color(), tSkyB: new THREE.Color(), tCore: new THREE.Color(),
  };
  look.skyA.copy(sections[0].skyA);
  look.skyB.copy(sections[0].skyB);
  look.core.copy(sections[0].core);
  let activeSection = sections[0];
  const smooth = (t) => t * t * (3 - 2 * t);

  function computeTarget() {
    const mid = window.scrollY + window.innerHeight / 2;
    let a = sections[0];
    let b = sections[0];
    let t = 0;
    const last = sections[sections.length - 1];
    if (mid >= last.center) {
      a = b = last;
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
    for (const k of ['x', 'y', 'z', 'amp', 's', 'ix', 'iy', 'is', 'spin', 'skyAmt']) target[k] = a[k] + (b[k] - a[k]) * t;
    look.tSkyA.copy(a.skyA).lerp(b.skyA, t);
    look.tSkyB.copy(a.skyB).lerp(b.skyB, t);
    look.tCore.copy(a.core).lerp(b.core, t);
    targetBg.copy(a.bg).lerp(b.bg, t);
    activeSection = t < 0.5 ? a : b;
    // past the last section (the night-sky ending): the pixel icon bows out
    if (mid > last.center + window.innerHeight * 0.6) target.is = 0;
    if (isNarrow()) {
      // On phones the mind stays centred and sits a bit higher, behind the text
      target.x = 0;
      target.y = target.y * 0.5 + 1.4;
      target.z += 4.5;
      target.ix = 0;
      target.iy = 0;
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
    sound.play('sparkle');
  });

  let lastScrollY = window.scrollY;
  let scrollVel = 0;

  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    composer.setSize(w, h);
    bloom.setSize(w, h);
    sky.uniforms.uAspect.value = w / h;
    fire.uniforms.uScale.value = pointScale();
    arrowFx.uniforms.uScale.value = pointScale();
    measure();
  });
  window.addEventListener('load', measure);

  // ---------------------------------------------------------
  // Animation loop
  // ---------------------------------------------------------
  const clock = new THREE.Clock();
  const motion = reduceMotion ? 0.15 : 1;
  let firstFrameCb = null;
  let started = false;

  function frame() {
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;

    computeTarget();
    const ease = 1 - Math.pow(0.0015, dt); // frame-rate independent smoothing
    for (const k in current) current[k] += (target[k] - current[k]) * ease;
    currentBg.lerp(targetBg, ease * 0.6);
    renderer.setClearColor(currentBg, 1);
    scene.fog.color.copy(currentBg);

    if (started && activeSection.icon !== currentIcon) {
      if (currentIcon) sound.play('whoosh');
      sound.play('blips');
      morphTo(activeSection.icon);
    }
    updateVoxels(dt);

    // painterly sky + core colour follow the section
    look.skyA.lerp(look.tSkyA, ease * 0.6);
    look.skyB.lerp(look.tSkyB, ease * 0.6);
    look.core.lerp(look.tCore, ease * 0.6);
    sky.uniforms.uColA.value.copy(look.skyA);
    sky.uniforms.uColB.value.copy(look.skyB);
    sky.uniforms.uBg.value.copy(currentBg);
    sky.uniforms.uAmount.value = current.skyAmt;
    sky.uniforms.uTime.value += dt * (0.6 + current.spin * 0.4) * motion;
    sky.uniforms.uScroll.value = (window.scrollY / window.innerHeight) * 0.35;
    coreUniforms.uColorA.value.copy(look.core);

    // flaming arrow -> ring of fire, every time you enter a "fire" section
    const wantsFire = activeSection.fire > 0;
    if (!wantsFire) fireOn = false;
    if (started && wantsFire && !fireOn && arrowT < 0) {
      if (reduceMotion) fireOn = true;
      else {
        arrowT = 0;
        arrowFx.arrow.visible = true;
        sound.play('arrow');
      }
    }
    if (arrowT >= 0) {
      arrowT = Math.min(1, arrowT + dt / 0.95);
      arrowEnd.copy(mind.position);
      arrowStart.copy(mind.position).add(isNarrow() ? new THREE.Vector3(-4.5, -6, 2) : new THREE.Vector3(-8, -3.4, 1.5));
      arrowDir.copy(arrowEnd).sub(arrowStart).normalize();
      const k = arrowT * arrowT * (2 - arrowT * 0.6);
      arrowFx.arrow.position.copy(arrowStart).lerp(arrowEnd, Math.min(1, k));
      arrowFx.arrow.lookAt(arrowEnd);
      arrowHead.copy(arrowFx.arrow.position).addScaledVector(arrowDir, 0.8);
      arrowFx.emit(arrowHead, arrowDir.clone().negate(), 9);
      if (arrowFx.arrow.position.distanceTo(arrowEnd) < 1.25 || arrowT >= 1) {
        arrowT = -1;
        arrowFx.arrow.visible = false;
        if (activeSection.fire > 0) {
          fireOn = true;
          triggerBurst();
          sound.play('impact');
        }
      }
    }
    arrowFx.update(dt);
    fireLevel += ((fireOn ? activeSection.fire : 0) - fireLevel) * Math.min(1, dt * 2.2);
    fire.uniforms.uIntensity.value = fireLevel;
    fire.uniforms.uTime.value += dt;
    fire.points.visible = fireLevel > 0.01;
    sound.setFire(fireLevel);

    const sy = window.scrollY;
    scrollVel += ((sy - lastScrollY) * 0.002 - scrollVel) * 0.1;
    lastScrollY = sy;

    mind.position.set(current.x, current.y, 0);
    mind.scale.setScalar(current.s * (1 + Math.sin(time * 1.2) * 0.015 * motion));

    core.rotation.y += dt * 0.25 * current.spin * motion + scrollVel * 0.5;
    core.rotation.x += dt * 0.08 * motion;
    shell.rotation.y -= dt * 0.18 * current.spin * motion + scrollVel * 0.6;
    shell.rotation.z += dt * 0.06 * motion;
    shell2.rotation.x += dt * 0.05 * motion;
    shell2.rotation.y += dt * 0.07 * motion - scrollVel * 0.3;

    rings.forEach((r, i) => {
      r.pivot.rotation.z += dt * r.speed * 0.4 * current.spin * motion;
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

    // confetti falls slowly and drifts the other way when you scroll
    confettiData.forEach((c, i) => {
      c.y -= dt * c.fall * motion;
      c.rx += dt * c.spin * motion;
      c.ry += dt * c.spin * 0.8 * motion;
      let y = ((c.y + sy * 0.0025 * (1 + c.z * -0.1) + 7) % 14 + 14) % 14 - 7;
      tmpObj.position.set(c.x, y, c.z);
      tmpObj.rotation.set(c.rx, c.ry, 0);
      tmpObj.scale.setScalar(c.s);
      tmpObj.updateMatrix();
      confetti.setMatrixAt(i, tmpObj.matrix);
    });
    confetti.instanceMatrix.needsUpdate = true;

    stars.rotation.y += dt * 0.012 * motion;
    stars.rotation.x = sy * 0.00008;

    coreUniforms.uTime.value += dt * (0.7 + current.spin * 0.3) * motion;
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
    camera.position.set(pointer.sx * 0.7 * motion, -pointer.sy * 0.45 * motion, current.z);
    camera.lookAt(0, current.y * 0.3, 0);

    // voxel icon floats in front of the glowing core
    iconGroup.position.set(
      current.x + current.ix,
      current.y + current.iy + Math.sin(time * 1.4) * 0.06 * motion,
      1.9 * current.s
    );
    iconGroup.scale.setScalar(current.s * current.is * 0.95);
    iconGroup.rotation.y = (Math.sin(time * 0.7) * 0.45 + pointer.sx * 0.4) * motion;
    iconGroup.rotation.x = (Math.sin(time * 0.5) * 0.1 - pointer.sy * 0.25) * motion;

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
    // begin icon morphs once the loader is gone
    reveal() {
      started = true;
    },
    burst: triggerBurst,
  };
}

// ---------------------------------------------------------
// PAGE UI
// ---------------------------------------------------------
function setupUI(world) {
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  // Nav background + scroll progress + active link
  const nav = document.getElementById('nav');
  const progress = document.getElementById('progress');
  const links = [...document.querySelectorAll('.nav-links a')];
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${max > 0 ? window.scrollY / max : 0})`;
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

  // 3D tilt cards
  const canHover = window.matchMedia('(hover: hover)').matches;
  if (canHover && !reduceMotion) {
    document.querySelectorAll('.tilt').forEach((card) => {
      card.addEventListener('pointerenter', () => sound.play('tick'));
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

  // Sound on/off buttons
  const soundBtns = document.querySelectorAll('[data-sound-toggle]');
  const showSound = (on) => {
    document.body.classList.toggle('sound-on', on);
    soundBtns.forEach((b) => {
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      const label = b.querySelector('.sound-label');
      if (label) label.textContent = on ? 'Sound on' : 'Sound off';
    });
  };
  sound.onChange(showSound);
  soundBtns.forEach((b) =>
    b.addEventListener('click', () => {
      sound.toggle();
      if (sound.isOn()) sound.play('sparkle');
    })
  );
  sound.init();

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
const startedAt = performance.now();
const fx = setupEffects({ words: ROTATING_WORDS });
const world = createWorld();
setupUI(world);

function hideLoader() {
  document.getElementById('loader').classList.add('done');
  document.body.classList.remove('loading');
  document.body.classList.add('ready');
  fx.start();
  if (world) world.reveal();
}

const finish = () => setTimeout(hideLoader, Math.max(0, 900 - (performance.now() - startedAt)));

if (world) {
  world.start(finish);
} else {
  document.body.classList.add('no-webgl');
  finish();
}
