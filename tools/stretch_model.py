"""Make a long-wheelbase version of a car model: everything behind a cut line moves back, the roof can rise a little.

    python3 tools/stretch_model.py src_key dst_key --cut 0.6 --dz 0.15 --roof 0.043 [--seats3]

Model files keep positions as int16 millimetres (page axes: +x right, +y up, +z rearward).
The result is re-centred on its wheelbase. Used for the Tesla Model Y L (Model Y + 150 mm wheelbase, +43 mm roof)."""
import json, base64, sys, argparse
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("--cut", type=float, default=0.6)
ap.add_argument("--dz", type=float, default=0.15); ap.add_argument("--roof", type=float, default=0.0); ap.add_argument("--seats3", action="store_true")
a = ap.parse_args()
d = json.load(open(f"models/{a.src}.json")); dz, cut = a.dz, a.cut
blend = 0.25   # metres over which the shift ramps in (no stretched sliver at the cut)
def shift_z(z): return dz * np.clip((z - (cut - blend / 2)) / blend, 0, 1)
def roof_y(y, z): return a.roof * np.clip((y - 1.15) / 0.3, 0, 1) * np.clip((z - (cut - 1.6)) / 0.6, 0, 1)
for k, o in d["objects"].items():
    P = np.frombuffer(base64.b64decode(o["p"]), "<i2").reshape(-1, 3).astype(float) / 1000
    if k.endswith(("_RL", "_RR")): P[:, 2] += dz
    elif k in ("tire_FL", "tire_FR", "rim_FL", "rim_FR", "steer"): pass
    else:
        P[:, 1] += roof_y(P[:, 1], P[:, 2]); P[:, 2] += shift_z(P[:, 2])
    P[:, 2] -= dz / 2
    o["p"] = base64.b64encode(np.clip(np.round(P * 1000), -32767, 32767).astype("<i2").tobytes()).decode()
for w in d["wheels"]:
    d["wheels"][w][2] = round(d["wheels"][w][2] + (dz if w[0] == "R" else 0) - dz / 2, 4)
m = d["meta"]
def mv(p):
    p = list(p); p[2] = round(p[2] + float(shift_z(np.array(p[2]))) - dz / 2, 4); return p
for k in ("head", "tail", "eye", "mirror", "steer"):
    if k in m: m[k] = mv(m[k])
for q in ("clu", "scr", "pano"):
    if q in m:
        for kk in ("bl", "br", "tl", "c"):
            if kk in m[q]: m[q][kk] = mv(m[q][kk])
if "seats" in m:
    m["seats"] = [mv(s) for s in m["seats"]]
    if a.seats3:   # a third row (Model Y L: six seats, 2+2+2)
        r2 = [s for s in m["seats"] if s[2] > 0.5][:2]
        m["seats"] += [[s[0], s[1] + 0.02, round(s[2] + 0.85, 4)] for s in r2]
m["length"] = round(m["length"] + dz, 3); m["wb"] = round(m["wb"] + dz, 3); m["height"] = round(m["height"] + a.roof, 3)
json.dump(d, open(f"models/{a.dst}.json", "w"), separators=(",", ":"))
print(a.dst, "length", m["length"], "wb", m["wb"], "height", m["height"])
