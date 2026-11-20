// Strata Test Drive — Road Props
// Speed bumps / humps / cushions / tables, stop signs, freeway guide signs,
// overhead + cantilever gantries, DMS boards — all procedural (tiny download),
// each with collision data and a physics helper (PropsWorld).
//
// Conventions
//  - Meters. Y is up. Every prop's origin sits on the road surface (y = 0).
//  - Signs face +Z (drivers approaching from +Z, driving toward -Z).
//  - Traffic bumps: travel direction is along Z, width along X.
//
// Collision data lives in obj.userData.strata:
//   surface   : { heightFn(lx, lz) -> local height, halfX, halfZ }  (drivable bumps)
//   obstacles : [{ type:'circle', x, z, r, breakaway }  |  { type:'box', x, z, hx, hz, rot }]
// PropsWorld turns those into world-space queries for any car physics.

import * as THREE from './three-shim.js';

// ---------------------------------------------------------------- utils
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

const cache = new Map();
const once = (key, make) => { if (!cache.has(key)) cache.set(key, make()); return cache.get(key); };
// Sign art / painted materials: LRU so editing text over and over doesn't pile up textures.
const artCache = new Map(); const ART_MAX = 220;
function art(key, make) {
  if (artCache.has(key)) { const v = artCache.get(key); artCache.delete(key); artCache.set(key, v); return v; }
  const v = make(); artCache.set(key, v);
  while (artCache.size > ART_MAX) { const [k, old] = artCache.entries().next().value; artCache.delete(k); (old.tex || old).dispose?.(); old.map?.dispose?.(); }
  return v;
}

const FONT = '"Overpass","Roboto Condensed","Arial Narrow","Helvetica Neue",Arial,sans-serif';
const CAP = 0.72; // cap-height / font-size for the font stack above

function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; }
function tex(c, { srgb = true, repeat = false } = {}) {
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}
function grain(ctx, w, h, amt, seed = 1) {
  const r = rng(seed), img = ctx.getImageData(0, 0, w, h), d = img.data;
  for (let i = 0; i < d.length; i += 4) { const n = (r() - 0.5) * amt; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  ctx.putImageData(img, 0, 0);
}

// Sign faces get an emissive copy of their art so you can fake retroreflection at night.
const signMats = new Set();
let retro = 0;
export function setRetroreflectivity(v) { retro = v; for (const m of signMats) m.emissiveIntensity = v; }

function faceMat(map) {
  const m = new THREE.MeshStandardMaterial({ map, roughness: 0.5, metalness: 0.0, emissive: 0xffffff, emissiveMap: map, emissiveIntensity: retro, polygonOffset: true, polygonOffsetFactor: -1 });
  signMats.add(m); return m;
}

// ---------------------------------------------------------------- shared materials
const M = {
  get alu() { return once('alu', () => { const [c, x] = canvas(128, 128); x.fillStyle = '#a9adb1'; x.fillRect(0, 0, 128, 128); grain(x, 128, 128, 18, 7); return new THREE.MeshStandardMaterial({ map: tex(c), roughness: 0.45, metalness: 0.75, polygonOffset: true, polygonOffsetFactor: -1 }); }); },
  get edge() { return once('edge', () => new THREE.MeshStandardMaterial({ color: 0x9a9ea3, roughness: 0.4, metalness: 0.8 })); },
  get galv() { return once('galv', () => new THREE.MeshStandardMaterial({ color: 0x9fa4a6, roughness: 0.42, metalness: 0.85 })); },
  get steel() { return once('steel', () => new THREE.MeshStandardMaterial({ color: 0x8c9196, roughness: 0.5, metalness: 0.8 })); },
  get concrete() { return once('concrete', () => { const [c, x] = canvas(128, 128); x.fillStyle = '#b4b1aa'; x.fillRect(0, 0, 128, 128); grain(x, 128, 128, 30, 3); return new THREE.MeshStandardMaterial({ map: tex(c, { repeat: true }), roughness: 0.92 }); }); },
  get bolt() { return once('bolt', () => new THREE.MeshStandardMaterial({ color: 0x55585b, roughness: 0.35, metalness: 0.9 })); },
  get rubberBlack() { return once('rb', () => new THREE.MeshStandardMaterial({ map: rubberTex('#1b1b1c', 11), bumpMap: ribTex(), bumpScale: 1.5, roughness: 0.9 })); },
  get rubberYellow() { return once('ry', () => new THREE.MeshStandardMaterial({ map: rubberTex('#e3b414', 12), bumpMap: ribTex(), bumpScale: 1.5, roughness: 0.75 })); },
  get reflector() { return once('refl', () => new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.15, metalness: 0.2, emissive: 0xffffff, emissiveIntensity: 0.08 })); },
  get perfPost() {
    return once('post', () => {
      const [c, x] = canvas(32, 128);
      x.fillStyle = '#a3a8aa'; x.fillRect(0, 0, 32, 128); grain(x, 32, 128, 22, 5);
      const [a, ax] = canvas(32, 128); ax.fillStyle = '#fff'; ax.fillRect(0, 0, 32, 128); ax.fillStyle = '#000';
      for (let i = 0; i < 4; i++) { ax.beginPath(); ax.arc(16, i * 32 + 16, 5.5, 0, Math.PI * 2); ax.fill(); }
      const am = tex(a, { srgb: false, repeat: true }), cm = tex(c, { repeat: true });
      return new THREE.MeshStandardMaterial({ map: cm, alphaMap: am, alphaTest: 0.5, roughness: 0.45, metalness: 0.8, side: THREE.DoubleSide });
    });
  },
};

function rubberTex(col, seed) { const [c, x] = canvas(128, 128); x.fillStyle = col; x.fillRect(0, 0, 128, 128); grain(x, 128, 128, 26, seed); return tex(c, { repeat: true }); }
function ribTex() { return once('rib', () => { const [c, x] = canvas(64, 64); for (let i = 0; i < 64; i++) { const v = 128 + 90 * Math.sin(i / 64 * Math.PI * 2 * 6); x.fillStyle = `rgb(${v},${v},${v})`; x.fillRect(i, 0, 1, 64); } return tex(c, { srgb: false, repeat: true }); }); }

function asphaltCanvas(w, h, seed = 2) {
  const [c, x] = canvas(w, h);
  x.fillStyle = '#3b3b3d'; x.fillRect(0, 0, w, h);
  const r = rng(seed), img = x.getImageData(0, 0, w, h), d = img.data;
  for (let i = 0; i < d.length; i += 4) { const n = (r() - 0.5) * 34 + (r() < 0.04 ? 40 : 0); d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  x.putImageData(img, 0, 0); return [c, x];
}

// ---------------------------------------------------------------- geometry helpers
// Heightfield over a local XZ rectangle, y = fn(x,z), closed with a skirt so it sits on any road.
function heightfield(fn, x0, x1, z0, z1, nx, nz, lift = 0.004) {
  const pos = [], uv = [], idx = [];
  for (let j = 0; j <= nz; j++) for (let i = 0; i <= nx; i++) {
    const x = x0 + (x1 - x0) * i / nx, z = z0 + (z1 - z0) * j / nz;
    pos.push(x, fn(x, z) + lift, z); uv.push(i / nx, 1 - j / nz);
  }
  const at = (i, j) => j * (nx + 1) + i;
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const a = at(i, j), b = at(i + 1, j), c = at(i, j + 1), d = at(i + 1, j + 1);
    idx.push(a, c, b, b, c, d);
  }
  // skirt
  const ring = [];
  for (let i = 0; i <= nx; i++) ring.push(at(i, 0));
  for (let j = 1; j <= nz; j++) ring.push(at(nx, j));
  for (let i = nx - 1; i >= 0; i--) ring.push(at(i, nz));
  for (let j = nz - 1; j >= 1; j--) ring.push(at(0, j));
  const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
  for (let k = 0; k < ring.length; k++) {
    const p = ring[k], q = ring[(k + 1) % ring.length];
    const px = pos[p * 3], pz = pos[p * 3 + 2], qx = pos[q * 3], qz = pos[q * 3 + 2];
    const base = pos.length / 3;
    pos.push(px, pos[p * 3 + 1], pz, px, -0.01, pz, qx, -0.01, qz, qx, pos[q * 3 + 1], qz);
    uv.push(0, 0.02, 0, 0, 0.02, 0, 0.02, 0.02);
    // orient outward
    const ex = qx - px, ez = qz - pz; const nx2 = ez, nz2 = -ex; // candidate normal
    const out = (nx2 * ((px + qx) / 2 - cx) + nz2 * ((pz + qz) / 2 - cz)) > 0;
    if (out) idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
    else idx.push(base, base + 2, base + 1, base, base + 3, base + 2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}

function mesh(geo, mat, { cast = true, receive = true } = {}) { const m = new THREE.Mesh(geo, mat); m.castShadow = cast; m.receiveShadow = receive; return m; }

// Batches many cylinders (truss members, rails) into one InstancedMesh.
class TubeBatch {
  constructor() { this.items = new Map(); }
  add(a, b, r) { const k = r.toFixed(3); if (!this.items.has(k)) this.items.set(k, []); this.items.get(k).push([a.clone(), b.clone()]); }
  build(mat) {
    const g = new THREE.Group(), up = new THREE.Vector3(0, 1, 0), m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), d = new THREE.Vector3(), c = new THREE.Vector3();
    for (const [k, list] of this.items) {
      const r = parseFloat(k), geo = new THREE.CylinderGeometry(1, 1, 1, 5, 1, true);
      const im = new THREE.InstancedMesh(geo, mat, list.length); im.castShadow = true; im.receiveShadow = true;
      list.forEach(([a, b], i) => { d.subVectors(b, a); const L = d.length(); q.setFromUnitVectors(up, d.normalize()); c.addVectors(a, b).multiplyScalar(0.5); s.set(r, L, r); m4.compose(c, q, s); im.setMatrixAt(i, m4); });
      im.computeBoundingSphere(); g.add(im);
    }
    return g;
  }
}
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------------------------------------------------------------- SHAPES
function roundRect(w, h, r) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s;
}
function octagon(w) { const R = (w / 2) / Math.cos(Math.PI / 8), s = new THREE.Shape(); for (let k = 0; k < 8; k++) { const a = Math.PI / 8 + k * Math.PI / 4; const p = [R * Math.cos(a), R * Math.sin(a)]; k ? s.lineTo(...p) : s.moveTo(...p); } s.closePath(); return s; }

// Sign blank: art on front, brushed aluminum back, rolled edge.
function signPanel(shape, w, h, art, { thickness = 0.004, stiffeners = 0 } = {}) {
  const g = new THREE.Group();
  const front = new THREE.ShapeGeometry(shape, 6), uv = front.attributes.uv, p = front.attributes.position;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, p.getX(i) / w + 0.5, p.getY(i) / h + 0.5);
  front.translate(0, 0, thickness / 2 + 0.0005);
  g.add(mesh(front, faceMat(art)));
  const back = new THREE.ShapeGeometry(shape, 6); back.rotateY(Math.PI); back.translate(0, 0, -thickness / 2 - 0.0005);
  const bu = back.attributes.uv; for (let i = 0; i < bu.count; i++) bu.setXY(i, bu.getX(i) * 0.5, bu.getY(i) * 0.5);
  g.add(mesh(back, M.alu));
  const edge = new THREE.ExtrudeGeometry(shape, { depth: thickness, bevelEnabled: false, curveSegments: 6 }); edge.translate(0, 0, -thickness / 2);
  g.add(mesh(edge, M.edge));
  // horizontal Z-bar stiffeners on big signs
  for (let i = 0; i < stiffeners; i++) {
    const y = -h / 2 + h * (i + 0.5) / stiffeners;
    const bar = mesh(new THREE.BoxGeometry(w * 0.96, 0.08, 0.05), M.alu); bar.position.set(0, y, -thickness / 2 - 0.025); g.add(bar);
  }
  return g;
}

// ---------------------------------------------------------------- shields & arrows (canvas)
function shieldPath(ctx, type, x, y, s) {
  ctx.beginPath();
  if (type === 'I') {
    const P = (u, v) => [x + u * s, y + v * s];
    ctx.moveTo(...P(0.07, 0.1)); ctx.quadraticCurveTo(...P(0.28, 0.0), ...P(0.5, 0.1)); ctx.quadraticCurveTo(...P(0.72, 0.0), ...P(0.93, 0.1));
    ctx.bezierCurveTo(...P(1.03, 0.45), ...P(0.86, 0.78), ...P(0.5, 0.98)); ctx.bezierCurveTo(...P(0.14, 0.78), ...P(-0.03, 0.45), ...P(0.07, 0.1));
  } else if (type === 'US') {
    const P = (u, v) => [x + u * s, y + v * s];
    ctx.moveTo(...P(0.14, 0.08)); ctx.quadraticCurveTo(...P(0.3, 0.14), ...P(0.5, 0.06)); ctx.quadraticCurveTo(...P(0.7, 0.14), ...P(0.86, 0.08));
    ctx.quadraticCurveTo(...P(0.97, 0.35), ...P(0.88, 0.58)); ctx.quadraticCurveTo(...P(0.75, 0.84), ...P(0.5, 0.94));
    ctx.quadraticCurveTo(...P(0.25, 0.84), ...P(0.12, 0.58)); ctx.quadraticCurveTo(...P(0.03, 0.35), ...P(0.14, 0.08));
  } else { // Michigan M-route diamond
    ctx.moveTo(x + s * 0.5, y + s * 0.05); ctx.lineTo(x + s * 0.95, y + s * 0.5); ctx.lineTo(x + s * 0.5, y + s * 0.95); ctx.lineTo(x + s * 0.05, y + s * 0.5);
  }
  ctx.closePath();
}
function fitText(ctx, text, cx, cy, capPx, maxW, color, align = 'center') {
  ctx.font = `700 ${capPx / CAP}px ${FONT}`; ctx.fillStyle = color; ctx.textBaseline = 'alphabetic';
  const w = ctx.measureText(text).width, sx = Math.min(1, maxW / w);
  ctx.save(); ctx.translate(cx, cy + capPx / 2); ctx.scale(sx, 1); ctx.textAlign = align; ctx.fillText(text, 0, 0); ctx.restore();
  return w * sx;
}
function drawShield(ctx, type, num, x, y, s) {
  num = String(num);
  if (type === 'I') {
    ctx.save(); shieldPath(ctx, 'I', x, y, s); ctx.fillStyle = '#fff'; ctx.fill(); ctx.clip();
    const i = s * 0.05; shieldPath(ctx, 'I', x + i, y + i, s - 2 * i); ctx.fillStyle = '#003f87'; ctx.fill();
    ctx.save(); shieldPath(ctx, 'I', x + i, y + i, s - 2 * i); ctx.clip(); ctx.fillStyle = '#c8102e'; ctx.fillRect(x, y, s, s * 0.27); ctx.fillStyle = '#fff'; ctx.fillRect(x, y + s * 0.27, s, s * 0.025); ctx.restore();
    fitText(ctx, 'INTERSTATE', x + s / 2, y + s * 0.175, s * 0.075, s * 0.62, '#fff');
    fitText(ctx, num, x + s / 2, y + s * 0.56, s * 0.36, s * 0.72, '#fff');
    ctx.restore();
  } else if (type === 'US') {
    ctx.fillStyle = '#111'; ctx.fillRect(x, y, s, s);
    shieldPath(ctx, 'US', x, y, s); ctx.fillStyle = '#fff'; ctx.fill();
    fitText(ctx, num, x + s / 2, y + s * 0.48, s * 0.38, s * 0.66, '#111');
  } else {
    ctx.fillStyle = '#111'; ctx.fillRect(x, y, s, s);
    shieldPath(ctx, 'M', x, y, s); ctx.fillStyle = '#fff'; ctx.fill();
    fitText(ctx, 'M', x + s / 2, y + s * 0.3, s * 0.13, s * 0.3, '#111');
    fitText(ctx, num, x + s / 2, y + s * 0.55, s * 0.24, s * 0.48, '#111');
  }
}
// arrow pointing "up" in its own frame, rotated by angle (radians, clockwise on canvas)
function drawArrow(ctx, cx, cy, size, angle, color) {
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(angle); ctx.fillStyle = color; ctx.beginPath();
  const s = size, sw = s * 0.11;
  ctx.moveTo(0, -s / 2); ctx.lineTo(s * 0.3, -s * 0.12); ctx.lineTo(sw, -s * 0.12); ctx.lineTo(sw, s / 2);
  ctx.lineTo(-sw, s / 2); ctx.lineTo(-sw, -s * 0.12); ctx.lineTo(-s * 0.3, -s * 0.12); ctx.closePath(); ctx.fill(); ctx.restore();
}

// ================================================================= SPEED BUMPS
function bumpObject(name, fn, halfX, halfZ, parts) {
  const g = new THREE.Group(); g.name = name; parts.forEach(p => g.add(p));
  g.userData.strata = { kind: 'surface', surface: { heightFn: fn, halfX, halfZ } };
  return g;
}

/** Bolt-down rubber speed bump (parking lots, drive-throughs). ~2 in tall, 14 in deep,
 *  modular 0.5 m black/yellow segments with glass-bead reflectors and rounded end caps. */
export function createRubberSpeedBump({ length = 3.5, height = 0.057, depth = 0.33, segment = 0.5 } = {}) {
  const half = length / 2, hd = depth / 2;
  const fn = (x, z) => {
    const t = Math.abs(z) / hd, ax = Math.abs(x);
    if (t >= 1 || ax >= half) return 0;
    const prof = 0.12 + 0.88 * smooth(1, 0.28, t);              // small leading lip then crowned top
    const end = 0.3 + 0.7 * smooth(half, half - 0.16, ax);       // rounded end caps
    return height * prof * end;
  };
  const parts = [];
  const n = Math.max(1, Math.round(length / segment)), seg = length / n;
  for (let i = 0; i < n; i++) {
    const x0 = -half + i * seg, x1 = x0 + seg;
    const geo = heightfield(fn, x0, x1, -hd, hd, 6, 16, 0.002);
    const uv = geo.attributes.uv; for (let k = 0; k < uv.count; k++) uv.setX(k, uv.getX(k) * 4);
    const yellow = i % 2 === 1;
    parts.push(mesh(geo, yellow ? M.rubberYellow : M.rubberBlack));
    // lag bolts in recessed holes
    for (const bx of [x0 + seg * 0.5]) {
      const b = mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.006, 10), M.bolt); b.position.set(bx, fn(bx, 0) + 0.001, 0); parts.push(b);
      const w = mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.003, 12), M.bolt); w.position.set(bx, fn(bx, 0) - 0.001, 0); parts.push(w);
    }
    // reflectors on both slopes of yellow segments
    if (yellow) for (const sz of [-1, 1]) {
      const z = sz * hd * 0.58, xm = (x0 + x1) / 2, y = fn(xm, z), slope = (fn(xm, z + 0.01) - fn(xm, z - 0.01)) / 0.02;
      const r = mesh(new THREE.BoxGeometry(seg * 0.5, 0.004, 0.03), M.reflector, { cast: false });
      r.position.set(xm, y + 0.003, z); r.rotation.x = -Math.atan(slope) * (1); parts.push(r);
    }
  }
  return bumpObject('RubberSpeedBump', fn, half, hd, parts);
}

