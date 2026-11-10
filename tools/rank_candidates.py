#!/usr/bin/env python3
"""Rank candidates using each file's Commons categories + sharpness/colorfulness metrics."""
import json, os, urllib.parse, urllib.request
from PIL import Image, ImageFilter, ImageStat
import numpy as np

UA = {"User-Agent": "StructuraDemoSite/1.0 (educational demo build)"}
API = "https://commons.wikimedia.org/w/api.php"
CAND = "assets/raw/cand"

# slot -> (category keyword weights, title keywords)
SIGNALS = {
    "service-structural":   (["steel", "beam", "column", "girder", "frame", "skeletal", "structural"], ["steel", "frame", "beam", "column", "girder"]),
    "service-renovation":   (["renovation", "restoration", "refurbish", "scaffold", "demolition", "construction"], ["renovat", "restor", "scaffold", "refurb"]),
    "service-turnkey":      (["interior", "living room", "staircase", "furniture", "residential", "house", "apartment"], ["interior", "living room", "staircase", "house", "interior"]),
    "service-management":   (["engineer", "construction", "worker", "crew", "site", "meeting", "office"], ["engineer", "site", "worker", "foreman", "meeting", "office"]),
    "before-site":          (["vacant", "land", "field", "lot", "clearing", "excavat", "construction", "soil"], ["vacant", "empty", "plot", "land", "clearing", "excavat"]),
    "case-design":          (["drawing", "blueprint", "plan", "technical", "draft", "drawing", "architect"], ["blueprint", "drawing", "plan", "draft", "architect"]),
    "case-structure":       (["concrete", "reinforced", "rcc", "column", "slab", "formwork", "construction", "building"], ["concrete", "column", "slab", "rcc", "formwork", "structure"]),
    "case-detail-1":        (["house", "villa", "residence", "residential", "night", "architecture", "building"], ["house", "villa", "night", "exterior", "lighting", "residence"]),
    "case-detail-3":        (["modern", "contemporary", "architecture", "house", "residential", "building"], ["modern", "contemporary", "house", "residence"]),
    "insights-materials":   (["cement", "brick", "building material", "aggregate", "block", "construction", "steel"], ["cement", "brick", "material", "block", "steel", "aggregate"]),
    "insights-planning":    (["model", "architect", "drawing", "design", "plan", "studio", "table"], ["model", "architect", "desk", "plan", "drawing"]),
    "insights-contractor":  (["inspection", "quality", "survey", "testing", "safety", "construction", "instrument"], ["inspect", "quality", "survey", "test", "checking"]),
    "gallery-1":            (["apartment", "residential", "housing", "high-rise", "building", "architecture"], ["apartment", "residential", "tower", "housing", "block"]),
    "gallery-2":            (["industrial", "factory", "warehouse", "plant", "factory", "shed", "industrial"], ["industrial", "factory", "warehouse", "shed", "plant"]),
}


def api(params):
    params = dict(params); params["format"] = "json"
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def file_categories(titles):
    """Map title -> list of category names."""
    out = {}
    for i in range(0, len(titles), 25):
        chunk = titles[i:i + 25]
        try:
            d = api({"action": "query", "titles": "|".join(chunk), "prop": "categories", "cllimit": "50"})
        except Exception:
            continue
        for p in d.get("query", {}).get("pages", {}).values():
            cats = [c["title"].replace("Category:", "") for c in p.get("categories", [])]
            out[p.get("title", "")] = cats
    return out


def sharpness(path):
    im = Image.open(path).convert("L").resize((600, 400))
    arr = np.asarray(im, dtype=np.float32)
    lap = arr[:-2, 1:-1] + arr[2:, 1:-1] + arr[1:-1, :-2] + arr[1:-1, 2:] - 4 * arr[1:-1, 1:-1]
    return float(lap.var())


def colorfulness(path):
    im = Image.open(path).convert("RGB").resize((300, 200))
    a = np.asarray(im, dtype=np.float32)
    rg = a[:, :, 0] - a[:, :, 1]
    yb = 0.5 * (a[:, :, 0] + a[:, :, 1]) - a[:, :, 2]
    return float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))


def main():
    idx = json.load(open(os.path.join(CAND, "index.json")))
    picks = {}
    for slot, entries in idx.items():
        if not entries:
            continue
        titles = [e["title"] for e in entries]
        cats = file_categories(titles)
        cat_kw, title_kw = SIGNALS.get(slot, (["construction", "building", "architecture"], []))
        scored = []
        for e in entries:
            c = [x.lower() for x in cats.get(e["title"], [])]
            t = e["title"].lower()
            cs = sum(2 for k in cat_kw if any(k in x for x in c))
            ts = sum(3 for k in title_kw if k in t)
            try:
                sh = sharpness(e["file"]); col = colorfulness(e["file"])
            except Exception:
                continue
            # normalise sharpness (0-40 typical) and colourfulness (0-90)
            quality = min(sh / 900.0, 3.0) * 2 + min(col / 40.0, 3.0)
            scored.append({"file": e["file"], "title": e["title"], "score": cs + ts + quality,
                           "cats": c[:8], "sharp": round(sh), "color": round(col)})
        scored.sort(key=lambda x: -x["score"])
        if scored:
            picks[slot] = scored
            best = scored[0]
            print(f"{slot:22s} -> {os.path.basename(best['file']):34s} score={best['score']:.1f} cats={best['cats'][:4]}")
    json.dump(picks, open("assets/raw/cand/scored.json", "w"), indent=2)


if __name__ == "__main__":
    main()
