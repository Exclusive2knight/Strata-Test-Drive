# Strata fluids and particles — integrated core

This is an implemented, runnable core for the existing Mission Strata / Strata Test Drive project. It is **not a completed or performance-certified version of every feature in the request**. The remaining limits are listed below rather than hidden behind passing reference tests.

## Enable and run

The actual engine is the project's custom JavaScript/WebGL 1 renderer with GLSL ES shaders. No Godot, Unity, Unreal, Three.js or native compute API was introduced. GPU compute uses float render-to-texture passes, with capability checks. The existing 300–400 Hz vehicle physics remains intact; fluids have their own fixed 60 Hz clock and 120 Hz substeps.

The changes are already applied to this checkout. From the project root:

```sh
python build.py
python -m http.server 8000
```

Use your existing esbuild installation (or set `ESBUILD` to its executable) for the protected build. Open `http://localhost:8000/dev.html` privately, start a test drive, then use **Fluids** at the bottom-left or **F8**. The panel has nine scene emitters, quality override, rain, temperature, depth/temperature views, an SDF slice, GPU smoke slice, velocity arrows, mass ledger and timing/budget display. `fluids/lab.html` has the nine reproducible fixture scenes on simple test geometry.

`index.html` is the minified official-host build; `dist/artifact.html` is the private unlocked build. Nothing was pushed to GitHub or published. Do not publish `dev.html` or the readable source.

## Files and integration

| File | Purpose |
|---|---|
| `core.js` | Conservative heightfield, CPU particle fallback, cooling, material parameters, wheel coupling, seeded random and ledger |
| `mesh_sdf.js` | Triangle distance collision for retained garage solid meshes |
| `gpu.js` | GPU grid advection, buoyancy, vorticity, pressure projection, SDF and timer passes |
| `flip.js` | PIC/FLIP water particles, trilinear scatter, free-surface pressure and mass return |
| `renderer.js` | Heightfield refraction/Fresnel, particle depth/thickness smoothing, volume raymarch, soft particles and windshield mud |
| `runtime.js` | Shared environment, fixed clocks, quality, vehicle emissions, diagnostics and scene menu |
| `integration.js` | Host coordinate conversion, surfaces, drains, vehicles, postprocessing and shader bindings |
| `tests/` | Node physics tests, browser GPU tests, host smoke test, render capture scripts and their raw results |
| `previews/` | Actual WebGL screenshots; simple fixture cars are test objects, not new vehicle models |

`build.py` inlines these modules at `/*FLUID_RUNTIME*/` and the host adapter at `/*FLUID_INTEGRATION*/`. The host shader samples wetness after the cloud pass binds its textures. Player wheel friction, water drag, buoyancy and engine flooding read the fluid state. Nearby AI cars receive per-wheel state; the main traffic acceleration path also clamps acceleration/braking by available grip and applies drag. Special scripted traffic movement paths still use their original logic.

Host physics `(x,y,height)` maps to API `[x,height,-y]`. API vectors are +Y up, metres/seconds. Volumes are **cubic metres**: 500 L is `0.5`, not `500`.

## API

After a drive starts, `window.StrataFluids` is available:

```js
const f = window.StrataFluids;
f.spawn_water([10, 1, -20], [0, -2, 1], 0.005); // 5 L
f.spawn_spill('asphalt', [10, 1.5, -20], 0.003, 150);
const smoke = f.emit_smoke('tyre', [10, 0.1, -20], 40);
smoke.move([11, 0.1, -20]);
smoke.stop();
const dust = f.emit_dust([10, 0.1, -20], 60);
dust.stop();
f.set_rain(0.7);
f.set_wind([3, 0, -1], 0.4);
f.set_temperature(25);
f.quality('Mobile'); // Mobile, Low, Medium, High, Ultra, Auto
f.on('on_splash', event => console.log(event));
f.on_wet_tyre = event => console.log(event);
f.on_burn = event => console.log(event);
f.on_spill_settled = event => console.log(event.type);
const wheel = f.sample_wheel([10, 0, -20], 25, 240, 7);
// wheel: depth (m), grip (0..1), wet, type, temperature (C)
f.mud_windshield(0.5);
f.wipe(1); // existing in-game wipers also wash the overlay
const hardened = f.get_hardened_mesh(); // typed positions, indices, heightmap
f.set_enabled(false);
```

`on_burn` is a hot-wheel contact notification, not a fire propagation/combustion solver. Fuel has a flammable metadata flag. The hardened height layer affects `groundAt` and is rendered by the liquid surface pass; the mesh API exposes exportable geometry. There is no save-to-disk persistence yet.

## Quality and performance tuning

| Tier | GPU water capacity | Smoke grid | GPU pressure iterations | Fallback |
|---|---:|---:|---:|---|
| Ultra | 131,072 | 96³ | 20 | CPU if extensions unavailable |
| High | 100,352 | 64³ | 20 | CPU if extensions unavailable |
| Medium | 16,384 | 40³ | 12 | CPU if extensions unavailable |
| Low | — | — | — | CPU heightfield, soft particles, spill film |
| Mobile | — | — | — | Same reduced path |

