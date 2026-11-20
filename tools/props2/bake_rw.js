// Bakes a few road props v2 pieces into the game's plain prop format (props/<key>.json: int16 mm positions, int8 normals, uint16
// indices, one group per material colour) for the road-work zones: a 6 m temporary concrete barrier and a water-filled barrier
// unit. Runs in the game page from tools/props2/bake.py. Each piece is centred, running along local +Z (like the road-work props).
(async () => {
  const P = await import('/tools/props2/strata-road-props.js'); const T = await import('/tools/props2/three-shim.js');
  const lin = c => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  const avg = img => { const c = document.createElement('canvas'); c.width = c.height = 1; const x = c.getContext('2d'); x.drawImage(img, 0, 0, 1, 1); const d = x.getImageData(0, 0, 1, 1).data; return [d[0] / 255, d[1] / 255, d[2] / 255]; };
  const b64 = (Ty, a) => { const u = new Uint8Array(new Ty(a).buffer); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); };
  const bake = (o, turn) => {
    o.updateMatrixWorld(); const groups = new Map();
    o.traverse(m => { if (!m.isMesh || m.visible === false) return; const mat = Array.isArray(m.material) ? m.material[0] : m.material;
      let c = [mat.color.r, mat.color.g, mat.color.b]; if (mat.map && mat.map.image) { const a = avg(mat.map.image); c = c.map((v, i) => v * a[i]); }
      const key = c.map(v => v.toFixed(2)).join(','); let G = groups.get(key); if (!G) groups.set(key, G = { c, p: [], n: [], i: [] });
      const g = m.geometry, pos = g.attributes.position, nor = g.attributes.normal, idx = g.index ? Array.from(g.index.array) : [...Array(pos.count).keys()];
      const Ms = m.isInstancedMesh ? m.mats.slice(0, m.count).map(x => m.matrixWorld.clone().multiply(x)) : [m.matrixWorld];
      for (const M of Ms) { const e = M.elements, inv = M.clone().invert().elements, b = G.p.length / 3;
        for (let i = 0; i < pos.count; i++) { const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i); G.p.push(e[0] * x + e[4] * y + e[8] * z + e[12], e[1] * x + e[5] * y + e[9] * z + e[13], e[2] * x + e[6] * y + e[10] * z + e[14]);
          const a = nor ? nor.getX(i) : 0, bb = nor ? nor.getY(i) : 1, cc = nor ? nor.getZ(i) : 0; let nx = inv[0] * a + inv[1] * bb + inv[2] * cc, ny = inv[4] * a + inv[5] * bb + inv[6] * cc, nz = inv[8] * a + inv[9] * bb + inv[10] * cc; const l = Math.hypot(nx, ny, nz) || 1; G.n.push(nx / l, ny / l, nz / l); }
        for (const k of idx) G.i.push(b + k); } });
    // centre it and (turn) run it along +Z
    const all = [...groups.values()]; let mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
    for (const G of all) for (let i = 0; i < G.p.length; i += 3) for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], G.p[i + k]); mx[k] = Math.max(mx[k], G.p[i + k]); }
    const cx = (mn[0] + mx[0]) / 2, cz = (mn[2] + mx[2]) / 2;
    const P_ = [], N_ = [], I_ = [], g_ = [], mats = []; let lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
    all.forEach((G, mi) => { const b = P_.length / 3, s0 = I_.length;
      for (let i = 0; i < G.p.length; i += 3) { let x = G.p[i] - cx, y = G.p[i + 1] - mn[1], z = G.p[i + 2] - cz, nx = G.n[i], nz = G.n[i + 2]; if (turn) { [x, z] = [-z, x]; [nx, nz] = [-nz, nx]; }
        P_.push(Math.round(x * 1000), Math.round(y * 1000), Math.round(z * 1000)); N_.push(Math.round(nx * 127), Math.round(G.n[i + 1] * 127), Math.round(nz * 127)); lo = [Math.min(lo[0], x), Math.min(lo[1], y), Math.min(lo[2], z)]; hi = [Math.max(hi[0], x), Math.max(hi[1], y), Math.max(hi[2], z)]; }
      for (const k of G.i) I_.push(b + k); g_.push([mi, s0, G.i.length]); mats.push([...G.c.map(v => +lin(v).toFixed(3)), 1, 0, 0.1, 0.6, 'm' + mi]); });
    const r3 = a => a.map(v => +v.toFixed(3));
    return { objects: { body: { p: b64(Int16Array, P_), n: b64(Int8Array, N_), i: b64(Uint16Array, I_), g: g_ } }, mats, nodes: { body: [0, 0, 0] }, parts: { body: [r3(lo), r3(hi)] }, min: r3(lo), max: r3(hi) };
  };
  const out = { rw_pcb: bake(P.createProp('concreteBarrier', { length: 6, bend: 0, reflectors: true }), true), rw_water: bake(P.createProp('waterBarrier', { count: 1 }), true) };
  window.__RW = out; return JSON.stringify(Object.fromEntries(Object.entries(out).map(([k, v]) => [k, [v.min, v.max, v.mats.length]])));
})()