function paintedAsphalt(key, W, L, paint) {
  return art(key, () => {
    const pxm = 72, w = Math.min(1024, Math.ceil(W * pxm)), h = Math.min(512, Math.ceil(L * pxm));
    const [c, x] = asphaltCanvas(w, h, 9);
    x.save(); x.scale(w / W, h / L); paint(x); x.restore(); grain(x, w, h, 10, 4);
    return new THREE.MeshStandardMaterial({ map: tex(c), roughness: 0.93 });
  });
}

/** Residential asphalt speed hump: 12–14 ft long, ~3.5 in tall, parabolic, with white chevrons. */
export function createSpeedHump({ width = 7.2, length = 3.8, height = 0.085, taper = 0.6, lanes = 2 } = {}) {
  const hx = width / 2, hz = length / 2;
  const fn = (x, z) => { const t = z / hz; if (Math.abs(t) >= 1 || Math.abs(x) >= hx) return 0; return height * (1 - t * t) * smooth(hx, hx - taper, Math.abs(x)); };
  const mat = paintedAsphalt(`hump${width}${length}${lanes}`, width, length, (x) => {
    x.fillStyle = 'rgba(240,240,236,0.93)';
    const lw = width / lanes;
    for (let l = 0; l < lanes; l++) {
      // canvas y grows toward +Z; lanes on +X travel toward -Z, so their chevrons point up the canvas.
      const dir = (l >= lanes / 2) ? -1 : 1, cx = lw * (l + 0.5);
      for (const off of [-0.32, 0.32]) {
        const base = length / 2 + off * length * 0.9 - dir * 0.35, tip = base + dir * 0.7, w2 = lw * 0.36, t = 0.3;
        x.beginPath(); x.moveTo(cx - w2, base); x.lineTo(cx, tip); x.lineTo(cx + w2, base); x.lineTo(cx + w2, base + dir * t); x.lineTo(cx, tip + dir * t); x.lineTo(cx - w2, base + dir * t); x.closePath(); x.fill();
      }
    }
  });
  const geo = heightfield(fn, -hx, hx, -hz, hz, 40, 24);
  return bumpObject('SpeedHump', fn, hx, hz, [mesh(geo, mat)]);
}

/** Speed table / raised crosswalk: ramps + 10 ft flat top. */
export function createSpeedTable({ width = 7.2, top = 3.0, ramp = 1.8, height = 0.085, taper = 0.6, crosswalk = true } = {}) {
  const hx = width / 2, hz = top / 2 + ramp;
  const fn = (x, z) => { const a = Math.abs(z); if (a >= hz || Math.abs(x) >= hx) return 0; const p = a <= top / 2 ? 1 : 0.5 + 0.5 * Math.cos(Math.PI * (a - top / 2) / ramp); return height * p * smooth(hx, hx - taper, Math.abs(x)); };
  const L = hz * 2;
  const mat = paintedAsphalt(`table${width}${top}${ramp}${crosswalk}`, width, L, (x) => {
    x.fillStyle = 'rgba(240,240,236,0.93)';
    // shark teeth on each ramp
    const n = Math.floor(width / 0.9);
    for (let i = 0; i < n; i++) { const cx = (i + 0.5) * width / n; for (const [y0, d] of [[0.2, 1], [L - 0.2, -1]]) { x.beginPath(); x.moveTo(cx - 0.3, y0); x.lineTo(cx + 0.3, y0); x.lineTo(cx, y0 + d * 0.9); x.closePath(); x.fill(); } }
    if (crosswalk) { // continental crosswalk bars across the flat top
      for (let xx = 0.3; xx < width - 0.3; xx += 1.2) x.fillRect(xx, ramp + 0.15, 0.6, top - 0.3);
    }
  });
  const geo = heightfield(fn, -hx, hx, -hz, hz, 40, 32);
  return bumpObject('SpeedTable', fn, hx, hz, [mesh(geo, mat)]);
}

/** Speed cushions: separate pads with gaps so wide-track fire trucks/buses straddle them. */
export function createSpeedCushion({ width = 7.2, pads = 3, padWidth = 1.85, length = 3.2, height = 0.075 } = {}) {
  const gap = (width - pads * padWidth) / (pads + 1), hx = width / 2, hz = length / 2;
  const centers = Array.from({ length: pads }, (_, i) => -hx + gap * (i + 1) + padWidth * (i + 0.5));
  const fn = (x, z) => {
    const t = z / hz; if (Math.abs(t) >= 1) return 0;
    let side = 0; for (const c of centers) side = Math.max(side, smooth(padWidth / 2, padWidth / 2 - 0.3, Math.abs(x - c)));
    return height * (1 - t * t) * side;
  };
  const mat = paintedAsphalt(`cush${width}${pads}${padWidth}${length}`, width, length, (x) => {
    x.fillStyle = 'rgba(240,240,236,0.93)';
    for (const c of centers) { const cx = c + hx; for (const [y0, d] of [[0.25, 1], [length - 0.25, -1]]) { x.beginPath(); x.moveTo(cx - 0.45, y0); x.lineTo(cx + 0.45, y0); x.lineTo(cx, y0 + d * 1.0); x.closePath(); x.fill(); } }
  });
  const geo = heightfield(fn, -hx, hx, -hz, hz, 72, 24);
  return bumpObject('SpeedCushion', fn, hx, hz, [mesh(geo, mat)]);
}

// ================================================================= POST-MOUNTED SIGNS
// 2" square perforated steel post (Telespar) in an anchor sleeve; breakaway.
function perfPost(height, size = 0.051) {
  const g = new THREE.Group();
  const geo = new THREE.BoxGeometry(size, height, size); const uv = geo.attributes.uv;
  const rep = height / (4 * 0.0254); for (let i = 0; i < uv.count; i++) uv.setY(i, uv.getY(i) * rep);
  const p = mesh(geo, M.perfPost); p.position.y = height / 2; g.add(p);
  const sleeve = mesh(new THREE.BoxGeometry(size + 0.012, 0.06, size + 0.012), M.galv); sleeve.position.y = 0.03; g.add(sleeve);
  const bolt = mesh(new THREE.CylinderGeometry(0.006, 0.006, size + 0.04, 6), M.bolt); bolt.rotation.z = Math.PI / 2; bolt.position.y = 0.035; g.add(bolt);
  return g;
}
function signBolts(g, xs, ys, z) { for (const x of xs) for (const y of ys) { const b = mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.006, 8), M.bolt, { cast: false }); b.rotation.x = Math.PI / 2; b.position.set(x, y, z); g.add(b); } }

function postMount(name, panel, w, h, { bottom = 2.13, posts = 1, postGap = null, breakaway = true } = {}) {
  const g = new THREE.Group(); g.name = name;
  panel.position.set(0, bottom + h / 2, 0); g.add(panel);
  const xs = posts === 1 ? [0] : [-(postGap ?? w * 0.6) / 2, (postGap ?? w * 0.6) / 2];
  for (const x of xs) { const p = perfPost(bottom + h - 0.05); p.position.set(x, 0, -0.03); g.add(p); }
  signBolts(g, xs, [bottom + 0.06, bottom + h - 0.06], 0.004);
  g.userData.strata = { kind: 'obstacle', obstacles: xs.map(x => ({ type: 'circle', x, z: -0.03, r: 0.045, breakaway })) };
  return g;
}

function stopArt() {
  return art('stopArt', () => {
    const S = 512, [c, x] = canvas(S, S);
    const oct = (inset) => { const R = (S / 2 - inset) / Math.cos(Math.PI / 8); x.beginPath(); for (let k = 0; k < 8; k++) { const a = Math.PI / 8 + k * Math.PI / 4; const px = S / 2 + R * Math.cos(a), py = S / 2 + R * Math.sin(a); k ? x.lineTo(px, py) : x.moveTo(px, py); } x.closePath(); };
    x.fillStyle = '#b8152a'; oct(0); x.fill();
    x.fillStyle = '#f4f4f0'; oct(S * 0.017); x.fill();
    x.fillStyle = '#b8152a'; oct(S * 0.042); x.fill();
    fitText(x, 'STOP', S / 2, S / 2, S * 0.33, S * 0.74, '#f4f4f0');
    grain(x, S, S, 9, 21);
    return tex(c);
  });
}
/** MUTCD R1-1 stop sign. size: 0.762 (30"), 0.914 (36" multi-lane), 1.219 (48"). */
export function createStopSign({ size = 0.762, bottom = 2.13, allWay = false } = {}) {
  const panel = signPanel(octagon(size), size, size, stopArt()); // art spans flat-to-flat
  const g = postMount('StopSign', panel, size, size, { bottom: allWay ? bottom + 0.2 : bottom });
  if (allWay) {
    const pw = size * 0.6, ph = pw / 3;
    const artT = art('allway', () => { const [c, x] = canvas(256, 86); x.fillStyle = '#f4f4f0'; x.fillRect(0, 0, 256, 86); x.fillStyle = '#b8152a'; x.fillRect(5, 5, 246, 76); fitText(x, 'ALL WAY', 128, 43, 40, 220, '#f4f4f0'); return tex(c); });
    const p = signPanel(roundRect(pw, ph, 0.01), pw, ph, artT); p.position.set(0, bottom + 0.2 - ph / 2 - 0.03, 0); g.add(p);
  }
  return g;
}

/** White stop bar (and optional STOP legend) painted on the road. Lies on XZ plane, across X. */
export function createStopLine({ width = 3.6, depth = 0.45, legend = false } = {}) {
  const g = new THREE.Group(); g.name = 'StopLine';
  const mat = once('paint', () => { const [c, x] = canvas(128, 32); x.fillStyle = '#ecebe6'; x.fillRect(0, 0, 128, 32); grain(x, 128, 32, 40, 8); return new THREE.MeshStandardMaterial({ map: tex(c), roughness: 0.7, polygonOffset: true, polygonOffsetFactor: -2 }); });
  const bar = mesh(new THREE.PlaneGeometry(width, depth), mat, { cast: false }); bar.rotation.x = -Math.PI / 2; bar.position.y = 0.003; g.add(bar);
  if (legend) {
    const artT = art('stopLegend', () => { const [c, x] = canvas(256, 512); x.clearRect(0, 0, 256, 512); fitText(x, 'STOP', 128, 256, 470 * CAP * 0.9, 240, '#ecebe6'); return tex(c); });
    const m = new THREE.MeshStandardMaterial({ map: artT, transparent: true, roughness: 0.7, polygonOffset: true, polygonOffsetFactor: -2 });
    const p = mesh(new THREE.PlaneGeometry(width * 0.62, 2.4), m, { cast: false }); p.rotation.x = -Math.PI / 2; p.position.set(0, 0.003, depth / 2 + 0.9 + 1.2); g.add(p);
  }
  return g;
}

/** R2-1 speed limit sign (24x30 in). */
export function createSpeedLimitSign({ limit = 70, bottom = 2.13 } = {}) {
  const w = 0.61, h = 0.762;
  const artT = art('sl' + limit, () => { const [c, x] = canvas(256, 320); x.fillStyle = '#f4f4f0'; x.fillRect(0, 0, 256, 320); x.strokeStyle = '#111'; x.lineWidth = 7; x.beginPath(); x.roundRect(9, 9, 238, 302, 14); x.stroke(); fitText(x, 'SPEED', 128, 62, 36, 200, '#111'); fitText(x, 'LIMIT', 128, 112, 36, 200, '#111'); fitText(x, String(limit), 128, 218, 118, 210, '#111'); grain(x, 256, 320, 8, 31); return tex(c); });
  return postMount('SpeedLimitSign', signPanel(roundRect(w, h, 0.03), w, h, artT), w, h, { bottom });
}

/** Yellow diamond warning sign, e.g. createWarningSign({ lines:['SPEED','HUMP'] }). */
export function createWarningSign({ lines = ['SPEED', 'HUMP'], size = 0.762, bottom = 2.13 } = {}) {
  const artT = art('warn' + lines.join('|'), () => {
    const S = 512, [c, x] = canvas(S, S);
    const dia = (i) => { x.beginPath(); x.moveTo(S / 2, i); x.lineTo(S - i, S / 2); x.lineTo(S / 2, S - i); x.lineTo(i, S / 2); x.closePath(); };
    x.fillStyle = '#f2c200'; dia(0); x.fill(); x.fillStyle = '#111'; dia(10); x.fill(); x.fillStyle = '#f2c200'; dia(24); x.fill();
    const lh = 92, y0 = S / 2 - (lines.length - 1) * lh / 2;
    lines.forEach((t, i) => fitText(x, t, S / 2, y0 + i * lh, 62, 250 - Math.abs(i - (lines.length - 1) / 2) * 40, '#111'));
    grain(x, S, S, 8, 41); return tex(c);
  });
  const d = size * Math.SQRT2; // point-to-point
  const shape = new THREE.Shape(); shape.moveTo(0, d / 2); shape.lineTo(d / 2, 0); shape.lineTo(0, -d / 2); shape.lineTo(-d / 2, 0); shape.closePath();
  return postMount('WarningSign', signPanel(shape, d, d, artT), d, d, { bottom });
}

/** Green freeway mile marker (D10-1). */
export function createMileMarker({ mile = 214, bottom = 1.2 } = {}) {
  const w = 0.3, h = 0.6 + String(mile).length * 0.15;
  const artT = art('mile' + mile, () => { const W = 120, H = Math.round(120 * h / w), [c, x] = canvas(W, H); x.fillStyle = '#f4f4f0'; x.fillRect(0, 0, W, H); x.fillStyle = '#00704a'; x.beginPath(); x.roundRect(4, 4, W - 8, H - 8, 8); x.fill(); fitText(x, 'MILE', W / 2, 46, 22, 96, '#f4f4f0'); String(mile).split('').forEach((d, i) => fitText(x, d, W / 2, 110 + i * 62, 48, 90, '#f4f4f0')); return tex(c); });
  return postMount('MileMarker', signPanel(roundRect(w, h, 0.02), w, h, artT), w, h, { bottom });
}

// ================================================================= FREEWAY GUIDE SIGNS
const GREEN = '#00704a', WHITE = '#f4f4f0';

/**
 * Layout spec for a green guide sign:
 *  { shields:[{type:'I'|'US'|'M', num:'75'}], direction:'NORTH', lines:['Flint','Saginaw'],
 *    arrows:'down'|'upright'|'upleft'|'none', arrowCount, exitOnly:false, exitTab:'51A', width, height }
 */
function guideArt(spec) {
  const key = 'guide' + JSON.stringify(spec);
  return art(key, () => {
    const PX = 96; // px per meter
    const meas = canvas(4, 4)[1];
    const capDest = 0.4, capDir = 0.3, shieldS = 0.95, margin = 0.32, gapY = 0.18;
    const textW = (t, cap) => { meas.font = `700 ${cap / CAP * PX}px ${FONT}`; return meas.measureText(t).width / PX; };
    const lines = spec.lines || [], shields = spec.shields || [];
    let rowsW = [margin * 2 + 2];
    if (shields.length) rowsW.push(shields.length * shieldS + (shields.length - 1) * 0.25 + margin * 2);
    if (spec.direction) rowsW.push(textW(spec.direction, capDir) + margin * 2);
    lines.forEach(l => rowsW.push(textW(l, capDest) + margin * 2));
    const arrows = spec.arrows || 'none';
    const exitOnlyH = spec.exitOnly ? 0.75 : 0;
    let H = margin;
    if (spec.direction) H += capDir + gapY;
    if (shields.length) H += shieldS + gapY;
    H += lines.length * (capDest + gapY);
    if (arrows !== 'none' && !spec.exitOnly) H += 0.8 + gapY;
    H += exitOnlyH + margin * (spec.exitOnly ? 0 : 1);
    const W = spec.width || Math.max(...rowsW, spec.exitOnly ? 3.6 : 0);
    H = spec.height || H;
    const cw = Math.min(2048, Math.round(W * PX)), ch = Math.min(2048, Math.round(H * PX)), sx = cw / W, sy = ch / H;
    const [c, x] = canvas(cw, ch);
    x.scale(sx, sy);
    x.fillStyle = WHITE; x.beginPath(); x.roundRect(0, 0, W, H, 0.15); x.fill();
    x.fillStyle = GREEN; x.beginPath(); x.roundRect(0.035, 0.035, W - 0.07, H - 0.07, 0.12); x.fill();
    // draw in px-space for text accuracy
    x.setTransform(1, 0, 0, 1, 0, 0);
    let y = margin * PX;
    const cx = cw / 2;
    if (spec.direction) { fitText(x, spec.direction, cx, y + capDir * PX / 2, capDir * PX, (W - 2 * margin) * PX, WHITE); y += (capDir + gapY) * PX; }
    if (shields.length) {
      const tot = shields.length * shieldS + (shields.length - 1) * 0.25; let sxp = cx - tot * PX / 2;
      shields.forEach(s => { drawShield(x, s.type, s.num, sxp, y, shieldS * PX); sxp += (shieldS + 0.25) * PX; }); y += (shieldS + gapY) * PX;
    }
    lines.forEach(l => { fitText(x, l, cx, y + capDest * PX / 2, capDest * PX, (W - 2 * margin) * PX, WHITE); y += (capDest + gapY) * PX; });
    if (spec.exitOnly) {
      const bh = exitOnlyH * PX, by = ch - bh - 0.035 * PX;
      x.fillStyle = '#f2c200'; x.beginPath(); x.roundRect(0.035 * PX, by, cw - 0.07 * PX, bh, [0, 0, 0.12 * PX, 0.12 * PX]); x.fill();
      const tw = fitText(x, 'EXIT ONLY', cx, by + bh / 2, 0.36 * PX, cw * 0.5, '#111');
      drawArrow(x, cx - tw / 2 - 0.5 * PX, by + bh / 2, 0.6 * PX, Math.PI, '#111'); drawArrow(x, cx + tw / 2 + 0.5 * PX, by + bh / 2, 0.6 * PX, Math.PI, '#111');
    } else if (arrows !== 'none') {
      const ang = { down: Math.PI, upright: Math.PI / 4, upleft: -Math.PI / 4, up: 0, right: Math.PI / 2, left: -Math.PI / 2 }[arrows] ?? Math.PI;
      const n = spec.arrowCount || 1;
      for (let i = 0; i < n; i++) drawArrow(x, cx + (i - (n - 1) / 2) * 1.4 * PX, y + 0.4 * PX, 0.8 * PX, ang, WHITE);
    }
    grain(x, cw, ch, 7, 51);
    return { tex: tex(c), W, H };
  });
}
function exitTabArt(num) {
  return art('tab' + num, () => {
    const W = 0.5 + 0.21 * (5 + String(num).length), H = 0.62, PX = 110;
    const [c, x] = canvas(Math.round(W * PX), Math.round(H * PX));
    x.fillStyle = WHITE; x.beginPath(); x.roundRect(0, 0, W * PX, H * PX, 10); x.fill();
    x.fillStyle = GREEN; x.beginPath(); x.roundRect(4, 4, W * PX - 8, H * PX - 8, 8); x.fill();
    fitText(x, `EXIT ${num}`, W * PX / 2, H * PX / 2, 0.3 * PX, (W - 0.3) * PX, WHITE);
    return { tex: tex(c), W, H };
  });
}

