// =========================================================
// Sound design. Everything is synthesised live with the
// Web Audio API: no audio files, nothing to license.
// Sound starts OFF (browsers only allow audio after a click).
// =========================================================

const STORE_KEY = 'mmi-sound';
const SA = 138.59; // the drone's tonic ("Sa"), C#3

let ctx = null;
let master;
let reverb;
let noiseBuf;
let enabled = false;
let droneTimer = null;
let nextPluck = 0;
let pluckIndex = 0;
let fireLevel = 0;
let fireRoar = null;
let fireTimer = null;
const lastPlayed = {};
const listeners = new Set();

function readPref() {
  try {
    return localStorage.getItem(STORE_KEY) === '1';
  } catch (e) {
    return false;
  }
}
function writePref(on) {
  try {
    localStorage.setItem(STORE_KEY, on ? '1' : '0');
  } catch (e) {
    /* storage blocked: fine, just not remembered */
  }
}

function setup() {
  if (ctx) return true;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return false;
  ctx = new AC();
  master = ctx.createGain();
  master.gain.value = 0;
  const comp = ctx.createDynamicsCompressor();
  master.connect(comp).connect(ctx.destination);

  // white noise used by whooshes, ticks, fire...
  noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
  const d = noiseBuf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

  // simple generated reverb (a temple-hall feel)
  reverb = ctx.createConvolver();
  const len = ctx.sampleRate * 3;
  const ir = ctx.createBuffer(2, len, ctx.sampleRate);
  for (let c = 0; c < 2; c++) {
    const ch = ir.getChannelData(c);
    for (let i = 0; i < len; i++) ch[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2);
  }
  reverb.buffer = ir;
  const wet = ctx.createGain();
  wet.gain.value = 0.35;
  reverb.connect(wet).connect(master);

  document.addEventListener('visibilitychange', () => {
    if (!ctx) return;
    if (document.hidden) ctx.suspend();
    else if (enabled) ctx.resume();
  });
  return true;
}

// ---------- building blocks ----------
function out(node, wetAmount = 0) {
  node.connect(master);
  if (wetAmount > 0) {
    const send = ctx.createGain();
    send.gain.value = wetAmount;
    node.connect(send).connect(reverb);
  }
}
function env(gainNode, t, peak, attack, decay) {
  const g = gainNode.gain;
  g.setValueAtTime(0.0001, t);
  g.exponentialRampToValueAtTime(peak, t + attack);
  g.exponentialRampToValueAtTime(0.0001, t + attack + decay);
}
function noise(t, dur) {
  const src = ctx.createBufferSource();
  src.buffer = noiseBuf;
  src.loop = true;
  src.start(t, Math.random() * 1.5);
  src.stop(t + dur + 0.05);
  return src;
}
function tone(type, freq, t, dur) {
  const o = ctx.createOscillator();
  o.type = type;
  o.frequency.setValueAtTime(freq, t);
  o.start(t);
  o.stop(t + dur + 0.05);
  return o;
}

// ---------- tanpura-style drone ----------
function pluck(freq, t) {
  const g = ctx.createGain();
  const f = ctx.createBiquadFilter();
  f.type = 'lowpass';
  f.Q.value = 3;
  f.frequency.setValueAtTime(freq * 9, t);
  f.frequency.exponentialRampToValueAtTime(freq * 2.5, t + 3);
  [1, 1.004].forEach((detune) => tone('sawtooth', freq * detune, t, 3.6).connect(f));
  f.connect(g);
  env(g, t, 0.05, 0.02, 3.5);
  out(g, 0.6);
}
function droneLoop() {
  const pattern = [SA * 0.75, SA, SA, SA * 0.5]; // Pa, Sa, Sa, low Sa
  while (nextPluck < ctx.currentTime + 1.5) {
    pluck(pattern[pluckIndex % 4], nextPluck);
    pluckIndex++;
    nextPluck += pluckIndex % 4 === 0 ? 1.6 : 1.15;
  }
}

