// A small stand-in for three.js: just enough of it for strata-road-props.js to build its props, so tools/props2/bake.py can
// turn them into plain triangles (no renderer, no physics). Geometry follows three's own conventions (CCW front faces,
// cylinders round Y with x = r sin(theta), z = r cos(theta), shapes in XY facing +Z, extrusions along +Z).
export const DoubleSide = 2, FrontSide = 0, BackSide = 1, SRGBColorSpace = 'srgb', RepeatWrapping = 1000, ClampToEdgeWrapping = 1001;

export class Vector3 {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
  set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; }
  copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; }
  clone() { return new Vector3(this.x, this.y, this.z); }
  add(v) { this.x += v.x; this.y += v.y; this.z += v.z; return this; }
  sub(v) { this.x -= v.x; this.y -= v.y; this.z -= v.z; return this; }
  addVectors(a, b) { return this.set(a.x + b.x, a.y + b.y, a.z + b.z); }
  subVectors(a, b) { return this.set(a.x - b.x, a.y - b.y, a.z - b.z); }
  multiplyScalar(s) { this.x *= s; this.y *= s; this.z *= s; return this; }
  divideScalar(s) { return this.multiplyScalar(1 / s); }
  length() { return Math.hypot(this.x, this.y, this.z); }
  lengthSq() { return this.x * this.x + this.y * this.y + this.z * this.z; }
  normalize() { const l = this.length() || 1; return this.multiplyScalar(1 / l); }
  dot(v) { return this.x * v.x + this.y * v.y + this.z * v.z; }
  cross(v) { return this.crossVectors(this.clone(), v); }
  crossVectors(a, b) { return this.set(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
  lerp(v, t) { this.x += (v.x - this.x) * t; this.y += (v.y - this.y) * t; this.z += (v.z - this.z) * t; return this; }
  distanceTo(v) { return Math.hypot(this.x - v.x, this.y - v.y, this.z - v.z); }
  negate() { return this.multiplyScalar(-1); }
  applyMatrix4(m) { const e = m.elements, x = this.x, y = this.y, z = this.z, w = 1 / (e[3] * x + e[7] * y + e[11] * z + e[15] || 1);
    return this.set((e[0] * x + e[4] * y + e[8] * z + e[12]) * w, (e[1] * x + e[5] * y + e[9] * z + e[13]) * w, (e[2] * x + e[6] * y + e[10] * z + e[14]) * w); }
  transformDirection(m) { const e = m.elements, x = this.x, y = this.y, z = this.z; return this.set(e[0] * x + e[4] * y + e[8] * z, e[1] * x + e[5] * y + e[9] * z, e[2] * x + e[6] * y + e[10] * z).normalize(); }
  applyQuaternion(q) { const m = new Matrix4().makeRotationFromQuaternion(q); const e = m.elements, x = this.x, y = this.y, z = this.z; return this.set(e[0] * x + e[4] * y + e[8] * z, e[1] * x + e[5] * y + e[9] * z, e[2] * x + e[6] * y + e[10] * z); }
  setFromMatrixPosition(m) { const e = m.elements; return this.set(e[12], e[13], e[14]); }
}
export class Vector2 { constructor(x = 0, y = 0) { this.x = x; this.y = y; } set(x, y) { this.x = x; this.y = y; return this; } clone() { return new Vector2(this.x, this.y); } }

export class Quaternion {
  constructor(x = 0, y = 0, z = 0, w = 1) { this.x = x; this.y = y; this.z = z; this.w = w; this._cb = null; }
  _ch() { if (this._cb) this._cb(); return this; }
  set(x, y, z, w) { this.x = x; this.y = y; this.z = z; this.w = w; return this._ch(); }
  copy(q) { return this.set(q.x, q.y, q.z, q.w); }
  clone() { return new Quaternion(this.x, this.y, this.z, this.w); }
  setFromAxisAngle(a, t) { const s = Math.sin(t / 2); return this.set(a.x * s, a.y * s, a.z * s, Math.cos(t / 2)); }
  setFromEuler(e) { const c1 = Math.cos(e.x / 2), c2 = Math.cos(e.y / 2), c3 = Math.cos(e.z / 2), s1 = Math.sin(e.x / 2), s2 = Math.sin(e.y / 2), s3 = Math.sin(e.z / 2);
    if ((e.order || 'XYZ') === 'YXZ') return this.set(s1 * c2 * c3 + c1 * s2 * s3, c1 * s2 * c3 - s1 * c2 * s3, c1 * c2 * s3 - s1 * s2 * c3, c1 * c2 * c3 + s1 * s2 * s3);
    return this.set(s1 * c2 * c3 + c1 * s2 * s3, c1 * s2 * c3 - s1 * c2 * s3, c1 * c2 * s3 + s1 * s2 * c3, c1 * c2 * c3 - s1 * s2 * s3); }
  setFromUnitVectors(a, b) { let r = a.dot(b) + 1; let x, y, z, w;
    if (r < 1e-8) { r = 0; if (Math.abs(a.x) > Math.abs(a.z)) { x = -a.y; y = a.x; z = 0; w = r } else { x = 0; y = -a.z; z = a.y; w = r } }
    else { x = a.y * b.z - a.z * b.y; y = a.z * b.x - a.x * b.z; z = a.x * b.y - a.y * b.x; w = r }
    const l = Math.hypot(x, y, z, w); return this.set(x / l, y / l, z / l, w / l); }
  multiply(q) { return this.multiplyQuaternions(this.clone(), q); }
  premultiply(q) { return this.multiplyQuaternions(q, this.clone()); }
  multiplyQuaternions(a, b) { return this.set(a.x * b.w + a.w * b.x + a.y * b.z - a.z * b.y, a.y * b.w + a.w * b.y + a.z * b.x - a.x * b.z, a.z * b.w + a.w * b.z + a.x * b.y - a.y * b.x, a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z); }
  invert() { return this.set(-this.x, -this.y, -this.z, this.w); }
}
export class Euler {
  constructor(x = 0, y = 0, z = 0, order = 'XYZ') { this._x = x; this._y = y; this._z = z; this.order = order; this._cb = null; }
  get x() { return this._x } set x(v) { this._x = v; this._cb && this._cb() }
  get y() { return this._y } set y(v) { this._y = v; this._cb && this._cb() }
  get z() { return this._z } set z(v) { this._z = v; this._cb && this._cb() }
  set(x, y, z, o) { this._x = x; this._y = y; this._z = z; if (o) this.order = o; this._cb && this._cb(); return this; }
  copy(e) { return this.set(e.x, e.y, e.z, e.order); }
  clone() { return new Euler(this._x, this._y, this._z, this.order); }
  setFromQuaternion(q, order = 'XYZ') { const m = new Matrix4().makeRotationFromQuaternion(q).elements; this.order = order;
    if (order === 'YXZ') { this._x = Math.asin(-Math.max(-1, Math.min(1, m[9]))); this._y = Math.atan2(m[8], m[10]); this._z = Math.atan2(m[1], m[5]); }
    else { this._y = Math.asin(Math.max(-1, Math.min(1, m[8]))); this._x = Math.atan2(-m[9], m[10]); this._z = Math.atan2(-m[4], m[0]); }
    return this; }
}
export class Matrix4 {
  constructor() { this.elements = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; }
  identity() { this.elements = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; return this; }
  copy(m) { this.elements = m.elements.slice(); return this; }
  clone() { return new Matrix4().copy(this); }
  makeRotationFromQuaternion(q) { return this.compose(new Vector3(), q, new Vector3(1, 1, 1)); }
  compose(p, q, s) { const x = q.x, y = q.y, z = q.z, w = q.w, x2 = x + x, y2 = y + y, z2 = z + z, xx = x * x2, xy = x * y2, xz = x * z2, yy = y * y2, yz = y * z2, zz = z * z2, wx = w * x2, wy = w * y2, wz = w * z2;
    this.elements = [(1 - (yy + zz)) * s.x, (xy + wz) * s.x, (xz - wy) * s.x, 0, (xy - wz) * s.y, (1 - (xx + zz)) * s.y, (yz + wx) * s.y, 0, (xz + wy) * s.z, (yz - wx) * s.z, (1 - (xx + yy)) * s.z, 0, p.x, p.y, p.z, 1]; return this; }
  multiply(m) { return this.multiplyMatrices(this.clone(), m); }
  premultiply(m) { return this.multiplyMatrices(m, this.clone()); }
  multiplyMatrices(a, b) { const A = a.elements, B = b.elements, r = new Array(16);
    for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += A[k * 4 + i] * B[j * 4 + k]; r[j * 4 + i] = s; }
    this.elements = r; return this; }
  makeRotationX(t) { const c = Math.cos(t), s = Math.sin(t); this.elements = [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]; return this; }
  makeRotationY(t) { const c = Math.cos(t), s = Math.sin(t); this.elements = [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]; return this; }
  makeRotationZ(t) { const c = Math.cos(t), s = Math.sin(t); this.elements = [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; return this; }
  makeTranslation(x, y, z) { this.elements = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, z, 1]; return this; }
  makeScale(x, y, z) { this.elements = [x, 0, 0, 0, 0, y, 0, 0, 0, 0, z, 0, 0, 0, 0, 1]; return this; }
  invert() { const m = this.elements, inv = new Array(16);
    inv[0] = m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] + m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10];
    inv[4] = -m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] - m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10];
    inv[8] = m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] + m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9];
    inv[12] = -m[4] * m[9] * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] - m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9];
    inv[1] = -m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] - m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10];
    inv[5] = m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] + m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10];
    inv[9] = -m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] - m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9];
    inv[13] = m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] + m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9];
    inv[2] = m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] + m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6];
    inv[6] = -m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] - m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6];
    inv[10] = m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] + m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5];
    inv[14] = -m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] - m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5];
    inv[3] = -m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] - m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6];
    inv[7] = m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] + m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6];
    inv[11] = -m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] - m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5];
    inv[15] = m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] + m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5];
    const det = m[0] * inv[0] + m[1] * inv[4] + m[2] * inv[8] + m[3] * inv[12]; this.elements = inv.map(v => v / (det || 1)); return this; }
}
export const MathUtils = { degToRad: d => d * Math.PI / 180, radToDeg: r => r * 180 / Math.PI, clamp: (v, a, b) => Math.min(b, Math.max(a, v)), lerp: (a, b, t) => a + (b - a) * t, randFloat: (a, b) => a + Math.random() * (b - a), generateUUID: () => Math.random().toString(36).slice(2) };

