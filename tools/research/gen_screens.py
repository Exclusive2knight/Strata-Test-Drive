"""Genesis models with one wide display panel (G80, GV60, GV70, Electrified GV70, GV80, GV80 Coupe): the importer used the whole panel
for both the cluster and the centre screen, so they were drawn on top of each other in the middle of the dash. Split it like the real cars:
the 12.3-in. cluster behind the wheel on the left, the touchscreen to the right of it (the far right of the glass stays black)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def part(q, x0, x1):
    y0, y1, z = q["bl"][1], q["tl"][1], q["bl"][2]; zt = q["tl"][2]
    return {"bl": [x0, y0, z], "br": [x1, y0, z], "tl": [x0, y1, zt], "c": [round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4), round((z + zt) / 2, 4)], "n": q["n"], "w": round(x1 - x0, 4), "h": q["h"]}
for k in ["gen_g80", "gen_gv60", "gen_gv70", "gen_egv70", "gen_gv80", "gen_gv80c"]:
    p = os.path.join(ROOT, "models", k + ".json"); d = json.load(open(p)); m = d["meta"]; q = m["clu"]
    if q["w"] < 0.9: print(k, "already split"); continue
    x0, x1 = q["bl"][0], q["br"][0]
    m["clu"] = part(q, x0 + 0.02, x0 + 0.44)          # behind the wheel (eye at x -0.42)
    m["scr"] = part(m["scr"], x0 + 0.47, min(x1 - 0.02, x0 + 1.03))
    json.dump(d, open(p, "w"), separators=(",", ":")); print(k, "clu", m["clu"]["c"], m["clu"]["w"], "scr", m["scr"]["c"], m["scr"]["w"])