/** Just the sign panel (with optional exit tab on top-right). Origin at sign center. */
export function createGuideSignPanel(spec = {}) {
  const { tex: art, W, H } = guideArt(spec);
  const g = new THREE.Group(); g.name = 'GuideSignPanel';
  g.add(signPanel(roundRect(W, H, 0.15), W, H, art, { stiffeners: Math.max(2, Math.round(H / 1.1)) }));
  if (spec.exitTab) {
    const t = exitTabArt(spec.exitTab); const p = signPanel(roundRect(t.W, t.H, 0.08), t.W, t.H, t.tex);
    p.position.set(W / 2 - t.W / 2 - 0.15, H / 2 + t.H / 2 - 0.02, 0.006); g.add(p);
  }
  g.userData.size = { w: W, h: H + (spec.exitTab ? 0.6 : 0) };
  return g;
}

// I-beam post (W6x9-ish) with slip base, extruded from section.
function iBeam(height, d = 0.15, bf = 0.1, tf = 0.008, tw = 0.0055) {
  const s = new THREE.Shape();
  s.moveTo(-bf / 2, -d / 2); s.lineTo(bf / 2, -d / 2); s.lineTo(bf / 2, -d / 2 + tf); s.lineTo(tw / 2, -d / 2 + tf); s.lineTo(tw / 2, d / 2 - tf); s.lineTo(bf / 2, d / 2 - tf);
  s.lineTo(bf / 2, d / 2); s.lineTo(-bf / 2, d / 2); s.lineTo(-bf / 2, d / 2 - tf); s.lineTo(-tw / 2, d / 2 - tf); s.lineTo(-tw / 2, -d / 2 + tf); s.lineTo(-bf / 2, -d / 2 + tf); s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, { depth: height, bevelEnabled: false }); geo.rotateX(-Math.PI / 2); // extrude up +Y
  geo.rotateY(Math.PI / 2); // web faces traffic edge-on like the real thing
  const g = new THREE.Group(); g.add(mesh(geo, M.galv));
  const plate = mesh(new THREE.BoxGeometry(0.2, 0.025, 0.24), M.galv); plate.position.y = 0.09; g.add(plate);
  const plate2 = plate.clone(); plate2.position.y = 0.06; g.add(plate2);
  const pad = mesh(new THREE.CylinderGeometry(0.22, 0.24, 0.05, 14), M.concrete); pad.position.y = 0.02; g.add(pad);
  return g;
}

/** Ground-mounted freeway guide sign on two breakaway I-beam posts. */
export function createGuideSign(spec = {}, { bottom = 2.1 } = {}) {
  const panel = createGuideSignPanel(spec); const { w, h } = panel.userData.size;
  const g = new THREE.Group(); g.name = 'GuideSign';
  const ph = spec.exitTab ? h - 0.6 : h;
  panel.position.set(0, bottom + ph / 2, 0); g.add(panel);
  const xs = [-w * 0.3, w * 0.3];
  for (const x of xs) { const p = iBeam(bottom + ph - 0.1); p.position.set(x, 0, -0.1); g.add(p); }
  g.userData.strata = { kind: 'obstacle', obstacles: xs.map(x => ({ type: 'circle', x, z: -0.1, r: 0.11, breakaway: true })) };
  return g;
}

/** Exit gore sign (E5-1): "EXIT" with up-left/right arrow + exit-number tab. */
export function createExitGoreSign({ exit = '51A', side = 'right', bottom = 2.1 } = {}) {
  const panel = createGuideSignPanel({ lines: ['EXIT'], arrows: side === 'right' ? 'upright' : 'upleft', exitTab: exit, width: 2.0 });
  const { w, h } = panel.userData.size; const ph = h - 0.6;
  const g = new THREE.Group(); g.name = 'ExitGoreSign';
  panel.position.set(0, bottom + ph / 2, 0); g.add(panel);
  const xs = [-w * 0.28, w * 0.28];
  for (const x of xs) { const p = perfPost(bottom + ph - 0.05, 0.064); p.position.set(x, 0, -0.04); g.add(p); }
  g.userData.strata = { kind: 'obstacle', obstacles: xs.map(x => ({ type: 'circle', x, z: -0.04, r: 0.05, breakaway: true })) };
  return g;
}

// ================================================================= DMS (electronic message board)
function dmsArt(lines) {
  lines = (lines || []).filter(Boolean).slice(0, 3); if (!lines.length) lines = [''];
  return art('dms' + lines.join('|'), () => {
    // draw the text at LED resolution, then light one round amber pixel per LED
    const cols = 120, rows = 30, [m, mx] = canvas(cols, rows);
    mx.fillStyle = '#000'; mx.fillRect(0, 0, cols, rows); mx.fillStyle = '#fff'; mx.textAlign = 'center'; mx.textBaseline = 'middle';
    const lh = rows / lines.length, fs = Math.min(lh * 0.82, 11);
    lines.forEach((l, i) => { mx.font = `700 ${fs}px ${FONT}`; const w = mx.measureText(l.toUpperCase()).width, sx = Math.min(1, (cols - 4) / Math.max(1, w)); mx.save(); mx.translate(cols / 2, lh * (i + 0.5) + 0.5); mx.scale(sx, 1); mx.fillText(l.toUpperCase(), 0, 0); mx.restore(); });
    const px = mx.getImageData(0, 0, cols, rows).data;
    const P = 8, [c, x] = canvas(cols * P, rows * P);
    x.fillStyle = '#050505'; x.fillRect(0, 0, c.width, c.height);
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const on = px[(j * cols + i) * 4] > 110;
      x.fillStyle = on ? '#ffb000' : '#1a1206'; x.beginPath(); x.arc(i * P + P / 2, j * P + P / 2, P * (on ? 0.42 : 0.3), 0, Math.PI * 2); x.fill();
    }
    return tex(c);
  });
}
export function createMessageBoard({ lines = ['CRASH AHEAD', 'LEFT LANE BLOCKED'], width = 7.6, height = 2.3 } = {}) {
  const g = new THREE.Group(); g.name = 'MessageBoard';
  const housing = mesh(new THREE.BoxGeometry(width, height, 0.7), M.steel); housing.position.z = -0.35; g.add(housing);
  const artT = dmsArt(lines);
  const fm = new THREE.MeshStandardMaterial({ map: artT, emissive: 0xffffff, emissiveMap: artT, emissiveIntensity: 1.1, roughness: 0.3 }); fm.userData.own = true;
  const face = mesh(new THREE.PlaneGeometry(width - 0.3, height - 0.35), fm, { cast: false });
  face.position.z = 0.012; g.add(face);
  const visor = mesh(new THREE.BoxGeometry(width, 0.04, 0.25), M.steel); visor.position.set(0, height / 2 - 0.02, 0.12); g.add(visor);
  g.userData.size = { w: width, h: height };
  // allow changing text at runtime
  g.userData.setLines = (ls) => { face.material.map = face.material.emissiveMap = dmsArt(ls); face.material.needsUpdate = true; };
  return g;
}

// ================================================================= GANTRIES
function jerseyBarrier(length) {
  const s = new THREE.Shape(); [[-0.3, 0], [0.3, 0], [0.3, 0.08], [0.17, 0.33], [0.075, 0.81], [-0.075, 0.81], [-0.17, 0.33], [-0.3, 0.08]].forEach(([a, b], i) => i ? s.lineTo(a, b) : s.moveTo(a, b)); s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, { depth: length, bevelEnabled: false }); geo.translate(0, 0, -length / 2);
  const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 0.5, uv.getY(i) * 0.5);
  return mesh(geo, M.concrete);
}

function trussBox(tb, x0, x1, yc, zc, hy, hz, bay) {
  const ys = [yc - hy / 2, yc + hy / 2], zs = [zc - hz / 2, zc + hz / 2];
  for (const y of ys) for (const z of zs) tb.add(V(x0, y, z), V(x1, y, z), 0.05);
  const n = Math.max(1, Math.round((x1 - x0) / bay));
  for (let i = 0; i <= n; i++) {
    const x = x0 + (x1 - x0) * i / n;
    tb.add(V(x, ys[0], zs[0]), V(x, ys[1], zs[0]), 0.025); tb.add(V(x, ys[0], zs[1]), V(x, ys[1], zs[1]), 0.025);
    tb.add(V(x, ys[0], zs[0]), V(x, ys[0], zs[1]), 0.025); tb.add(V(x, ys[1], zs[0]), V(x, ys[1], zs[1]), 0.025);
    if (i < n) {
      const x2 = x0 + (x1 - x0) * (i + 1) / n, f = i % 2;
      tb.add(V(x, ys[f], zs[0]), V(x2, ys[1 - f], zs[0]), 0.02); tb.add(V(x, ys[f], zs[1]), V(x2, ys[1 - f], zs[1]), 0.02);
      tb.add(V(x, ys[0], zs[f]), V(x2, ys[0], zs[1 - f]), 0.02); tb.add(V(x, ys[1], zs[f]), V(x2, ys[1], zs[1 - f]), 0.02);
    }
  }
}
function trussTower(tb, xc, y0, y1, zc, wx, wz, bay) {
  const xs = [xc - wx / 2, xc + wx / 2], zs = [zc - wz / 2, zc + wz / 2];
  for (const x of xs) for (const z of zs) tb.add(V(x, y0, z), V(x, y1, z), 0.06);
  const n = Math.max(1, Math.round((y1 - y0) / bay));
  for (let i = 0; i <= n; i++) {
    const y = y0 + (y1 - y0) * i / n;
    tb.add(V(xs[0], y, zs[0]), V(xs[1], y, zs[0]), 0.025); tb.add(V(xs[0], y, zs[1]), V(xs[1], y, zs[1]), 0.025);
    tb.add(V(xs[0], y, zs[0]), V(xs[0], y, zs[1]), 0.025); tb.add(V(xs[1], y, zs[0]), V(xs[1], y, zs[1]), 0.025);
    if (i < n) { const y2 = y0 + (y1 - y0) * (i + 1) / n, f = i % 2; tb.add(V(xs[f], y, zs[0]), V(xs[1 - f], y2, zs[0]), 0.02); tb.add(V(xs[f], y, zs[1]), V(xs[1 - f], y2, zs[1]), 0.02); tb.add(V(xs[0], y, zs[f]), V(xs[0], y2, zs[1 - f]), 0.02); tb.add(V(xs[1], y, zs[f]), V(xs[1], y2, zs[1 - f]), 0.02); }
  }
}

function hangSign(g, tb, item, clearance, trussY, trussZ, trussH) {
  const panel = item.dms ? createMessageBoard(item.dms) : createGuideSignPanel(item.spec || item);
  const { w, h } = panel.userData.size; const ph = (item.spec?.exitTab || item.exitTab) ? h - 0.6 : h;
  panel.position.set(item.x || 0, clearance + ph / 2, item.dms ? 0.35 : 0); g.add(panel); // DMS cabinet sits proud of the truss
  if (!item.dms) {
    // vertical hanger tubes behind the sign, tied into the truss
    for (const hx of [-w * 0.33, w * 0.33]) {
      const X = (item.x || 0) + hx;
      tb.add(V(X, clearance + 0.05, -0.08), V(X, clearance + ph - 0.05, -0.08), 0.035);
      tb.add(V(X, trussY - trussH / 2, -0.08), V(X, trussY - trussH / 2, trussZ + 0.5), 0.025);
      tb.add(V(X, trussY + trussH / 2, -0.08), V(X, trussY + trussH / 2, trussZ + 0.5), 0.025);
    }
  } else {
    for (const hx of [-w * 0.35, w * 0.35]) { const X = (item.x || 0) + hx; tb.add(V(X, trussY - trussH / 2, -0.33), V(X, trussY - trussH / 2, trussZ + 0.5), 0.04); tb.add(V(X, trussY + trussH / 2, -0.33), V(X, trussY + trussH / 2, trussZ + 0.5), 0.04); }
  }
  return { w, x: item.x || 0 };
}

/**
 * Full-span overhead sign bridge (4-chord box truss on two truss towers, concrete pedestals,
 * shielding barriers, optional catwalk). Origin = road center at ground. Signs face +Z.
 *  signs: [{ x, spec:{...guide spec} }, { x, dms:{ lines:[...] } }]
 */
export function createOverheadGantry({ span = 22, clearance = 5.4, signs = [], catwalk = true, barriers = true } = {}) {
  const g = new THREE.Group(); g.name = 'OverheadGantry';
  const tb = new TubeBatch();
  const maxH = Math.max(3, ...signs.map(s => (s.dms ? createMessageBoardSize(s.dms).h : guideArt(s.spec || s).H)));
  const trussH = 1.3, trussY = clearance + Math.min(maxH, 3.6) / 2 + 0.2, trussZ = -0.95;
  const half = span / 2;
  trussBox(tb, -half - 0.5, half + 0.5, trussY, trussZ, trussH, 1.0, 1.25);
  const obstacles = [];
  for (const sx of [-1, 1]) {
    const xc = sx * (half + 0.5);
    trussTower(tb, xc, 1.0, trussY + trussH / 2, trussZ, 0.6, 1.0, 1.2);
    const ped = mesh(new THREE.BoxGeometry(1.2, 1.0, 1.6), M.concrete); ped.position.set(xc, 0.5, trussZ); g.add(ped);
    obstacles.push({ type: 'box', x: xc, z: trussZ, hx: 0.6, hz: 0.8, rot: 0 });
    if (barriers) {
      const L = 9, bx = xc - sx * 1.25, b = jerseyBarrier(L); b.position.set(bx, 0, trussZ + 1.5); g.add(b);
      obstacles.push({ type: 'box', x: bx, z: trussZ + 1.5, hx: 0.3, hz: L / 2, rot: 0 });
    }
  }
  const placed = signs.map(s => hangSign(g, tb, s, clearance, trussY, trussZ, trussH));
  if (catwalk && placed.length) {
    const gr = once('grate', () => { const [c, x] = canvas(64, 64); x.fillStyle = '#7d8286'; x.fillRect(0, 0, 64, 64); x.fillStyle = '#000'; for (let i = 4; i < 64; i += 8) for (let j = 4; j < 64; j += 8) x.fillRect(i - 2, j - 2, 5, 5); const t = tex(c, { srgb: false, repeat: true }); return new THREE.MeshStandardMaterial({ color: 0x8b9095, metalness: 0.7, roughness: 0.5, alphaMap: t, alphaTest: 0.5, side: THREE.DoubleSide }); });
    const x0 = Math.min(...placed.map(p => p.x - p.w / 2)) - 0.3, x1 = Math.max(...placed.map(p => p.x + p.w / 2)) + 0.3;
    const deck = mesh(new THREE.PlaneGeometry(x1 - x0, 0.75), gr); deck.rotation.x = -Math.PI / 2; deck.position.set((x0 + x1) / 2, clearance - 0.1, 0.25); g.add(deck);
    tb.add(V(x0, clearance - 0.1, 0.62), V(x1, clearance - 0.1, 0.62), 0.02);
    tb.add(V(x0, clearance + 1.0, 0.62), V(x1, clearance + 1.0, 0.62), 0.022);
    tb.add(V(x0, clearance + 0.5, 0.62), V(x1, clearance + 0.5, 0.62), 0.016);
    for (let x = x0; x <= x1 + 0.01; x += 1.5) { tb.add(V(x, clearance - 0.1, 0.62), V(x, clearance + 1.0, 0.62), 0.02); tb.add(V(x, clearance - 0.1, 0.62), V(x, clearance - 0.1, -0.05), 0.02); }
    // sign lights hanging off the catwalk
    for (const p of placed) for (const lx of [-p.w * 0.25, p.w * 0.25]) { const l = mesh(new THREE.BoxGeometry(0.45, 0.16, 0.3), M.steel); l.position.set(p.x + lx, clearance - 0.02, 0.5); g.add(l); }
  }
  g.add(tb.build(M.galv));
  g.userData.strata = { kind: 'obstacle', obstacles };
  return g;
}
function createMessageBoardSize(d) { return { w: d.width || 7.6, h: d.height || 2.3 }; }

/** Single-column cantilever (butterfly-arm) sign structure. Column at origin; arm reaches toward -X over the road. */
export function createCantileverSign({ arm = 9, clearance = 5.4, spec = {}, signX = null, barrier = true } = {}) {
  const g = new THREE.Group(); g.name = 'CantileverSign';
  const tb = new TubeBatch();
  const artG = guideArt(spec);
  const trussH = 1.1, trussY = clearance + Math.min(artG.H, 3.4) / 2 + 0.15, trussZ = -0.85;
  const col = mesh(new THREE.CylinderGeometry(0.22, 0.26, trussY + trussH / 2 + 0.3 - 1.0, 16), M.galv); col.position.set(0, 1.0 + (trussY + trussH / 2 + 0.3 - 1.0) / 2, trussZ); g.add(col);
  const ped = mesh(new THREE.CylinderGeometry(0.5, 0.55, 1.0, 16), M.concrete); ped.position.set(0, 0.5, trussZ); g.add(ped);
  trussBox(tb, -arm, 0, trussY, trussZ, trussH, 0.8, 1.2);
  const sx = signX ?? (-arm + artG.W / 2 + 0.6);
  hangSign(g, tb, { x: sx, spec }, clearance, trussY, trussZ, trussH);
  g.add(tb.build(M.galv));
  const obstacles = [{ type: 'circle', x: 0, z: trussZ, r: 0.55, breakaway: false }];
  if (barrier) { const b = jerseyBarrier(8); b.position.set(-1.0, 0, trussZ + 1.5); g.add(b); obstacles.push({ type: 'box', x: -1.0, z: trussZ + 1.5, hx: 0.3, hz: 4, rot: 0 }); }
  g.userData.strata = { kind: 'obstacle', obstacles };
  return g;
}