export class Color {
  constructor(c) { this.r = 1; this.g = 1; this.b = 1; if (c !== undefined) this.set(c); }
  set(c) { if (c instanceof Color) { this.r = c.r; this.g = c.g; this.b = c.b; return this; }
    if (typeof c === 'number') { this.r = (c >> 16 & 255) / 255; this.g = (c >> 8 & 255) / 255; this.b = (c & 255) / 255; return this; }
    if (typeof c === 'string') { const cv = document.createElement('canvas').getContext('2d'); cv.fillStyle = c; const s = cv.fillStyle; if (s[0] === '#') return this.set(parseInt(s.slice(1), 16)); const m = s.match(/[\d.]+/g); if (m) { this.r = m[0] / 255; this.g = m[1] / 255; this.b = m[2] / 255; } }
    return this; }
  setHex(h) { return this.set(h); } copy(c) { return this.set(c); } clone() { return new Color(this); }
  multiplyScalar(s) { this.r *= s; this.g *= s; this.b *= s; return this; }
}

export class BufferAttribute {
  constructor(array, itemSize) { this.array = array; this.itemSize = itemSize; this.count = array.length / itemSize; this.needsUpdate = false; }
  getX(i) { return this.array[i * this.itemSize] } getY(i) { return this.array[i * this.itemSize + 1] } getZ(i) { return this.array[i * this.itemSize + 2] }
  setX(i, v) { this.array[i * this.itemSize] = v; return this } setY(i, v) { this.array[i * this.itemSize + 1] = v; return this } setZ(i, v) { this.array[i * this.itemSize + 2] = v; return this }
  setXY(i, x, y) { const k = i * this.itemSize; this.array[k] = x; this.array[k + 1] = y; return this; }
  setXYZ(i, x, y, z) { const k = i * this.itemSize; this.array[k] = x; this.array[k + 1] = y; this.array[k + 2] = z; return this; }
  clone() { return new BufferAttribute(this.array.slice(), this.itemSize); }
}
export class Float32BufferAttribute extends BufferAttribute { constructor(a, n) { super(new Float32Array(a), n); } }
export class Uint16BufferAttribute extends BufferAttribute { constructor(a, n) { super(new Uint16Array(a), n); } }
export class Uint32BufferAttribute extends BufferAttribute { constructor(a, n) { super(new Uint32Array(a), n); } }

