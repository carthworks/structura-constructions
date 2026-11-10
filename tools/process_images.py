#!/usr/bin/env python3
"""Final asset pipeline: crop, cinematic grade (navy shadows / warm highlights), resize, WebP+JPEG."""
import os
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

RAW = "assets/raw"
CAND = "assets/raw/cand"
OUT = "assets/img"
os.makedirs(OUT, exist_ok=True)

# name -> (source path, aspect w/h, target width)
PLAN = {
    "hero":                 (f"{RAW}/../img/src/hero.jpg", 16 / 9, 2000),
    "project-villa":        (f"{RAW}/../img/src/project-villa.jpg", 16 / 10, 1400),
    "project-office":       (f"{RAW}/../img/src/project-office.jpg", 16 / 10, 1400),
    "project-warehouse":    (f"{RAW}/../img/src/project-warehouse.jpg", 16 / 10, 1400),
    "project-apartment":    (f"{RAW}/../img/src/project-apartment.jpg", 16 / 10, 1400),
    "project-institutional": (f"{RAW}/../img/src/project-institutional.jpg", 16 / 10, 1400),
    "project-road":         (f"{RAW}/../img/src/project-road.jpg", 16 / 10, 1400),
    "service-residential":  (f"{RAW}/../img/src/service-residential.jpg", 4 / 3, 1100),
    "service-commercial":   (f"{RAW}/../img/src/service-commercial.jpg", 4 / 3, 1100),
    "service-industrial":   (f"{RAW}/../img/src/service-industrial.jpg", 4 / 3, 1100),
    "service-infrastructure": (f"{RAW}/gallery-5.jpg", 4 / 3, 1100),
    "service-structural":   (f"{CAND}/case-structure__1.jpg", 4 / 3, 1100),
    "service-renovation":   (f"{RAW}/gallery-6.jpg", 4 / 3, 1100),
    "service-turnkey":      (f"{RAW}/case-detail-2.jpg", 4 / 3, 1100),
    "service-planning":     (f"{CAND}/case-design__2.jpg", 4 / 3, 1100),
    "before-site":          (f"{CAND}/before-site__3.jpg", 16 / 10, 1400),
    "after-villa":          (f"{RAW}/../img/src/project-villa.jpg", 16 / 10, 1400),
    "case-design":          (f"{CAND}/case-design__0.jpg", 16 / 10, 1400),
    "case-detail-1":        (f"{CAND}/case-detail-1__3.jpg", 4 / 3, 1100),
    "case-detail-2":        (f"{CAND}/case-detail-1__4.jpg", 4 / 3, 1100),
    "case-structure":       (f"{CAND}/case-structure__1.jpg", 16 / 10, 1400),
    "gallery-1":            (f"{CAND}/gallery-1__2.jpg", 16 / 10, 1400),
    "gallery-2":            (f"{CAND}/gallery-2__2.jpg", 16 / 10, 1400),
    "insights-contractor":  (f"{CAND}/insights-contractor__2.jpg", 4 / 3, 1100),
    "insights-materials":   (f"{CAND}/insights-materials__3.jpg", 4 / 3, 1100),
    "insights-planning":    (f"{CAND}/case-design__1.jpg", 4 / 3, 1100),
    "about-team":           (f"{RAW}/../img/src/service-residential.jpg", 4 / 3, 1100),
    "city-coimbatore":      (f"{RAW}/city-coimbatore.jpg", 3 / 2, 900),
    "city-chennai":         (f"{RAW}/../img/src/project-office.jpg", 3 / 2, 900),
    "city-hosur":           (f"{RAW}/../img/src/project-warehouse.jpg", 3 / 2, 900),
    "city-bengaluru":       (f"{RAW}/city-bengaluru.jpg", 3 / 2, 900),
    "og-image":             (f"{RAW}/../img/src/hero.jpg", 1200 / 630, 1200),
}
# de-dupe (dict comprehension keeps last) -> fix explicit


def grade(im, strength=1.0):
    """Cinematic grade: cool navy shadows, warm highlights, gentle contrast + saturation."""
    im = im.convert("RGB")
    a = np.asarray(im, dtype=np.float32) / 255.0
    luma = a[:, :, 0] * 0.2126 + a[:, :, 1] * 0.7152 + a[:, :, 2] * 0.0722
    shadow = (1.0 - luma)[..., None]
    high = luma[..., None]
    a = a + shadow * np.array([0.004, 0.016, 0.052]) * strength
    a = a + high * np.array([0.055, 0.022, -0.030]) * strength
    a = (a - 0.5) * (1.0 + 0.055 * strength) + 0.5
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * (1.0 - 0.10 * strength)
    a = np.clip(a, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def crop_ar(im, ar):
    w, h = im.size
    if w / h > ar:
        nw = int(h * ar); left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / ar)
    top = int((h - nh) * 0.42)
    return im.crop((0, top, w, top + nh))


def main():
    seen = set()
    for name, (src, ar, width) in PLAN.items():
        if name in seen:
            continue
        seen.add(name)
        if not os.path.exists(src):
            print("MISSING", name, src)
            continue
        im = Image.open(src)
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (12, 18, 30))
            im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        im = crop_ar(im, ar)
        im = im.resize((width, int(round(width / ar))), Image.LANCZOS)
        im = grade(im)
        jpg = os.path.join(OUT, name + ".jpg")
        im.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
        im.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=80, method=6)
        print(f"{name:24s} {im.size[0]}x{im.size[1]}  {os.path.getsize(jpg)//1024}KB")


if __name__ == "__main__":
    main()
