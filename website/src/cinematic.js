// =========================================================
// Painterly / cinematic 3D pieces:
//  - a watercolour ink-smoke sky behind everything
//  - a ring of fire with flying embers
//  - a flaming arrow with a fire trail
// =========================================================
import * as THREE from 'three';

// ---------------------------------------------------------
// Watercolour ink-smoke sky (full-screen shader)
// ---------------------------------------------------------
export function createSky(octaves) {
  const uniforms = {
    uTime: { value: 0 },
    uAmount: { value: 0.3 },
    uColA: { value: new THREE.Color('#3b1d5c') },
    uColB: { value: new THREE.Color('#ff9933') },
    uBg: { value: new THREE.Color('#07070d') },
    uAspect: { value: window.innerWidth / window.innerHeight },
    uScroll: { value: 0 },
    // background video (Nachiket's Tandav), drawn under the smoke
    uVideo: { value: null },
    uHasVideo: { value: 0 },
    uVideoAspect: { value: 9 / 16 },
    uVideoX: { value: 0.5 },
    uVideoZoom: { value: 1 },
    uVideoDim: { value: 0.9 },
    uVideoY: { value: 0 },
  };
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(2, 2),
    new THREE.ShaderMaterial({
      uniforms,
      defines: { OCT: octaves },
      depthTest: false,
      depthWrite: false,
      vertexShader: /* glsl */ `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.9999, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        uniform float uTime;
        uniform float uAmount;
        uniform vec3 uColA;
        uniform vec3 uColB;
        uniform vec3 uBg;
        uniform float uAspect;
        uniform float uScroll;
        uniform sampler2D uVideo;
        uniform float uHasVideo;
        uniform float uVideoAspect;
        uniform float uVideoX;
        uniform float uVideoZoom;
        uniform float uVideoDim;
        uniform float uVideoY;
        varying vec2 vUv;

        float hash(vec2 p) {
          p = fract(p * vec2(123.34, 456.21));
          p += dot(p, p + 45.32);
          return fract(p.x * p.y);
        }
        float noise(vec2 p) {
          vec2 i = floor(p);
          vec2 f = fract(p);
          vec2 u = f * f * (3.0 - 2.0 * f);
          return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
                     mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
        }
        float fbm(vec2 p) {
          float v = 0.0;
          float a = 0.5;
          for (int i = 0; i < OCT; i++) {
            v += a * noise(p);
            p = p * 2.03 + vec2(1.7, 9.2);
            a *= 0.5;
          }
          return v;
        }
        void main() {
          vec2 p = (vUv - 0.5) * vec2(uAspect, 1.0) * 2.4;
          p.y -= uScroll;
          float t = uTime * 0.05;
          // domain warping = slowly curling ink smoke
          vec2 q = vec2(fbm(p + vec2(0.0, t)), fbm(p + vec2(5.2, 1.3) - t));
          vec2 r = vec2(fbm(p + 2.6 * q + vec2(1.7, 9.2) + t * 1.3),
                        fbm(p + 2.6 * q + vec2(8.3, 2.8) - t * 0.9));
          float f = fbm(p + 2.4 * r);

          // the video: full height, centred on uVideoX (cropped at the sides on phones)
          vec3 base = uBg;
          if (uHasVideo > 0.5) {
            float vu = (vUv.x - uVideoX) * uAspect / uVideoAspect / uVideoZoom + 0.5;
            float vv = (vUv.y - 0.5 + uVideoY) / uVideoZoom + 0.5;
            float inside = smoothstep(0.0, 0.06, vu) * smoothstep(1.0, 0.94, vu) * step(0.0, vv) * step(vv, 1.0);
            vec3 vid = texture2D(uVideo, vec2(clamp(vu, 0.0, 1.0), clamp(vv, 0.0, 1.0))).rgb;
            base = mix(uBg, max(uBg, vid * uVideoDim), inside);
          }

          float ink = smoothstep(0.38, 0.85, f);
          vec3 col = mix(base, uColA, ink);
          col = mix(col, uColB, smoothstep(0.55, 0.95, f) * clamp(length(r), 0.0, 1.0) * 0.9);
          // watercolour: pigment pools at the edges of each wash
          float edge = 1.0 - smoothstep(0.0, 0.035, abs(f - 0.5));
          col = mix(col, uColA * 0.45, edge * 0.35);

          float vig = smoothstep(1.25, 0.35, length((vUv - 0.5) * vec2(uAspect, 1.0)));
          col = mix(base, col, uAmount * (0.55 + 0.45 * vig) * (uHasVideo > 0.5 ? 0.42 : 1.0));
          col += (hash(vUv * 1000.0 + fract(uTime * 0.37)) - 0.5) * 0.012; // paper grain
          gl_FragColor = vec4(col, 1.0);
        }
      `,
    })
  );
  mesh.frustumCulled = false;
  mesh.renderOrder = -1000;
  return { mesh, uniforms };
}

// ---------------------------------------------------------
// Shared flame colouring for point sprites
// ---------------------------------------------------------
const FLAME_FRAG = /* glsl */ `
  uniform float uIntensity;
  varying float vLife;
  varying float vEmber;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    float a = smoothstep(0.5, 0.0, d);
    vec3 hot = vec3(1.0, 0.95, 0.72);
    vec3 mid = vec3(1.0, 0.48, 0.07);
    vec3 cool = vec3(0.75, 0.08, 0.02);
    vec3 col = vLife < 0.35 ? mix(hot, mid, vLife / 0.35) : mix(mid, cool, (vLife - 0.35) / 0.65);
    if (vEmber > 0.5) { col = vec3(1.0, 0.72, 0.32); a = a * 1.5; }
    float alpha = a * (1.0 - vLife) * uIntensity;
    gl_FragColor = vec4(col * 0.9, alpha * 0.75);
  }
`;

