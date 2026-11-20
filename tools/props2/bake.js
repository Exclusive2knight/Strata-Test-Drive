// Runs inside the game page (dev.html) from tools/props2/bake.py. Builds every freeway sign the game listed in RP2_SPEC with
// strata-road-props.js (on the three.js stand-in), and bakes them into the road-kit piece format: positions in cm, normals x127,
// UVs x10000 into one texture atlas (sign art packed in, plain materials as small colour swatches), plus world colliders.
(async () => {
  const P = await import('/tools/props2/strata-road-props.js');
  const T = await import('/tools/props2/three-shim.js');
  if (document.fonts && document.fonts.ready) await document.fonts.ready;
  const card = { East: 'EAST', West: 'WEST', North: 'NORTH', South: 'SOUTH' };
  const destSpec = (to) => { const m = /^I-(\d+) (North|South|East|West)$/.exec(to || ''); return m ? { shields: [{ type: 'I', num: m[1] }], direction: card[m[2]], lines: [] } : { shields: [], direction: '', lines: [to] }; };
  const build = (S) => {
    if (S.k === 'gantry' || S.k === 'dms') {
      const signs = S.k === 'dms' ? [{ x: 0, dms: { lines: S.lines } }] : S.signs.map(g => {
        if (g.exit !== undefined) { const d = destSpec(g.to); return { x: g.x, spec: { ...d, lines: d.lines.concat(g.dist ? [g.dist] : []), arrows: 'none', exitTab: String(g.exit), width: 4.6 } }; }
        return { x: g.x, spec: g.route ? { shields: [{ type: 'I', num: g.route.slice(2) }], direction: (g.card || '').toUpperCase(), lines: [], arrows: 'down', arrowCount: 2, width: 4.6 } : { shields: [], direction: '', lines: g.dest, arrows: 'down', width: 4.6 } };
      });
      return P.createOverheadGantry({ span: Math.max(8, S.span - 1), clearance: 5.4, signs, catwalk: true, barriers: true });
    }
    if (S.k === 'cant') { const d = destSpec(S.to); return P.createCantileverSign({ arm: Math.max(7, -S.signX + 3), clearance: 5.4, spec: { ...d, arrows: 'upright', exitTab: String(S.exit), width: 4.4 }, signX: S.signX, barrier: true }); }
    if (S.k === 'gore') return P.createExitGoreSign({ exit: String(S.exit), side: 'right' });
    if (S.k === 'rail') return P.createProp('guardrail', { length: S.len, bend: 0, posts: 'steel', ends: 'terminal' });
    return null;
  };
  // ---- atlas
  const AW = 4096, regions = new Map(), solids = new Map(); let shelfX = 2, shelfY = 2, shelfH = 0; const items = [];
  const place = (w, h) => { if (shelfX + w + 2 > AW) { shelfX = 2; shelfY += shelfH + 2; shelfH = 0; } const r = { x: shelfX, y: shelfY, w, h }; shelfX += w + 2; shelfH = Math.max(shelfH, h); return r; };
  const hex = c => '#' + [c.r, c.g, c.b].map(v => Math.round(Math.max(0, Math.min(1, v)) * 255).toString(16).padStart(2, '0')).join('');
  const avg = (img) => { const c = document.createElement('canvas'); c.width = c.height = 1; const x = c.getContext('2d'); x.drawImage(img, 0, 0, 1, 1); const d = x.getImageData(0, 0, 1, 1).data; return { r: d[0] / 255, g: d[1] / 255, b: d[2] / 255 }; };
  const solid = (c) => { const k = hex(c); if (!solids.has(k)) { const r = place(6, 6); solids.set(k, r); items.push({ r, fill: k }); } return solids.get(k); };
  const region = (mat) => {
    const map = mat.map, col = mat.color || { r: 1, g: 1, b: 1 };
    if (!map || !map.image) return { solid: solid(col) };
    const img = map.image, rep = map.wrapS === T.RepeatWrapping || map.wrapT === T.RepeatWrapping;
    if (rep) { const a = avg(img); return { solid: solid({ r: a.r * col.r, g: a.g * col.g, b: a.b * col.b }) }; }
    const k = img; if (!regions.has(k)) { const s = Math.min(1, 640 / Math.max(img.width, img.height)), w = Math.max(4, Math.round(img.width * s)), h = Math.max(4, Math.round(img.height * s)); const r = place(w, h); regions.set(k, r); items.push({ r, img }); }
    return { reg: regions.get(k), img };
  };
  // ---- bake one prop into a piece
  const bakeObj = (root) => {
    const p = [], n = [], t = [], I = []; root.updateMatrixWorld();
    root.traverse(m => {
      if (!m.isMesh || m.visible === false) return; const mat = Array.isArray(m.material) ? m.material[0] : m.material; if (!mat || mat.visible === false) return;
      const g = m.geometry, pos = g.attributes.position, nor = g.attributes.normal, uv = g.attributes.uv; if (!pos) return;
      const idx = g.index ? Array.from(g.index.array) : [...Array(pos.count).keys()], R = region(mat), two = mat.side === T.DoubleSide;
      const Ms = m.isInstancedMesh ? m.mats.slice(0, m.count).map(x => m.matrixWorld.clone().multiply(x)) : [m.matrixWorld];
      for (const M of Ms) {
        const e = M.elements, inv = M.clone().invert().elements, b = p.length / 3;
        for (let i = 0; i < pos.count; i++) {
          const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i); p.push(Math.round((e[0] * x + e[4] * y + e[8] * z + e[12]) * 100), Math.round((e[1] * x + e[5] * y + e[9] * z + e[13]) * 100), Math.round((e[2] * x + e[6] * y + e[10] * z + e[14]) * 100));
          let nx = 0, ny = 1, nz = 0; if (nor) { const a = nor.getX(i), bb = nor.getY(i), c = nor.getZ(i); nx = inv[0] * a + inv[1] * bb + inv[2] * c; ny = inv[4] * a + inv[5] * bb + inv[6] * c; nz = inv[8] * a + inv[9] * bb + inv[10] * c; const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l; }
          n.push(Math.round(nx * 127), Math.round(ny * 127), Math.round(nz * 127));
          let u, v; if (R.solid) { u = (R.solid.x + 3) / AW; v = R.solid.y + 3; }
          else { const r = R.reg; let a = uv ? uv.getX(i) : 0, c = uv ? uv.getY(i) : 0; a = Math.max(0, Math.min(1, a)); c = Math.max(0, Math.min(1, c)); u = (r.x + 0.5 + a * (r.w - 1)) / AW; v = r.y + 0.5 + (1 - c) * (r.h - 1); }
          t.push(Math.round(u * 10000), v);   // v in atlas pixels for now (the atlas height is known at the end)
        }
        for (let k = 0; k < idx.length; k += 3) { I.push(b + idx[k], b + idx[k + 1], b + idx[k + 2]); }
        if (two) { const b2 = p.length / 3; for (let i = 0; i < pos.count; i++) { p.push(p[(b + i) * 3], p[(b + i) * 3 + 1], p[(b + i) * 3 + 2]); n.push(-n[(b + i) * 3], -n[(b + i) * 3 + 1], -n[(b + i) * 3 + 2]); t.push(t[(b + i) * 2], t[(b + i) * 2 + 1]); }
          for (let k = 0; k < idx.length; k += 3) I.push(b2 + idx[k], b2 + idx[k + 2], b2 + idx[k + 1]); }
      }
    });
    return { p, n, t, i: I };
  };
  // ---- colliders: the prop's own obstacle list, in world coordinates
  const toWorld = (S, lx, lz) => { const h = Math.PI / 2 - S.h, c = Math.cos(h * 1), sn = Math.sin(h), ex = lx, ny = -lz; return [S.x + ex * c + ny * sn, S.y - ex * sn + ny * c]; };
  // ---- W-beam guardrail either side of the bridge piers in the freeway median (each carriageway gets its own run, rail toward the traffic)
  { const seen = new Set(), piers = [];
    for (const L of COLL.g.values()) for (const o of L) { if (seen.has(o)) continue; seen.add(o); if (!/bridge pier/.test(o.what || '')) continue;
      let b = null; for (const e of EDGES) { if (e.type !== 'xway') continue; const q = eProj(e, o.x, o.y); if (q.u < 0 || q.u > e.L) continue; if (!b || q.d < b.q.d) b = { e, q }; } if (b && b.q.d < 3) piers.push({ x: o.x, y: o.y, e: b.e, u: b.q.u }); }
    const groups = []; for (const p of piers) { const g = groups.find(g => g.e === p.e && Math.abs(g.u0 - p.u) < 40); if (g) { g.u0 = Math.min(g.u0, p.u); g.u1 = Math.max(g.u1, p.u); } else groups.push({ e: p.e, u0: p.u, u1: p.u }); }
    for (const g of groups) { const e = g.e, a = Math.max(0, Math.floor(g.u0 - 15)), b = Math.min(e.L, Math.ceil(g.u1 + 15)), L = b - a; if (L < 20) continue;
      for (const dir of [1, -1]) { const s0 = dir > 0 ? a : e.L - b, P0 = eAt(e, dir > 0 ? a : b), T = dir > 0 ? P0.h : P0.h + Math.PI;   // the run's start, upstream for this carriageway
        const side = 2.4, x = P0.x - Math.sin(T) * side, y = P0.y + Math.cos(T) * side;   // left of the traffic: in the median, 2.4 m off the centre line
        RP2_SPEC.push({ k: 'rail', x, y, z: ez(e, dir > 0 ? a : b), h: T + Math.PI / 2, len: L, T }); } } }
  const out = { pieces: {}, place: [], coll: [] }; let k = 0;
  for (const S of RP2_SPEC) {
    let o; try { o = build(S); } catch (e) { console.warn('rp2', S.k, e); continue; } if (!o) continue;
    const key = S.k + (k++); out.pieces[key] = bakeObj(o); const hd = (90 - S.h * 180 / Math.PI + 720) % 360; out.place.push([key, +S.x.toFixed(3), +S.y.toFixed(3), +hd.toFixed(3), +S.z.toFixed(3)]);
    if (S.k === 'rail') { const m = [S.x + Math.cos(S.T) * S.len / 2, S.y + Math.sin(S.T) * S.len / 2]; out.coll.push({ t: 'b', x: +m[0].toFixed(2), y: +m[1].toFixed(2), h: +S.T.toFixed(4), hl: S.len / 2, hw: 0.22, z0: S.z - 0.3, z1: S.z + 0.85 }); continue; }
    const obs = (o.userData.strata && o.userData.strata.obstacles) || [];
    for (const b of obs) { const w = toWorld(S, b.x, b.z);
      if (b.type === 'circle') out.coll.push({ t: 'c', x: +w[0].toFixed(2), y: +w[1].toFixed(2), r: b.r, z0: S.z - 0.3, z1: S.z + 7 });
      else { const ax = toWorld(S, b.x + Math.sin(b.rot || 0), b.z + Math.cos(b.rot || 0)); out.coll.push({ t: 'b', x: +w[0].toFixed(2), y: +w[1].toFixed(2), h: +Math.atan2(ax[1] - w[1], ax[0] - w[0]).toFixed(4), hl: b.hz, hw: b.hx, z0: S.z - 0.3, z1: S.z + 1.5 }); } }
  }
  // gore signs are a single post: a small collider of their own
  for (const pl of out.place) if (pl[0].startsWith('gore')) out.coll.push({ t: 'c', x: pl[1], y: pl[2], r: 0.12, z0: pl[4] - 0.3, z1: pl[4] + 4 });
  // ---- draw the atlas, then turn pixel V into 0..1
  const AH = Math.pow(2, Math.ceil(Math.log2(shelfY + shelfH + 4)));
  const cv = document.createElement('canvas'); cv.width = AW; cv.height = AH; const x = cv.getContext('2d'); x.fillStyle = '#808080'; x.fillRect(0, 0, AW, AH);
  for (const it of items) { if (it.fill) { x.fillStyle = it.fill; x.fillRect(it.r.x - 1, it.r.y - 1, it.r.w + 2, it.r.h + 2); } else { x.drawImage(it.img, it.r.x, it.r.y, it.r.w, it.r.h); } }
  let tris = 0; for (const pc of Object.values(out.pieces)) { tris += pc.i.length / 3; for (let i = 1; i < pc.t.length; i += 2) pc.t[i] = Math.round(pc.t[i] / AH * 10000); }
  out.tris = tris;
  out.atlas = [AW, AH];
  // compact: each array as little-endian binary in base64 (positions int16 cm, normals int8, UVs uint16 x10000, indices uint16)
  const b64 = (T_, a) => { const u = new Uint8Array(new T_(a).buffer); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); };
  const same = new Map(), alias = {};
  for (const [kk, pc] of Object.entries(out.pieces)) { if (pc.p.length / 3 > 65535) throw new Error('piece too big ' + kk); const enc = { p: b64(Int16Array, pc.p), n: b64(Int8Array, pc.n), t: b64(Uint16Array, pc.t), i: b64(Uint16Array, pc.i) };
    const sig = enc.p + enc.t; if (same.has(sig)) { alias[kk] = same.get(sig); delete out.pieces[kk]; } else { same.set(sig, kk); out.pieces[kk] = enc; } }   /* identical props (guardrail runs of one length) share one piece */
  for (const pl of out.place) if (alias[pl[0]]) pl[0] = alias[pl[0]];

  window.__RP2 = { json: JSON.stringify(out), jpg: cv.toDataURL('image/jpeg', 0.88) };
  return JSON.stringify({ tris: out.tris, props: out.place.length, kinds: [...new Set(RP2_SPEC.map(s => s.k))], coll: out.coll.length, atlas: [AW, AH], tex: regions.size, solids: solids.size });
})()
