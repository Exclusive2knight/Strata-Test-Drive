# Research plan: every car and feature

Goal: every real car in Strata Test Drive should match the real car. This file lists what is already researched, what is only estimated, and what still needs research, with the data formats the game uses. Work through it in Claude Code; each section can be its own session.

See `docs/CARS.md` for the full inventory (541 real trims + the built-in Strata cars) with each car's current modes, EV modes, suspension and research status.

## How to run a research task

1. Split the work by model line into batches of about 20 lines, and research them in parallel with subagents (about 1–3 web searches per model line; manufacturer spec sheets, owner's manuals, press kits, Car and Driver / MotorTrend / Edmunds / GM Authority).
2. Each batch writes JSON to `tools/research/<topic>_<n>.json` in the format below and marks every entry `"conf": "confirmed"` (found in a source) or `"estimate"`.
3. Merge the batches, check every trim key is covered, then apply the data in `src/app_template.html` (the tables named below), rebuild, run the tests listed in `CLAUDE.md`, and release with a changelog entry.
4. Never invent data for fictional cars (`Strata …`, `Aureon HX`, the `2027 Infiniti QX55 Concept`); give them sensible values and say they're made up.

## Status

| Area | Status | Where it lives |
|---|---|---|
| Drive mode names and what each does | Done for 541 trims (some from memory: mostly Kia, some Volvo/Audi; GM trim splits partly guessed) | `DMODES` (`m` list), applied by `dmApply()` |
| Terrain programs (Multi-Terrain Select, X-MODE, Trail Mode) | Done where present | `DMODES[k].t`, `terrList()` |
| EV / battery modes for hybrids and plug-ins | Done for 25 hybrids/PHEVs | `DMODES[k].ev` → `T.evBtn`, `T.evName`, `T.eModes` |
| Suspension hardware | Done for 541 trims, **97 estimates** (list below) | `SUSR`, `susDerive()`, `susApply()` |
| Wheel travel, ground clearance, ride-height ranges | Mostly estimates | `SUSR` fields 6–8 |
| Matrix / adaptive driving beam headlights | Done (US availability, Oct 2026) | `MATRIX_ON` |
| Driver assists: which trims have which, and the real names | **Needs research** | trim `std` text, `has()`, `FEAT_PKG`, packages `PKGS` |
| Clusters and screens (real layout per brand) | Partly (Tesla, Toyota, Ford, GM, Hyundai/Kia ACC, EV ring) | `drawCluster`, `accView`, `drawEVRingCluster` |
| Performance figures (hp, torque, weight, 0–60, top speed, battery, range, mpg) | **Needs a verification pass** | `TRIMS[k]` (`kW`, `mass`, `mpg`, `kWh`, `evMi`), `DRIVES[k]` |
| Packages, prices, colours, wheels | **Needs a verification pass** | `BDATA`, `PKGS` |
| Cadillac Escalade model | Waiting for the player to re-upload the Cadillac zip (the first upload was corrupt) | — |

## Task 1 — Driver assists per trim (biggest gap)

For every real trim, find which of these it has as standard, optional (and in which package), or not at all, and the real marketing name:
automatic emergency braking (and pedestrian/cyclist, junction turn), forward collision warning, adaptive cruise (stop & go?), lane keeping / lane centring, hands-free driving (Super Cruise, BlueCruise, Highway Driving Assist 2, Pilot Assist, Autopilot / FSD), automatic lane change, blind spot monitoring, rear cross-traffic alert and braking, reverse AEB, evasive steering assist, emergency lane keeping, speed sign recognition / intelligent speed assist, automatic high beams, matrix headlights, park assist (perpendicular / parallel / remote), 360° camera, head-up display, auto hold, hill descent control, trailer assist.

Format, per trim key:
```json
{"aeb": ["std", "Pre-Collision System"], "acc": ["std", "Full-Speed Dynamic Radar Cruise Control"], "pilot": ["opt:Driver Assist Pro", "BlueCruise"], "...": ["none", ""], "conf": "confirmed"}
```
Apply by updating each trim's feature availability (`has()` rules, `FEAT_PKG`, `OLD_NO`) and the names shown in the HUD and settings (e.g. `pilotName`, `pilotShort`).

## Task 2 — Check the suspension estimates

These trims' suspension entries are estimates; confirm or correct them (same format as `tools/research/susres*.json`):

- **Acura MDX · 2026**: `acura_mdx_tys`
- **Audi Q3 · 2027**: `audi_q3_pr`, `audi_q3_pp`, `audi_q3_ps`
- **Audi Q6 Sportback e-tron · 2027**: `audi_q6_sportback_etron_ps`
- **Audi Q6 e-tron · 2027**: `audi_q6_etron_ps`, `audi_q6_etron_sq6`
- **Buick Envision · 2026**: `buick_envision_pref`, `buick_envision_st`, `buick_envision_av`
- **Chevrolet Blazer EV · 2027**: `chv_blazer_ev_ss`
- **Chevrolet Colorado · 2026**: `chv_colorado_wt`, `chv_colorado_lt`, `chv_colorado_z71`
- **Chevrolet Equinox · 2027**: `chv_equinox_lt`, `chv_equinox_rs`
- **Chevrolet Silverado EV · 2026**: `chv_silverado_ev_wt`, `chv_silverado_ev_lt`, `chv_silverado_ev_trail`
- **Chevrolet Suburban · 2026**: `chv_suburban_z71`
- **Chevrolet Tahoe · 2026**: `chv_tahoe_z71`
- **Ford Bronco Sport · 2026**: `ford_bronco_sport_sq`
- **Ford E-Transit · 2027**: `ford_e_transit_cc`
- **Ford Escape · 2025**: `esc_elite`
- **Ford Expedition · 2027**: `ford_expedition_act`, `ford_expedition_ki`
- **Ford Explorer · 2026**: `expl_stline`
- **Ford Maverick · 2026**: `ford_maverick_lobo`
- **Ford Transit · 2027**: `ford_transit_trail`
- **GMC Acadia · 2027**: `acadia_den`
- **GMC Hummer EV SUV · 2026**: `hummersuv`
- **GMC Sierra 1500 Crew Cab · 2027**: `sierra_elev`
- **GMC Sierra 3500 HD Crew Cab Dually · 2026**: `sierra3500`
- **GMC Sierra EV Crew Cab · 2026**: `sierraev_elev`
- **GMC Terrain · 2027**: `terrain`, `terrain_at4`
- **Honda CR-V · 2027**: `honda_cr_v_tsl`
- **Honda Passport · 2027**: `honda_passport_rtl`
- **Honda Prologue · 2026**: `honda_prologue_ex`, `honda_prologue_exl`, `honda_prologue_tour`
- **Infiniti QX55 · 2027 Concept**: `qx_sens`, `qx_auto`
- **Jeep Gladiator · 2026**: `jeep_gladiator_rubx`
- **Jeep Wagoneer S · 2026**: `jeep_wagoneer_s_lim`, `jeep_wagoneer_s_lim2`, `jeep_wagoneer_s_trail`
- **Kia EV3 · 2027**: `kia_ev3_light`, `kia_ev3_wind`, `kia_ev3_gtl`
- **Kia Seltos · 2027**: `kia_seltos_lx`, `kia_seltos_s`, `kia_seltos_xl`, `kia_seltos_sx`
- **Kia Sportage · 2027**: `kia_sportage_xp`
- **Kia Telluride · 2027**: `kia_telluride_lx`, `kia_telluride_s`, `kia_telluride_ex`, `kia_telluride_xp`, `kia_telluride_sxp`, `kia_telluride_hev`
- **Lexus RZ · 2026**: `lex_rz_550e`
- **Lincoln Corsair · 2025**: `cor_res`
- **Nissan Armada · 2026**: `nissan_armada_sv`, `nissan_armada_sl`, `nissan_armada_plat`
- **Nissan LEAF · 2026**: `nissan_leaf_s`, `nissan_leaf_sv`, `nissan_leaf_plat`
- **Nissan Rogue · 2027**: `nissan_rogue_s`, `nissan_rogue_sv`, `nissan_rogue_rs`, `nissan_rogue_sl`, `nissan_rogue_plat`
- **Nissan Sentra · 2027**: `nissan_sentra_s`, `nissan_sentra_sv`, `nissan_sentra_sr`
- **Ram 1500 · 2026**: `ram_1500_ten`
- **Ram 3500 Chassis Cab · 2026**: `ram_3500_chassis_cab_tr`, `ram_3500_chassis_cab_slt`
- **Subaru Impreza · 2026**: `sub_impreza_rs`
- **Subaru Trailseeker · 2027**: `sub_trailseeker_prem`, `sub_trailseeker_lim`, `sub_trailseeker_tour`
- **Tesla Model 3 · 2026**: `m3_std`
- **Tesla Model Y · 2026**: `ty_std`
- **Toyota 4Runner · 2026**: `toy_4runner_sr5`, `toy_4runner_trd`, `toy_4runner_lim`, `toy_4runner_limh`
- **Toyota C-HR · 2027**: `toy_chr_se`, `toy_chr_xse`
- **Toyota Tacoma · 2026**: `toy_tacoma_pro`
- **Volvo EX60 · 2027**: `ex60_p6`, `ex60_p10`
- **Volvo EX90 · 2026**: `ex90_sm`, `ex90_tm`

Also confirm published wheel travel and ground clearance where they exist (off-road trims usually publish them).

## Task 3 — Performance and spec check

For every real trim: horsepower, torque, curb weight, drivetrain, transmission, 0–60 mph, top speed, EPA mpg or range, battery kWh, EV-only range for plug-ins. Compare with `TRIMS[k]` and `DRIVES[k]` and correct anything more than about 5 % off.

## Task 4 — Packages, prices, colours and wheels

For every model line in `BDATA`: real trim prices (MSRP), package names, prices and contents, paint colour names, wheel sizes and designs.

## Task 5 — Clusters and screens

For each brand without its real instrument cluster or infotainment layout modelled, describe the real one (layout, gauges, colours, what shows in each drive mode) so it can be drawn. Start with the most-driven cars.

## Task 6 — Drive mode re-check

Re-verify drive modes flagged as from memory: Kia (Sportage, EV9, Carnival, Sorento hybrids), Volvo EX60/EX90/XC60, Audi Q7 2027, GM truck trim splits (which trims get Terrain, Baja, Wide Open Watts), Chrysler Pacifica, Ram ProMaster, Chevy Trax.