// ---------------------------------------------------------
// Ring of fire (GPU-animated particles)
// ---------------------------------------------------------
export function createFireRing(count, radius) {
  const geo = new THREE.BufferGeometry();
  const angle = new Float32Array(count);
  const seed = new Float32Array(count);
  const speed = new Float32Array(count);
  const ember = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    angle[i] = Math.random() * Math.PI * 2;
    seed[i] = Math.random();
    ember[i] = Math.random() < 0.12 ? 1 : 0;
    speed[i] = ember[i] ? 0.25 + Math.random() * 0.3 : 0.6 + Math.random() * 0.9;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  geo.setAttribute('aAngle', new THREE.BufferAttribute(angle, 1));
  geo.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  geo.setAttribute('aSpeed', new THREE.BufferAttribute(speed, 1));
  geo.setAttribute('aEmber', new THREE.BufferAttribute(ember, 1));
  const uniforms = {
    uTime: { value: 0 },
    uIntensity: { value: 0 },
    uRadius: { value: radius },
    uScale: { value: 400 },
  };
  const points = new THREE.Points(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexShader: /* glsl */ `
        attribute float aAngle;
        attribute float aSeed;
        attribute float aSpeed;
        attribute float aEmber;
        uniform float uTime;
        uniform float uIntensity;
        uniform float uRadius;
        uniform float uScale;
        varying float vLife;
        varying float vEmber;
        void main() {
          float life = fract(uTime * aSpeed + aSeed);
          float rise = aEmber > 0.5 ? life * 1.9 : life * 0.6 * (0.5 + aSeed);
          float th = aAngle + sin(life * 5.0 + aSeed * 40.0) * 0.05;
          float r = uRadius + rise + sin(aAngle * 7.0 + uTime * 3.0) * 0.05;
          vec3 pos = vec3(cos(th) * r, sin(th) * r, (aSeed - 0.5) * 0.4);
          vec4 mv = modelViewMatrix * vec4(pos, 1.0);
          float size = aEmber > 0.5 ? 0.045 : 0.24 * (1.0 - life * 0.7) * (0.6 + aSeed * 0.8);
          gl_PointSize = size * uScale / -mv.z * uIntensity;
          gl_Position = projectionMatrix * mv;
          vLife = life;
          vEmber = aEmber;
        }
      `,
      fragmentShader: FLAME_FRAG,
    })
  );
  points.frustumCulled = false;
  return { points, uniforms };
}

// ---------------------------------------------------------
// Flaming arrow + fire trail (CPU particles)
// ---------------------------------------------------------
export function createArrow(trailCount) {
  const arrow = new THREE.Group();
  const dark = new THREE.MeshBasicMaterial({ color: '#2a1a10' });
  const glow = new THREE.MeshBasicMaterial({ color: new THREE.Color('#ffcf73').multiplyScalar(2.2) });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.5, 6).rotateX(Math.PI / 2), dark);
  const head = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.26, 8).rotateX(Math.PI / 2), glow);
  head.position.z = 0.86;
  arrow.add(shaft, head);
  for (let i = 0; i < 3; i++) {
    const fin = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 0.24), new THREE.MeshBasicMaterial({ color: '#ff9933', side: THREE.DoubleSide }));
    fin.position.z = -0.66;
    fin.rotation.set(Math.PI / 2, 0, (i * Math.PI * 2) / 3);
    fin.translateY(0.07);
    arrow.add(fin);
  }
  arrow.visible = false;

  const pos = new Float32Array(trailCount * 3);
  const life = new Float32Array(trailCount).fill(1);
  const vel = new Float32Array(trailCount * 3);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('aLife', new THREE.BufferAttribute(life, 1));
  const uniforms = { uIntensity: { value: 1 }, uScale: { value: 400 } };
  const trail = new THREE.Points(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexShader: /* glsl */ `
        attribute float aLife;
        uniform float uScale;
        varying float vLife;
        varying float vEmber;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = 0.26 * (1.0 - aLife * 0.6) * uScale / -mv.z * step(aLife, 0.999);
          gl_Position = projectionMatrix * mv;
          vLife = aLife;
          vEmber = 0.0;
        }
      `,
      fragmentShader: FLAME_FRAG,
    })
  );
  trail.frustumCulled = false;

  let next = 0;
  function emit(at, back, n) {
    for (let k = 0; k < n; k++) {
      const i = next;
      next = (next + 1) % trailCount;
      pos[i * 3] = at.x + (Math.random() - 0.5) * 0.08;
      pos[i * 3 + 1] = at.y + (Math.random() - 0.5) * 0.08;
      pos[i * 3 + 2] = at.z + (Math.random() - 0.5) * 0.08;
      vel[i * 3] = back.x * 0.6 + (Math.random() - 0.5) * 0.5;
      vel[i * 3 + 1] = back.y * 0.6 + Math.random() * 0.6;
      vel[i * 3 + 2] = back.z * 0.6 + (Math.random() - 0.5) * 0.5;
      life[i] = Math.random() * 0.15;
    }
  }
  function update(dt) {
    for (let i = 0; i < trailCount; i++) {
      if (life[i] >= 1) continue;
      life[i] = Math.min(1, life[i] + dt * 1.7);
      pos[i * 3] += vel[i * 3] * dt;
      pos[i * 3 + 1] += vel[i * 3 + 1] * dt;
      pos[i * 3 + 2] += vel[i * 3 + 2] * dt;
    }
    geo.attributes.position.needsUpdate = true;
    geo.attributes.aLife.needsUpdate = true;
  }
  return { arrow, trail, uniforms, emit, update };
}
