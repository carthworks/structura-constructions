#!/usr/bin/env python3
"""Curated photo pipeline v2 — Commons categories with strict photo filtering."""
import json, os, re, time, urllib.parse, urllib.request
from collections import deque

UA = {"User-Agent": "StructuraDemoSite/1.0 (educational demo build; contact: demo@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
OUT = "assets/raw"
os.makedirs(OUT, exist_ok=True)

BAD = re.compile(
    r"logo|map|diagram|chart|svg|poster|\bsign\b|stamp|coin|coat.of.arms|seal|banner|flag|"
    r"painting|drawings?|sketch|engraving|woodcut|lithograph|watercolou?r|oil.on|illustration|"
    r"poster|screenshot|cover|newspaper|journal|manuscript|plan of|floorplan|floor plan|graph|"
    r"icon|bulletin|certificate|award|plaque|statue|sculpture|coin|portrait of|"
    r"lady and child|sher ali|empire state|museum of|somerset house|spectacle|money|"
    r"portrait|engraving|comic|manga|artifact|antique|fossil|species|flower|butterfly|"
    r"aerial pollution|air pollution|microscope|x-ray|radiograph", re.I)

SLOTS = {
    "service-infrastructure": {
        "cats": ["Category:Bridge construction", "Category:Construction of bridges", "Category:Road construction"],
        "kw": ["bridge", "pier", "viaduct", "flyover", "highway construction", "culvert"]},
    "service-structural": {
        "cats": ["Category:Steel construction", "Category:Steel frame construction", "Category:Concrete construction"],
        "kw": ["steel frame", "beam", "girder", "column", "rebar", "reinforcement", "scaffold"]},
    "service-renovation": {
        "cats": ["Category:Building renovation", "Category:Renovation of buildings", "Category:Restoration of buildings"],
        "kw": ["renovation", "restoration", "scaffold", "refurbish"]},
    "service-turnkey": {
        "cats": ["Category:Modern interiors", "Category:Interiors of houses", "Category:Living rooms"],
        "kw": ["interior", "living room", "staircase", "interior design", "apartment interior"]},
    "service-management": {
        "cats": ["Category:Construction workers", "Category:Engineers at work", "Category:Construction sites"],
        "kw": ["engineer", "site meeting", "foreman", "site office", "workers", "inspector"]},
    "before-site": {
        "cats": ["Category:Vacant lots", "Category:Land development", "Category:Construction sites"],
        "kw": ["empty land", "vacant", "plot", "site clearing", "excavation"]},
    "video-progress": {
        "cats": ["Category:Aerial photographs of construction sites", "Category:Construction sites from above"],
        "kw": ["aerial", "drone", "construction"]},
    "video-interview": {
        "cats": ["Category:Portrait photographs of engineers", "Category:Portrait photographs of construction workers",
                 "Category:Hard hats"],
        "kw": ["helmet", "hard hat", "portrait", "worker"]},
    "case-design": {
        "cats": ["Category:Architectural drawings", "Category:Blueprints", "Category:Architectural plans"],
        "kw": ["blueprint", "drawing", "plan", "drafting", "architect"]},
    "case-structure": {
        "cats": ["Category:Concrete construction", "Category:Reinforced concrete", "Category:Building frames"],
        "kw": ["concrete frame", "column", "rcc", "slab", "formwork", "structure"]},
    "case-detail-1": {
        "cats": ["Category:Modern house exteriors", "Category:Houses at night", "Category:Modern villas"],
        "kw": ["house", "villa", "facade", "exterior", "night", "lighting"]},
    "case-detail-2": {
        "cats": ["Category:Staircases", "Category:Modern staircases", "Category:Interiors of houses"],
        "kw": ["staircase", "stair", "interior", "spiral"]},
    "case-detail-3": {
        "cats": ["Category:Modern architecture in India", "Category:Contemporary architecture"],
        "kw": ["modern", "contemporary", "residence", "house"]},
    "about-team": {
        "cats": ["Category:Construction workers at work", "Category:Construction sites"],
        "kw": ["worker", "workers", "site", "crew", "helmet"]},
    "insights-materials": {
        "cats": ["Category:Building materials", "Category:Cement", "Category:Construction materials"],
        "kw": ["cement", "brick", "block", "material", "steel bar", "aggregate"]},
    "insights-planning": {
        "cats": ["Category:Architects at work", "Category:Architectural models", "Category:Scale models"],
        "kw": ["architect", "model", "drawing", "plan", "drafting", "design"]},
    "insights-contractor": {
        "cats": ["Category:Construction inspection", "Category:Quality control in construction", "Category:Construction safety"],
        "kw": ["inspection", "quality", "safety", "checklist", "survey", "testing"]},
    "city-coimbatore": {
        "cats": ["Category:Coimbatore", "Category:Buildings in Coimbatore"],
        "kw": ["coimbatore", "city", "skyline", "temple", "street"]},
    "city-chennai": {
        "cats": ["Category:Chennai", "Category:Buildings in Chennai"],
        "kw": ["chennai", "marine drive", "skyline", "kapaleeswarar", "city"]},
    "city-hosur": {
        "cats": ["Category:Hosur", "Category:Buildings in Hosur"],
        "kw": ["hosur", "town", "industrial", "road", "building"]},
    "city-bengaluru": {
        "cats": ["Category:Skyline of Bengaluru", "Category:Buildings in Bengaluru"],
        "kw": ["bengaluru", "bangalore", "skyline", "mg road", "city"]},
    "avatar-1": {
        "cats": ["Category:Portrait photographs of men of India", "Category:Businesspeople of India"],
        "kw": ["portrait", "man", "business", "professional"]},
    "avatar-2": {
        "cats": ["Category:Portrait photographs of women of India", "Category:Businesswomen of India"],
        "kw": ["portrait", "woman", "business", "professional"]},
    "avatar-3": {
        "cats": ["Category:Portrait photographs of men", "Category:Engineers of India"],
        "kw": ["portrait", "man", "engineer", "professional"]},
    "gallery-1": {
        "cats": ["Category:Residential buildings in India", "Category:Apartment buildings in India"],
        "kw": ["apartment", "residential", "housing", "tower"]},
    "gallery-2": {
        "cats": ["Category:Warehouses in India", "Category:Industrial buildings in India"],
        "kw": ["warehouse", "factory", "industrial", "shed", "logistics"]},
    "gallery-3": {
        "cats": ["Category:Foundation (engineering)", "Category:Piling", "Category:Excavation"],
        "kw": ["foundation", "piling", "excavation", "rebar", "pile"]},
    "gallery-4": {
        "cats": ["Category:Roads in Tamil Nadu", "Category:Highways in India", "Category:Road construction"],
        "kw": ["road", "highway", "motorway", "asphalt", "interchange"]},
    "gallery-5": {
        "cats": ["Category:Tower cranes", "Category:Construction at dusk"],
        "kw": ["crane", "sunset", "dusk", "silhouette", "site"]},
    "gallery-6": {
        "cats": ["Category:Office buildings in India", "Category:Modern architecture in India"],
        "kw": ["office", "commercial", "business", "building", "modern"]},
}


def api(params):
    params = dict(params); params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def cat_files(cat, limit=60):
    """Files directly in a category + one level of subcategories."""
    try:
        d = api({"action": "query", "list": "categorymembers", "cmtitle": cat,
                 "cmtype": "file|subcat", "cmlimit": str(limit)})
    except Exception:
        return [], []
    files = [m["title"] for m in d.get("query", {}).get("categorymembers", []) if m["title"].lower().endswith((".jpg", ".jpeg", ".png"))
             and "Category:" not in m["title"]]
    subs = [m["title"] for m in d.get("query", {}).get("categorymembers", []) if m["title"].startswith("Category:")]
    return files, subs


def image_info(titles):
    out = []
    for i in range(0, len(titles), 25):
        chunk = titles[i:i + 25]
        try:
            d = api({"action": "query", "titles": "|".join(chunk), "prop": "imageinfo",
                     "iiprop": "url|size|mime", "iiurlwidth": "2000"})
        except Exception:
            continue
        for p in d.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if not ii:
                continue
            out.append({"title": p.get("title", ""), "w": ii.get("width", 0), "h": ii.get("height", 0),
                        "mime": ii.get("mime", ""), "url": ii.get("thumburl") or ii.get("url"),
                        "descurl": ii.get("descriptionurl", "")})
        time.sleep(0.15)
    return out


def collect(slot):
    spec = SLOTS[slot]
    titles = []
    for cat in spec["cats"]:
        f, subs = cat_files(cat)
        titles += f
        for s in subs[:12]:
            sf, _ = cat_files(s, limit=30)
            titles += sf
        if len(titles) > 90:
            break
    titles = list(dict.fromkeys(titles))
    if not titles:
        return []
    info = image_info(titles)
    kws = [k.lower() for k in spec["kw"]]
    cand = []
    for ii in info:
        t = ii["title"]
        if ii["mime"] not in ("image/jpeg", "image/png"):
            continue
        if BAD.search(t):
            continue
        w, h = ii["w"], ii["h"]
        if w < 1600 or h < 1000:
            continue
        ar = w / h
        if ar < 0.85 or ar > 2.4:
            continue
        tl = t.lower()
        score = sum(2 for k in kws if k in tl)
        score += min(4, (w * h) // (2_000_000))
        cand.append({**ii, "score": score})
    cand.sort(key=lambda x: -x["score"])
    return cand


def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if len(data) < 20000:
        return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def main():
    manifest = {}
    if os.path.exists("assets/raw/credits.json"):
        manifest = json.load(open("assets/raw/credits.json"))
    for slot in SLOTS:
        dest = os.path.join(OUT, slot + ".jpg")
        if os.path.exists(dest) and manifest.get(slot, {}).get("ok"):
            print("skip", slot); continue
        cands = collect(slot)
        got = False
        for c in cands[:8]:
            try:
                if download(c["url"], dest):
                    manifest[slot] = {"title": c["title"], "source": c["descurl"], "w": c["w"], "h": c["h"], "ok": True}
                    print(f"OK  {slot:22s} <- {c['title'][:72]}")
                    got = True
                    break
            except Exception:
                continue
        if not got:
            print("FAIL", slot, f"({len(cands)} cands)")
        time.sleep(0.2)
    json.dump(manifest, open("assets/raw/credits.json", "w"), indent=2)
    print(f"\n{sum(1 for v in manifest.values() if v.get('ok'))} slots ready")


if __name__ == "__main__":
    main()