// ================================================================= PHYSICS HELPER
/**
 * PropsWorld: register props, then query:
 *   heightAt(x, z)     → road-surface height including bumps (use it for each wheel)
 *   collideCar(car)    → car vs posts / barriers / guardrails / cones. Mutates car.x, z, yaw, speed.
 *                        Call it inside your physics sub-steps (no tunnelling at high speed).
 *   update(dt)         → animates knocked signs, flying cones, sliding barriers, flex posts, blinking lights
 *   colliders()        → world-space shapes for Rapier/Cannon/Ammo if you use a physics engine
 *   toLayout() / loadLayout(list) → save / restore every editable prop
 *
 * car = { x, z, yaw, halfW, halfL, speed }  (yaw like Object3D.rotation.y; forward = -Z at yaw 0)
 *
 * Obstacle definitions (obj.userData.strata.obstacles):
 *   { type:'circle', x, z, r, breakaway }                 post (breakaway → sign folds over)
 *   { type:'box', x, z, hx, hz, rot }                     solid (pedestal, concrete barrier)
 *   { type:'box', ..., rail:{ t0, t1 } }                  guardrail segment: dents + redirects the car
 *   { type:'circle', node, r, dyn:'fly', mass, lieY, lieR, h }  cone / drum: gets launched and tumbles
 *   { type:'box', node, hx, hz, dyn:'push', mass }        water-filled barrier: gets shoved
 *   { type:'circle', node, r, dyn:'flex' }                flexible delineator: bends under the car, springs back
 */
