#!/usr/bin/env python3
"""Download candidate photos per slot so they can be visually reviewed before selection."""
import json, os, re, time, urllib.parse, urllib.request

UA = {"User-Agent": "StructuraDemoSite/1.0 (educational demo build; contact: demo@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
CAND = "assets/raw/cand"
os.makedirs(CAND, exist_ok=True)

BAD = re.compile(
    r"logo|diagram|chart|poster|\bsign\b|stamp|coat.of.arms|seal|banner|flag|painting|drawing|sketch|"
    r"engraving|lithograph|watercolou?r|illustration|screenshot|cover|newspaper|plan of|floorplan|"
    r"graph|icon|bulletin|certificate|award|plaque|statue|sculpture|coin|slug|cat |spice|"
    r"advertis|advertiz|poszolith|goddess|makeup|mytholog|alice|alberto|steffan|"
    r"night in the|star|aurora|mosaic|painting", re.I)

SLOTS = {
    "service-structural":   (["Category:Structural steel", "Category:Steel construction", "Category:Steel framed buildings"], ["steel", "frame", "beam", "column", "girder"]),
    "service-renovation":   (["Category:Renovation", "Category:Building renovation", "Category:Restoration"], ["renovat", "restor", "scaffold", "refurb"]),
    "service-turnkey":      (["Category:Interiors of houses", "Category:Modern living rooms", "Category:House interiors"], ["interior", "living room", "staircase", "lounge"]),
    "service-management":   (["Category:Construction workers of India", "Category:Engineers", "Category:Site engineers"], ["engineer", "site", "worker", "foreman", "meeting"]),
    "before-site":          (["Category:Vacant lots", "Category:Land development", "Category:Construction site clearing"], ["vacant", "empty", "plot", "land", "clearing", "excavat"]),
    "video-progress":       (["Category:Aerial photographs of construction", "Category:Construction sites from above", "Category:Aerial photographs of building sites"], ["aerial", "drone", "construction", "site"]),
    "video-interview":      (["Category:Construction workers wearing hard hats", "Category:Workers in hard hats", "Category:Builders of India"], ["hard hat", "helmet", "worker", "builder"]),
    "case-design":          (["Category:Architectural drawings", "Category:Blueprints", "Category:Technical drawings"], ["blueprint", "drawing", "draft", "plan", "architect"]),
    "case-structure":       (["Category:Reinforced concrete", "Category:Concrete construction", "Category:Building frames"], ["concrete", "column", "slab", "rcc", "formwork", "structure"]),
    "case-detail-1":        (["Category:Houses at night", "Category:Modern villas", "Category:Residential buildings in India"], ["house", "villa", "night", "exterior", "lighting", "residence"]),
    "case-detail-3":        (["Category:Modern architecture in India", "Category:Contemporary architecture", "Category:Modern houses in India"], ["modern", "contemporary", "house", "residence"]),
    "about-team":           (["Category:Construction workers of India", "Category:Construction crews", "Category:Workers of India"], ["worker", "crew", "site", "construction"]),
    "insights-materials":   (["Category:Cement bags", "Category:Building materials", "Category:Bricks"], ["cement", "brick", "material", "block", "steel"]),
    "insights-planning":    (["Category:Architectural models", "Category:Scale models of buildings", "Category:Architects' desks"], ["model", "architect", "desk", "plan", "drawing"]),
    "insights-contractor":  (["Category:Construction inspection", "Category:Building inspection", "Category:Surveying"], ["inspect", "quality", "survey", "test", "checking"]),
    "gallery-1":            (["Category:Apartment buildings in India", "Category:Residential buildings in Chennai", "Category:High-rise buildings in India"], ["apartment", "residential", "tower", "housing", "block"]),
    "gallery-2":            (["Category:Industrial buildings in India", "Category:Factories in India", "Category:Warehouses"], ["industrial", "factory", "warehouse", "shed", "plant"]),
    "gallery-3":            (["Category:Foundation (engineering)", "Category:Pile foundations", "Category:Excavation"], ["foundation", "pile", "excavat", "rebar", "pile"]),
}


def api(params):
    params = dict(params); params["format"] = "json"
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def cat_files(cat, limit=50):
    try:
        d = api({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmtype": "file|subcat", "cmlimit": str(limit)})
    except Exception:
        return [], []
    files = [m["title"] for m in d.get("query", {}).get("categorymembers", []) if m["title"].lower().endswith((".jpg", ".jpeg", ".png")) and "Category:" not in m["title"]]
    subs = [m["title"] for m in d.get("query", {}).get("categorymembers", []) if m["title"].startswith("Category:")]
    return files, subs


def info(titles):
    out = []
    for i in range(0, len(titles), 25):
        chunk = titles[i:i + 25]
        try:
            d = api({"action": "query", "titles": "|".join(chunk), "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1600"})
        except Exception:
            continue
        for p in d.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if ii:
                out.append({"title": p.get("title", ""), "w": ii.get("width", 0), "h": ii.get("height", 0),
                            "mime": ii.get("mime", ""), "url": ii.get("thumburl") or ii.get("url")})
        time.sleep(0.1)
    return out


def main():
    index = {}
    for slot, (cats, kws) in SLOTS.items():
        titles = []
        for cat in cats:
            f, subs = cat_files(cat)
            titles += f
            for s in subs[:10]:
                sf, _ = cat_files(s, 30)
                titles += sf
            if len(titles) > 80:
                break
        titles = list(dict.fromkeys(titles))
        meta = info(titles)
        cand = []
        for m in meta:
            if m["mime"] not in ("image/jpeg", "image/png"):
                continue
            if BAD.search(m["title"]):
                continue
            if m["w"] < 1500 or m["h"] < 900:
                continue
            ar = m["w"] / m["h"]
            if ar < 0.9 or ar > 2.3:
                continue
            tl = m["title"].lower()
            s = sum(3 for k in kws if k in tl) + min(3, (m["w"] * m["h"]) // 3_000_000)
            cand.append({**m, "score": s})
        cand.sort(key=lambda x: -x["score"])
        got = []
        for c in cand[:6]:
            fn = os.path.join(CAND, f"{slot}__{len(got)}.jpg")
            try:
                req = urllib.request.Request(c["url"], headers=UA)
                data = urllib.request.urlopen(req, timeout=60).read()
                if len(data) < 30000:
                    continue
                open(fn, "wb").write(data)
                got.append({"file": fn, "title": c["title"], "src": c["url"]})
            except Exception:
                continue
        index[slot] = got
        print(f"{slot:22s} {len(got)} candidates")
    json.dump(index, open("assets/raw/cand/index.json", "w"), indent=2)


if __name__ == "__main__":
    main()
