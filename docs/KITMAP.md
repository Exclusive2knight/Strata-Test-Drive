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

## Done so far (on branch wip-pack-cars-kitmap, open with ?world=kit)
- `tools/kitmaps/strata.py`: map v1 — a 5 x 5 downtown (two-lane streets, four-lane main streets, signals, curved corners) inside a
  3-lane freeway ring (3.2 km x 1.8 km sides, 400 m radius corners) with a diamond interchange on every side: exit ramps climb 7 m to
  signalised ramp terminals on an overpass street, entrance ramps drop back down. 443 pieces, 0 bad joints.
- kit_map.py also writes the road graph: junction nodes (with heights), edges with per-point heights (`kz`), freeway exits /
  entrances as merge nodes on the median line with the ramp curving off along the speed-change lane, one-way roads in traffic order,
  "out" connectors only mate with "in" ones (the two carriageways share the median line).
- Game: `?world=kit` builds the network from it (`buildNetKit`), draws the kit meshes (`kitDraw`) instead of the generated road
  surface / markings / sidewalks, keeps the land flat, drops the old rivers and the fixed Grand River retail strip, and sends every
  start point downtown. Old places that hang off named old roads fall back to the longest road (`ePick`).
- Tests: `Q="?world=kit" python3 tools/run.py tools/tests/tai.js` (0 stuck in 5 min), `tools/tests/tkit.js` (ground follows every
  kit ramp / overpass, worst 0.15 m).

## Still to do
1. Game side: load the packed pieces (`props/kitmap_pieces.json` + the new atlas as `props/roadkit2_atlas.jpg`; keep the old
   `props/road_atlas.jpg` until the old map is gone), draw them chunked by 320 m tiles like the other static meshes, and use the
   `_col` meshes / road surface for `groundAt`.
2. Road graph from the layout: chains of linear pieces between intersections become one edge each (polyline from the connector
   poses, arcs sampled), intersections become nodes (signals from the kit's `conn_prop_signal_*`). Profile → road type:
   CITY2 st, CITY4 art, CITY5 ave, CITY6D/BLVD6D blvd, RES2 res, RURAL2 road, FWYnG/B paired carriageways → xway, RAMP1/2 ramp.
   The engine's own road meshes are skipped for kit edges.
3. Grow the layout: the four outer streets stop 190 m past the freeway (dead ends for now); add suburbs (RES2 grids off
   x_city4_res2_T), rural roads (RURAL2; no kit piece joins RURAL2 to the city profiles, so allow a CITY2/RURAL2 joint),
   then re-place every place (garage, mall, airport, dealerships, gas stations, homes) along the new roads.
4. Road props v2 (three.js library) need a small THREE shim that turns its meshes into the game's format; place them on the new map.
5. Houses from the homes pack (cottage, modern shed); the apartments stay on hold.
6. Tests: tai, tgr, tfw, pa1-5, t_all, tfsd on the new map; switch the default world when they pass.
