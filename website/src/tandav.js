// =========================================================
// Shiv Tandav: an original, scroll-driven scene drawn live on
// a <canvas>. A Nataraja-style silhouette dances inside a ring
// of fire (prabha mandala). Your scroll position is the timeline.
// =========================================================
import { sound } from './sound.js';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const smooth = (t) => t * t * t * (t * (t * 6 - 15) + 10);
const rad = (d) => (d * Math.PI) / 180;
const dir = (deg) => [Math.cos(rad(deg)), Math.sin(rad(deg))];

// ---------- dance poses (angles in degrees, 0 = right, 90 = down) ----------
// L = viewer's left, R = viewer's right. Arms: [upper arm, forearm]. Legs: [thigh, shin].
const POSES = [
  // 1. classic Nataraja: right leg planted, left leg swept across, fire & damru raised
  { lean: -6, aL1: [160, -95], aL2: [205, 240], aR1: [172, 125], aR2: [-18, -65], legL: [112, 78], legR: [-12, 118] },
  // 2. leap: arms thrown wide
  { lean: 9, aL1: [188, 150], aL2: [218, 262], aR1: [-8, 30], aR2: [-38, -82], legL: [122, 150], legR: [42, 100] },
  // 3. rising: arms up, leg lifted high
  { lean: -13, aL1: [228, 262], aL2: [196, 238], aR1: [-52, -82], aR2: [-20, -42], legL: [98, 86], legR: [-42, 62] },
  // 4. turn: the other leg raised
  { lean: 11, aL1: [200, 152], aL2: [236, 276], aR1: [10, -58], aR2: [-30, -76], legL: [188, 110], legR: [76, 100] },
  // 5. back to the classic pose
  { lean: -6, aL1: [160, -95], aL2: [205, 240], aR1: [172, 125], aR2: [-18, -65], legL: [112, 78], legR: [-12, 118] },
];
const POSE_AT = [0, 0.27, 0.52, 0.76, 1];
const LIMBS = ['aL1', 'aL2', 'aR1', 'aR2', 'legL', 'legR'];

function poseAt(p) {
  let i = 0;
  while (i < POSE_AT.length - 2 && p > POSE_AT[i + 1]) i++;
  const t = smooth(clamp((p - POSE_AT[i]) / (POSE_AT[i + 1] - POSE_AT[i])));
  const a = POSES[i];
  const b = POSES[i + 1];
  const out = { lean: a.lean + (b.lean - a.lean) * t };
  LIMBS.forEach((k) => {
    out[k] = [a[k][0] + (b[k][0] - a[k][0]) * t, a[k][1] + (b[k][1] - a[k][1]) * t];
  });
  // how fast we're moving between poses: drives flying hair
  out.energy = 0.45 + Math.sin(t * Math.PI) * 0.55;
  return out;
}

// ---------- painted red/purple watercolour backdrop (made once) ----------
function paintBackdrop() {
  const c = document.createElement('canvas');
  c.width = 1200;
  c.height = 760;
  const g = c.getContext('2d');
  const base = g.createRadialGradient(600, 360, 40, 600, 380, 760);
  base.addColorStop(0, '#5a0d0d');
  base.addColorStop(0.5, '#2a0610');
  base.addColorStop(1, '#0a0206');
  g.fillStyle = base;
  g.fillRect(0, 0, c.width, c.height);
  const cols = ['127,29,29', '185,28,28', '88,28,135', '194,65,12', '26,3,6', '76,5,25'];
  for (let i = 0; i < 150; i++) {
    const x = Math.random() * c.width;
    const y = Math.random() * c.height;
    const r = 50 + Math.random() * 230;
    const col = cols[(Math.random() * cols.length) | 0];
    const rg = g.createRadialGradient(x, y, 0, x, y, r);
    rg.addColorStop(0, `rgba(${col},${0.12 + Math.random() * 0.25})`);
    rg.addColorStop(0.7, `rgba(${col},${0.05 + Math.random() * 0.08})`);
    rg.addColorStop(1, `rgba(${col},0)`);
    g.fillStyle = rg;
    g.fillRect(x - r, y - r, r * 2, r * 2);
  }
  // ink splatter
  g.fillStyle = 'rgba(10,2,4,0.55)';
  for (let i = 0; i < 160; i++) {
    g.beginPath();
    g.arc(Math.random() * c.width, Math.random() * c.height, Math.random() * Math.random() * 7, 0, Math.PI * 2);
    g.fill();
  }
  // paper grain
  const img = g.getImageData(0, 0, c.width, c.height);
  for (let i = 0; i < img.data.length; i += 4) {
    const n = (Math.random() - 0.5) * 18;
    img.data[i] += n;
    img.data[i + 1] += n;
    img.data[i + 2] += n;
  }
  g.putImageData(img, 0, 0);
  return c;
}

