"""Vehicle weights: research + class estimates -> weights/vehicle_weights.csv, weights/mass/<key>.json and props/weights.json (spliced into the game).

    python3 tools/weights/build.py            (reads tools/weights/trims.json and tools/weights/research/*.json)

Every value is [value, tag, source, url, note]. Tags: "from manufacturer", "from third-party source", "estimated for this class", "typical".
Research files: a list of {"match": regex on the trim key or name, "fields": {field: [value, tag, source, url, note]}}; later entries win.
US units in every file a person reads (lb, in, gal); the game converts to SI once at load.
"""
import json, re, os, glob, csv, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
TRIMS = json.load(open(os.path.join(HERE, "trims.json")))
LB = 2.20462; GAL = 0.264172
FUEL_LB_GAL = {"gasoline": 6.1, "diesel": 7.1}   # typical densities (EIA / ASTM ranges: gasoline 6.0-6.3, diesel 7.0-7.2 lb/gal)
FIELDS = ["curb_weight_lb", "front_curb_lb", "rear_curb_lb", "gvwr_lb", "front_gawr_lb", "rear_gawr_lb", "payload_lb", "tow_lb", "gcwr_lb",
          "tongue_lb", "tank_gal", "battery_lb", "cg_height_in", "fuel_type"]

def klass(t):
    g = (t["group"] + " " + t["name"]).lower()
    if re.search(r"chassis cab|4500|5500|work trucks", g): return "chassis"
    if re.search(r"super duty|silverado hd|2500|3500|sierra 2500|sierra 3500", g): return "hd_pickup"
    if re.search(r"f-150|silverado|sierra 1500|ram 1500|tundra|cybertruck|r1t|hummer ev pickup|sierra ev|silverado ev", g): return "pickup"
    if re.search(r"tacoma|ranger|colorado|canyon|frontier|gladiator|ridgeline|maverick|santa cruz", g): return "mid_pickup"
    if re.search(r"express|savana|transit|promaster", g): return "van"
    if re.search(r"sienna|odyssey|pacifica|carnival|id\. buzz", g): return "minivan"
    if re.search(r"corvette|911|cayman|boxster|roadster|prelude|mustang|charger|type r", g): return "sports"
    if re.search(r"camry|civic|accord|corolla|altima|sentra|sonata|k4|k5|optima|malibu|fusion|jetta|impreza|mazda3|integra|model 3|model s|panamera|taycan|lucid air|g70|g80|g90|5 series|7 series|celestiq|town car|prius|sx4|a6|v60|golf|soul|leaf|bolt|venue|kicks|trax|hornet|niro|ex30|velora|solace", g): return "car"
    if re.search(r"tahoe|suburban|yukon|escalade|expedition|navigator|sequoia|armada|qx80|grand wagoneer|land cruiser|lx|g-class|gls|x7|range rover\b|hummer", g): return "full_suv"
    return "suv"
TYP = {   # class: payload, tow, cg height (in), body share of curb for the breakdown; values are "typical" for the class (US spec sheets)
    "car": dict(payload=950, tow=1000, cg=21.0, gvwr_k=None), "sports": dict(payload=700, tow=0, cg=18.5), "suv": dict(payload=1200, tow=3500, cg=25.0),
    "full_suv": dict(payload=1700, tow=8000, cg=28.0), "minivan": dict(payload=1300, tow=3500, cg=25.0), "van": dict(payload=3500, tow=6000, cg=30.0),
    "mid_pickup": dict(payload=1400, tow=6500, cg=28.0), "pickup": dict(payload=1700, tow=11000, cg=30.0), "hd_pickup": dict(payload=3300, tow=18000, cg=32.0),
    "chassis": dict(payload=7500, tow=20000, cg=34.0)}
FRONT = {"car": 0.61, "sports": 0.45, "suv": 0.57, "full_suv": 0.53, "minivan": 0.57, "van": 0.55, "mid_pickup": 0.58, "pickup": 0.58, "hd_pickup": 0.63, "chassis": 0.68}

def tagged(v, tag, src="", url="", note=""): return [v, tag, src, url, note]

