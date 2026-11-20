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
1. DONE v35.7-35.8: kit merges on the old freeway. The game reshapes each straight-freeway exit / entrance ramp to the kit piece
   (`kitMerges`: hidden diagonal off the centre line, the kit's parallel lane and S-shaped split (`KMD`), a bend onto the old ramp). The split
   runs as far out as the bend onto the rest of the ramp allows (`fits`), the piece is cut to k = 0.74-1 so the S stays gentle (traffic keeps
   ~22 m/s through it), a plain joint in the replaced stretch moves to where the split starts, and the ramp's junction leg heading is taken
   there (`e.kmLeg`; merge nodes only allow straight-on moves, and the hidden diagonal is steep). The ramp holds the freeway's height along
   the piece (`e.kmH`, zfx). `kitMrgOut` lists the ones that fit (level or evenly graded), `tools/export_net.js` exports them as `M`,
   `oldmap.py` places them and cuts the carriageway / ramp straights around them. 22 of 32 placed; the rest cross grade changes (the cuts,
   the I-61 bridge, the stack's outer exits) and keep the reshaped ramp drawn with bent straights.
2. The I-38/I-61 interchange from a kit interchange piece (`ix01_full_cloverleaf`, `ix05_stack_four_level`, …): replace the old cloverleaf's
   edges in `buildNet2` with the kit piece's ramps (derive lane paths from the piece mesh or author them along its ramps), line I-38 and I-61
   up to its eight joints, rebuild AI routes / GPS there, keep `tfw.js` and `tai.js` clean.
3. DONE v35.8, traffic: curve speed from grip (`aiMu`, `aiLatG`: 0.22-0.46 g by driving style, x0.7 in rain, x0.45 on snow), GTA-style
   nudging round stopped things that stick part way into the lane (`aiNudge`, up to 1.2 m, 0.6 m past an outside lane, not with someone
   alongside), two new styles (eco, sport). `tools/tests/txover.js` 5-min heavy traffic: overlaps ~950-1030 vs 1020-1500 before, stuck 19-24 vs 35-39.
4. DONE v35.9, road props v2: `tools/props2/bake.py` runs strata-road-props.js (its `three` import pointed at `three-shim.js`) in the game page,
   builds every freeway sign the game lists in `RP2_SPEC` (sign bridges, cantilevers, gore signs, message boards; `rp2Clear` keeps sign bridges
   out from under overpasses) plus median guardrail at bridge piers, and bakes them to props/rp2.json (base64 binary pieces, colliders) +
   props/rp2_atlas.jpg. The game draws them with the textured shader (`rp2Load` / `rp2Draw`); ?props=old brings back the generated signs.
   Rebake after anything that moves the freeway signs: build, then `python3 tools/props2/bake.py`.
   Flyovers: raised stretches (over 2.5 m above ground) use `ramp1_flyover_st48!p` (the kit's deck, pier stripped); the generated dark deck is hidden.
5. Notes: tfw.js steering was under-damped (its own scripted car weaved into the piers now and then); it now steers 0.1 x offset + 0.8 x heading.
   Random scripted traffic crashes (evCrash) can still put a crash scene in its path. Flyover decks: the generated dark deck (SCN.fDeck)
   is drawn over the kit ramp up there; hiding it showed patchy kit pieces, so it stays.