// ---------- fire crackle + roar ----------
function fireLoop() {
  if (!enabled) return;
  if (fireRoar) fireRoar.gain.setTargetAtTime(fireLevel * 0.09, ctx.currentTime, 0.2);
  if (fireLevel < 0.05) return;
  const pops = Math.random() < fireLevel * 0.9 ? 1 + ((Math.random() * 2) | 0) : 0;
  for (let i = 0; i < pops; i++) {
    const t = ctx.currentTime + Math.random() * 0.06;
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 1200 + Math.random() * 4500;
    bp.Q.value = 2;
    const g = ctx.createGain();
    noise(t, 0.04).connect(bp).connect(g);
    env(g, t, (0.04 + Math.random() * 0.12) * fireLevel, 0.002, 0.02 + Math.random() * 0.03);
    out(g, 0.15);
  }
}
function startFireBed() {
  if (fireRoar) return;
  const lp = ctx.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 420;
  fireRoar = ctx.createGain();
  fireRoar.gain.value = 0;
  const src = ctx.createBufferSource();
  src.buffer = noiseBuf;
  src.loop = true;
  src.connect(lp).connect(fireRoar);
  out(fireRoar);
  src.start();
  fireTimer = setInterval(fireLoop, 70);
}

// ---------- one-shot sounds ----------
const PENTA = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3]; // Sa Re Ga Pa Dha

const SOUNDS = {
  // section change
  whoosh(t) {
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.Q.value = 1.4;
    bp.frequency.setValueAtTime(260, t);
    bp.frequency.exponentialRampToValueAtTime(2600, t + 0.35);
    bp.frequency.exponentialRampToValueAtTime(500, t + 0.8);
    const g = ctx.createGain();
    noise(t, 0.9).connect(bp).connect(g);
    env(g, t, 0.22, 0.25, 0.6);
    out(g, 0.3);
  },
  // soft swoosh when a heading assembles
  swoosh(t) {
    const hp = ctx.createBiquadFilter();
    hp.type = 'bandpass';
    hp.Q.value = 0.8;
    hp.frequency.setValueAtTime(3200, t);
    hp.frequency.exponentialRampToValueAtTime(900, t + 0.45);
    const g = ctx.createGain();
    noise(t, 0.5).connect(hp).connect(g);
    env(g, t, 0.07, 0.08, 0.4);
    out(g, 0.2);
  },
  // 8-bit blips as the pixel icon rebuilds
  blips(t) {
    for (let i = 0; i < 7; i++) {
      const f = SA * 4 * PENTA[(Math.random() * 5) | 0] * (i > 3 ? 2 : 1);
      const g = ctx.createGain();
      tone('square', f, t + 0.25 + i * 0.07, 0.08).connect(g);
      env(g, t + 0.25 + i * 0.07, 0.03, 0.005, 0.07);
      out(g, 0.1);
    }
  },
  // typewriter key
  type(t) {
    const hp = ctx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = 2500 + Math.random() * 2000;
    const g = ctx.createGain();
    noise(t, 0.03).connect(hp).connect(g);
    env(g, t, 0.06, 0.001, 0.025);
    out(g);
  },
  // pencil scribble for the hand-drawn circles
  scribble(t) {
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.Q.value = 6;
    bp.frequency.setValueAtTime(1800, t);
    const g = ctx.createGain();
    for (let i = 0; i < 6; i++) bp.frequency.setValueAtTime(1500 + Math.random() * 1500, t + i * 0.12);
    noise(t, 0.8).connect(bp).connect(g);
    g.gain.setValueAtTime(0.0001, t);
    for (let i = 0; i < 6; i++) {
      g.gain.exponentialRampToValueAtTime(0.05, t + i * 0.13 + 0.05);
      g.gain.exponentialRampToValueAtTime(0.008, t + i * 0.13 + 0.12);
    }
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.85);
    out(g);
  },
  // the churn: deep rumble swell
  rumble(t) {
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.value = 180;
    const g = ctx.createGain();
    noise(t, 2.4).connect(lp).connect(g);
    tone('sine', 55, t, 2.4).connect(g);
    env(g, t, 0.35, 0.9, 1.4);
    out(g, 0.4);
  },
  // flaming arrow flying in
  arrow(t) {
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.Q.value = 3;
    bp.frequency.setValueAtTime(700, t);
    bp.frequency.exponentialRampToValueAtTime(4200, t + 0.9);
    const g = ctx.createGain();
    noise(t, 1).connect(bp).connect(g);
    const w = tone('sine', 520, t, 1);
    w.frequency.exponentialRampToValueAtTime(1500, t + 0.9);
    const wg = ctx.createGain();
    w.connect(wg);
    env(wg, t, 0.05, 0.6, 0.35);
    out(wg, 0.2);
    env(g, t, 0.3, 0.75, 0.25);
    out(g, 0.3);
  },
  // arrow hits the core
  impact(t) {
    const o = tone('sine', 120, t, 1.2);
    o.frequency.exponentialRampToValueAtTime(32, t + 0.9);
    const g = ctx.createGain();
    o.connect(g);
    env(g, t, 0.75, 0.005, 1.1);
    out(g, 0.5);
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.setValueAtTime(3000, t);
    lp.frequency.exponentialRampToValueAtTime(200, t + 0.6);
    const ng = ctx.createGain();
    noise(t, 0.7).connect(lp).connect(ng);
    env(ng, t, 0.4, 0.003, 0.6);
    out(ng, 0.5);
  },
  // scissors cutting the timeline
  snip(t) {
    [0, 0.11].forEach((dt) => {
      const hp = ctx.createBiquadFilter();
      hp.type = 'highpass';
      hp.frequency.value = 4500;
      const g = ctx.createGain();
      noise(t + dt, 0.03).connect(hp).connect(g);
      env(g, t + dt, 0.28, 0.001, 0.03);
      out(g, 0.1);
      const mg = ctx.createGain();
      tone('triangle', 2600 - dt * 3000, t + dt, 0.03).connect(mg);
      env(mg, t + dt, 0.05, 0.001, 0.025);
      out(mg);
    });
  },
  // click on the background: sparkle arpeggio
  sparkle(t) {
    for (let i = 0; i < 5; i++) {
      const g = ctx.createGain();
      tone('sine', SA * 8 * PENTA[i], t + i * 0.055, 0.7).connect(g);
      env(g, t + i * 0.055, 0.06, 0.004, 0.6);
      out(g, 0.6);
    }
  },
  // card hover
  tick(t) {
    const g = ctx.createGain();
    tone('sine', 1300 + Math.random() * 200, t, 0.05).connect(g);
    env(g, t, 0.025, 0.002, 0.04);
    out(g);
  },
  // temple bell for the finale
  bell(t) {
    const base = SA * 2.4;
    [
      [1, 0.22, 4.5],
      [2.76, 0.1, 2.6],
      [5.4, 0.05, 1.6],
      [8.93, 0.03, 1],
    ].forEach(([ratio, peak, decay]) => {
      const g = ctx.createGain();
      tone('sine', base * ratio, t, decay + 0.1).connect(g);
      env(g, t, peak, 0.004, decay);
      out(g, 0.8);
    });
  },
};