def defaults(t):
    k = klass(t); ty = TYP[k]; ev = not t["ice"] and not t["hybrid"]
    curb = round(t["mass_kg"] * LB / 10) * 10
    fr = t.get("fwd") or FRONT[k]
    if k == "sports" and re.search(r"911|cayman|boxster", t["name"].lower()): fr = 0.39 if "911" in t["name"] else 0.44
    if ev and k in ("car", "suv", "full_suv"): fr = min(fr, 0.52)
    payload = ty["payload"]; gvwr = curb + payload; tow = ty["tow"] if not (ev and k == "car") else 0
    out = {
        "curb_weight_lb": tagged(curb, "estimated for this class", "game data (model-level mass)", "", "not yet researched for this trim"),
        "front_curb_lb": tagged(round(curb * fr), "estimated for this class", "", "", f"front share {fr:.0%} for this class / layout"),
        "rear_curb_lb": tagged(curb - round(curb * fr), "estimated for this class", "", "", ""),
        "gvwr_lb": tagged(gvwr, "estimated for this class", "", "", f"curb + {payload} lb typical {k} payload"),
        "front_gawr_lb": tagged(round(gvwr * max(fr, 0.5) * 1.08 / 10) * 10, "estimated for this class", "", "", "front share of GVWR + 8% margin (typical)"),
        "rear_gawr_lb": tagged(round(gvwr * max(1 - fr + 0.08, 0.5) * 1.08 / 10) * 10, "estimated for this class", "", "", "rear share of GVWR + 8% margin, load sits rearward (typical)"),
        "payload_lb": tagged(payload, "typical", "", "", f"typical {k} payload"),
        "tow_lb": tagged(tow, "typical", "", "", f"typical {k} tow rating"),
        "gcwr_lb": tagged(gvwr + tow if tow else 0, "estimated for this class", "", "", "GVWR + tow rating (typical relation)"),
        "tongue_lb": tagged(round(tow * 0.10 / 10) * 10, "typical", "", "", "10% of the tow rating (typical tongue limit)"),
        "tank_gal": tagged(round(t["tank"] * GAL, 1) if t.get("tank") and not ev else 0, "estimated for this class", "game data", "", "") ,
        "battery_lb": tagged(round((t.get("kWh") or 0) * 13) if ev or t["phev"] else (95 if t["hybrid"] else 0), "typical", "", "", "about 13 lb per kWh for a pack (pack-level energy density ~170 Wh/kg); hybrid packs ~70-110 lb"),
        "cg_height_in": tagged(round(ty["cg"] - (1.5 if ev else 0), 1), "typical", "", "", f"typical {k}" + (", EV pack lowers it ~1.5 in" if ev else "")),
        "fuel_type": tagged("electric" if ev else ("diesel" if re.search(r"diesel|duramax|power stroke|cummins|ecodiesel|6\.7|6\.6l", t["name"].lower()) else "gasoline"), "typical", "", "", ""),
    }
    return k, out

def research():
    R = []
    for f in sorted(glob.glob(os.path.join(HERE, "research", "*.json"))): R += json.load(open(f))
    return R

def main():
    R = research(); rows = []; prof = {}; review = {"not found": [], "conflicts": [], "estimates": []}
    os.makedirs(os.path.join(ROOT, "weights", "mass"), exist_ok=True)
    for t in TRIMS:
        k, F = defaults(t)
        for r in R:
            if re.search(r["match"], t["key"]) or re.search(r["match"], t["name"]):
                for f, v in r["fields"].items():
                    if f == "conflict": review["conflicts"].append([t["key"], v]); continue
                    F[f] = v
        # keep the axle split consistent with a researched curb weight that came without one
        c = F["curb_weight_lb"][0]
        if F["front_curb_lb"][1] != "from manufacturer" and F["front_curb_lb"][1] != "from third-party source":
            fr = F["front_curb_lb"][0] / max(1, F["front_curb_lb"][0] + F["rear_curb_lb"][0])
            F["front_curb_lb"][0] = round(c * fr); F["rear_curb_lb"][0] = c - F["front_curb_lb"][0]
        if F["gvwr_lb"][1] in ("estimated for this class",) and F["payload_lb"][1] not in ("estimated for this class", "typical"):
            F["gvwr_lb"] = tagged(c + F["payload_lb"][0], "estimated for this class", "", "", "curb + researched payload")
        if F["payload_lb"][1] in ("typical", "estimated for this class") and F["gvwr_lb"][1] in ("from manufacturer", "from third-party source"):
            F["payload_lb"] = tagged(F["gvwr_lb"][0] - c, "estimated for this class", "", "", "GVWR - curb")
        for f, v in F.items():
            if v[1] == "estimated for this class": review["estimates"].append([t["key"], f, v[0], v[4]])
            if "not found" in (v[4] or ""): review["not found"].append([t["key"], f, v[4]])
        srcs = sorted({v[2] for v in F.values() if v[2]}); urls = sorted({v[3] for v in F.values() if v[3]})
        conf = "high" if F["curb_weight_lb"][1] == "from manufacturer" else "medium" if F["curb_weight_lb"][1] == "from third-party source" else "low"
        rows.append([t["key"], t["name"]] + [F[f][0] for f in FIELDS[:12]] + ["; ".join(srcs), " ".join(urls), conf, F["curb_weight_lb"][4]])
        J = {"id": t["key"], "trim": t["name"], "class": k, **{f: {"value": v[0], "tag": v[1], "source": v[2], "url": v[3], "note": v[4]} for f, v in F.items()}}
        json.dump(J, open(os.path.join(ROOT, "weights", "mass", t["key"] + ".json"), "w"), indent=1)
        # the game's copy (US units; converted once at load): curb, front, gvwr, gawrF, gawrR, payload, tow, gcwr, tongue, tank, battery, cg, class, fuel, tag of curb
        prof[t["key"]] = [F[f][0] for f in FIELDS[:13]] + [k, F["fuel_type"][0], F["curb_weight_lb"][1][:4]]
    with open(os.path.join(ROOT, "weights", "vehicle_weights.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["id", "trim"] + FIELDS[:12] + ["source", "source_url", "confidence", "notes"]); w.writerows(rows)
    json.dump(prof, open(os.path.join(ROOT, "props", "weights.json"), "w"), separators=(",", ":"))
    json.dump(review, open(os.path.join(ROOT, "weights", "review.json"), "w"), indent=0)
    n = len(rows); rs = sum(1 for r in rows if r[-2] != "low")
    print(f"{n} trims, {rs} with a researched curb weight; {len(review['estimates'])} estimated values, {len(review['conflicts'])} conflicts, {len(review['not found'])} not found")

if __name__ == "__main__": main()