export class BufferGeometry {
  constructor() { this.attributes = {}; this.index = null; this.groups = []; this.userData = {}; }
  setAttribute(n, a) { this.attributes[n] = a; return this; }
  getAttribute(n) { return this.attributes[n]; }
  deleteAttribute(n) { delete this.attributes[n]; return this; }
  setIndex(i) { this.index = Array.isArray(i) ? new BufferAttribute(new Uint32Array(i), 1) : i; return this; }
  getIndex() { return this.index; }
  addGroup(s, c, m) { this.groups.push({ start: s, count: c, materialIndex: m || 0 }); }
  applyMatrix4(m) { const p = this.attributes.position; if (p) for (let i = 0; i < p.count; i++) { const v = new Vector3(p.getX(i), p.getY(i), p.getZ(i)).applyMatrix4(m); p.setXYZ(i, v.x, v.y, v.z); }
    const n = this.attributes.normal; if (n) { const nm = m.clone(); nm.elements[12] = nm.elements[13] = nm.elements[14] = 0; const inv = nm.clone().invert().elements;
      for (let i = 0; i < n.count; i++) { const x = n.getX(i), y = n.getY(i), z = n.getZ(i); const v = new Vector3(inv[0] * x + inv[1] * y + inv[2] * z, inv[4] * x + inv[5] * y + inv[6] * z, inv[8] * x + inv[9] * y + inv[10] * z).normalize(); n.setXYZ(i, v.x, v.y, v.z); } }
    return this; }
  applyQuaternion(q) { return this.applyMatrix4(new Matrix4().makeRotationFromQuaternion(q)); }
  translate(x, y, z) { return this.applyMatrix4(new Matrix4().makeTranslation(x, y, z)); }
  rotateX(t) { return this.applyMatrix4(new Matrix4().makeRotationX(t)); }
  rotateY(t) { return this.applyMatrix4(new Matrix4().makeRotationY(t)); }
  rotateZ(t) { return this.applyMatrix4(new Matrix4().makeRotationZ(t)); }
  scale(x, y, z) { return this.applyMatrix4(new Matrix4().makeScale(x, y, z)); }
  center() { this.computeBoundingBox(); const b = this.boundingBox; return this.translate(-(b.min.x + b.max.x) / 2, -(b.min.y + b.max.y) / 2, -(b.min.z + b.max.z) / 2); }
  computeBoundingBox() { const b = new Box3(), p = this.attributes.position; for (let i = 0; i < p.count; i++) b.expandByPoint(new Vector3(p.getX(i), p.getY(i), p.getZ(i))); this.boundingBox = b; }
  computeBoundingSphere() { this.computeBoundingBox(); }
  computeVertexNormals() { const p = this.attributes.position, n = new Float32Array(p.count * 3), I = this.index ? this.index.array : [...Array(p.count).keys()];
    for (let k = 0; k < I.length; k += 3) { const a = I[k], b = I[k + 1], c = I[k + 2];
      const ax = p.getX(a), ay = p.getY(a), az = p.getZ(a), ux = p.getX(b) - ax, uy = p.getY(b) - ay, uz = p.getZ(b) - az, vx = p.getX(c) - ax, vy = p.getY(c) - ay, vz = p.getZ(c) - az;
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; for (const q of [a, b, c]) { n[q * 3] += nx; n[q * 3 + 1] += ny; n[q * 3 + 2] += nz; } }
    for (let i = 0; i < p.count; i++) { const l = Math.hypot(n[i * 3], n[i * 3 + 1], n[i * 3 + 2]) || 1; n[i * 3] /= l; n[i * 3 + 1] /= l; n[i * 3 + 2] /= l; }
    this.setAttribute('normal', new BufferAttribute(n, 3)); }
  clone() { const g = new BufferGeometry(); for (const k in this.attributes) g.attributes[k] = this.attributes[k].clone(); if (this.index) g.index = this.index.clone(); g.groups = this.groups.slice(); return g; }
  toNonIndexed() { return this.clone(); }
  dispose() { }
  _build(P, N, T, I) { this.setAttribute('position', new Float32BufferAttribute(P, 3)); this.setAttribute('normal', new Float32BufferAttribute(N, 3)); this.setAttribute('uv', new Float32BufferAttribute(T, 2)); this.setIndex(I); return this; }
}