const _v = new THREE.Vector3(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), UPV = new THREE.Vector3(0, 1, 0);
const angLerp = (a, b, t) => { let d = ((b - a + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI; return a + d * t; };

export class PropsWorld {
  constructor(scene) { this.scene = scene; this.surfaces = []; this.obstacles = []; this.falling = []; this.props = []; this.ticks = []; this.time = 0; this.onHit = null; }

  add(obj) {
    if (this.scene && !obj.parent) this.scene.add(obj);
    obj.updateMatrixWorld(true);
    if (obj.userData.prop && !this.props.includes(obj)) this.props.push(obj);
    if (obj.userData.tick && !this.ticks.includes(obj)) this.ticks.push(obj);
    obj.userData.home = { p: obj.position.clone(), q: obj.quaternion.clone() };
    const d = obj.userData.strata; if (!d) return obj;
    if (d.surface) {
      const s = d.surface, inv = obj.matrixWorld.clone().invert(), c = new THREE.Vector3().setFromMatrixPosition(obj.matrixWorld);
      this.surfaces.push({ obj, fn: s.heightFn, inv, cx: c.x, cz: c.z, r2: (s.halfX ** 2 + s.halfZ ** 2) * 1.05, baseY: c.y });
    }
    if (d.obstacles) for (const o of d.obstacles) {
      const rec = { obj, def: o, type: o.type, breakaway: !!o.breakaway, active: true, touching: false };
      if (o.node) {
        rec.node = o.node; rec.dyn = o.dyn; rec.mass = o.mass || 5; rec.lieY = o.lieY ?? 0.15; rec.lieR = o.lieR ?? o.r; rec.h = o.h || 0.7;
        rec.wp = o.node.getWorldPosition(new THREE.Vector3()); rec.wq = o.node.getWorldQuaternion(new THREE.Quaternion());
        rec.q0 = rec.wq.clone(); rec.home = { p: o.node.position.clone(), q: o.node.quaternion.clone() };
        rec.vel = new THREE.Vector3(); rec.w = new THREE.Vector3(); rec.state = 'rest'; rec.wy = 0;
        rec.x = rec.wp.x; rec.z = rec.wp.z;
      } else {
        const p = new THREE.Vector3(o.x, 0, o.z).applyMatrix4(obj.matrixWorld); rec.x = p.x; rec.z = p.z;
      }
      if (o.type === 'circle') rec.r = o.r;
      else { this._axes(rec, o.rot || 0, o.node ? rec.wq : null); rec.hx = o.hx; rec.hz = o.hz; }
      if (o.rail) rec.rail = o.rail;
      this.obstacles.push(rec);
    }
    return obj;
  }
  _axes(rec, rot, wq) {
    const ax = new THREE.Vector3(Math.cos(rot), 0, -Math.sin(rot));
    if (wq) ax.applyQuaternion(wq); else ax.transformDirection(rec.obj.matrixWorld);
    ax.y = 0; ax.normalize(); rec.ux = ax.x; rec.uz = ax.z;
  }

  heightAt(x, z) {
    let h = 0;
    for (const s of this.surfaces) {
      const dx = x - s.cx, dz = z - s.cz; if (dx * dx + dz * dz > s.r2) continue;
      _v.set(x, s.baseY, z).applyMatrix4(s.inv); h = Math.max(h, s.baseY + s.fn(_v.x, _v.z));
    }
    return h;
  }

  collideCar(car) {
    const events = [];
    const fx = -Math.sin(car.yaw), fz = -Math.cos(car.yaw), rx = Math.cos(car.yaw), rz = -Math.sin(car.yaw);
    const sg = Math.sign(car.speed) || 1, impact = Math.abs(car.speed);
    for (const o of this.obstacles) {
      if (!o.active) { o.touching = false; continue; }
      const dx = o.x - car.x, dz = o.z - car.z; const reach = car.halfL + car.halfW + (o.r || Math.hypot(o.hx, o.hz));
      if (dx * dx + dz * dz > reach * reach) { o.touching = false; continue; }
      let nx = 0, nz = 0, depth = -1;
      if (o.type === 'circle') {
        const lr = dx * rx + dz * rz, lf = dx * fx + dz * fz;
        const cr = clamp(lr, -car.halfW, car.halfW), cf = clamp(lf, -car.halfL, car.halfL);
        let ex = lr - cr, ef = lf - cf, dist = Math.hypot(ex, ef);
        if (dist >= o.r) { o.touching = false; continue; }
        if (dist < 1e-5) {
          const pr = car.halfW - Math.abs(lr), pf = car.halfL - Math.abs(lf);
          if (pr < pf) { ex = Math.sign(lr) || 1; ef = 0; depth = pr + o.r; } else { ex = 0; ef = Math.sign(lf) || 1; depth = pf + o.r; }
          dist = 1;
        } else depth = o.r - dist;
        ex /= dist; ef /= dist; nx = ex * rx + ef * fx; nz = ex * rz + ef * fz;
      } else {
        const axes = [[rx, rz], [fx, fz], [o.ux, o.uz], [-o.uz, o.ux]];
        let best = Infinity, bx = 0, bz = 0, sep = false;
        for (const [ax, az] of axes) {
          const ra = car.halfW * Math.abs(rx * ax + rz * az) + car.halfL * Math.abs(fx * ax + fz * az);
          const rb = o.hx * Math.abs(o.ux * ax + o.uz * az) + o.hz * Math.abs(-o.uz * ax + o.ux * az);
          const dist = dx * ax + dz * az, ov = ra + rb - Math.abs(dist);
          if (ov <= 0) { sep = true; break; }
          if (ov < best) { best = ov; const s = Math.sign(dist) || 1; bx = ax * s; bz = az * s; }
        }
        if (sep) { o.touching = false; continue; }
        depth = best; nx = bx; nz = bz;
      }
      const first = !o.touching; o.touching = true;
      const cosA = Math.abs(fx * nx + fz * nz), vAlong = car.speed * (fx * nx + fz * nz);
      // ---- dynamic props
      if (o.dyn === 'fly') { if (impact <= 0.4) { car.x -= nx * depth; car.z -= nz * depth; continue; } { this._launch(o, car, fx * sg, fz * sg, rx, rz); car.speed *= 1 - Math.min(0.2, o.mass / 1650 * 1.4); events.push({ obj: o.obj, node: o.node, type: 'launch', speed: impact }); } continue; }
      if (o.dyn === 'flex') { if (impact > 0.8) { this._flex(o, fx * sg, fz * sg); car.speed *= 0.995; events.push({ obj: o.obj, node: o.node, type: 'flex', speed: impact }); } continue; }
      if (o.dyn === 'push') {
        const closing = vAlong - (o.vel.x * nx + o.vel.z * nz);
        car.x -= nx * depth * 0.5; car.z -= nz * depth * 0.5; o.wp.x += nx * depth * 0.5; o.wp.z += nz * depth * 0.5;
        if (closing > 0.2) {
          const mc = 1650, mb = o.mass, j = closing * (2 * mc * mb / (mc + mb)) * 0.55; // inelastic-ish impulse
          o.vel.x += nx * j / mb; o.vel.z += nz * j / mb; o.wy += (Math.random() - 0.5) * closing * 0.6; o.state = 'slide';
          car.speed -= sg * (j / mc) * cosA;
          if (first && closing > 1.5) events.push({ obj: o.obj, node: o.node, type: 'shove', speed: closing });
        }
        continue;
      }
      // ---- breakaway posts
      if (o.breakaway && impact > 2.5) {
        o.active = false; this._knock(o.obj, fx * sg, fz * sg, impact);
        car.speed *= 0.86; events.push({ obj: o.obj, type: 'knockdown', speed: impact }); continue;
      }
      // ---- solid: push out
      car.x -= nx * depth; car.z -= nz * depth;
      if (o.rail) { // guardrail: dent it and redirect the car along it
        const along = clamp((car.x - o.x) * o.ux + (car.z - o.z) * o.uz, -o.hx, o.hx), t = (o.rail.t0 + o.rail.t1) / 2 + along;
        const nSpeed = impact * cosA;
        if (nSpeed > 1.5) o.obj.userData.dent?.(t, Math.min(0.5, nSpeed * 0.022));
        let tx = o.ux, tz = o.uz; if (tx * fx * sg + tz * fz * sg < 0) { tx = -tx; tz = -tz; }
        const target = Math.atan2(-tx * sg, -tz * sg);
        if (first) { car.speed *= 1 - 0.6 * cosA; car.yaw = angLerp(car.yaw, target, 0.55); if (nSpeed > 2) events.push({ obj: o.obj, type: 'guardrail', speed: nSpeed }); }
        else { car.speed *= 0.9992; car.yaw = angLerp(car.yaw, target, 0.04); }
        continue;
      }
      if (vAlong > 0) car.speed = -car.speed * 0.12;
      if (first && impact > 0.5) events.push({ obj: o.obj, type: 'impact', speed: impact });
    }
    if (events.length && this.onHit) events.forEach(e => this.onHit(e));
    return events;
  }

  _launch(o, car, dx, dz, rx, rz) {
    const spd = Math.min(Math.abs(car.speed), 40), lat = Math.sign((o.x - car.x) * rx + (o.z - car.z) * rz) || 1, j = () => (Math.random() - 0.5);
    const k = Math.min(1.05, 0.55 + 100 / (o.mass * 40 + 60)); // light cones fly further than drums
    o.vel.set(dx * spd * k + rx * lat * (1 + spd * 0.12) + j(), 1.0 + spd * 0.16 * k + j() * 0.6, dz * spd * k + rz * lat * (1 + spd * 0.12) + j());
    o.w.set(j(), j() * 0.4, j()).normalize().multiplyScalar(3 + spd * 0.45 * k);
    o.state = 'fly'; o.active = false; o.t = 0;
  }
  _flex(o, dx, dz) { o.active = false; o.state = 'flex'; o.axis = new THREE.Vector3().crossVectors(UPV, _v.set(dx, 0, dz).normalize()).normalize(); o.th = 1.35; o.thv = 0; o.t = 0; }

  _knock(obj, dx, dz, speed) {
    for (const o of this.obstacles) if (o.obj === obj && !o.node) o.active = false; // two-post signs fall as one
    const dir = new THREE.Vector3(dx, 0, dz).normalize(); const axis = new THREE.Vector3().crossVectors(UPV, dir).normalize();
    this.falling.push({ obj, axis, q0: obj.quaternion.clone(), p0: obj.position.clone(), dir, th: 0, w: Math.min(3, speed * 0.15), slide: speed * 0.25, done: false, h: obj.userData.fallHeight || 2.5 });
  }

  _writeNode(o) {
    const n = o.node, par = n.parent;
    par.updateMatrixWorld(); n.position.copy(par.worldToLocal(_v.copy(o.wp)));
    par.getWorldQuaternion(_q2).invert(); n.quaternion.copy(_q2.multiply(o.wq));
  }

  update(dt) {
    this.time += dt;
    // knocked signs
    for (const f of this.falling) {
      if (f.done) continue;
      f.w += (3 * 9.81 / (2 * f.h)) * Math.sin(f.th + 0.05) * dt; f.th += f.w * dt;
      f.slide = Math.max(0, f.slide - 6 * dt); f.p0.addScaledVector(f.dir, f.slide * dt);
      if (f.th >= 1.48) { f.th = 1.48; f.w = -f.w * 0.25; if (Math.abs(f.w) < 0.3) f.done = true; }
      _q.setFromAxisAngle(f.axis, f.th); f.obj.quaternion.copy(_q).multiply(f.q0); f.obj.position.copy(f.p0);
    }
    // dynamic props
    for (const o of this.obstacles) {
      if (!o.node || o.state === 'rest') continue;
      o.t += dt;
      if (o.state === 'fly') {
        o.vel.y -= 9.81 * dt; o.wp.addScaledVector(o.vel, dt);
        const wl = o.w.length(); if (wl > 1e-3) { _q.setFromAxisAngle(_v.copy(o.w).divideScalar(wl), wl * dt); o.wq.premultiply(_q); }
        const floor = this.heightAt(o.wp.x, o.wp.z) + o.lieY;
        if (o.wp.y <= floor && o.vel.y < 0) {
          o.wp.y = floor; o.vel.y *= -0.32; o.vel.x *= 0.55; o.vel.z *= 0.55; o.w.multiplyScalar(0.55);
          if (Math.hypot(o.vel.x, o.vel.z) < 1.4 && o.vel.y < 1.2) {
            o.state = 'settle'; o.t = 0;
            const hd = Math.hypot(o.vel.x, o.vel.z) > 0.05 ? _v.set(o.vel.x, 0, o.vel.z).normalize() : _v.set(Math.random() - 0.5, 0, Math.random() - 0.5).normalize();
            const axis = new THREE.Vector3().crossVectors(UPV, hd).normalize();
            const yaw = new THREE.Quaternion().setFromAxisAngle(UPV, Math.random() * Math.PI * 2);
            o.tq = new THREE.Quaternion().setFromAxisAngle(axis, Math.PI / 2).multiply(yaw).multiply(o.q0);
          }
        }
      } else if (o.state === 'settle') {
        o.wp.x += o.vel.x * dt; o.wp.z += o.vel.z * dt; o.vel.multiplyScalar(Math.exp(-6 * dt));
        o.wp.y += (this.heightAt(o.wp.x, o.wp.z) + o.lieY - o.wp.y) * Math.min(1, dt * 12);
        o.wq.slerp(o.tq, Math.min(1, dt * 10));
        if (o.t > 0.5) {
          o.wq.copy(o.tq); o.state = 'rest'; o.active = true; o.r = o.lieR;
          const ax = _v.set(0, 1, 0).applyQuaternion(o.wq); o.x = o.wp.x + ax.x * o.h * 0.45; o.z = o.wp.z + ax.z * o.h * 0.45;
        }
      } else if (o.state === 'slide') {
        const sp = Math.hypot(o.vel.x, o.vel.z), dec = 6.5 * dt;
        if (sp <= dec) { o.vel.set(0, 0, 0); } else { o.vel.x -= o.vel.x / sp * dec; o.vel.z -= o.vel.z / sp * dec; }
        o.wp.x += o.vel.x * dt; o.wp.z += o.vel.z * dt; o.wy *= Math.exp(-3 * dt);
        _q.setFromAxisAngle(UPV, o.wy * dt); o.wq.premultiply(_q);
        o.x = o.wp.x; o.z = o.wp.z; this._axes(o, 0, o.wq);
        if (sp < 0.05 && Math.abs(o.wy) < 0.05) o.state = 'rest';
      } else if (o.state === 'flex') {
        if (o.t > 0.35) { o.thv += (-55 * o.th - 7 * o.thv) * dt; o.th += o.thv * dt; }
        _q.setFromAxisAngle(o.axis, o.th); o.wq.copy(_q).multiply(o.q0);
        if (o.t > 0.6 && Math.abs(o.th) < 0.03 && Math.abs(o.thv) < 0.3) { o.wq.copy(o.q0); o.state = 'rest'; o.active = true; }
      }
      this._writeNode(o);
    }
    for (const t of this.ticks) t.userData.tick(this.time);
  }

  /** Remove a prop (and free its GPU memory). */
  remove(obj, dispose = true) {
    this.surfaces = this.surfaces.filter(s => s.obj !== obj); this.obstacles = this.obstacles.filter(o => o.obj !== obj);
    this.falling = this.falling.filter(f => f.obj !== obj); this.props = this.props.filter(p => p !== obj); this.ticks = this.ticks.filter(p => p !== obj);
    obj.parent?.remove(obj);
    if (dispose) disposeProp(obj);
  }

  /** Re-register after you move/rotate a prop. */
  refresh(obj) { this.remove(obj, false); this.add(obj); }

  /** Serializable layout of every prop made with createProp(). */
  toLayout() {
    const r = (v) => Math.round(v * 100) / 100;
    return this.props.map(o => { const h = o.userData.home || { p: o.position, q: o.quaternion }; const e = new THREE.Euler().setFromQuaternion(h.q, 'YXZ');
      return { type: o.userData.prop.type, x: r(h.p.x), z: r(h.p.z), rot: Math.round(THREE.MathUtils.radToDeg(e.y)), params: o.userData.prop.params }; });
  }

  /** Replace all createProp() props with a saved layout. Returns the new objects. */
  loadLayout(list, { clear = true } = {}) {
    if (clear) [...this.props].forEach(o => this.remove(o));
    const out = [];
    for (const it of list || []) {
      if (!it || !PROP_TYPES[it.type]) continue;
      try { const o = createProp(it.type, it.params); o.position.set(+it.x || 0, 0, +it.z || 0); o.rotation.y = THREE.MathUtils.degToRad(+it.rot || 0); out.push(this.add(o)); }
      catch (e) { console.warn('[strata] skipped a layout item', it, e); } // one bad item never blocks the rest
    }
    return out;
  }

  /** Put every knocked sign, cone, barrier back and repair guardrails. */
  resetAll() {
    for (const f of this.falling) { const h = f.obj.userData.home; f.obj.position.copy(h.p); f.obj.quaternion.copy(h.q); }
    this.falling = [];
    for (const o of this.obstacles) {
      o.active = true; o.touching = false;
      if (o.node) {
        o.node.position.copy(o.home.p); o.node.quaternion.copy(o.home.q); o.obj.updateMatrixWorld(true);
        o.node.getWorldPosition(o.wp); o.node.getWorldQuaternion(o.wq); o.vel.set(0, 0, 0); o.w.set(0, 0, 0); o.wy = 0; o.state = 'rest';
        o.x = o.wp.x; o.z = o.wp.z; o.r = o.def.r; if (o.type === 'box') this._axes(o, 0, o.wq);
      }
    }
    for (const p of this.props) p.userData.repair?.();
  }

  colliders() {
    return {
      obstacles: this.obstacles.filter(o => o.active).map(o => o.type === 'circle'
        ? { type: 'cylinder', x: o.x, z: o.z, radius: o.r, height: o.h || 3, breakaway: o.breakaway, dynamic: o.dyn || null, object: o.obj }
        : { type: 'box', x: o.x, z: o.z, halfX: o.hx, halfZ: o.hz, yaw: Math.atan2(-o.uz, o.ux), height: 1, guardrail: !!o.rail, dynamic: o.dyn || null, object: o.obj }),
      surfaces: this.surfaces.map(s => ({ object: s.obj, sample: (x, z) => this.heightAt(x, z) })),
    };
  }
}

// ================================================================= GENERIC SIGN SYSTEM
export const SCHEMES = {
  regulatory: { bg: '#f4f4f0', fg: '#111111', border: '#111111' },
  red: { bg: '#b8152a', fg: '#f4f4f0', border: '#f4f4f0' },
  warning: { bg: '#f2c200', fg: '#111111', border: '#111111' },
  school: { bg: '#c6dc1e', fg: '#111111', border: '#111111' },
  construction: { bg: '#f07b14', fg: '#111111', border: '#111111' },
  guide: { bg: '#00704a', fg: '#f4f4f0', border: '#f4f4f0' },
  services: { bg: '#1f4fa3', fg: '#f4f4f0', border: '#f4f4f0' },
  black: { bg: '#141414', fg: '#f4f4f0', border: '#f4f4f0' },
  brown: { bg: '#6b3f1d', fg: '#f4f4f0', border: '#f4f4f0' },
};
const KIND_PTS = {
  diamond: [[0, 0.5], [0.5, 0], [0, -0.5], [-0.5, 0]],
  yield: [[-0.5, 0.5], [0.5, 0.5], [0, -0.5]],
  pentagon: [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.12], [0, 0.5], [-0.5, 0.12]],
  octagon: Array.from({ length: 8 }, (_, k) => { const a = Math.PI / 8 + k * Math.PI / 4, R = 0.5 / Math.cos(Math.PI / 8); return [R * Math.cos(a), R * Math.sin(a)]; }),
};
const KIND_C = { diamond: [0, 0, 1.42], yield: [0, 1 / 6, 2.0], pentagon: [0, -0.04, 1.12], octagon: [0, 0, 1.0] };
function kindShape(kind, w, h) {
  if (kind === 'rect') return roundRect(w, h, Math.min(w, h) * 0.06);
  if (kind === 'circle') { const s = new THREE.Shape(); s.absarc(0, 0, w / 2, 0, Math.PI * 2, false); return s; }
  const s = new THREE.Shape(); KIND_PTS[kind].forEach(([x, y], i) => i ? s.lineTo(x * w, y * h) : s.moveTo(x * w, y * h)); s.closePath(); return s;
}
function kindPath(ctx, kind, W, H, inset) {
  ctx.beginPath();
  if (kind === 'rect') { const r = Math.min(W, H) * 0.06; ctx.roundRect(inset, inset, W - 2 * inset, H - 2 * inset, Math.max(1, r - inset * 0.6)); return; }
  if (kind === 'circle') { ctx.arc(W / 2, H / 2, Math.max(1, W / 2 - inset), 0, Math.PI * 2); return; }
  const [cx, cy, f] = KIND_C[kind], s = 1 - inset * f / (Math.min(W, H) / 2);
  KIND_PTS[kind].forEach(([x, y], i) => { const px = (cx + (x - cx) * s + 0.5) * W, py = (0.5 - (cy + (y - cy) * s)) * H; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
  ctx.closePath();
}
function baseArt(ctx, kind, W, H, sch, border = 0.035, margin = 0.014) {
  const m = Math.min(W, H);
  ctx.fillStyle = sch.bg; kindPath(ctx, kind, W, H, 0); ctx.fill();
  if (border > 0) { ctx.fillStyle = sch.border; kindPath(ctx, kind, W, H, m * margin); ctx.fill(); ctx.fillStyle = sch.bg; kindPath(ctx, kind, W, H, m * (margin + border)); ctx.fill(); }
}
const splitLines = (t) => String(t ?? '').split('|').map(s => s.trim()).filter(Boolean);
function textBlock(ctx, lines, cx, top, bottom, maxW, color, capFrac = 0.6) {
  lines = lines.filter(l => l !== '' && l != null); if (!lines.length) return;
  const slot = (bottom - top) / lines.length, cap = slot * capFrac;
  lines.forEach((l, i) => fitText(ctx, String(l).toUpperCase() === l ? l : l, cx, top + slot * (i + 0.5), cap, maxW, color));
}

// Text inside a diamond: each line gets the width actually available at its height.
function diamondText(ctx, lines, W, H, color) {
  lines = lines.filter(Boolean); if (!lines.length) return;
  const n = lines.length, span = n === 1 ? 0.2 : n === 2 ? 0.34 : 0.46, top = H * (0.5 - span / 2), slot = H * span / n;
  lines.forEach((l, i) => { const cy = top + slot * (i + 0.5), edge = Math.abs(cy - H / 2) + slot * 0.35; const avail = W * (1 - 2 * edge / H) - W * 0.16; fitText(ctx, l, W / 2, cy, slot * 0.66, Math.max(W * 0.12, avail), color); });
}
// --- pictograms, drawn in a 100x100 box
function sym(ctx, name, cx, cy, size, color, flip = false) {
  ctx.save(); ctx.translate(cx - size / 2, cy - size / 2); ctx.scale(size / 100, size / 100);
  if (flip) { ctx.translate(100, 0); ctx.scale(-1, 1); }
  ctx.fillStyle = color; ctx.strokeStyle = color; ctx.lineJoin = 'miter'; ctx.lineCap = 'butt';
  const head = (x, y, ang, s = 26) => { ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.beginPath(); ctx.moveTo(0, -s * 0.75); ctx.lineTo(s * 0.62, s * 0.25); ctx.lineTo(-s * 0.62, s * 0.25); ctx.closePath(); ctx.fill(); ctx.restore(); };
  const line = (w, pts) => { ctx.lineWidth = w; ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke(); };
  switch (name) {
    case 'arrow': line(13, [[50, 96], [50, 28]]); head(50, 22, 0, 34); break;
    case 'turn': ctx.lineWidth = 13; ctx.beginPath(); ctx.moveTo(42, 96); ctx.lineTo(42, 52); ctx.quadraticCurveTo(42, 34, 60, 34); ctx.lineTo(70, 34); ctx.stroke(); head(80, 34, Math.PI / 2, 32); break;
    case 'curve': ctx.lineWidth = 13; ctx.beginPath(); ctx.moveTo(38, 96); ctx.lineTo(38, 70); ctx.bezierCurveTo(38, 48, 62, 50, 62, 30); ctx.stroke(); head(62, 20, 0, 32); break;
    case 'uturn': ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(66, 96); ctx.lineTo(66, 44); ctx.arc(48, 44, 18, 0, Math.PI, true); ctx.lineTo(30, 66); ctx.stroke(); head(30, 76, Math.PI, 30); break;
    case 'no': ctx.strokeStyle = '#c8102e'; ctx.lineWidth = 9; ctx.beginPath(); ctx.arc(50, 50, 44, 0, Math.PI * 2); ctx.stroke(); line(9, [[19, 19], [81, 81]]); break;
    case 'signal': ctx.beginPath(); ctx.roundRect(33, 4, 34, 92, 8); ctx.fill(); [['#d81e1e', 22], ['#f2b705', 50], ['#1aa34a', 78]].forEach(([c, y]) => { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(50, y, 11, 0, Math.PI * 2); ctx.fill(); }); break;
    case 'merge': line(13, [[62, 96], [62, 26]]); head(62, 20, 0, 32); ctx.lineWidth = 11; ctx.beginPath(); ctx.moveTo(26, 96); ctx.bezierCurveTo(26, 70, 58, 62, 60, 46); ctx.stroke(); break;
    case 'laneEnds': line(11, [[34, 96], [34, 6]]); ctx.lineWidth = 11; ctx.beginPath(); ctx.moveTo(72, 96); ctx.lineTo(72, 60); ctx.lineTo(46, 30); ctx.lineTo(46, 6); ctx.stroke(); break;
    case 'ped': ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(54, 13, 9, 0, Math.PI * 2); ctx.fill();
      line(12, [[52, 27], [46, 58]]); line(9, [[50, 33], [36, 50]]); line(9, [[50, 33], [66, 46]]); line(10, [[46, 58], [32, 90]]); line(10, [[46, 58], [62, 76], [62, 94]]); break;
    case 'kids': ctx.save(); ctx.translate(-14, 8); ctx.scale(0.85, 0.85); sym(ctx, 'ped', 50, 50, 100, color); ctx.restore(); ctx.save(); ctx.translate(30, 18); ctx.scale(0.72, 0.72); sym(ctx, 'ped', 50, 50, 100, color); ctx.restore(); break;
    case 'deer':
      ctx.beginPath(); ctx.ellipse(46, 52, 25, 11, -0.12, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(64, 50); ctx.lineTo(74, 26); ctx.lineTo(84, 20); ctx.lineTo(93, 24); ctx.lineTo(84, 30); ctx.lineTo(74, 50); ctx.closePath(); ctx.fill();
      ctx.lineCap = 'round'; line(4, [[80, 21], [76, 8], [70, 4]]); line(4, [[77, 12], [83, 6]]); line(4, [[84, 20], [90, 9]]);
      line(6, [[66, 58], [84, 70], [94, 66]]); line(6, [[62, 60], [74, 78], [80, 88]]); line(6, [[28, 56], [12, 66], [6, 78]]); line(6, [[32, 58], [24, 76], [26, 90]]);
      ctx.beginPath(); ctx.moveTo(22, 46); ctx.lineTo(12, 38); ctx.lineTo(20, 50); ctx.fill(); break;
    case 'chevron': ctx.beginPath(); ctx.moveTo(22, 6); ctx.lineTo(50, 6); ctx.lineTo(80, 50); ctx.lineTo(50, 94); ctx.lineTo(22, 94); ctx.lineTo(52, 50); ctx.closePath(); ctx.fill(); break;
    case 'rrx': line(9, [[10, 10], [90, 90]]); line(9, [[90, 10], [10, 90]]); break;
    case 'keepRight': ctx.beginPath(); ctx.roundRect(16, 56, 22, 40, 6); ctx.fill(); ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(30, 4); ctx.lineTo(30, 26); ctx.lineTo(62, 50); ctx.lineTo(62, 76); ctx.stroke(); head(62, 86, Math.PI, 30); break;
    case 'stopSmall': { ctx.fillStyle = '#b8152a'; ctx.beginPath(); for (let k = 0; k < 8; k++) { const a = Math.PI / 8 + k * Math.PI / 4; const x = 50 + 46 * Math.cos(a), y = 50 + 46 * Math.sin(a); k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.closePath(); ctx.fill(); fitText(ctx, 'STOP', 50, 50, 26, 72, '#f4f4f0'); break; }
    case 'hill': ctx.beginPath(); ctx.moveTo(4, 90); ctx.lineTo(44, 50); ctx.lineTo(96, 50); ctx.lineTo(96, 90); ctx.closePath(); ctx.fill(); ctx.fillStyle = '#f2c200'; ctx.beginPath(); ctx.roundRect(52, 26, 30, 16, 4); ctx.fill(); ctx.fillStyle = color; ctx.beginPath(); ctx.roundRect(50, 28, 34, 14, 5); ctx.fill(); ctx.beginPath(); ctx.arc(57, 44, 5, 0, 7); ctx.arc(77, 44, 5, 0, 7); ctx.fill(); break;
    case 'slippery': ctx.beginPath(); ctx.roundRect(30, 12, 40, 26, 8); ctx.fill(); ctx.beginPath(); ctx.arc(38, 40, 6, 0, 7); ctx.arc(62, 40, 6, 0, 7); ctx.fill(); ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(28, 92); ctx.bezierCurveTo(44, 78, 30, 62, 46, 52); ctx.moveTo(72, 92); ctx.bezierCurveTo(56, 78, 70, 62, 54, 52); ctx.stroke(); break;
  }
  ctx.restore();
}
const ARROW_ANG = { up: 0, right: Math.PI / 2, down: Math.PI, left: -Math.PI / 2, upright: Math.PI / 4, upleft: -Math.PI / 4 };

// Post-mounted sign from a shape + art function. p = params (size, bottom, posts, breakaway, plaque)
function postSign(name, p, { kind, aspect = 1, scheme, draw, border = 0.035, plaqueScheme }) {
  const sch = typeof scheme === 'string' ? SCHEMES[scheme] : scheme;
  const w = +p.size || 0.76, h = w * aspect, PX = 512, k = PX / Math.max(w, h);
  const art_ = art('ps:' + name + JSON.stringify(p) + kind + aspect, () => {
    const [c, x] = canvas(Math.max(8, Math.round(w * k)), Math.max(8, Math.round(h * k)));
    baseArt(x, kind, c.width, c.height, sch, border); draw(x, c.width, c.height, sch); grain(x, c.width, c.height, 7, 13); return tex(c);
  });
  const panel = signPanel(kindShape(kind, w, h), w, h, art_);
  const plaque = splitLines(p.plaque);
  let plH = 0, plW = 0;
  if (plaque.length) { plW = (kind === 'diamond' ? 0.62 : 0.8) * w; plH = plW * (0.24 + 0.14 * plaque.length); }
  const bottom = +p.bottom || 2.13;
  const g = postMount(name, panel, w, h, { bottom: bottom + (plH ? plH + 0.05 : 0), posts: +p.posts || 1, breakaway: p.breakaway !== false });
  if (plH) {
    const ps = SCHEMES[plaqueScheme || (typeof scheme === 'string' ? scheme : 'regulatory')] || sch;
    const pt = art('pl:' + plaque.join('|') + plW + plH + JSON.stringify(ps), () => { const [c, x] = canvas(384, Math.round(384 * plH / plW)); baseArt(x, 'rect', c.width, c.height, ps, 0.04); textBlock(x, plaque, c.width / 2, c.height * 0.12, c.height * 0.88, c.width * 0.86, ps.fg, 0.62); return tex(c); });
    const pp = signPanel(roundRect(plW, plH, 0.02), plW, plH, pt); pp.position.set(0, bottom + plH / 2, 0); g.add(pp);
  }
  g.userData.fallHeight = bottom + h;
  return g;
}

// --- special assemblies
function streetBlade(name, len) {
  const h = 0.2, w = Math.max(0.6, len);
  const t = art('blade:' + name + w, () => { const [c, x] = canvas(Math.round(w * 240), Math.round(h * 240)); baseArt(x, 'rect', c.width, c.height, SCHEMES.guide, 0.06, 0.03); fitText(x, name, c.width / 2, c.height / 2, c.height * 0.5, c.width * 0.9, '#f4f4f0'); return tex(c); });
  const g = new THREE.Group(); const a = signPanel(roundRect(w, h, 0.02), w, h, t); a.position.z = 0.003; g.add(a);
  const b = signPanel(roundRect(w, h, 0.02), w, h, t); b.rotation.y = Math.PI; b.position.z = -0.003; g.add(b);
  return g;
}
function roundPole(h, r = 0.03) { const p = mesh(new THREE.CylinderGeometry(r, r * 1.1, h, 12), M.galv); p.position.y = h / 2; const cap = mesh(new THREE.SphereGeometry(r * 1.15, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2), M.galv); cap.position.y = h; const g = new THREE.Group(); g.add(p, cap); return g; }
const bladeLen = (t) => 0.25 + String(t).length * 0.085;

function buildStreetName(p) {
  const g = new THREE.Group(); g.name = 'StreetName';
  const H = +p.height || 2.9; g.add(roundPole(H + 0.45));
  if (p.name1) { const b = streetBlade(p.name1, bladeLen(p.name1)); b.position.set(0, H + 0.12, 0); b.rotation.y = 0; g.add(b); }
  if (p.name2) { const b = streetBlade(p.name2, bladeLen(p.name2)); b.position.set(0, H + 0.36, 0); b.rotation.y = Math.PI / 2; g.add(b); }
  if (p.stop) { const s = createProp('stop', { size: 0.762, bottom: 2.13, posts: '1' }); const panel = s.children[0]; panel.position.z = 0.04; g.add(panel); }
  g.userData.strata = { kind: 'obstacle', obstacles: [{ type: 'circle', x: 0, z: 0, r: 0.05, breakaway: true }] };
  g.userData.fallHeight = H;
  return g;
}

function plate(w, h, drawFn, key) { const t = art('plate:' + key, () => { const [c, x] = canvas(Math.round(w * 400), Math.round(h * 400)); x.fillStyle = '#f4f4f0'; x.fillRect(0, 0, c.width, c.height); drawFn(x, c.width, c.height); return tex(c); }); return signPanel(roundRect(w, h, 0.015), w, h, t); }
function buildRouteMarker(p) {
  const g = new THREE.Group(); g.name = 'RouteMarker';
  let y = +p.bottom || 1.5; const items = [];
  if (p.arrow && p.arrow !== 'none') items.push(plate(0.53, 0.38, (x, W, H) => drawArrow(x, W / 2, H / 2, H * 0.8, ARROW_ANG[p.arrow] ?? 0, '#111'), 'ar' + p.arrow));
  const s = p.shield || 'I', S = 0.61;
  items.push(plate(S, S, (x, W, H) => { if (s === 'I') drawShield(x, 'I', p.num, W * 0.04, H * 0.03, W * 0.92); else drawShield(x, s, p.num, 0, 0, W); }, 'sh' + s + p.num));
  if (p.direction) items.push(plate(0.61, 0.3, (x, W, H) => { x.strokeStyle = '#111'; x.lineWidth = 6; x.strokeRect(5, 5, W - 10, H - 10); fitText(x, p.direction, W / 2, H / 2, H * 0.48, W * 0.86, '#111'); }, 'dir' + p.direction));
  if (p.aux) items.push(plate(0.61, 0.3, (x, W, H) => { x.strokeStyle = '#111'; x.lineWidth = 6; x.strokeRect(5, 5, W - 10, H - 10); fitText(x, p.aux, W / 2, H / 2, H * 0.44, W * 0.86, '#111'); }, 'aux' + p.aux));
  for (const it of items) { const bb = new THREE.Box3().setFromObject(it), hh = bb.max.y - bb.min.y; it.position.y = y + hh / 2; y += hh + 0.04; g.add(it); }
  const post = perfPost(y - 0.06); post.position.z = -0.03; g.add(post);
  g.userData.strata = { kind: 'obstacle', obstacles: [{ type: 'circle', x: 0, z: -0.03, r: 0.045, breakaway: true }] };
  g.userData.fallHeight = y;
  return g;
}

function buildCrossbuck(p) {
  const g = new THREE.Group(); g.name = 'Crossbuck';
  const w = 1.22, h = 0.23, top = +p.height || 2.75;
  const words = ['RAILROAD', 'CROSSING'];
  words.forEach((wd, i) => {
    const tt = art('xb' + wd, () => { const [c, x] = canvas(512, 96); x.fillStyle = '#f4f4f0'; x.fillRect(0, 0, 512, 96); x.strokeStyle = '#111'; x.lineWidth = 6; x.strokeRect(4, 4, 504, 88); fitText(x, wd, 256, 48, 52, 440, '#111'); return tex(c); });
    const b = signPanel(roundRect(w, h, 0.015), w, h, tt); b.rotation.z = (i ? -1 : 1) * Math.PI / 4; b.position.set(0, top, 0.006 * (i + 1)); g.add(b);
  });
  const lines = splitLines(p.tracks);
  if (lines.length) { const pl = postSign('x', { size: 0.69, bottom: top - 1.25, plaque: '' }, { kind: 'rect', aspect: 0.39, scheme: 'regulatory', draw: (x, W, H, s) => textBlock(x, lines, W / 2, H * 0.15, H * 0.85, W * 0.85, s.fg) }); const pn = pl.children[0]; pn.position.y = top - 0.85; g.add(pn); }
  const post = mesh(new THREE.CylinderGeometry(0.045, 0.05, top + 0.1, 12), M.galv); post.position.set(0, (top + 0.1) / 2, -0.06); g.add(post);
  // white retroreflective strip on the post
  const strip = mesh(new THREE.BoxGeometry(0.03, 1.2, 0.002), M.reflector, { cast: false }); strip.position.set(0, 1.0, -0.012); g.add(strip);
  g.userData.strata = { kind: 'obstacle', obstacles: [{ type: 'circle', x: 0, z: -0.06, r: 0.06, breakaway: false }] };
  return g;
}

// ================================================================= TRAFFIC DEVICES (cones, drums, flex posts, barricades)
const mats = {
  get orange() { return once('mOr', () => new THREE.MeshStandardMaterial({ color: 0xff5a0a, roughness: 0.55 })); },
  get white() { return once('mWh', () => { const m = new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.35, emissive: 0xffffff, emissiveIntensity: retro * 0.6 }); signMats.add(m); return m; }); },
  get blackRubber() { return once('mBr', () => new THREE.MeshStandardMaterial({ color: 0x161616, roughness: 0.95 })); },
  get amberOn() { return once('mAmOn', () => new THREE.MeshStandardMaterial({ color: 0xffb000, emissive: 0xffa000, emissiveIntensity: 2.2 })); },
  get amberOff() { return once('mAmOff', () => new THREE.MeshStandardMaterial({ color: 0x8a5a00, roughness: 0.3 })); },
  get plasticOrange() { return once('mPo', () => new THREE.MeshStandardMaterial({ color: 0xf26a10, roughness: 0.45 })); },
  get plasticWhite() { return once('mPw', () => new THREE.MeshStandardMaterial({ color: 0xeeeeee, roughness: 0.45 })); },
  get wood() { return once('mWood', () => { const [c, x] = canvas(64, 128); x.fillStyle = '#7a5532'; x.fillRect(0, 0, 64, 128); for (let i = 0; i < 40; i++) { x.fillStyle = `rgba(40,25,10,${0.1 + Math.random() * 0.2})`; x.fillRect(Math.random() * 64, 0, 1 + Math.random() * 2, 128); } return new THREE.MeshStandardMaterial({ map: tex(c), roughness: 0.9 }); }); },
};

function frustum(rb, rt, h, mat, y0, seg = 20) { const m = mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat); m.position.y = y0 + h / 2; return m; }

function coneNode(H) {
  const n = new THREE.Group(); n.name = 'Cone';
  const base = mesh(new THREE.BoxGeometry(0.38 * H / 0.71, 0.035, 0.38 * H / 0.71), mats.blackRubber); base.position.y = 0.0175; n.add(base);
  const rb = 0.15 * H / 0.71, rt = 0.025, body = H - 0.035, r = (y) => rb + (rt - rb) * (y / body);
  const bands = H > 0.8 ? [[0.62, 0.72], [0.82, 0.9]] : [[0.55, 0.68], [0.76, 0.86]]; // white retro collars (fraction of height)
  let y = 0; const cuts = [0, ...bands.flat(), 1];
  for (let i = 0; i < cuts.length - 1; i++) { const a = cuts[i] * body, b = cuts[i + 1] * body; n.add(frustum(r(a), r(b), b - a, i % 2 ? mats.white : mats.orange, 0.035 + a)); y = b; }
  return n;
}
function drumNode(light) {
  const n = new THREE.Group(); n.name = 'Drum';
  n.add(frustum(0.4, 0.38, 0.09, mats.blackRubber, 0, 18));
  const H = 0.92, bands = 5; for (let i = 0; i < bands; i++) { const a = 0.06 + i * (H - 0.06) / bands, b = a + (H - 0.06) / bands; n.add(frustum(0.29 - a * 0.03, 0.29 - b * 0.03, b - a, i % 2 ? mats.white : mats.orange, a, 22)); }
  const top = frustum(0.262, 0.2, 0.05, mats.orange, H, 22); n.add(top);
  const handle = mesh(new THREE.TorusGeometry(0.07, 0.015, 6, 14, Math.PI), mats.orange); handle.position.y = H + 0.05; n.add(handle);
  if (light) { const l = mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.05, 16), mats.amberOff); l.rotation.x = Math.PI / 2; l.position.set(0, H + 0.14, 0.03); l.name = 'lamp'; n.add(l); }
  return n;
}
function flexNode() {
  const n = new THREE.Group(); n.name = 'FlexPost';
  const base = mesh(new THREE.CylinderGeometry(0.12, 0.13, 0.04, 16), mats.blackRubber); base.position.y = 0.02; n.add(base);
  const cuts = [0, 0.72, 0.8, 0.88, 0.94, 1.0], H = 1.07;
  for (let i = 0; i < cuts.length - 1; i++) n.add(frustum(0.04, 0.04, (cuts[i + 1] - cuts[i]) * H, (i === 1 || i === 3) ? mats.white : mats.orange, 0.04 + cuts[i] * H, 12));
  return n;
}
function rowOf(make, count, spacing) { const g = new THREE.Group(); const nodes = []; for (let i = 0; i < count; i++) { const n = make(i); n.position.x = (i - (count - 1) / 2) * spacing; g.add(n); nodes.push(n); } return [g, nodes]; }
function blinker(g, rate = 1.0) {
  const lamps = []; g.traverse(o => { if (o.name === 'lamp') lamps.push(o); });
  if (lamps.length) g.userData.tick = (t) => { const on = (t * rate) % 1 < 0.45; for (const l of lamps) l.material = on ? mats.amberOn : mats.amberOff; };
}