const MIN_GAP = { type: 0.025, tick: 0.06, whoosh: 0.35, swoosh: 0.15, blips: 0.3, scribble: 0.4 };

function setEnabled(on) {
  enabled = on;
  writePref(on);
  if (on) {
    if (!setup()) return;
    ctx.resume();
    master.gain.setTargetAtTime(0.7, ctx.currentTime, 0.3);
    if (!droneTimer) {
      nextPluck = ctx.currentTime + 0.1;
      droneTimer = setInterval(droneLoop, 300);
      droneLoop();
    }
    startFireBed();
  } else if (ctx) {
    master.gain.setTargetAtTime(0, ctx.currentTime, 0.15);
    clearInterval(droneTimer);
    droneTimer = null;
  }
  listeners.forEach((fn) => fn(on));
}

export const sound = {
  // remembered "on" choice waits for the first click/tap (browser rule)
  init() {
    if (!readPref()) return;
    const unlock = () => {
      window.removeEventListener('pointerdown', unlock, true);
      window.removeEventListener('keydown', unlock, true);
      if (!enabled) setEnabled(true);
    };
    window.addEventListener('pointerdown', unlock, true);
    window.addEventListener('keydown', unlock, true);
    listeners.forEach((fn) => fn(true, true));
  },
  toggle() {
    setEnabled(!enabled);
  },
  isOn: () => enabled,
  onChange(fn) {
    listeners.add(fn);
  },
  play(name, delay = 0) {
    if (!enabled || !ctx || !SOUNDS[name]) return;
    const now = ctx.currentTime;
    if (MIN_GAP[name] && lastPlayed[name] && now - lastPlayed[name] < MIN_GAP[name]) return;
    lastPlayed[name] = now;
    SOUNDS[name](now + delay);
  },
  setFire(level) {
    fireLevel = level;
  },
};
