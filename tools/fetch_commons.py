#!/usr/bin/env python3
"""Fetch curated, license-friendly photography from Wikimedia Commons for demo assets."""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "StructuraDemoSite/1.0 (educational demo build; contact: demo@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
OUT = "assets/raw"
os.makedirs(OUT, exist_ok=True)

BAD = re.compile(r"logo|map|diagram|chart|svg|poster|sign|stamp|coin|coat.of.arms|seal|banner|"
                 r"flag|portrait of|graffiti|screenshot|book|cover|journal|newspaper|painting|drawing|"
                 r"plan of|floor plan|graph|icon|bulletin|certificate|award|plaque|statue|monument of", re.I)

SLOTS = {
    # ---- service imagery ----
    "service-infrastructure":  ["bridge construction piers crane", "concrete bridge segment construction", "flyover construction india highway"],
    "service-structural":      ["steel frame building construction beams", "structural steel erection columns", "reinforced concrete columns rebar building"],
    "service-renovation":      ["building renovation scaffolding restoration", "heritage building restoration construction", "renovation interior construction site"],
    "service-turnkey":         ["modern luxury house interior living room", "contemporary villa interior staircase", "modern apartment interior finished"],
    "service-management":      ["engineers construction site meeting plans", "architects reviewing blueprints site", "construction manager tablet site"],
    # ---- media showcase ----
    "before-site":             ["empty land plot survey", "vacant construction land plot", "bare land site before construction"],
    "video-progress":          ["aerial view construction site drone", "construction site aerial view crane building", "timelapse construction site aerial"],
    "video-interview":         ["engineer hard hat portrait", "construction worker portrait helmet", "site engineer portrait safety helmet"],
    # ---- case study ----
    "case-design":             ["architectural blueprint drawing plans desk", "construction drawings technical", "architect desk plans model"],
    "case-structure":          ["reinforced concrete frame construction building", "rcc column beam construction", "concrete structure under construction rebar"],
    "case-detail-1":           ["modern house facade evening lights", "luxury house exterior night lighting", "modern villa exterior pool"],
    "case-detail-2":           ["modern house staircase interior", "concrete staircase architecture interior", "modern interior staircase design"],
    "case-detail-3":           ["contemporary house exterior architecture india", "modern residential architecture exterior", "architectural house exterior modern"],
    # ---- about / team ----
    "about-team":              ["construction workers team site india", "civil engineers site discussion", "workers hard hat construction portrait group"],
    # ---- insights ----
    "insights-materials":      ["construction materials cement bricks steel", "cement bags construction material", "building materials pile construction"],
    "insights-planning":       ["architect working on plans table model", "architect desk scale model blueprints", "planning table architecture drawings"],
    "insights-contractor":     ["construction site safety inspection helmet checklist", "site inspection engineer clipboard", "quality inspection construction"],
    # ---- local SEO cities ----
    "city-coimbatore":         ["Coimbatore city skyline", "Coimbatore aerial view city", "Coimbatore market street"],
    "city-chennai":            ["Chennai skyline marine drive", "Chennai city aerial view", "Chennai Kapaleeswarar temple city"],
    "city-hosur":              ["Hosur town aerial view", "Hosur industrial area", "Hosur bus stand town"],
    "city-bengaluru":          ["Bengaluru skyline aerial", "Bangalore city skyline MG road", "Bengaluru city view night"],
    # ---- testimonials avatars ----
    "avatar-1":                ["Indian businessman portrait professional", "indian man professional headshot suit", "portrait businessman india smiling"],
    "avatar-2":                ["Indian businesswoman portrait professional", "indian woman professional headshot office", "portrait businesswoman india"],
    "avatar-3":                ["Indian man professional portrait office", "portrait engineer india professional", "professional indian man headshot"],
    # ---- gallery extras ----
    "gallery-1":               ["modern apartment building exterior india", "residential apartment tower exterior", "housing complex architecture"],
    "gallery-2":               ["industrial warehouse logistics exterior", "factory shed industrial building", "industrial plant building exterior"],
    "gallery-3":               ["construction site foundation rebar cage", "foundation excavation piling construction", "concrete foundation site work"],
    "gallery-4":               ["road highway construction asphalt paving", "highway construction machinery", "new road infrastructure india"],
    "gallery-5":               ["building site tower crane sunset", "construction silhouette crane dusk", "crane construction site evening"],
    "gallery-6":               ["completed modern building architecture india", "office building modern exterior", "commercial building exterior modern"],
}


def search(query, limit=14):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "2000",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    pages = data.get("query", {}).get("pages", {})
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        title = p.get("title", "")
        w, h = ii.get("width", 0), ii.get("height", 0)
        mime = ii.get("mime", "")
        if mime not in ("image/jpeg", "image/png"):
            continue
        if BAD.search(title):
            continue
        if w < 1500 or h < 900:
            continue
        out.append({"title": title, "w": w, "h": h, "url": ii.get("thumburl") or ii.get("url"),
                    "descurl": ii.get("descriptionurl", ""), "mime": mime})
    out.sort(key=lambda x: x["w"] * x["h"], reverse=True)
    return out


def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
    if len(data) < 8000:
        return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def main():
    manifest = {}
    for slot, queries in SLOTS.items():
        dest = os.path.join(OUT, slot + ".jpg")
        if os.path.exists(dest):
            print("skip", slot); continue
        got = False
        for q in queries:
            try:
                cands = search(q)
            except Exception as e:
                print("  search fail", q, e); continue
            for c in cands[:6]:
                try:
                    if download(c["url"], dest):
                        manifest[slot] = {"query": q, "title": c["title"], "source": c["descurl"],
                                          "w": c["w"], "h": c["h"]}
                        print(f"OK  {slot:24s} <- {c['title'][:70]}")
                        got = True
                        break
                except Exception as e:
                    continue
            if got:
                break
            time.sleep(0.3)
        if not got:
            print("FAIL", slot)
        time.sleep(0.2)
    with open("assets/raw/credits.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n{len(manifest)}/{len(SLOTS)} downloaded")


if __name__ == "__main__":
    main()
