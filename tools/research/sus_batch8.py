"""Suspension (SUSR rows) for the trims added in v100-v106: layout, springs, dampers, anti-roll bars, air-suspension range,
ground clearance (mm), wheel travel (mm) and tune, from the makers' US spec sheets / press kits (2025-2026 models).
Row: [front, rear, spring, damper, damper name, arb, ride range or None, ground mm, [travel F, travel R], tune]
    python3 sus_batch8.py nosus.json out.js"""
import json, sys
TR = json.load(open(sys.argv[1]))          # [[key, group, short], ...]
R = {}
def S(fr, rr, sp, dp, name, arb="front_rear", ride=None, gc=170, tv=(160, 180), tune="comfort"): return [fr, rr, sp, dp, name, arb, list(ride) if ride else None, gc, list(tv), tune]
for k, g, short in TR:
    n = short or ""
    # ---------------- Mazda: MacPherson front; Mazda3 / CX-30 torsion beam (multilink on AWD Mazda3/CX-30 is still a beam), CX-5/CX-50 multilink,
    # CX-70/90 double wishbone + multilink on the RWD-based platform
    if k.startswith("mz_3hb"): R[k] = S("macpherson", "torsion_beam", "coil", "passive", "Passive dampers, torsion-beam rear with G-Vectoring Control Plus", gc=140, tv=(150, 160), tune="balanced")
    elif k.startswith("mz_cx30"): R[k] = S("macpherson", "torsion_beam", "coil", "passive", "Passive dampers, torsion-beam rear with G-Vectoring Control Plus", gc=175, tv=(155, 165), tune="balanced")
    elif k.startswith("mz_cx5"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear (2026 platform)", gc=208, tv=(165, 185), tune="comfort")
    elif k.startswith("mz_cx50"): R[k] = S("macpherson", "multilink", "coil", "passive", ("All-terrain tuned dampers" if "Meridian" in n else "Passive dampers") + ", multilink rear, Mi-Drive Off-Road", gc=218, tv=(175, 195), tune="offroad" if "Meridian" in n else "balanced")
    elif k.startswith("mz_cx70") or k.startswith("mz_cx90"): R[k] = S("double_wishbone", "multilink", "coil", "passive", "Double wishbone front, multilink rear, Kinematic Posture Control", gc=212 if "cx70" in k else 213, tv=(170, 190), tune="balanced" if "Turbo S" in n else "comfort")
    # ---------------- Volkswagen: MQB (MacPherson + multilink, torsion beam on FWD Jetta / Taos), MEB (MacPherson + multilink)
    elif k == "vw_jetta_gli": R[k] = S("macpherson", "multilink", "coil", "adaptive", "DCC Adaptive Chassis Control, XDS electronic diff", gc=135, tv=(140, 150), tune="sport")
    elif k.startswith("vw_jetta"): R[k] = S("macpherson", "torsion_beam", "coil", "passive", "Passive dampers, torsion-beam rear", gc=140, tv=(150, 160), tune="comfort")
    elif k == "vw_taos_s": R[k] = S("macpherson", "torsion_beam", "coil", "passive", "Passive dampers, torsion-beam rear (FWD)", gc=170, tv=(160, 170), tune="comfort")
    elif k.startswith("vw_taos"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear (4MOTION)", gc=170, tv=(160, 175), tune="comfort")
    elif k == "vw_tiguan_selr": R[k] = S("macpherson", "multilink", "coil", "adaptive", "DCC Pro two-valve adaptive dampers", gc=200, tv=(165, 180), tune="balanced")
    elif k.startswith("vw_tiguan"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear", gc=200, tv=(165, 180), tune="comfort")
    elif k.startswith("vw_atlas_cs"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear", gc=203, tv=(170, 185), tune="comfort")
    elif k == "vw_atlas_peak": R[k] = S("macpherson", "multilink", "coil", "passive", "Off-road tuned dampers, all-terrain tires, Offroad mode", gc=211, tv=(175, 190), tune="offroad")
    elif k.startswith("vw_atlas"): R[k] = S("macpherson", "multilink", "coil", "adaptive" if "Premium" in n else "passive", "DCC adaptive dampers" if "Premium" in n else "Passive dampers, multilink rear", gc=203, tv=(170, 190), tune="comfort")
    elif k.startswith("vw_id4"): R[k] = S("macpherson", "multilink", "coil", "adaptive" if "Plus" in n else "passive", "DCC adaptive dampers" if "Plus" in n else "Passive dampers, multilink rear (MEB)", gc=165, tv=(155, 170), tune="comfort")
    elif k.startswith("vw_idbuzz"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear (MEB, long wheelbase)", gc=160, tv=(150, 165), tune="comfort")
    # ---------------- RAV4 2026 (TNGA-K): MacPherson + double wishbone rear (multilink)
    elif k.startswith("toy_rav4_26"):
        gr = "gr" in k.split("_")[-1]
        R[k] = S("macpherson", "multilink", "coil", "passive", "GR-tuned dampers and stiffer springs, rear performance damper" if gr else ("Off-road tuned dampers, all-terrain tires" if "wood" in k else "Passive dampers, double-wishbone rear"), gc=203 if "wood" in k else 208 - (8 if gr else 0), tv=(170, 190), tune="sport" if gr else "offroad" if "wood" in k else "comfort")
    # ---------------- Hyundai
    elif k.startswith("hy_venue"): R[k] = S("macpherson", "torsion_beam", "coil", "passive", "Passive dampers, coupled torsion-beam rear", gc=170, tv=(150, 160))
    elif k.startswith("hy_kona_ev"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, multilink rear", gc=150, tv=(150, 165))
    elif k.startswith("hy_kona"): R[k] = S("macpherson", "multilink" if k in ("hy_kona_nl", "hy_kona_lim") else "torsion_beam", "coil", "passive", "Passive dampers, " + ("multilink rear (AWD)" if k in ("hy_kona_nl", "hy_kona_lim") else "coupled torsion-beam rear"), gc=170, tv=(155, 170), tune="balanced" if k == "hy_kona_nl" else "comfort")
    elif k.startswith("hy_tucson"): R[k] = S("macpherson", "multilink", "coil", "passive", "XRT off-road tuned dampers" if "xrt" in k else "Passive dampers, multilink rear", gc=211 if "xrt" in k else 208, tv=(165, 185), tune="offroad" if "xrt" in k else "comfort")
    elif k.startswith("hy_santafe"): R[k] = S("macpherson", "multilink", "coil", "passive", ("XRT off-road tuned dampers" if "xrt" in k else "Passive dampers") + (", self-levelling rear" if "cal" in k else ""), gc=211 if "xrt" in k else 180, tv=(170, 190), tune="offroad" if "xrt" in k else "comfort")
    elif k.startswith("hy_palisade"): R[k] = S("macpherson", "multilink", "coil", "passive", ("XRT PRO off-road dampers, all-terrain tires" if "xrt" in k else "Passive dampers") + (", self-levelling rear" if "cal" in k or "lim" in k else ""), gc=203 if "xrt" in k else 190, tv=(170, 195), tune="offroad" if "xrt" in k else "comfort")
    elif k.startswith("hy_santacruz"): R[k] = S("macpherson", "multilink", "coil", "passive", ("XRT off-road dampers" if "xrt" in k else "Passive dampers") + ", self-levelling rear", gc=221, tv=(175, 190), tune="offroad" if "xrt" in k else "balanced")
    elif k.startswith("hy_ioniq5"): R[k] = S("macpherson", "multilink", "coil", "passive", "XRT off-road tuned dampers, all-terrain tires" if "xrt" in k else "Passive dampers, multilink rear (E-GMP)", gc=185 if "xrt" in k else 155, tv=(155, 170), tune="offroad" if "xrt" in k else "comfort")
    elif k.startswith("hy_ioniq9"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers, self-levelling rear (E-GMP)", gc=175, tv=(160, 175))
    # ---------------- BMW (CLAR / UKL)
    elif k in ("bmw_x1_28i", "bmw_x2_28i"): R[k] = S("macpherson", "multilink", "coil", "passive", "Passive dampers with frequency-selective valving", gc=203, tv=(160, 175), tune="balanced")
    elif k in ("bmw_x1_m35i", "bmw_x2_m35i"): R[k] = S("macpherson", "multilink", "coil", "adaptive", "Adaptive M suspension", gc=193, tv=(150, 165), tune="sport")
    elif k == "bmw_x3_30": R[k] = S("double_wishbone", "multilink", "coil", "passive", "Double-joint spring strut front, 5-link rear", gc=210, tv=(165, 180), tune="balanced")
    elif k == "bmw_x3_m50": R[k] = S("double_wishbone", "multilink", "coil", "adaptive", "Adaptive M suspension", gc=200, tv=(160, 175), tune="sport")
    elif k == "bmw_ix3_50": R[k] = S("double_wishbone", "multilink", "coil", "passive", "Neue Klasse passive dampers, 5-link rear", gc=185, tv=(160, 175), tune="balanced")
    elif k.startswith("bmw_x5") or k.startswith("bmw_x6") or k.startswith("bmw_x7"):
        m60 = "m60i" in k or "alpina" in k
        R[k] = S("double_wishbone", "multilink", "air" if (k.startswith("bmw_x7") or m60) else "coil", "adaptive", ("Two-axle air suspension, " if (k.startswith("bmw_x7") or m60) else "") + ("Adaptive M Professional with active roll stabilization" if m60 else "Dynamic Damper Control"),
                 arb="active" if m60 else "front_rear", ride=(-40, 40) if (k.startswith("bmw_x7") or m60) else None, gc=214 if k.startswith("bmw_x5") else 216 if k.startswith("bmw_x6") else 221, tv=(175, 190), tune="sport" if m60 else "balanced")
    # ---------------- Mercedes-Benz
    elif k in ("mb_gla_250", "mb_glb_250"): R[k] = S("macpherson", "multilink", "coil", "passive", "Comfort suspension", gc=155 if "gla" in k else 200, tv=(150, 170))
    elif k in ("mb_gla_amg35", "mb_glb_amg35"): R[k] = S("macpherson", "multilink", "coil", "adaptive", "AMG RIDE CONTROL adaptive damping", gc=145, tv=(145, 160), tune="sport")
    elif k in ("mb_glc_300", "mb_glc_350e", "mb_glc_coupe_300"): R[k] = S("multilink", "multilink", "coil", "passive", "Comfort suspension with selective damping, four-link front", gc=180, tv=(165, 180))
    elif k in ("mb_glc_amg43", "mb_glc_coupe_amg43"): R[k] = S("multilink", "multilink", "coil", "adaptive", "AMG RIDE CONTROL adaptive damping, rear-axle steering", gc=170, tv=(160, 175), tune="sport")
    elif k == "mb_glc_ev_400": R[k] = S("multilink", "multilink", "air", "adaptive", "AIRMATIC air suspension (est.)", ride=(-15, 20), gc=180, tv=(165, 180), tune="comfort")
    elif k in ("mb_gle_350", "mb_gle_450", "mb_gle_coupe_450"): R[k] = S("double_wishbone", "multilink", "coil" if k == "mb_gle_350" else "air", "adaptive" if k != "mb_gle_350" else "passive", "Steel springs with selective damping" if k == "mb_gle_350" else "AIRMATIC with ADS+ adaptive damping", ride=None if k == "mb_gle_350" else (-15, 55), gc=205, tv=(175, 195))
    elif k in ("mb_gle_amg53", "mb_gle_coupe_amg53", "mb_gle_580"): R[k] = S("double_wishbone", "multilink", "air", "adaptive", "AMG ACTIVE RIDE CONTROL with active roll stabilization" if "amg" in k else "E-ACTIVE BODY CONTROL", arb="active", ride=(-15, 55), gc=200, tv=(175, 195), tune="sport" if "amg" in k else "comfort")
    elif k.startswith("mb_gls") or k == "mb_maybach_gls_600": R[k] = S("double_wishbone", "multilink", "air", "adaptive", "AIRMATIC with ADS+" + (" and E-ACTIVE BODY CONTROL" if k != "mb_gls_450" else ""), arb="active" if k != "mb_gls_450" else "front_rear", ride=(-15, 55), gc=216, tv=(180, 200), tune="soft" if "maybach" in k else "comfort")
    elif k.startswith("mb_eqb"): R[k] = S("macpherson", "multilink", "coil", "passive", "Comfort suspension", gc=190, tv=(150, 170))
    elif k.startswith("mb_eqe_suv") or k.startswith("mb_eqs_suv") or k == "mb_maybach_eqs_680": R[k] = S("multilink", "multilink", "air", "adaptive", "AIRMATIC with ADS+, rear-axle steering", ride=(-15, 25), gc=200, tv=(165, 185), tune="soft" if "maybach" in k else "comfort")
    elif k in ("mb_g550", "mb_g63"): R[k] = S("double_wishbone", "solid_axle_coil", "coil", "adaptive", "Adaptive Damping System" + (" with AMG ACTIVE RIDE CONTROL" if k == "mb_g63" else ""), arb="active" if k == "mb_g63" else "front_rear", gc=241, tv=(220, 250), tune="offroad" if k == "mb_g550" else "firm")
    elif k == "mb_g580": R[k] = S("double_wishbone", "solid_axle_coil", "coil", "adaptive", "Adaptive Damping System, rigid De Dion rear", gc=250, tv=(220, 250), tune="offroad")
    # ---------------- Cadillac (BEV3 / Ultium)
    elif k.startswith("cad_lyriq") or k.startswith("cad_optiq") or k.startswith("cad_vistiq"):
        v = k.endswith("_v"); air = k == "cad_vistiq_plat"
        R[k] = S("multilink", "multilink", "air" if air else "coil", "magnetic" if (v or air) else "passive", ("Air Ride Adaptive Suspension, " if air else "") + ("Magnetic Ride Control 4.0" if (v or air) else "Frequency-dependent passive dampers, 5-link front and rear"), ride=(-25, 25) if air else None, gc=150 if "lyriq" in k else 165, tv=(165, 180), tune="sport" if v else "comfort")
    elif k == "cad_celestiq": R[k] = S("multilink", "multilink", "air", "magnetic", "Air springs, Magnetic Ride Control 4.0, active rear steer", arb="active", ride=(-25, 25), gc=125, tv=(160, 175), tune="soft")
    # ---------------- Tesla
    elif k.startswith("ct_"): R[k] = S("double_wishbone", "multilink", "air", "adaptive", "Adaptive air suspension (up to 17 in. clearance), steer-by-wire, rear-wheel steer", ride=(-100, 100), gc=325, tv=(230, 250), tune="offroad")
    elif k.startswith("ms20") or k.startswith("mx20"): R[k] = S("double_wishbone", "multilink", "air", "adaptive", "Smart Air Suspension with adaptive damping", ride=(-25, 40) if k.startswith("ms20") else (-30, 50), gc=117 if k.startswith("ms20") else 158, tv=(160, 175), tune="balanced" if "perf" in k else "comfort")
    # ---------------- concept
    elif g.startswith("Aureon"): R[k] = S("double_wishbone", "multilink", "air", "adaptive", "Adaptive air suspension", ride=(-30, 40), gc=190, tv=(175, 190), tune="balanced")
missing = [k for k, g, s in TR if k not in R]
open(sys.argv[2], "w").write("Object.assign(SUSR," + json.dumps(R, separators=(",", ":")) + ");   // v107: suspension research for the Hyundai, BMW, Mercedes, Cadillac, Mazda, VW, RAV4 2026, Cybertruck and 2020 Tesla trims\n")
print(len(R), "rows; missing", missing)