export class BoxGeometry extends BufferGeometry {
  constructor(w = 1, h = 1, d = 1) { super(); const P = [], N = [], T = [], I = [];
    const face = (u, v, wd, ax, ay, az, nx, ny, nz) => { const b = P.length / 3;   // u and v axes and the face centre
      for (const [s, t] of [[-1, 1], [1, 1], [-1, -1], [1, -1]]) { P.push(ax + u[0] * s + v[0] * t, ay + u[1] * s + v[1] * t, az + u[2] * s + v[2] * t); N.push(nx, ny, nz); T.push((s + 1) / 2, (t + 1) / 2); }
      I.push(b, b + 2, b + 1, b + 2, b + 3, b + 1); };
    const X = w / 2, Y = h / 2, Z = d / 2;
    face([0, 0, -Z], [0, Y, 0], 0, X, 0, 0, 1, 0, 0); face([0, 0, Z], [0, Y, 0], 0, -X, 0, 0, -1, 0, 0);
    face([X, 0, 0], [0, 0, -Z], 0, 0, Y, 0, 0, 1, 0); face([X, 0, 0], [0, 0, Z], 0, 0, -Y, 0, 0, -1, 0);
    face([X, 0, 0], [0, Y, 0], 0, 0, 0, Z, 0, 0, 1); face([-X, 0, 0], [0, Y, 0], 0, 0, 0, -Z, 0, 0, -1);
    this._build(P, N, T, I); }
}
export class PlaneGeometry extends BufferGeometry {
  constructor(w = 1, h = 1, ws = 1, hs = 1) { super(); const P = [], N = [], T = [], I = [];
    for (let j = 0; j <= hs; j++) for (let i = 0; i <= ws; i++) { P.push(-w / 2 + w * i / ws, h / 2 - h * j / hs, 0); N.push(0, 0, 1); T.push(i / ws, 1 - j / hs); }
    for (let j = 0; j < hs; j++) for (let i = 0; i < ws; i++) { const a = j * (ws + 1) + i, b = a + ws + 1; I.push(a, b, a + 1, b, b + 1, a + 1); }
    this._build(P, N, T, I); }
}
export class CylinderGeometry extends BufferGeometry {
  constructor(rt = 1, rb = 1, h = 1, rs = 32, hs = 1, open = false, t0 = 0, tl = Math.PI * 2) { super(); const P = [], N = [], T = [], I = [];
    const slope = (rb - rt) / h;
    for (let y = 0; y <= hs; y++) { const v = y / hs, r = v * (rb - rt) + rt;
      for (let x = 0; x <= rs; x++) { const u = x / rs, th = u * tl + t0, s = Math.sin(th), c = Math.cos(th);
        P.push(r * s, -v * h + h / 2, r * c); const n = new Vector3(s, slope, c).normalize(); N.push(n.x, n.y, n.z); T.push(u, 1 - v); } }
    for (let x = 0; x < rs; x++) for (let y = 0; y < hs; y++) { const a = y * (rs + 1) + x, b = (y + 1) * (rs + 1) + x, c = b + 1, d = a + 1; I.push(a, b, d, b, c, d); }
    if (!open) for (const top of [true, false]) { const r = top ? rt : rb; if (r <= 0) continue; const sg = top ? 1 : -1, cy = h / 2 * sg, c0 = P.length / 3;
      P.push(0, cy, 0); N.push(0, sg, 0); T.push(0.5, 0.5);
      for (let x = 0; x <= rs; x++) { const th = x / rs * tl + t0, s = Math.sin(th), c = Math.cos(th); P.push(r * s, cy, r * c); N.push(0, sg, 0); T.push(c * 0.5 + 0.5, s * 0.5 * sg + 0.5); }
      for (let x = 0; x < rs; x++) { const a = c0 + 1 + x, b = a + 1; if (top) I.push(a, b, c0); else I.push(b, a, c0); } }
    this._build(P, N, T, I); }
}
export class SphereGeometry extends BufferGeometry {
  constructor(r = 1, ws = 32, hs = 16, p0 = 0, pl = Math.PI * 2, t0 = 0, tl = Math.PI) { super(); const P = [], N = [], T = [], I = [];
    for (let y = 0; y <= hs; y++) { const v = y / hs; for (let x = 0; x <= ws; x++) { const u = x / ws, ph = p0 + u * pl, th = t0 + v * tl;
      const px = -r * Math.cos(ph) * Math.sin(th), py = r * Math.cos(th), pz = r * Math.sin(ph) * Math.sin(th); P.push(px, py, pz); const l = Math.hypot(px, py, pz) || 1; N.push(px / l, py / l, pz / l); T.push(u, 1 - v); } }
    for (let y = 0; y < hs; y++) for (let x = 0; x < ws; x++) { const a = y * (ws + 1) + x + 1, b = y * (ws + 1) + x, c = (y + 1) * (ws + 1) + x, d = (y + 1) * (ws + 1) + x + 1;
      if (y !== 0 || t0 > 0) I.push(a, b, d); if (y !== hs - 1 || t0 + tl < Math.PI) I.push(b, c, d); }
    this._build(P, N, T, I); }
}
export class TorusGeometry extends BufferGeometry {
  constructor(R = 1, tube = 0.4, rs = 12, ts = 48, arc = Math.PI * 2) { super(); const P = [], N = [], T = [], I = [];
    for (let j = 0; j <= rs; j++) for (let i = 0; i <= ts; i++) { const u = i / ts * arc, v = j / rs * Math.PI * 2;
      const x = (R + tube * Math.cos(v)) * Math.cos(u), y = (R + tube * Math.cos(v)) * Math.sin(u), z = tube * Math.sin(v); P.push(x, y, z);
      const n = new Vector3(x - R * Math.cos(u), y - R * Math.sin(u), z).normalize(); N.push(n.x, n.y, n.z); T.push(i / ts, j / rs); }
    for (let j = 1; j <= rs; j++) for (let i = 1; i <= ts; i++) { const a = (ts + 1) * j + i - 1, b = (ts + 1) * (j - 1) + i - 1, c = (ts + 1) * (j - 1) + i, d = (ts + 1) * j + i; I.push(a, b, d, b, c, d); }
    this._build(P, N, T, I); }
}

