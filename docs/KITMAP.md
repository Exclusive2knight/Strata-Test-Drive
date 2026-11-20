# The road-kit map (in progress, not released)

The whole map is being rebuilt from the road kit (roadkit_fixed: 473 snap-together pieces, one shared atlas).
It is a silent change: nothing about it goes in the changelog.

## Tools (done)
- `tools/kit_pack.py <roadkit> <out.json> [--layout kitmap.json | names…]`: packs the pieces a layout uses into one JSON
  (positions in cm, normals ×127, atlas UVs ×10000, indices, connectors, optional `lod`). The whole kit is 438k triangles / 32 MB,
  so only the pieces a map uses are packed.
- `tools/kit_map.py <roadkit> <layout script> <out.json> [preview.png]`: runs a layout script against a `Kit`,
  snaps pieces at their connectors, checks every joint (2 cm / 0.5° / same profile) and lists open ends, and draws a top-down preview.
  World axes are the game's road-graph axes: x east, y north; heading 0 = north, clockwise.
- `tools/kitmaps/test_grid.py`: a 3 × 3 four-lane grid. Loops close exactly (0 bad joints).

## Grid arithmetic
- Straights come in 24 / 48 / 96 m, so with `x_city4_4way` (legs at ±28.4 m) the intersection pitch is 56.8 + 24·n m.
- Curves: 90° r18 (city), 45° r60, 30° r150; freeway 15° r700 and 30° r400; ramp curves 30/45/90°.

## Still to do
1. Game side: load the packed pieces (`props/kitmap_pieces.json` + the new atlas as `props/roadkit2_atlas.jpg`; keep the old
   `props/road_atlas.jpg` until the old map is gone), draw them chunked by 320 m tiles like the other static meshes, and use the
   `_col` meshes / road surface for `groundAt`.
2. Road graph from the layout: chains of linear pieces between intersections become one edge each (polyline from the connector
   poses, arcs sampled), intersections become nodes (signals from the kit's `conn_prop_signal_*`). Profile → road type:
   CITY2 st, CITY4 art, CITY5 ave, CITY6D/BLVD6D blvd, RES2 res, RURAL2 road, FWYnG/B paired carriageways → xway, RAMP1/2 ramp.
   The engine's own road meshes are skipped for kit edges.
3. The map layout itself: downtown grid, suburbs (RES2), rural roads, a freeway with diamond / cloverleaf interchanges,
   then every place (garage, mall, airport, dealerships, gas stations, homes) re-placed along the new roads.
4. Road props v2 (three.js library) need a small THREE shim that turns its meshes into the game's format; place them on the new map.
5. Houses from the homes pack (cottage, modern shed); the apartments stay on hold.
6. Tests: tai, tgr, tfw, pa1-5, t_all, tfsd on the new map; switch the default world when they pass.