The integrated CPU heightfield uses 24×24 cells at 1 m spacing per retained local tile. Lab/test fixtures use finer grids. The `waterN` preset metadata is reserved; it does not change the CPU grid automatically. Medium/High/Ultra allocate local particle grids of 32³/40³/48³. Float textures, renderable float targets, vertex textures and float blending must be supported for FLIP. Grid smoke can run with float targets even if FLIP cannot blend.

Desktop defaults to Low and touch devices to Mobile. Auto currently downshifts from a chosen tier when measured fluid time exceeds 6 ms; it does not probe upward aggressively. Override through the panel/API. Reduce `smokeN`, pressure iterations, raymarch steps (48), volume target width (512), particle capacity and screen-space particle target width (512) first. Volume SDF preparation is spread over frames. Avoid many simultaneous retained heightfield tiles; there is not yet a world-streaming disk cache.

The 4 ms GPU / 1 ms CPU / 60 fps High target is **not met/validated** in this environment. Browser tests use Chromium with SwiftShader software rendering, not a midrange laptop GPU. Raw measured times are in `tests/gpu_results.json` and the test report. Synchronous particle mass readback and full CPU terrain coupling remain optimization work.

## Surfaces and collisions

Road-kit geometry is classified through the engine's `groundAt().kind` tags, not by guessing RGB pixels in atlas artwork. The adapter maps road→asphalt, pavement/kerb/garage→concrete, rock→gravel; dirt, grass, metal and glass can be returned directly by a surface provider. For custom surfaces return:

```js
{ height: 0, kind: 'dirt', color: [0.46, 0.31, 0.17],
  sheltered: false, drain: 0.003 } // drain capacity as depth m/s
```

Existing authored unblocked drain locations in `PUD.grid` become metered sinks. `sheltered` cells do not receive rain. Heightfield survey elevates obstructions and captures terrain slope; kerbs narrower than a cell require a finer grid. Existing adjacent tiles exchange conservative boundary flux when their terrain edges match. Tiles beyond the loaded camera/vehicle neighborhood are not automatically created; complete roof-to-gutter shedding is not implemented.

Static collision uses the host's existing `COLL` spatial map, sampled terrain and retained triangle meshes from the garage layer. Call `world.add(id,{pos,half,angle,vel})`, `world.remove(id)` or increment `world.version` after geometry changes to rebuild voxel SDFs. Moving vehicles have analytic body/undercarriage boxes on CPU and the nearest eight GPU boxes. This is **not** an all-map triangle SDF covering every decorative prop, animated gate and wheel; those need explicit registered colliders. Do not treat the fixture zero-penetration test as proof of complete world collision coverage.

## Parameters and adding types

`StrataFluidCore.LIQUIDS` and `SMOKE` in `core.js` are the parameter tables. Add a liquid key there, add a renderer colour/type mapping, and call `spawn_spill(key,...)`. Mud uses apparent viscosity `yield/shear + K*shear^(n-1)` with yield 18 Pa, K=4 and n=0.45. The temperature law is a calibrated Arrhenius approximation, not a measured binder specification.

| Liquid | Density kg/m³ | Reference viscosity Pa·s | Surface tension N/m | Grip | Evaporation m/s |
|---|---:|---:|---:|---:|---:|
| water | 1000 | 0.001002 | 0.07275 | 1 | 1e-7 |
| asphalt | 1100 | 0.35 | 0.032 | 0.62 | 0 |
| tar | 1150 | 0.8 | 0.035 | 0.55 | 0 |
| oil | 860 | 0.12 | 0.03 | 0.3 | 1e-9 |
| fuel | 740 | 0.0006 | 0.022 | 0.45 | 0.000002 |
| coolant | 1060 | 0.003 | 0.05 | 0.55 | 1e-7 |
| mud | 1600 | 4 | 0.06 | 0.48 | 2e-8 |
| paint | 1200 | 2 | 0.04 | 0.5 | 2e-7 |

| Smoke | Temperature °C | Buoyancy factor | Lifetime s | Colour RGB |
|---|---:|---:|---:|---|
| tyre | 35 | 0.12 | 12 | 0.72, 0.73, 0.74 |
| exhaust | 95 | 0.6 | 6 | 0.43, 0.46, 0.48 |
| diesel | 160 | 0.7 | 18 | 0.06, 0.065, 0.07 |
| damage | 130 | 0.65 | 18 | 0.18, 0.19, 0.2 |
| fire | 550 | 1 | 24 | 0.035, 0.03, 0.028 |
| steam | 100 | 0.7 | 3 | 0.85, 0.88, 0.9 |
| flare | 100 | 0.45 | 18 | 0.45, 0.06, 0.26 |

Water uses density 1000 kg/m³, dynamic viscosity 0.001002 Pa·s and surface tension 0.07275 N/m near 20°C. Hot asphalt here means **binder**, using 0.35 Pa·s at 150°C, rho 1100 kg/m³, cp 1900 J/(kg·K), a 55°C hardening threshold, a 1e10 Pa·s viscosity cap, convection 12 W/(m²·K), emissivity 0.92 and conduction to a fixed-temperature substrate. A thin 3 L test cools much faster than a tanker-sized pile. The material does not visibly incandesce at 150°C.