function buildCones(p) {
  const H = +p.height || 0.71, n = clamp(Math.round(+p.count || 1), 1, 40);
  const [g, nodes] = rowOf(() => coneNode(H), n, +p.spacing || 3); g.name = n > 1 ? 'ConeRow' : 'Cone';
  g.userData.strata = { kind: 'obstacle', obstacles: nodes.map(nd => ({ type: 'circle', node: nd, r: 0.17 * H / 0.71, dyn: 'fly', mass: H > 0.8 ? 5 : 3, lieY: 0.12 * H / 0.71, lieR: 0.3, h: H })) };
  return g;
}
function buildDrums(p) {
  const n = clamp(Math.round(+p.count || 1), 1, 30);
  const [g, nodes] = rowOf(() => drumNode(!!p.light), n, +p.spacing || 4); g.name = n > 1 ? 'DrumRow' : 'Drum';
  g.userData.strata = { kind: 'obstacle', obstacles: nodes.map(nd => ({ type: 'circle', node: nd, r: 0.36, dyn: 'fly', mass: 18, lieY: 0.3, lieR: 0.5, h: 0.95 })) };
  blinker(g);
  return g;
}
function buildFlexPosts(p) {
  const n = clamp(Math.round(+p.count || 1), 1, 40);
  const [g, nodes] = rowOf(() => flexNode(), n, +p.spacing || 2); g.name = n > 1 ? 'FlexPostRow' : 'FlexPost';
  g.userData.strata = { kind: 'obstacle', obstacles: nodes.map(nd => ({ type: 'circle', node: nd, r: 0.07, dyn: 'flex', h: 1.1 })) };
  return g;
}
function stripeTex(key, flip) {
  return art('stripe' + key + flip, () => { const [c, x] = canvas(512, 96); x.fillStyle = '#f4f4f0'; x.fillRect(0, 0, 512, 96); x.fillStyle = '#f07b14'; for (let i = -2; i < 8; i++) { const x0 = i * 96; x.beginPath(); if (flip) { x.moveTo(x0, 96); x.lineTo(x0 + 48, 96); x.lineTo(x0 + 144, 0); x.lineTo(x0 + 96, 0); } else { x.moveTo(x0, 0); x.lineTo(x0 + 48, 0); x.lineTo(x0 + 144, 96); x.lineTo(x0 + 96, 96); } x.closePath(); x.fill(); } grain(x, 512, 96, 8, 3); return tex(c); });
}
function buildBarricade(p) {
  const g = new THREE.Group(); g.name = 'Barricade';
  const w = +p.width || 2.4, legs = [-w / 2 + 0.25, w / 2 - 0.25], rails = [0.45, 0.85, 1.25];
  for (const lx of legs) {
    const leg = mesh(new THREE.BoxGeometry(0.06, 1.42, 0.06), M.galv); leg.position.set(lx, 0.71, -0.03); g.add(leg);
    const foot = mesh(new THREE.BoxGeometry(0.08, 0.06, 0.9), M.galv); foot.position.set(lx, 0.03, -0.03); g.add(foot);
    const sand = mesh(new THREE.BoxGeometry(0.3, 0.12, 0.45), new THREE.MeshStandardMaterial({ color: 0x3a3f2a, roughness: 1 })); sand.position.set(lx, 0.06, 0.35); sand.material.userData.own = true; g.add(sand);
  }
  rails.forEach((y, i) => { const flip = p.arrowLeft ? true : false; const b = signPanel(roundRect(w, 0.2, 0.01), w, 0.2, stripeTex('b', flip)); b.position.set(0, y, 0); g.add(b); void i; });
  if (p.lights) for (const lx of legs) { const l = mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.05, 16), mats.amberOff); l.rotation.x = Math.PI / 2; l.position.set(lx, 1.5, 0.02); l.name = 'lamp'; g.add(l); }
  const txt = splitLines(p.sign);
  if (txt.length) {
    const sw = 1.22, sh = 0.76;
    const t = art('rc' + txt.join('|'), () => { const [c, x] = canvas(512, 320); baseArt(x, 'rect', 512, 320, SCHEMES.regulatory); textBlock(x, txt, 256, 50, 270, 440, '#111'); grain(x, 512, 320, 7, 9); return tex(c); });
    const s = signPanel(roundRect(sw, sh, 0.03), sw, sh, t); s.position.set(0, 1.42 + sh / 2 + 0.05, 0.03); g.add(s);
  }
  blinker(g, 1.1);
  g.userData.strata = { kind: 'obstacle', obstacles: legs.map(x => ({ type: 'circle', x, z: -0.03, r: 0.12, breakaway: true })) };
  g.userData.fallHeight = 1.5;
  return g;
}

// ================================================================= BARRIERS
// Path helper: a run of given length with a bend (degrees) spread evenly along it, centred on the origin.
function runPath(L, bendDeg, n) {
  const th = THREE.MathUtils.degToRad(bendDeg || 0), pts = []; let x = 0, z = 0;
  for (let i = 0; i <= n; i++) {
    const phi = -th / 2 + th * i / n;
    if (i > 0) { const pm = -th / 2 + th * (i - 0.5) / n; x += Math.cos(pm) * L / n; z += -Math.sin(pm) * L / n; }
    pts.push({ x, z, phi, t: L * i / n });
  }
  const m = pts[Math.floor(n / 2)], m2 = pts[Math.ceil(n / 2)], cx = (m.x + m2.x) / 2, cz = (m.z + m2.z) / 2;
  pts.forEach(p => { p.x -= cx; p.z -= cz; p.dx = Math.cos(p.phi); p.dz = -Math.sin(p.phi); p.nx = Math.sin(p.phi); p.nz = Math.cos(p.phi); });
  return pts;
}

function buildConcreteBarrier(p) {
  const g = new THREE.Group(); g.name = 'ConcreteBarrier';
  const L = +p.length || 12, seg = 3.8, n = Math.max(1, Math.round(L / seg)), pts = runPath(L, p.bend, n);
  const obstacles = [];
  for (let i = 0; i < n; i++) {
    const a = pts[i], b = pts[i + 1], len = Math.hypot(b.x - a.x, b.z - a.z) - 0.02;
    const s = jerseyBarrier(len); s.rotation.y = Math.atan2(b.x - a.x, b.z - a.z); s.position.set((a.x + b.x) / 2, 0, (a.z + b.z) / 2); g.add(s);
    if (p.reflectors) { const r = mesh(new THREE.BoxGeometry(0.02, 0.08, 0.1), new THREE.MeshStandardMaterial({ color: 0xffc000, emissive: 0xffa000, emissiveIntensity: 0.3 }), { cast: false }); r.material.userData.own = true; r.position.set((a.x + b.x) / 2 + a.nx * 0.12, 0.7, (a.z + b.z) / 2 + a.nz * 0.12); r.rotation.y = s.rotation.y; g.add(r); }
    obstacles.push({ type: 'box', x: (a.x + b.x) / 2, z: (a.z + b.z) / 2, hx: len / 2, hz: 0.3, rot: Math.atan2(-(b.z - a.z), b.x - a.x) });
  }
  g.userData.strata = { kind: 'obstacle', obstacles };
  return g;
}

function waterBarrierNode(white) {
  const n = new THREE.Group(); n.name = 'WaterBarrier';
  const s = new THREE.Shape(); [[-0.23, 0], [0.23, 0], [0.2, 0.12], [0.1, 0.8], [-0.1, 0.8], [-0.2, 0.12]].forEach(([a, b], i) => i ? s.lineTo(a, b) : s.moveTo(a, b)); s.closePath();
  const geo = new THREE.ExtrudeGeometry(s, { depth: 1.78, bevelEnabled: true, bevelSize: 0.025, bevelThickness: 0.025, bevelSegments: 2 }); geo.translate(0, 0, -0.89); geo.rotateY(Math.PI / 2);
  n.add(mesh(geo, white ? mats.plasticWhite : mats.plasticOrange));
  for (const x of [-0.6, 0.6]) { const sl = mesh(new THREE.BoxGeometry(0.22, 0.04, 0.24), mats.blackRubber); sl.position.set(x, 0.42, 0); n.add(sl); }
  const cap = mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.03, 12), white ? mats.plasticOrange : mats.plasticWhite); cap.position.set(0, 0.82, 0); n.add(cap);
  return n;
}
function buildWaterBarriers(p) {
  const n = clamp(Math.round(+p.count || 4), 1, 30);
  const [g, nodes] = rowOf((i) => waterBarrierNode(i % 2 === 1), n, 1.84); g.name = 'WaterBarriers';
  g.userData.strata = { kind: 'obstacle', obstacles: nodes.map(nd => ({ type: 'box', node: nd, hx: 0.92, hz: 0.24, dyn: 'push', mass: +p.mass || 450 })) };
  return g;
}

