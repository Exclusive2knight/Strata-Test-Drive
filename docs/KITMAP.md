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

## Also done
- Outer two-lane ring road (x ±2200, y ±2900); the four main streets cross it at four-ways and end in residential loops;
  a residential loop off the middle of each ring side. No dead ends (855 pieces, 0 bad joints, 0 open ends).
- Pieces with two ends stay part of the road even when the profile changes; a road takes the lane layout of the narrowest
  profile it runs through (lane counts changing at a node stopped traffic).
- Kit world zones: downtown is "city", each cluster of residential streets is "sub" (the builders fill it with houses);
  the freight line runs south of the map.
- Homes pack: 8 house shells added to the house kit (`tools/import_homes.py`, objects `House_Pack*`), on the builders' lists.

## Still to do
1. Re-place the places on the kit map: Fort St garage, the mall, the airport (its roads were built in buildNet2), dealerships,
   gas stations, the service plaza (PAD) and the parallel-parking block (PARK), the start points.
2. More country: rural roads (RURAL2 butts onto CITY2 / RES2, see COMPAT), hills, a river with the kit's river bridges.
3. Road props v2 (three.js) need a small THREE shim; place them on the new map.
4. Switch the default world to the kit world when the tests pass on it (tai, tkit, tgr, tfw, pa1-5, t_all, tfsd), silent release.

## Live since v35.2–35.6 (old map in kit pieces, on by default; ?roads=old for the generated look)
- `tools/kitmaps/oldmap.py` fits kit pieces to `tools/kitmaps/oldnet.json` (exported by `tools/export_net.js` from the running game):
  straights cut / graded / bent per segment (16 m on hills, 32 m flat), each placed on its own sample point (no drift);
  `%dw` widens a piece's kerb to the road's own kerb line (`hw`), `!f` drops kerb + sidewalk within 80 m of a ramp merge;
  95 kit intersections at near-right-angle 4-ways / T's (exact profile matches first), their leg reach saved as `kj`.
- Game: `kitShape` cuts / grades / bends / widens / flattens base pieces itself (`props/kitold_pieces.json` holds only ~17 bases),
  `kitLoad` builds the mesh 8 ms a slice; at kit intersections the generated crosswalks, stop lines and junction pad are skipped and
  traffic stops at `kj` reach − 1.2 m; generated sidewalks / kerbs / bike lanes are not drawn under kit roads; the generated surface sits 4 cm lower.
- Freeway crossover work zones (`rwXMake`, `rwXSteer`, test `tools/tests/txover.js`): lane 0 is the OUTSIDE lane, n-1 next to the median.
  Remaining: ~770 overlap samples / 5 min in very heavy traffic at the start of the drum taper.

## Next (asked for: "all of it")
1. DONE v35.7: kit merges on the old freeway. The game reshapes each straight-freeway exit / entrance ramp to the kit piece
   (`kitMerges`: hidden diagonal off the centre line, the kit's parallel lane and S-shaped split (`KMD`), a bend onto the old ramp; the
   piece is cut shorter (k 0.42-1) where the ramp is short) and holds the ramp level with the freeway along it (`e.kmH`, zfx). `kitMrgOut`
   lists the ones that fit (level or evenly graded), `tools/export_net.js` exports them as `M`, `oldmap.py` places them and cuts the
   carriageway / ramp straights around them. 29 of 35 placed; the rest sit on uneven grades (cut, I-61 bridge).
2. The I-38/I-61 interchange from a kit interchange piece (`ix01_full_cloverleaf`, `ix05_stack_four_level`, …): replace the old cloverleaf's
   edges in `buildNet2` with the kit piece's ramps (derive lane paths from the piece mesh or author them along its ramps), line I-38 and I-61
   up to its eight joints, rebuild AI routes / GPS there, keep `tfw.js` and `tai.js` clean.
3. Traffic: BeamNG-style curve speed from grip (slower in rain / snow), GTA-style side probes so cars steer round off-lane obstacles
   (also fixes the crossover taper bunching), more driving styles.
4. Road props v2 (three.js) need a THREE shim; place them with the work zones.