The wheel hydroplaning approximation is:

```
Vc = 9 * sqrt(pressure_kPa * 0.1450377) * 0.514444  [m/s]
film = clamp(depth_m / (0.0015 + 0.00065*tread_mm), 0, 1)
lift = film * (abs(speed_mps)/Vc)^2
grip = clamp(1/(1 + lift^2), 0.08, 1)
```

The 9√psi knots anchor comes from NASA's conventional hydroplaning relation. The depth/tread extension is an empirical game calibration, not a validated road tyre friction prediction. Water drag is `0.5*rho*Cd*width*min(depth,0.7)*v*abs(v)` with Cd=0.8. Buoyancy uses a submerged hull-volume approximation, capped at vehicle weight. Oil/mud minima are 0.30/0.48 per wheel. Flooding accumulates above 0.3 m; an ICE can stall above 0.5 m after sufficient exposure.

## What is simplified or unfinished

| Requested capability | Current implementation / limit |
|---|---|
| Conserving puddles/downhill/drains | Working finite-volume solver and mass ledger in local tiles with conservative exchange between loaded neighbors; no global terrain streaming |
| GPU water | Working PIC/FLIP with 95% FLIP/5% PIC, free-surface pressure, water viscosity/surface-tension approximation, GPU collisions, measured mass return; only a short 100k numerical run, not 100k at 60 fps |
| Water rendering | Screen-space depth/thickness, bilateral smoothing, refraction, absorption, Fresnel and ripple/foam approximation; reflections reuse scene colour and sky, not full SSR/planar reflection |
| Wheel spray | Contact spray and mass return, wet trails, drag/grip/flooding; no separate validated bow-wave, arch-sheet or wheel-mesh flow model |
| Rain/roofs | Rain accumulation and sheltered masks, existing game rain visuals; no complete roof shedding/routed downspouts |
| Viscous fluids | CPU conservative films, cooling/hardening, spatially coupled falling droplets, Herschel–Bulkley mud and slick grip; not a GPU viscoelastic rope-fold/string solver |
| Hot asphalt visuals | Dark binder, temperature-dependent sheen and field debug; no calibrated hot-air shimmer or full crust fracture |
| Grid smoke | GPU semi-Lagrangian advection, projection, buoyancy, vorticity, obstacles and raymarch self-shadowing; one dominant local emitter, dense atlas rather than sparse tiles |
| Distant smoke/dust | Sorted expanding soft particles; no baked flipbook impostor or prewarmed distance transition |
| Dust and grime | Fine settling, bouncing grit, dust deposition/resuspension, rain suppression, body-grime darkening, rain wash; no rigid clod solver or mapped per-body-part mud decals |
| Windshield | Procedural mud overlay washed by rain/wiper state; not a traced wiper-blade mask on the physical windshield UVs |
| Determinism | Seeded CPU reference repeat verified for 120 s on one JS runtime; no cross-device GPU bitwise determinism promise |
| Long stress run | 600 s CPU multiphysics fixture passed; no 600 s full GPU + traffic/render stress certification |
| Global collision proof | Fixture OBB and triangle tests pass; not complete coverage of every object across the entire game |
| Hardware budgets | Instrumented, not met/certified on target hardware |

These gaps are genuine remaining work; the supplied report does not relabel them as passes.

## Reproduce tests

```sh
node fluids/tests/physics.test.js
python fluids/tests/browser_compile.py
python fluids/tests/run_gpu.py
python fluids/tests/render_lab.py
python fluids/tests/game_browser.py
```

Browser scripts use Playwright and default to `/tmp/chromium` in this execution environment. Change `executable_path` to your installed Chromium or use your normal Playwright browser. Each script runs its own local HTTP server. The game test starts the actual builder's test drive; the nine screenshot fixtures use the same fluid modules on deliberately simple test geometry. Read the report for the precise scope of each PASS.

Reference sources: [IAPWS viscosity](https://iapws.org/technical-guidance/release/viscosity), [IAPWS surface tension](https://iapws.org/technical-guidance/release/Surf-H2O), [FHWA asphalt mix design](https://www.fhwa.dot.gov/publications/research/infrastructure/pavements/asphalt/mixdsgn.pdf), [Asphalt Institute binder viscosity guidance](https://www.asphaltinstitute.org/wp-content/uploads/Guidance-on-AASHTO-M320-Specification-Limit-for-Rotational-Viscosity-1.pdf), [NVIDIA GPU fluid methods](https://developer.nvidia.com/gpugems/gpugems/part-vi-beyond-triangles/chapter-38-fast-fluid-dynamics-simulation-gpu), [NASA hydroplaning discussion](https://www.nasa.gov/wp-content/uploads/2024/06/aircraft-operating-problems-talk-1964.pdf). Binder values are chosen illustrative parameters; the sources do not specify a universal 150°C viscosity for every asphalt grade.