export function setupTandav() {
  const section = document.querySelector('.tandav');
  const canvas = document.getElementById('tandavCanvas');
  if (!section || !canvas) return;
  const ctx = canvas.getContext('2d');
  const backdrop = paintBackdrop();
  let W = 0;
  let H = 0;
  let dpr = 1;
  const embers = [];
  let lastBeat = -1;
  let visible = false;
  let lastT = performance.now();

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
  }
  resize();
  window.addEventListener('resize', resize);

  function progress() {
    const r = section.getBoundingClientRect();
    return clamp(-r.top / (r.height - window.innerHeight));
  }

  // ---------- ring of fire ----------
  function drawRing(cx, cy, R, ringP, t) {
    const a0 = -Math.PI / 2;
    const a1 = a0 + Math.PI * 2 * ringP;
    if (ringP <= 0) return;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round';
    ctx.shadowColor = '#ff6a00';
    ctx.shadowBlur = R * 0.12;
    ctx.strokeStyle = 'rgba(255,110,20,0.85)';
    ctx.lineWidth = R * 0.05;
    ctx.beginPath();
    ctx.arc(cx, cy, R, a0, a1);
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = 'rgba(255,232,170,0.9)';
    ctx.lineWidth = R * 0.014;
    ctx.stroke();

    const N = 84;
    for (let k = 0; k < N; k++) {
      const a = a0 + (k / N) * Math.PI * 2;
      if (a > a1) break;
      const ca = Math.cos(a);
      const sa = Math.sin(a);
      const flick = 0.55 + 0.25 * Math.sin(t * 7 + k * 2.3) + 0.2 * Math.sin(t * 2.3 + k * 0.61) * Math.sin(k * 1.37);
      [
        [1, 0.17, 'rgba(255,80,10,0.5)', 0.06],
        [1, 0.09, 'rgba(255,205,110,0.65)', 0.035],
        [-1, 0.07, 'rgba(255,120,30,0.45)', 0.04],
      ].forEach(([side, len, col, wid]) => {
        const L = R * len * flick;
        const w = R * wid;
        const bx = cx + ca * R;
        const by = cy + sa * R;
        const sway = Math.sin(t * 5 + k * 1.7) * L * 0.35;
        const tx = bx + ca * L * side - sa * sway;
        const ty = by + sa * L * side + ca * sway;
        ctx.fillStyle = col;
        ctx.beginPath();
        ctx.moveTo(bx - sa * w, by + ca * w);
        ctx.quadraticCurveTo(bx + ca * L * 0.5 * side - sa * w, by + sa * L * 0.5 * side + ca * w, tx, ty);
        ctx.quadraticCurveTo(bx + ca * L * 0.5 * side + sa * w, by + sa * L * 0.5 * side - ca * w, bx + sa * w, by - ca * w);
        ctx.fill();
      });
    }
    ctx.restore();
  }

  // ---------- embers flying off the ring ----------
  function updateEmbers(cx, cy, R, ringP, dt, rate) {
    const a1 = Math.PI * 2 * ringP;
    for (let i = 0; i < rate; i++) {
      if (embers.length > 160 || ringP <= 0) break;
      const a = -Math.PI / 2 + Math.random() * a1;
      const sp = R * (0.25 + Math.random() * 0.5);
      embers.push({
        x: cx + Math.cos(a) * R,
        y: cy + Math.sin(a) * R,
        vx: Math.cos(a) * sp + (Math.random() - 0.5) * R * 0.2,
        vy: Math.sin(a) * sp - R * 0.25,
        life: 1,
        s: 1 + Math.random() * 2.2,
      });
    }
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (let i = embers.length - 1; i >= 0; i--) {
      const e = embers[i];
      e.life -= dt * 0.75;
      if (e.life <= 0) {
        embers.splice(i, 1);
        continue;
      }
      e.x += e.vx * dt;
      e.y += e.vy * dt;
      e.vy -= R * 0.1 * dt;
      ctx.fillStyle = `rgba(255,${(150 + e.life * 90) | 0},60,${e.life})`;
      ctx.beginPath();
      ctx.arc(e.x, e.y, e.s * (R / 300), 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  // ---------- the dancer ----------
  function drawFigure(cx, cy, S, pose, t) {
    const sway = Math.sin(t * 2.2) * 3 * pose.energy;
    const lean = pose.lean + sway;
    const td = dir(-90 + lean);
    const perp = [-td[1], td[0]];
    const pelvis = [cx + Math.sin(t * 1.6) * S * 0.02, cy + S * 0.24];
    const chest = [pelvis[0] + td[0] * S * 0.72, pelvis[1] + td[1] * S * 0.72];
    const head = [chest[0] + td[0] * S * 0.3, chest[1] + td[1] * S * 0.3];
    const off = (pt, v, k) => [pt[0] + v[0] * k, pt[1] + v[1] * k];
    const shL = off(chest, perp, -S * 0.21);
    const shR = off(chest, perp, S * 0.21);
    const hipL = off(pelvis, perp, -S * 0.13);
    const hipR = off(pelvis, perp, S * 0.13);
    const wob = (i) => Math.sin(t * 3 + i * 1.3) * 4 * pose.energy;
    const limb = (start, [u, l], len1, len2, i) => {
      const j = off(start, dir(u + wob(i)), S * len1);
      return [start, j, off(j, dir(l + wob(i + 7)), S * len2)];
    };
    const armL1 = limb(shL, pose.aL1, 0.4, 0.36, 1);
    const armL2 = limb(off(shL, td, S * 0.03), pose.aL2, 0.38, 0.34, 2);
    const armR1 = limb(shR, pose.aR1, 0.4, 0.36, 3);
    const armR2 = limb(off(shR, td, S * 0.03), pose.aR2, 0.38, 0.34, 4);
    const legL = limb(hipL, pose.legL, 0.52, 0.5, 5);
    const legR = limb(hipR, pose.legR, 0.52, 0.5, 6);

    const strokeLimb = (pts, w1, w2) => {
      ctx.lineWidth = w1;
      ctx.beginPath();
      ctx.moveTo(pts[0][0], pts[0][1]);
      ctx.lineTo(pts[1][0], pts[1][1]);
      ctx.stroke();
      ctx.lineWidth = w2;
      ctx.beginPath();
      ctx.moveTo(pts[1][0], pts[1][1]);
      ctx.lineTo(pts[2][0], pts[2][1]);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(pts[2][0], pts[2][1], w2 * 0.62, 0, Math.PI * 2);
      ctx.fill();
    };

    // flowing jata (matted hair locks), fanning out behind the head
    const rot = (v, deg) => {
      const c = Math.cos(rad(deg));
      const sn = Math.sin(rad(deg));
      return [v[0] * c - v[1] * sn, v[0] * sn + v[1] * c];
    };
    const hair = (pad) => {
      for (let side = -1; side <= 1; side += 2) {
        for (let k = 0; k < 7; k++) {
          const d = rot([perp[0] * side, perp[1] * side], (16 - k * 11) * side);
          const n = [-d[1], d[0]];
          const L = S * (0.62 + 0.09 * (k % 3)) * (0.7 + pose.energy * 0.5);
          const wave = Math.sin(t * 2.6 + k * 1.1 + side) * S * 0.1 * pose.energy;
          const wave2 = Math.sin(t * 3.3 + k * 0.7) * S * 0.16 * pose.energy;
          const w = S * 0.05 + pad * 0.5;
          const rx = head[0] + d[0] * S * 0.08;
          const ry = head[1] + d[1] * S * 0.08;
          const mx = rx + d[0] * L * 0.5 + n[0] * wave;
          const my = ry + d[1] * L * 0.5 + n[1] * wave;
          const tx = rx + d[0] * L + n[0] * wave2 + td[0] * S * 0.05;
          const ty = ry + d[1] * L + n[1] * wave2 + td[1] * S * 0.05;
          ctx.beginPath();
          ctx.moveTo(rx + n[0] * w, ry + n[1] * w);
          ctx.quadraticCurveTo(mx + n[0] * w * 0.7, my + n[1] * w * 0.7, tx, ty);
          ctx.quadraticCurveTo(mx - n[0] * w * 0.7, my - n[1] * w * 0.7, rx - n[0] * w, ry - n[1] * w);
          ctx.closePath();
          ctx.fill();
        }
      }
    };

    // damru (hourglass drum) in the upper-left hand
    const damru = (pos, d, pad) => {
      const s2 = S * 0.085 + pad * 0.4;
      const n = [-d[1], d[0]];
      const end = (k) => [pos[0] + d[0] * s2 * k, pos[1] + d[1] * s2 * k];
      const a = end(1);
      const b = end(-1);
      ctx.beginPath();
      ctx.moveTo(a[0] + n[0] * s2, a[1] + n[1] * s2);
      ctx.lineTo(pos[0] + n[0] * s2 * 0.25, pos[1] + n[1] * s2 * 0.25);
      ctx.lineTo(b[0] + n[0] * s2, b[1] + n[1] * s2);
      ctx.lineTo(b[0] - n[0] * s2, b[1] - n[1] * s2);
      ctx.lineTo(pos[0] - n[0] * s2 * 0.25, pos[1] - n[1] * s2 * 0.25);
      ctx.lineTo(a[0] - n[0] * s2, a[1] - n[1] * s2);
      ctx.closePath();
      ctx.fill();
      const ang = Math.atan2(n[1], n[0]);
      [a, b].forEach((e) => {
        ctx.beginPath();
        ctx.ellipse(e[0], e[1], s2, s2 * 0.32, ang, 0, Math.PI * 2);
        ctx.fill();
      });
    };

    const body = (rim) => {
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      const pad = rim ? S * 0.035 : 0;
      // back arms + legs
      strokeLimb(armL2, S * 0.12 + pad, S * 0.095 + pad);
      strokeLimb(armR2, S * 0.12 + pad, S * 0.095 + pad);
      strokeLimb(legL, S * 0.2 + pad, S * 0.135 + pad);
      strokeLimb(legR, S * 0.2 + pad, S * 0.135 + pad);
      // torso
      const waist = off(pelvis, td, S * 0.22);
      const wL = off(waist, perp, -S * 0.1);
      const wR = off(waist, perp, S * 0.1);
      ctx.lineWidth = S * 0.09 + pad;
      ctx.beginPath();
      ctx.moveTo(shL[0], shL[1]);
      ctx.quadraticCurveTo(chest[0] + td[0] * S * 0.05, chest[1] + td[1] * S * 0.05, shR[0], shR[1]);
      ctx.quadraticCurveTo(off(chest, perp, S * 0.2)[0] - td[0] * S * 0.2, off(chest, perp, S * 0.2)[1] - td[1] * S * 0.2, wR[0], wR[1]);
      ctx.lineTo(hipR[0], hipR[1]);
      ctx.lineTo(hipL[0], hipL[1]);
      ctx.lineTo(wL[0], wL[1]);
      ctx.quadraticCurveTo(off(chest, perp, -S * 0.2)[0] - td[0] * S * 0.2, off(chest, perp, -S * 0.2)[1] - td[1] * S * 0.2, shL[0], shL[1]);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      // flared dhoti around the hips
      const flare = S * 0.32;
      ctx.beginPath();
      ctx.moveTo(hipL[0] - perp[0] * S * 0.03, hipL[1] - perp[1] * S * 0.03);
      ctx.lineTo(hipR[0] + perp[0] * S * 0.03, hipR[1] + perp[1] * S * 0.03);
      ctx.lineTo(legR[1][0] * 0.45 + hipR[0] * 0.55 + perp[0] * S * 0.06, legR[1][1] * 0.45 + hipR[1] * 0.55 + flare * 0.1);
      ctx.lineTo(legL[1][0] * 0.45 + hipL[0] * 0.55 - perp[0] * S * 0.06, legL[1][1] * 0.45 + hipL[1] * 0.55 + flare * 0.1);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      // front arms
      strokeLimb(armL1, S * 0.13 + pad, S * 0.1 + pad);
      strokeLimb(armR1, S * 0.13 + pad, S * 0.1 + pad);
      // neck + head + topknot
      ctx.lineWidth = S * 0.09 + pad;
      ctx.beginPath();
      ctx.moveTo(chest[0], chest[1]);
      ctx.lineTo(head[0], head[1]);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(head[0], head[1], S * 0.14 + pad / 2, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(head[0] + td[0] * S * 0.2, head[1] + td[1] * S * 0.2, S * 0.08 + pad / 2, S * 0.14 + pad / 2, rad(lean), 0, Math.PI * 2);
      ctx.fill();
      hair(pad);
      const lh = armL2[2];
      damru(off(lh, dir(pose.aL2[1]), S * 0.07), dir(pose.aL2[1] + 90), pad);
    };

    // pass 1: orange rim light
    ctx.save();
    ctx.strokeStyle = 'rgba(255,140,40,0.9)';
    ctx.fillStyle = 'rgba(255,140,40,0.9)';
    ctx.shadowColor = '#ff7a1a';
    ctx.shadowBlur = S * 0.12;
    body(true);
    ctx.restore();
    // pass 2: the black silhouette
    ctx.save();
    ctx.strokeStyle = '#0b0406';
    ctx.fillStyle = '#0b0406';
    body(false);
    ctx.restore();

    // crescent moon in the hair
    ctx.save();
    const mx = head[0] + td[0] * S * 0.33 + perp[0] * S * 0.09;
    const my = head[1] + td[1] * S * 0.33 + perp[1] * S * 0.09;
    ctx.fillStyle = '#f6efdc';
    ctx.shadowColor = '#fff6dc';
    ctx.shadowBlur = S * 0.08;
    ctx.beginPath();
    // crescent drawn as two arcs (no cut-out, so nothing behind gets erased)
    const mr = S * 0.05;
    ctx.beginPath();
    ctx.arc(mx, my, mr, rad(100), rad(340));
    ctx.arc(mx + mr * 0.35, my - mr * 0.25, mr * 0.78, rad(340), rad(100), true);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // third eye
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = 'rgba(120,170,255,0.9)';
    ctx.shadowColor = '#7aa8ff';
    ctx.shadowBlur = S * 0.06;
    ctx.beginPath();
    ctx.ellipse(head[0] + td[0] * S * 0.06, head[1] + td[1] * S * 0.06, S * 0.008, S * 0.02, rad(lean), 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // flame held in the upper-right hand
    const fh = armR2[2];
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (let k = 0; k < 3; k++) {
      const fl = S * (0.2 - k * 0.05) * (0.8 + 0.2 * Math.sin(t * 9 + k));
      ctx.fillStyle = ['rgba(255,80,10,0.55)', 'rgba(255,160,40,0.6)', 'rgba(255,240,190,0.8)'][k];
      ctx.beginPath();
      ctx.moveTo(fh[0] - fl * 0.35, fh[1]);
      ctx.quadraticCurveTo(fh[0] - fl * 0.3, fh[1] - fl * 0.6, fh[0] + Math.sin(t * 6) * fl * 0.2, fh[1] - fl * 1.25);
      ctx.quadraticCurveTo(fh[0] + fl * 0.3, fh[1] - fl * 0.6, fh[0] + fl * 0.35, fh[1]);
      ctx.fill();
    }
    ctx.restore();
  }

  // ---------- frame ----------
  function frame(now) {
    const dt = Math.min(0.05, (now - lastT) / 1000);
    lastT = now;
    if (!visible) return;
    const p = reduceMotion ? 0.999 : progress();
    const t = now / 1000;
    const desktop = W >= 860;
    const R = desktop ? Math.min(W * 0.27, H * 0.38) : Math.min(W * 0.42, H * 0.27);
    const cx = desktop ? W * 0.64 : W * 0.5;
    const cy = desktop ? H * 0.5 : H * 0.36;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // backdrop with a slow Ken Burns zoom
    const z = 1.05 + p * 0.12;
    const bw = Math.max(W / backdrop.width, H / backdrop.height) * z;
    ctx.drawImage(backdrop, (W - backdrop.width * bw) / 2, (H - backdrop.height * bw) / 2 - p * H * 0.04, backdrop.width * bw, backdrop.height * bw);
    // glow behind the ring
    const glow = ctx.createRadialGradient(cx, cy, R * 0.2, cx, cy, R * 1.6);
    glow.addColorStop(0, `rgba(255,120,40,${0.18 + p * 0.12})`);
    glow.addColorStop(1, 'rgba(255,120,40,0)');
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, W, H);

    const ringP = reduceMotion ? 1 : clamp(p / 0.22);
    drawRing(cx, cy, R, ringP, t);
    updateEmbers(cx, cy, R, ringP, dt, reduceMotion ? 0 : 2);
    drawFigure(cx, cy, R * 0.82, poseAt(p), t);

    // stage the text + damru beats
    const stage = p < 0.04 ? 0 : p < 0.4 ? 1 : p < 0.7 ? 2 : 3;
    if (section.dataset.stage !== String(stage)) section.dataset.stage = stage;
    const beat = Math.floor(p * 22);
    if (beat !== lastBeat) {
      if (lastBeat !== -1 && p > 0.01 && p < 0.99) sound.play('damru');
      lastBeat = beat;
    }
    requestAnimationFrame(frame);
  }

  new IntersectionObserver((entries) => {
    const was = visible;
    visible = entries[0].isIntersecting;
    if (visible && !was) {
      lastT = performance.now();
      requestAnimationFrame(frame);
    }
  }).observe(section);
}