// W-beam guardrail that can be curved (bend) and dents where you hit it.
function buildGuardrail(p) {
  const g = new THREE.Group(); g.name = 'Guardrail';
  const L = Math.max(4, +p.length || 30), step = +p.bend ? 0.25 : 1.0, n = Math.ceil(L / step), pts = runPath(L, p.bend, n);
  const prof = [[-0.156, 0.0], [-0.15, 0.02], [-0.105, 0.083], [-0.06, 0.083], [-0.03, 0.035], [0.03, 0.035], [0.06, 0.083], [0.105, 0.083], [0.15, 0.02], [0.156, 0.0]];
  const RAILY = 0.63, BLOCK = 0.2, POSTOFF = BLOCK + 0.08;
  const dent = new Float32Array(n + 1);
  const pos = new Float32Array((n + 1) * prof.length * 3), uv = [], idx = [];
  for (let i = 0; i <= n; i++) for (let j = 0; j < prof.length; j++) uv.push(pts[i].t / 4, j / (prof.length - 1));
  for (let i = 0; i < n; i++) for (let j = 0; j < prof.length - 1; j++) { const a = i * prof.length + j, b = a + 1, c = a + prof.length, d = c + 1; idx.push(a, c, b, b, c, d); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx);
  const railMat = once('railMat', () => { const [c, x] = canvas(128, 64); x.fillStyle = '#a7acae'; x.fillRect(0, 0, 128, 64); grain(x, 128, 64, 30, 77); for (let i = 0; i < 6; i++) { x.fillStyle = 'rgba(120,90,60,0.12)'; x.fillRect(Math.random() * 128, Math.random() * 64, 20, 6); } const t = tex(c, { repeat: true }); return new THREE.MeshStandardMaterial({ map: t, roughness: 0.45, metalness: 0.8, side: THREE.DoubleSide }); });
  const rail = mesh(geo, railMat); g.add(rail);
  const rebuild = () => {
    let k = 0;
    for (let i = 0; i <= n; i++) { const P = pts[i], d = dent[i]; const sag = d * 0.35; for (const [py, pz] of prof) { const off = pz - d; pos[k++] = P.x + P.nx * off; pos[k++] = RAILY + py - sag; pos[k++] = P.z + P.nz * off; } }
    geo.attributes.position.needsUpdate = true; geo.computeVertexNormals(); geo.computeBoundingSphere();
  };
  // posts every 6'3" with blockouts; wood or steel
  const posts = [], spacing = 1.905, np = Math.max(2, Math.floor(L / spacing) + 1);
  const wood = p.posts === 'wood';
  for (let k = 0; k < np; k++) {
    const t = Math.min(L, k * spacing + (L - (np - 1) * spacing) / 2), i = Math.round(t / step), P = pts[i];
    const pg = new THREE.Group();
    const post = wood ? mesh(new THREE.BoxGeometry(0.15, 0.82, 0.2), mats.wood) : mesh(iSection(0.15, 0.1, 0.82), M.galv); post.position.y = 0.41; pg.add(post);
    const blk = mesh(new THREE.BoxGeometry(0.15, 0.36, BLOCK - 0.01), wood ? mats.wood : mats.blackRubber); blk.position.set(0, RAILY, POSTOFF - BLOCK / 2 - 0.005 - 0.08 + 0.08); pg.add(blk);
    if (k % 4 === 0) { const r = mesh(new THREE.BoxGeometry(0.08, 0.1, 0.005), M.reflector, { cast: false }); r.position.set(0, RAILY + 0.24, POSTOFF - 0.02); pg.add(r); }
    pg.position.set(P.x - P.nx * POSTOFF, 0, P.z - P.nz * POSTOFF); pg.rotation.y = P.phi; pg.userData.i = i; g.add(pg); posts.push(pg);
  }
  // end treatments: energy-absorbing terminal head upstream (t = 0), buffer end downstream
  if (p.ends !== 'none') {
    const hz = art('termHead', () => { const [c, x] = canvas(128, 128); x.fillStyle = '#f2c200'; x.fillRect(0, 0, 128, 128); x.fillStyle = '#111'; for (let i = -4; i < 8; i++) { x.beginPath(); x.moveTo(i * 32, 128); x.lineTo(i * 32 + 16, 128); x.lineTo(i * 32 + 144, 0); x.lineTo(i * 32 + 128, 0); x.closePath(); x.fill(); } return tex(c); });
    const P0 = pts[0], head = new THREE.Group();
    const box = mesh(new THREE.BoxGeometry(0.5, 0.62, 0.32), M.steel); head.add(box);
    const face = mesh(new THREE.PlaneGeometry(0.3, 0.55), faceMat(hz), { cast: false }); face.rotation.y = -Math.PI / 2; face.position.x = -0.252; head.add(face);
    head.position.set(P0.x - P0.dx * 0.25 - P0.nx * 0.08, RAILY - 0.02, P0.z - P0.dz * 0.25 - P0.nz * 0.08); head.rotation.y = P0.phi; g.add(head);
    const Pn = pts[n], buf = mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.31, 14, 1, true, 0, Math.PI), railMat); buf.rotation.set(0, Pn.phi + Math.PI / 2, 0);
    buf.position.set(Pn.x + Pn.dx * 0.02 - Pn.nx * 0.12, RAILY, Pn.z + Pn.dz * 0.02 - Pn.nz * 0.12); g.add(buf);
  }
  rebuild();
  // collision boxes every ~2 m along the run
  const obstacles = [], segN = Math.max(1, Math.round(L / 2));
  for (let s = 0; s < segN; s++) {
    const i0 = Math.round(n * s / segN), i1 = Math.round(n * (s + 1) / segN), a = pts[i0], b = pts[i1], im = pts[Math.round((i0 + i1) / 2)];
    const len = Math.hypot(b.x - a.x, b.z - a.z);
    obstacles.push({ type: 'box', x: (a.x + b.x) / 2 - im.nx * 0.07, z: (a.z + b.z) / 2 - im.nz * 0.07, hx: len / 2 + 0.05, hz: 0.15, rot: Math.atan2(-(b.z - a.z), b.x - a.x), rail: { t0: a.t, t1: b.t } });
  }
  g.userData.strata = { kind: 'obstacle', obstacles };
  g.userData.dent = (t, amount) => {
    let changed = false;
    for (let i = 0; i <= n; i++) { const w = Math.exp(-(((pts[i].t - t) / 1.3) ** 2)); const v = Math.min(0.55, amount * w); if (v > dent[i] + 0.002) { dent[i] = v; changed = true; } }
    if (!changed) return; rebuild();
    for (const pg of posts) { const d = dent[pg.userData.i]; pg.children[0].rotation.x = 0; pg.rotation.set(0, pts[pg.userData.i].phi, 0); pg.rotateX(-Math.min(0.9, d / 0.6)); }
  };
  g.userData.repair = () => { dent.fill(0); rebuild(); for (const pg of posts) pg.rotation.set(0, pts[pg.userData.i].phi, 0); };
  return g;
}
function iSection(d, bf, h) {
  const tf = 0.008, tw = 0.006, s = new THREE.Shape();
  s.moveTo(-bf / 2, -d / 2); s.lineTo(bf / 2, -d / 2); s.lineTo(bf / 2, -d / 2 + tf); s.lineTo(tw / 2, -d / 2 + tf); s.lineTo(tw / 2, d / 2 - tf); s.lineTo(bf / 2, d / 2 - tf);
  s.lineTo(bf / 2, d / 2); s.lineTo(-bf / 2, d / 2); s.lineTo(-bf / 2, d / 2 - tf); s.lineTo(-tw / 2, d / 2 - tf); s.lineTo(-tw / 2, -d / 2 + tf); s.lineTo(-bf / 2, -d / 2 + tf); s.closePath();
  return new THREE.BoxGeometry(bf, h, d);   // baked for the game: a plain box post (the I-section was 44 triangles a post)
}

// ================================================================= EDITABLE PROP REGISTRY
// Every prop type: label, category, fields (for an editor UI), defaults, build(params).
const F = {
  num: (k, label, min, max, step = 1) => ({ k, label, type: 'number', min, max, step }),
  text: (k, label, hint = '') => ({ k, label, type: 'text', hint }),
  sel: (k, label, options) => ({ k, label, type: 'select', options }),
  bool: (k, label) => ({ k, label, type: 'bool' }),
};
const MOUNT = [F.num('size', 'Sign width (m)', 0.3, 2.5, 0.01), F.num('bottom', 'Height to bottom (m)', 0.5, 4, 0.05), F.sel('posts', 'Posts', ['1', '2']), F.bool('breakaway', 'Breakaway post')];
const PLAQUE = F.text('plaque', 'Plaque under sign', 'use | for a new line');
const SIDES = ['right', 'left'];
const SHIELDS = ['I', 'US', 'M', 'none'];
const ARROWS = ['none', 'down', 'up', 'upright', 'upleft', 'right', 'left'];
const mount = { size: 0.762, bottom: 2.13, posts: '1', breakaway: true };