// ---- 2D paths
export class Shape {
  constructor(pts) { this.cmds = []; this.holes = []; this.cur = [0, 0]; if (pts && pts.length) { this.moveTo(pts[0].x, pts[0].y); for (const p of pts.slice(1)) this.lineTo(p.x, p.y); } }
  moveTo(x, y) { this.cmds.push(['M', x, y]); this.cur = [x, y]; return this; }
  lineTo(x, y) { this.cmds.push(['L', x, y]); this.cur = [x, y]; return this; }
  quadraticCurveTo(cx, cy, x, y) { this.cmds.push(['Q', cx, cy, x, y]); this.cur = [x, y]; return this; }
  bezierCurveTo(a, b, c, d, x, y) { this.cmds.push(['C', a, b, c, d, x, y]); this.cur = [x, y]; return this; }
  absarc(x, y, r, a0, a1, cw) { this.cmds.push(['A', x, y, r, a0, a1, !!cw]); this.cur = [x + r * Math.cos(a1), y + r * Math.sin(a1)]; return this; }
  arc(dx, dy, r, a0, a1, cw) { return this.absarc(this.cur[0] + dx, this.cur[1] + dy, r, a0, a1, cw); }
  absellipse(x, y, rx, ry, a0, a1, cw) { this.cmds.push(['E', x, y, rx, ry, a0, a1, !!cw]); return this; }
  closePath() { return this; }
  getPoints(div = 12) { const out = []; let c = [0, 0];
    for (const k of this.cmds) {
      if (k[0] === 'M' || k[0] === 'L') { out.push(new Vector2(k[1], k[2])); c = [k[1], k[2]]; }
      else if (k[0] === 'Q') { for (let i = 1; i <= div; i++) { const t = i / div, a = (1 - t) * (1 - t), b = 2 * (1 - t) * t, d = t * t; out.push(new Vector2(a * c[0] + b * k[1] + d * k[3], a * c[1] + b * k[2] + d * k[4])); } c = [k[3], k[4]]; }
      else if (k[0] === 'C') { for (let i = 1; i <= div; i++) { const t = i / div, a = (1 - t) ** 3, b = 3 * (1 - t) ** 2 * t, d = 3 * (1 - t) * t * t, e = t ** 3; out.push(new Vector2(a * c[0] + b * k[1] + d * k[3] + e * k[5], a * c[1] + b * k[2] + d * k[4] + e * k[6])); } c = [k[5], k[6]]; }
      else if (k[0] === 'A' || k[0] === 'E') { const [x, y, rx, ry, a0, a1, cw] = k[0] === 'A' ? [k[1], k[2], k[3], k[3], k[4], k[5], k[6]] : k.slice(1);
        let d = a1 - a0; if (cw) { if (d > 0) d -= Math.PI * 2 } else if (d < 0) d += Math.PI * 2; if (Math.abs(d) < 1e-9) d = cw ? -Math.PI * 2 : Math.PI * 2;
        const n = Math.max(div * 2, Math.ceil(Math.abs(d) / (Math.PI / 16)));
        for (let i = 0; i <= n; i++) { const a = a0 + d * i / n; out.push(new Vector2(x + rx * Math.cos(a), y + ry * Math.sin(a))); } c = [out[out.length - 1].x, out[out.length - 1].y]; } }
    const cl = []; for (const p of out) { const q = cl[cl.length - 1]; if (!q || Math.hypot(p.x - q.x, p.y - q.y) > 1e-7) cl.push(p); }
    if (cl.length > 2 && Math.hypot(cl[0].x - cl[cl.length - 1].x, cl[0].y - cl[cl.length - 1].y) < 1e-7) cl.pop();
    return cl; }
  extractPoints(d) { return { shape: this.getPoints(d), holes: this.holes.map(h => h.getPoints(d)) }; }
}
export class Path extends Shape { }
const area = P => { let a = 0; for (let i = 0, j = P.length - 1; i < P.length; j = i++) a += P[j].x * P[i].y - P[i].x * P[j].y; return a / 2; };
// ear clipping on a CCW outline (holes are bridged in first). Returns triangles as index triplets into pts.
function triangulate(outer, holes) { let pts = outer.slice(); if (area(pts) < 0) pts.reverse();
  for (let h of holes) { if (area(h) > 0) h = h.slice().reverse(); let hi = 0; for (let i = 1; i < h.length; i++) if (h[i].x > h[hi].x) hi = i; const H = h[hi];
    let bi = -1, bd = 1e18; for (let i = 0; i < pts.length; i++) { const d = (pts[i].x - H.x) ** 2 + (pts[i].y - H.y) ** 2; if (pts[i].x >= H.x - 1e-9 && d < bd) { bd = d; bi = i; } } if (bi < 0) bi = 0;
    const ring = h.slice(hi).concat(h.slice(0, hi + 1)); pts = pts.slice(0, bi + 1).concat(ring, [pts[bi]], pts.slice(bi + 1)); }
  const idx = pts.map((_, i) => i), tris = []; let guard = 0;
  const cross = (a, b, c) => (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
  while (idx.length > 3 && guard++ < 20000) { let cut = false;
    for (let i = 0; i < idx.length; i++) { const a = pts[idx[(i + idx.length - 1) % idx.length]], b = pts[idx[i]], c = pts[idx[(i + 1) % idx.length]];
      if (cross(a, b, c) <= 1e-12) continue; let inside = false;
      for (const j of idx) { const p = pts[j]; if (p === a || p === b || p === c) continue; if (cross(a, b, p) > 0 && cross(b, c, p) > 0 && cross(c, a, p) > 0) { inside = true; break; } }
      if (inside) continue; tris.push([idx[(i + idx.length - 1) % idx.length], idx[i], idx[(i + 1) % idx.length]]); idx.splice(i, 1); cut = true; break; }
    if (!cut) { tris.push([idx[0], idx[1], idx[2]]); idx.splice(1, 1); } }
  if (idx.length === 3) tris.push(idx.slice());
  return { pts, tris }; }
export class ShapeGeometry extends BufferGeometry {
  constructor(shapes, segs = 12) { super(); const P = [], N = [], T = [], I = [];
    for (const s of [].concat(shapes)) { const { pts, tris } = triangulate(s.getPoints(segs), s.holes.map(h => h.getPoints(segs))), b = P.length / 3;
      for (const p of pts) { P.push(p.x, p.y, 0); N.push(0, 0, 1); T.push(p.x, p.y); } for (const t of tris) I.push(b + t[0], b + t[1], b + t[2]); }
    this._build(P, N, T, I); }
}
export class ExtrudeGeometry extends BufferGeometry {
  constructor(shapes, o = {}) { super(); const P = [], N = [], T = [], I = [], D = o.depth ?? 1, segs = o.curveSegments ?? 12, bv = o.bevelEnabled ? (o.bevelSize ?? 0.1) : 0;
    for (const s of [].concat(shapes)) { let outer = s.getPoints(segs); if (area(outer) < 0) outer = outer.slice().reverse();
      if (bv) { const n = outer.length; outer = outer.map((p, i) => { const a = outer[(i + n - 1) % n], c = outer[(i + 1) % n]; const e1 = new Vector3(p.x - a.x, p.y - a.y, 0).normalize(), e2 = new Vector3(c.x - p.x, c.y - p.y, 0).normalize();
        const nx = (e1.y + e2.y), ny = -(e1.x + e2.x), l = Math.hypot(nx, ny) || 1; return new Vector2(p.x + nx / l * bv, p.y + ny / l * bv); }); }
      const holes = s.holes.map(h => h.getPoints(segs)), { pts, tris } = triangulate(outer, holes);
      for (const [z, nz, flip] of [[0, -1, true], [D, 1, false]]) { const b = P.length / 3; for (const p of pts) { P.push(p.x, p.y, z); N.push(0, 0, nz); T.push(p.x, p.y); }
        for (const t of tris) flip ? I.push(b + t[0], b + t[2], b + t[1]) : I.push(b + t[0], b + t[1], b + t[2]); }
      for (let ring of [outer, ...holes]) { if (ring !== outer && area(ring) > 0) ring = ring.slice().reverse(); let acc = 0;
        for (let i = 0; i < ring.length; i++) { const a = ring[i], c = ring[(i + 1) % ring.length], L = Math.hypot(c.x - a.x, c.y - a.y); if (L < 1e-9) continue;
          const nx = (c.y - a.y) / L, ny = -(c.x - a.x) / L, b = P.length / 3;
          P.push(a.x, a.y, 0, c.x, c.y, 0, c.x, c.y, D, a.x, a.y, D); for (let k = 0; k < 4; k++) N.push(nx, ny, 0); T.push(acc, 0, acc + L, 0, acc + L, D, acc, D); acc += L;
          I.push(b, b + 1, b + 2, b, b + 2, b + 3); } } }
    this._build(P, N, T, I); }
}

// ---- materials and textures
export class Texture { constructor(img) { this.image = img; this.wrapS = this.wrapT = ClampToEdgeWrapping; this.repeat = new Vector2(1, 1); this.offset = new Vector2(0, 0); this.needsUpdate = false; this.userData = {}; } dispose() { } clone() { const t = new this.constructor(this.image); Object.assign(t, this); return t; } }
export class CanvasTexture extends Texture { }
class Material { constructor(o = {}) { this.color = new Color(0xffffff); this.emissive = new Color(0); this.userData = {}; this.side = FrontSide; this.transparent = false; this.opacity = 1;
    for (const k in o) { if (k === 'color' || k === 'emissive') this[k].set(o[k]); else this[k] = o[k]; } }
  dispose() { } clone() { const m = new this.constructor(); Object.assign(m, this); m.color = this.color.clone(); m.emissive = this.emissive.clone(); return m; } }
export class MeshStandardMaterial extends Material { }
export class MeshBasicMaterial extends Material { }
export class MeshLambertMaterial extends Material { }
export class MeshPhongMaterial extends Material { }

// ---- scene graph
export class Object3D {
  constructor() { this.children = []; this.parent = null; this.position = new Vector3(); this.scale = new Vector3(1, 1, 1); this.userData = {}; this.name = ''; this.visible = true;
    this.rotation = new Euler(); this.quaternion = new Quaternion();
    this.rotation._cb = () => { this.quaternion._cb = null; this.quaternion.setFromEuler(this.rotation); this.quaternion._cb = qcb; };
    const qcb = () => { this.rotation._cb = null; this.rotation.setFromQuaternion(this.quaternion, this.rotation.order); this.rotation._cb = ecb; }; const ecb = this.rotation._cb;
    this.quaternion._cb = qcb; this.matrix = new Matrix4(); this.matrixWorld = new Matrix4(); }
  add(...o) { for (const c of o) { if (!c) continue; if (c.parent) c.parent.remove(c); c.parent = this; this.children.push(c); } return this; }
  remove(...o) { for (const c of o) { const i = this.children.indexOf(c); if (i >= 0) { this.children.splice(i, 1); c.parent = null; } } return this; }
  traverse(f) { f(this); for (const c of this.children.slice()) c.traverse(f); }
  updateMatrix() { this.matrix.compose(this.position, this.quaternion, this.scale); }
  updateMatrixWorld() { this.updateMatrix(); this.matrixWorld = this.parent ? this.parent.matrixWorld.clone().multiply(this.matrix) : this.matrix.clone(); for (const c of this.children) c.updateMatrixWorld(); }
  updateWorldMatrix() { this.updateMatrixWorld(); }
  rotateX(t) { this.quaternion.multiply(new Quaternion().setFromAxisAngle(new Vector3(1, 0, 0), t)); return this; }
  rotateY(t) { this.quaternion.multiply(new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), t)); return this; }
  rotateZ(t) { this.quaternion.multiply(new Quaternion().setFromAxisAngle(new Vector3(0, 0, 1), t)); return this; }
  lookAt() { return this; }
  getWorldPosition(v) { this.updateMatrixWorld(); return v.setFromMatrixPosition(this.matrixWorld); }
  getWorldQuaternion(q) { return q.copy(this.quaternion); }
  getObjectByName(n) { let r = null; this.traverse(o => { if (!r && o.name === n) r = o; }); return r; }
  clone() { const o = new this.constructor(this.geometry, this.material); o.position.copy(this.position); o.quaternion.copy(this.quaternion); o.scale.copy(this.scale); o.name = this.name; o.userData = { ...this.userData };
    for (const c of this.children) o.add(c.clone()); return o; }
}
export class Group extends Object3D { }
export class Scene extends Object3D { }
export class Mesh extends Object3D { constructor(g, m) { super(); this.geometry = g; this.material = m; this.isMesh = true; } }
export class InstancedMesh extends Mesh { constructor(g, m, n) { super(g, m); this.count = n; this.mats = []; this.isInstancedMesh = true; } setMatrixAt(i, m) { this.mats[i] = m.clone(); } setColorAt() { } computeBoundingSphere() { } }
export class Box3 {
  constructor() { this.min = new Vector3(Infinity, Infinity, Infinity); this.max = new Vector3(-Infinity, -Infinity, -Infinity); }
  expandByPoint(p) { this.min.set(Math.min(this.min.x, p.x), Math.min(this.min.y, p.y), Math.min(this.min.z, p.z)); this.max.set(Math.max(this.max.x, p.x), Math.max(this.max.y, p.y), Math.max(this.max.z, p.z)); return this; }
  setFromObject(o) { const par = o.parent; o.parent = null; o.updateMatrixWorld(); o.parent = par;
    o.traverse(m => { if (!m.isMesh) return; const p = m.geometry.attributes.position, Ms = m.isInstancedMesh ? m.mats.map(x => m.matrixWorld.clone().multiply(x)) : [m.matrixWorld];
      for (const M of Ms) for (let i = 0; i < p.count; i++) this.expandByPoint(new Vector3(p.getX(i), p.getY(i), p.getZ(i)).applyMatrix4(M)); }); return this; }
  getSize(v) { return v.set(this.max.x - this.min.x, this.max.y - this.min.y, this.max.z - this.min.z); }
  getCenter(v) { return v.set((this.max.x + this.min.x) / 2, (this.max.y + this.min.y) / 2, (this.max.z + this.min.z) / 2); }
}
export class PointLight extends Object3D { } export class SpotLight extends Object3D { }