export const PROP_TYPES = {
  // ---- regulatory
  stop: { label: 'Stop', cat: 'Regulatory', defaults: { ...mount, text: 'STOP', plaque: '' }, fields: [F.text('text', 'Text'), PLAQUE, ...MOUNT],
    build: (p) => postSign('StopSign', p, { kind: 'octagon', scheme: 'red', border: 0.025, plaqueScheme: 'red', draw: (x, W, H, s) => fitText(x, p.text, W / 2, H / 2, H * 0.33, W * 0.74, s.fg) }) },
  yield: { label: 'Yield', cat: 'Regulatory', defaults: { ...mount, size: 0.914, text: 'YIELD', plaque: '' }, fields: [F.text('text', 'Text'), PLAQUE, ...MOUNT],
    build: (p) => postSign('YieldSign', p, { kind: 'yield', aspect: 0.866, scheme: { bg: '#f4f4f0', fg: '#b8152a', border: '#b8152a' }, border: 0.09, draw: (x, W, H, s) => fitText(x, p.text, W / 2, H * 0.27, H * 0.095, W * 0.44, s.fg) }) },
  doNotEnter: { label: 'Do Not Enter', cat: 'Regulatory', defaults: { ...mount, top: 'DO NOT', bottomText: 'ENTER' }, fields: [F.text('top', 'Top text'), F.text('bottomText', 'Bottom text'), ...MOUNT],
    build: (p) => postSign('DoNotEnter', p, { kind: 'rect', scheme: 'regulatory', border: 0, draw: (x, W, H) => { x.fillStyle = '#b8152a'; x.beginPath(); x.arc(W / 2, H / 2, W * 0.44, 0, 7); x.fill(); x.fillStyle = '#f4f4f0'; x.fillRect(W * 0.14, H * 0.44, W * 0.72, H * 0.12); fitText(x, p.top, W / 2, H * 0.3, H * 0.1, W * 0.56, '#f4f4f0'); fitText(x, p.bottomText, W / 2, H * 0.7, H * 0.1, W * 0.56, '#f4f4f0'); } }) },
  wrongWay: { label: 'Wrong Way', cat: 'Regulatory', defaults: { ...mount, size: 0.914, lines: 'WRONG|WAY' }, fields: [F.text('lines', 'Text', '| = new line'), ...MOUNT],
    build: (p) => postSign('WrongWay', p, { kind: 'rect', aspect: 0.667, scheme: 'red', draw: (x, W, H, s) => textBlock(x, splitLines(p.lines), W / 2, H * 0.12, H * 0.88, W * 0.84, s.fg) }) },
  oneWay: { label: 'One Way', cat: 'Regulatory', defaults: { ...mount, size: 0.914, dir: 'right', text: 'ONE WAY' }, fields: [F.sel('dir', 'Arrow', SIDES), F.text('text', 'Text'), ...MOUNT],
    build: (p) => postSign('OneWay', p, { kind: 'rect', aspect: 0.333, scheme: 'black', border: 0.02, draw: (x, W, H) => { x.save(); if (p.dir === 'left') { x.translate(W, 0); x.scale(-1, 1); } x.fillStyle = '#f4f4f0'; x.beginPath(); x.moveTo(W * 0.06, H * 0.32); x.lineTo(W * 0.72, H * 0.32); x.lineTo(W * 0.72, H * 0.14); x.lineTo(W * 0.94, H * 0.5); x.lineTo(W * 0.72, H * 0.86); x.lineTo(W * 0.72, H * 0.68); x.lineTo(W * 0.06, H * 0.68); x.closePath(); x.fill(); x.restore(); fitText(x, p.text, p.dir === 'left' ? W * 0.56 : W * 0.44, H / 2, H * 0.24, W * 0.56, '#111'); } }) },
  speedLimit: { label: 'Speed Limit', cat: 'Regulatory', defaults: { ...mount, size: 0.61, top: 'SPEED', mid: 'LIMIT', limit: 70, plaque: '' }, fields: [F.num('limit', 'Speed', 5, 90, 5), F.text('top', 'Line 1'), F.text('mid', 'Line 2'), PLAQUE, ...MOUNT],
    build: (p) => postSign('SpeedLimit', p, { kind: 'rect', aspect: 1.25, scheme: 'regulatory', border: 0.025, draw: (x, W, H, s) => { textBlock(x, [p.top, p.mid], W / 2, H * 0.06, H * 0.42, W * 0.82, s.fg, 0.55); fitText(x, String(p.limit), W / 2, H * 0.68, H * 0.33, W * 0.82, s.fg); } }) },
  noTurn: { label: 'No Turn / No U-Turn', cat: 'Regulatory', defaults: { ...mount, turn: 'left' }, fields: [F.sel('turn', 'Which', ['left', 'right', 'uturn', 'straight']), ...MOUNT],
    build: (p) => postSign('NoTurn', p, { kind: 'rect', scheme: 'regulatory', border: 0.025, draw: (x, W, H, s) => { const n = p.turn === 'uturn' ? 'uturn' : p.turn === 'straight' ? 'arrow' : 'turn'; sym(x, n, W / 2, H / 2, W * 0.62, s.fg, p.turn === 'left'); sym(x, 'no', W / 2, H / 2, W * 0.86, s.fg); } }) },
  keepRight: { label: 'Keep Right', cat: 'Regulatory', defaults: { ...mount, size: 0.61, side: 'right' }, fields: [F.sel('side', 'Side', SIDES), ...MOUNT],
    build: (p) => postSign('KeepRight', p, { kind: 'rect', aspect: 1.25, scheme: 'regulatory', border: 0.025, draw: (x, W, H, s) => sym(x, 'keepRight', W / 2, H / 2, W * 0.8, s.fg, p.side === 'left') }) },
  regText: { label: 'Text sign (No Parking, etc.)', cat: 'Regulatory', defaults: { ...mount, size: 0.61, lines: 'NO|PARKING|ANY TIME', color: 'red text', aspect: 1.25 }, fields: [F.text('lines', 'Text', '| = new line'), F.sel('color', 'Style', ['red text', 'black text', 'red sign']), F.num('aspect', 'Height ÷ width', 0.3, 2, 0.05), ...MOUNT],
    build: (p) => { const sch = p.color === 'red sign' ? 'red' : 'regulatory'; return postSign('TextSign', p, { kind: 'rect', aspect: +p.aspect || 1.25, scheme: sch, border: 0.025, draw: (x, W, H, s) => textBlock(x, splitLines(p.lines), W / 2, H * 0.1, H * 0.9, W * 0.84, p.color === 'red text' ? '#b8152a' : s.fg) }); } },
  // ---- warning
  warnText: { label: 'Warning (text)', cat: 'Warning', defaults: { ...mount, lines: 'SPEED|HUMP', plaque: '' }, fields: [F.text('lines', 'Text', '| = new line'), PLAQUE, ...MOUNT],
    build: (p) => postSign('WarningSign', p, { kind: 'diamond', scheme: 'warning', draw: (x, W, H, s) => diamondText(x, splitLines(p.lines), W, H, s.fg) }) },
  curve: { label: 'Curve / Turn ahead', cat: 'Warning', defaults: { ...mount, dir: 'right', sharp: false, plaque: '25 MPH' }, fields: [F.sel('dir', 'Direction', SIDES), F.bool('sharp', 'Sharp turn'), PLAQUE, ...MOUNT],
    build: (p) => postSign('CurveSign', p, { kind: 'diamond', scheme: 'warning', draw: (x, W, H, s) => sym(x, p.sharp ? 'turn' : 'curve', W / 2, H / 2, W * 0.5, s.fg, p.dir === 'left') }) },
  symbolWarn: { label: 'Warning (symbol)', cat: 'Warning', defaults: { ...mount, symbol: 'deer', flip: false, plaque: '' }, fields: [F.sel('symbol', 'Symbol', ['deer', 'ped', 'signal', 'stopSmall', 'merge', 'laneEnds', 'hill', 'slippery', 'rrx']), F.bool('flip', 'Mirror'), PLAQUE, ...MOUNT],
    build: (p) => postSign('WarningSymbol', p, { kind: 'diamond', scheme: 'warning', draw: (x, W, H, s) => { if (p.symbol === 'stopSmall') { sym(x, 'stopSmall', W / 2, H * 0.4, W * 0.3, s.fg); sym(x, 'arrow', W / 2, H * 0.68, W * 0.22, s.fg); } else sym(x, p.symbol, W / 2, H / 2, W * 0.5, s.fg, !!p.flip); } }) },
  school: { label: 'School crossing', cat: 'Warning', defaults: { ...mount, plaque: '' }, fields: [PLAQUE, ...MOUNT],
    build: (p) => postSign('SchoolSign', p, { kind: 'pentagon', aspect: 1.0, scheme: 'school', plaqueScheme: 'school', draw: (x, W, H, s) => sym(x, 'kids', W / 2, H * 0.56, W * 0.66, s.fg) }) },
  pedXing: { label: 'Pedestrian crossing', cat: 'Warning', defaults: { ...mount, fluorescent: true, plaque: '' }, fields: [F.bool('fluorescent', 'Fluorescent yellow-green'), PLAQUE, ...MOUNT],
    build: (p) => postSign('PedSign', p, { kind: 'diamond', scheme: p.fluorescent ? 'school' : 'warning', plaqueScheme: p.fluorescent ? 'school' : 'warning', draw: (x, W, H, s) => sym(x, 'ped', W / 2, H / 2, W * 0.5, s.fg) }) },
  chevron: { label: 'Curve chevron', cat: 'Warning', defaults: { ...mount, size: 0.46, dir: 'right', bottom: 1.2 }, fields: [F.sel('dir', 'Points', SIDES), ...MOUNT],
    build: (p) => postSign('Chevron', p, { kind: 'rect', aspect: 1.333, scheme: 'warning', border: 0.02, draw: (x, W, H, s) => sym(x, 'chevron', W / 2, H / 2, Math.min(W, H) * 0.95, s.fg, p.dir === 'left') }) },
  exitAdvisory: { label: 'Exit / ramp speed', cat: 'Warning', defaults: { ...mount, size: 0.61, top: 'EXIT', speed: 35, unit: 'MPH' }, fields: [F.text('top', 'Top'), F.num('speed', 'Speed', 5, 70, 5), F.text('unit', 'Unit'), ...MOUNT],
    build: (p) => postSign('ExitAdvisory', p, { kind: 'rect', aspect: 1.25, scheme: 'warning', border: 0.025, draw: (x, W, H, s) => { fitText(x, p.top, W / 2, H * 0.2, H * 0.12, W * 0.8, s.fg); fitText(x, String(p.speed), W / 2, H * 0.52, H * 0.28, W * 0.8, s.fg); fitText(x, p.unit, W / 2, H * 0.82, H * 0.12, W * 0.8, s.fg); } }) },
  rrAdvance: { label: 'Railroad advance (round)', cat: 'Warning', defaults: { ...mount, size: 0.914 }, fields: [...MOUNT],
    build: (p) => postSign('RRAdvance', p, { kind: 'circle', scheme: 'warning', draw: (x, W, H, s) => { sym(x, 'rrx', W / 2, H / 2, W * 0.6, s.fg); fitText(x, 'R', W * 0.24, H / 2, H * 0.16, W * 0.2, s.fg); fitText(x, 'R', W * 0.76, H / 2, H * 0.16, W * 0.2, s.fg); } }) },
  crossbuck: { label: 'Railroad crossbuck', cat: 'Warning', defaults: { height: 2.75, tracks: '' }, fields: [F.num('height', 'Height (m)', 2, 4, 0.05), F.text('tracks', 'Track plaque', 'e.g. 2|TRACKS')], build: buildCrossbuck },
  // ---- work zone
  roadWork: { label: 'Road Work (orange)', cat: 'Work zone', defaults: { ...mount, size: 1.22, bottom: 1.6, lines: 'ROAD|WORK|AHEAD', plaque: '' }, fields: [F.text('lines', 'Text', '| = new line'), PLAQUE, ...MOUNT],
    build: (p) => postSign('RoadWork', p, { kind: 'diamond', scheme: 'construction', plaqueScheme: 'construction', draw: (x, W, H, s) => diamondText(x, splitLines(p.lines), W, H, s.fg) }) },
  detour: { label: 'Detour arrow', cat: 'Work zone', defaults: { ...mount, size: 1.22, text: 'DETOUR', dir: 'right' }, fields: [F.text('text', 'Text'), F.sel('dir', 'Arrow', ['right', 'left', 'up']), ...MOUNT],
    build: (p) => postSign('Detour', p, { kind: 'rect', aspect: 0.375, scheme: 'construction', border: 0.02, draw: (x, W, H, s) => { const a = ARROW_ANG[p.dir] ?? Math.PI / 2, left = p.dir === 'left'; const as = Math.min(H * 0.8, W * 0.2); if (p.dir === 'up') { fitText(x, p.text, W * 0.42, H / 2, H * 0.42, W * 0.6, s.fg); drawArrow(x, W * 0.86, H / 2, H * 0.78, 0, s.fg); } else { fitText(x, p.text, left ? W * 0.6 : W * 0.4, H / 2, H * 0.42, W * 0.56, s.fg); drawArrow(x, left ? W * 0.15 : W * 0.85, H / 2, as, a, s.fg); } } }) },
  barricade: { label: 'Barricade (Type III)', cat: 'Work zone', defaults: { width: 2.4, lights: true, sign: 'ROAD|CLOSED', arrowLeft: false }, fields: [F.num('width', 'Width (m)', 1.2, 4, 0.1), F.bool('lights', 'Flashing lights'), F.text('sign', 'Sign on top', '| = new line, blank = none'), F.bool('arrowLeft', 'Stripes slope left')], build: buildBarricade },
  cones: { label: 'Traffic cones', cat: 'Work zone', defaults: { count: 6, spacing: 3, height: 0.71 }, fields: [F.num('count', 'How many', 1, 40), F.num('spacing', 'Spacing (m)', 0.5, 20, 0.5), F.sel('height', 'Cone size', ['0.71', '0.91'])], build: buildCones },
  drums: { label: 'Barrels / drums', cat: 'Work zone', defaults: { count: 4, spacing: 4, light: true }, fields: [F.num('count', 'How many', 1, 30), F.num('spacing', 'Spacing (m)', 0.8, 20, 0.5), F.bool('light', 'Flashing light')], build: buildDrums },
  flexPosts: { label: 'Flex delineator posts', cat: 'Work zone', defaults: { count: 8, spacing: 2 }, fields: [F.num('count', 'How many', 1, 40), F.num('spacing', 'Spacing (m)', 0.5, 10, 0.25)], build: buildFlexPosts },
  // ---- barriers
  guardrail: { label: 'Guardrail (W-beam)', cat: 'Barriers', defaults: { length: 30, bend: 0, posts: 'steel', ends: 'terminal' }, fields: [F.num('length', 'Length (m)', 4, 150, 1), F.num('bend', 'Bend (°, + curves away)', -180, 180, 1), F.sel('posts', 'Posts', ['steel', 'wood']), F.sel('ends', 'Ends', ['terminal', 'none'])], build: buildGuardrail },
  concreteBarrier: { label: 'Concrete barrier', cat: 'Barriers', defaults: { length: 15, bend: 0, reflectors: true }, fields: [F.num('length', 'Length (m)', 3.8, 150, 0.1), F.num('bend', 'Bend (°)', -180, 180, 1), F.bool('reflectors', 'Reflectors')], build: buildConcreteBarrier },
  waterBarrier: { label: 'Water-filled barriers', cat: 'Barriers', defaults: { count: 5, mass: 450 }, fields: [F.num('count', 'How many', 1, 30), F.num('mass', 'Weight (kg, filled ≈ 450)', 40, 900, 10)], build: buildWaterBarriers },
  // ---- guide
  streetName: { label: 'Street name blades', cat: 'Guide', defaults: { name1: 'Woodward Ave', name2: 'Grand River Ave', height: 2.9, stop: false }, fields: [F.text('name1', 'Street 1'), F.text('name2', 'Street 2 (blank = none)'), F.num('height', 'Height (m)', 2, 4, 0.05), F.bool('stop', 'Stop sign on pole')], build: buildStreetName },
  routeMarker: { label: 'Route marker', cat: 'Guide', defaults: { shield: 'I', num: '96', direction: 'WEST', aux: '', arrow: 'up', bottom: 1.5 }, fields: [F.sel('shield', 'Shield', ['I', 'US', 'M']), F.text('num', 'Number'), F.text('direction', 'Direction (blank = none)'), F.text('aux', 'Extra plate (TO, JCT, BUSINESS…)'), F.sel('arrow', 'Arrow', ARROWS), F.num('bottom', 'Height to bottom (m)', 0.5, 3, 0.05)], build: buildRouteMarker },
  services: { label: 'Services (blue)', cat: 'Guide', defaults: { ...mount, size: 1.5, lines: 'GAS|FOOD|LODGING', exit: 'NEXT RIGHT' }, fields: [F.text('lines', 'Text', '| = new line'), F.text('exit', 'Bottom line'), ...MOUNT],
    build: (p) => postSign('Services', p, { kind: 'rect', aspect: 0.75, scheme: 'services', border: 0.02, draw: (x, W, H, s) => { const L = splitLines(p.lines); textBlock(x, L, W / 2, H * 0.08, H * (p.exit ? 0.74 : 0.92), W * 0.86, s.fg, 0.62); if (p.exit) fitText(x, p.exit, W / 2, H * 0.84, H * 0.1, W * 0.8, s.fg); } }) },
  guideSign: { label: 'Freeway guide sign', cat: 'Guide', defaults: guideDefaults({ shield1: 'US', num1: '12', direction: 'EAST', line1: 'Michigan Ave', exitTab: '50', arrows: 'upright', bottom: 2.1 }), fields: [...guideFields(''), F.num('bottom', 'Height to bottom (m)', 1, 4, 0.05)],
    build: (p) => createGuideSign(flatToSpec(p, ''), { bottom: +p.bottom || 2.1 }) },
  exitGore: { label: 'Exit gore sign', cat: 'Guide', defaults: { exit: '51A', side: 'right' }, fields: [F.text('exit', 'Exit number'), F.sel('side', 'Arrow side', SIDES)], build: (p) => createExitGoreSign(p) },
  mileMarker: { label: 'Mile marker', cat: 'Guide', defaults: { mile: 214 }, fields: [F.num('mile', 'Mile', 0, 999)], build: (p) => createMileMarker(p) },
  overheadGantry: { label: 'Overhead sign bridge', cat: 'Guide', defaults: { span: 20, clearance: 5.4, catwalk: true, ...gantryDefaults() }, fields: [F.num('span', 'Span (m)', 8, 40, 0.5), F.num('clearance', 'Clearance (m)', 4.8, 7, 0.1), F.bool('catwalk', 'Catwalk + lights'), ...[1, 2, 3].flatMap(i => gantryFields(i))],
    build: (p) => createOverheadGantry({ span: +p.span, clearance: +p.clearance, catwalk: !!p.catwalk, signs: [1, 2, 3].map(i => gantryItem(p, i)).filter(Boolean) }) },
  cantilever: { label: 'Cantilever sign', cat: 'Guide', defaults: guideDefaults({ arm: 9.5, clearance: 5.4, shield1: 'I', num1: '94', direction: 'WEST', line1: 'Chicago', arrows: 'down', arrowCount: 2 }), fields: [F.num('arm', 'Arm length (m)', 4, 16, 0.5), F.num('clearance', 'Clearance (m)', 4.8, 7, 0.1), ...guideFields('')],
    build: (p) => createCantileverSign({ arm: +p.arm, clearance: +p.clearance, spec: flatToSpec(p, '') }) },
  messageBoard: { label: 'Message board (DMS)', cat: 'Guide', defaults: { line1: 'CRASH AHEAD', line2: 'LEFT LANE BLOCKED', line3: '', height: 5.4 }, fields: [F.text('line1', 'Line 1'), F.text('line2', 'Line 2'), F.text('line3', 'Line 3'), F.num('height', 'Height to bottom (m)', 1, 7, 0.1)],
    build: (p) => { const g = new THREE.Group(); g.name = 'MessageBoardPole'; const b = createMessageBoard({ lines: [p.line1, p.line2, p.line3].filter(Boolean) }); const H = +p.height || 5.4; b.position.set(0, H + 1.15, 0); g.add(b); const pole = mesh(new THREE.CylinderGeometry(0.2, 0.24, H + 1.2, 14), M.galv); pole.position.set(0, (H + 1.2) / 2, -0.7); g.add(pole); g.userData.strata = { kind: 'obstacle', obstacles: [{ type: 'circle', x: 0, z: -0.7, r: 0.3 }] }; return g; } },
  custom: { label: 'Custom sign', cat: 'Guide', defaults: { ...mount, plaque: '', shape: 'rect', scheme: 'guide', lines: 'YOUR|TEXT', arrow: 'none', aspect: 0.75 }, fields: [F.sel('shape', 'Shape', ['rect', 'diamond', 'circle', 'octagon', 'yield', 'pentagon']), F.sel('scheme', 'Colors', Object.keys(SCHEMES)), F.text('lines', 'Text', '| = new line'), F.sel('arrow', 'Arrow', ARROWS), F.num('aspect', 'Height ÷ width', 0.2, 2, 0.05), PLAQUE, ...MOUNT],
    build: (p) => { const sq = ['diamond', 'circle', 'octagon'].includes(p.shape); const asp = p.shape === 'yield' ? 0.866 : sq ? 1 : +p.aspect || 0.75; return postSign('CustomSign', p, { kind: p.shape, aspect: asp, scheme: p.scheme, draw: (x, W, H, s) => { const L = splitLines(p.lines), hasA = p.arrow && p.arrow !== 'none'; const inner = sq ? 0.2 : 0.1; if (p.shape === 'diamond' && !hasA) diamondText(x, L, W, H, s.fg); else textBlock(x, L, W / 2, H * inner, H * (hasA ? 0.66 : 1 - inner), W * (sq ? 0.56 : 0.86), s.fg, 0.62); if (hasA) drawArrow(x, W / 2, H * 0.8, H * 0.24, ARROW_ANG[p.arrow], s.fg); } }); } },
  // ---- pavement
  stopLine: { label: 'Stop bar (paint)', cat: 'Pavement', defaults: { width: 3.6, legend: false }, fields: [F.num('width', 'Width (m)', 1, 20, 0.1), F.bool('legend', 'STOP on pavement')], build: (p) => createStopLine({ width: +p.width, legend: !!p.legend }) },
  rubberBump: { label: 'Rubber speed bump', cat: 'Pavement', defaults: { length: 3.5, height: 0.057 }, fields: [F.num('length', 'Length (m)', 0.5, 20, 0.5), F.num('height', 'Height (m)', 0.03, 0.1, 0.005)], build: (p) => createRubberSpeedBump({ length: +p.length, height: +p.height }) },
  speedHump: { label: 'Speed hump', cat: 'Pavement', defaults: { width: 7.2, length: 3.8, height: 0.085, lanes: 2 }, fields: [F.num('width', 'Width (m)', 2, 20, 0.1), F.num('length', 'Length (m)', 2, 6, 0.1), F.num('height', 'Height (m)', 0.04, 0.12, 0.005), F.num('lanes', 'Lanes', 1, 6)], build: (p) => createSpeedHump({ width: +p.width, length: +p.length, height: +p.height, lanes: +p.lanes }) },
  speedTable: { label: 'Speed table / raised crosswalk', cat: 'Pavement', defaults: { width: 7.2, top: 3, height: 0.085, crosswalk: true }, fields: [F.num('width', 'Width (m)', 2, 20, 0.1), F.num('top', 'Flat top (m)', 1, 8, 0.1), F.num('height', 'Height (m)', 0.04, 0.12, 0.005), F.bool('crosswalk', 'Crosswalk stripes')], build: (p) => createSpeedTable({ width: +p.width, top: +p.top, height: +p.height, crosswalk: !!p.crosswalk }) },
  speedCushion: { label: 'Speed cushions', cat: 'Pavement', defaults: { width: 7.2, pads: 3, height: 0.075 }, fields: [F.num('width', 'Width (m)', 3, 20, 0.1), F.num('pads', 'Pads', 1, 6), F.num('height', 'Height (m)', 0.04, 0.1, 0.005)], build: (p) => createSpeedCushion({ width: +p.width, pads: +p.pads, height: +p.height }) },
};

function guideDefaults(extra) { return { shield1: 'I', num1: '75', shield2: 'none', num2: '', direction: 'NORTH', line1: 'Flint', line2: '', line3: '', arrows: 'none', arrowCount: 1, exitTab: '', exitOnly: false, width: 0, ...extra }; }
function guideFields(pre, lbl = '') {
  return [F.sel(pre + 'shield1', lbl + 'Shield 1', SHIELDS), F.text(pre + 'num1', lbl + 'Route 1'), F.sel(pre + 'shield2', lbl + 'Shield 2', SHIELDS), F.text(pre + 'num2', lbl + 'Route 2'),
    F.text(pre + 'direction', lbl + 'Direction'), F.text(pre + 'line1', lbl + 'Destination 1'), F.text(pre + 'line2', lbl + 'Destination 2'), F.text(pre + 'line3', lbl + 'Destination 3'),
    F.sel(pre + 'arrows', lbl + 'Arrows', ARROWS), F.num(pre + 'arrowCount', lbl + 'Arrow count', 1, 4), F.text(pre + 'exitTab', lbl + 'Exit tab (blank = none)'), F.bool(pre + 'exitOnly', lbl + 'EXIT ONLY bar'), F.num(pre + 'width', lbl + 'Width (m, 0 = auto)', 0, 12, 0.1)];
}
function flatToSpec(p, pre) {
  const g = (k) => p[pre + k];
  const shields = [[g('shield1'), g('num1')], [g('shield2'), g('num2')]].filter(([t, n]) => t && t !== 'none' && n).map(([type, num]) => ({ type, num: String(num) }));
  const spec = { shields, direction: g('direction') || '', lines: [g('line1'), g('line2'), g('line3')].filter(Boolean), arrows: g('arrows') || 'none', arrowCount: +g('arrowCount') || 1, exitOnly: !!g('exitOnly') };
  if (g('exitTab')) spec.exitTab = String(g('exitTab'));
  if (+g('width') > 0) spec.width = +g('width');
  return spec;
}
function gantryDefaults() {
  const d = {};
  Object.assign(d, prefixed('p1', { kind: 'guide', x: 1.8, ...guideDefaults({ width: 3.5, arrows: 'down' }) }));
  Object.assign(d, prefixed('p2', { kind: 'guide', x: 5.6, ...guideDefaults({ shield1: 'M', num1: '10', direction: '', line1: 'Lodge Fwy', exitTab: '51A', exitOnly: true, width: 3.7 }) }));
  Object.assign(d, prefixed('p3', { kind: 'none', x: -5, ...guideDefaults({ line1: 'CRASH AHEAD', line2: 'LEFT LANE BLOCKED' }) }));
  return d;
}
function prefixed(pre, o) { const r = {}; for (const k in o) r[pre + '_' + k] = o[k]; return r; }
function gantryFields(i) { const pre = `p${i}_`, L = `Panel ${i}: `; return [F.sel(pre + 'kind', L + 'type', ['guide', 'dms', 'none']), F.num(pre + 'x', L + 'position across (m)', -20, 20, 0.1), ...guideFields(pre, L)]; }
function gantryItem(p, i) {
  const pre = `p${i}_`, kind = p[pre + 'kind']; if (!kind || kind === 'none') return null;
  if (kind === 'dms') return { x: +p[pre + 'x'] || 0, dms: { lines: [p[pre + 'line1'], p[pre + 'line2'], p[pre + 'line3']].filter(Boolean) } };
  return { x: +p[pre + 'x'] || 0, spec: flatToSpec(p, pre) };
}

/** Build any registered prop. params are merged over the type's defaults. */
export function createProp(type, params = {}) {
  const T = PROP_TYPES[type]; if (!T) throw new Error('Unknown prop type ' + type);
  const p = { ...T.defaults, ...params };
  let obj;
  try { obj = T.build(p); } catch (e) { console.warn('[strata] build failed for', type, e); obj = T.build({ ...T.defaults }); }
  obj.userData.prop = { type, params: p };
  if (!obj.name) obj.name = T.label;
  return obj;
}
export const PROP_CATEGORIES = ['Regulatory', 'Warning', 'Work zone', 'Barriers', 'Guide', 'Pavement'];

function disposeProp(obj) {
  obj.traverse(o => {
    o.geometry?.dispose();
    for (const m of [].concat(o.material || [])) if (signMats.has(m) || m.userData?.own) { signMats.delete(m); m.dispose(); }
  });
}

export const RoadProps = {
  createProp, PROP_TYPES, PROP_CATEGORIES, SCHEMES,
  createRubberSpeedBump, createSpeedHump, createSpeedTable, createSpeedCushion,
  createStopSign, createStopLine, createSpeedLimitSign, createWarningSign, createMileMarker,
  createGuideSignPanel, createGuideSign, createExitGoreSign, createMessageBoard,
  createOverheadGantry, createCantileverSign, PropsWorld, setRetroreflectivity,
};
