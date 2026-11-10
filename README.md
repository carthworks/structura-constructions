# STRUCTURA CONSTRUCTIONS — Construction & Civil Engineering Portfolio Website

A complete, production-quality demonstration website for a fictional civil engineering
and construction company. It doubles as a live sales demonstration for **MIN MURASU —
Digital Growth & AI Automation**, while **STRUCTURA CONSTRUCTIONS** remains the primary
brand throughout.

> **Everything on this site is sample content.** All projects, statistics, testimonials,
> contact details and case studies are fictional and clearly labelled as demonstration
> material. Nothing here claims a real client, certification, award or completed project.

---

## 1. Run it

```bash
cd /home/user
python3 -m http.server 8080 --bind 0.0.0.0
# → http://localhost:8080
```

No build step, no framework, no dependencies. Plain HTML5, CSS and vanilla JavaScript.
Deploy by copying the folder to any static host (Netlify, Vercel, Cloudflare Pages, S3,
or plain shared hosting).

---

## 2. File structure

```
index.html                 Single-page site (all 14 sections)
privacy.html               Privacy policy (sample wording)
terms.html                 Terms of use (sample wording)
robots.txt / sitemap.xml   Search engine files
site.webmanifest           PWA manifest
assets/
  css/styles.css           Design system + all component styles
  css/fonts.css            Self-hosted @font-face declarations
  fonts/                   Archivo, Inter, IBM Plex Mono (woff2, latin + latin-ext)
  js/main.js               All interactions (vanilla, dependency-free)
  img/                     Optimised photography: .jpg + .webp pairs
  img/src/                 Original AI-generated source frames
  img/CREDITS.md           Image attribution (AI + Wikimedia Commons sources)
tools/                     Image pipeline + QA scripts (not part of the website)
```

---

## 3. Section map (matches the brief)

| # | Section | Anchor | Notes |
|---|---|---|---|
| 1 | Sticky navigation | `#top` | Glass nav, scroll progress, mobile drawer |
| 2 | Hero | `#top` | Cinematic image, blueprint grid, animated stat cards, Ken Burns + parallax |
| 3 | Credibility / trust | `#about` | Capability list, animated counters, demo-figure labels |
| 4 | Services | `#services` | 8 service cards, expandable detail, photography |
| 5 | Project portfolio | `#projects` | 6 projects, animated category filters, case-study modal |
| 6 | Content engine | `#expertise` | 7 interactive showcases (A–G) |
| 7 | Case study deep dive | `#case-study` | Overview → handover accordion, specs, timeline, gallery, social previews |
| 8 | Marketing system | `#marketing-system` | 5-stage pipeline + 7 distribution channels |
| 9 | Why choose us | `#why` | 6 positioning cards + 4-step process |
| 10 | Testimonials | `#testimonials` | 3 clearly-marked sample cards |
| 11 | Insights | `#insights` | 7 SEO article cards with related project links |
| 12 | FAQ | `#faq` | 8 accordion items + matching FAQPage schema |
| 13 | Local SEO | `#locations` | 4 city cards, NAP panel, 12 service areas |
| 14 | CTA + enquiry form | `#contact` | 9 fields, inline validation, WhatsApp hand-off |
| — | Footer | — | 5 columns, legal, Min Murasu demonstration credit |

---

## 4. Interactive features

- **Project filters** — All / Residential / Commercial / Industrial / Infrastructure,
  with animated reflow and a live count.
- **Before & after slider** — draggable comparison with keyboard support.
- **Lightbox gallery** — grouped image sets, arrow-key navigation, focus trap, Esc to close.
- **Case study modal** — six fully-written project case studies with specs and image sets.
- **Video modal** — demonstration reel placeholders with a simulated progress bar.
- **Content engine tabs** — 7 showcases with roving-tabindex arrow-key navigation.
- **Animated statistics** — easing counters that trigger on scroll into view.
- **Accordions** — FAQ and case-study sections (single-open behaviour).
- **Enquiry form** — per-field validation, `aria-live` status, demo reference number,
  WhatsApp pre-fill, and a local-only success state.
- **Sticky WhatsApp button**, back-to-top, scroll progress bar, scroll-spy navigation,
  mobile drawer, full keyboard operability, and `prefers-reduced-motion` support.

---

## 5. SEO and performance

- Unique title and meta description targeting civil engineering / construction intent.
- Semantic HTML5 with one `<h1>` and a clean `h2 → h3` hierarchy.
- JSON-LD: `Organization`, `GeneralContractor` (with service catalogue), `WebSite`,
  `BreadcrumbList`, `FAQPage`.
- Open Graph and Twitter card metadata with a 1200×630 share image.
- Local SEO sections and NAP block for Coimbatore, Chennai, Hosur and Bengaluru.
- Descriptive alt text on all 53 images; `<picture>` with WebP + JPEG fallback.
- Self-hosted subsetted fonts, preloaded hero image and key font files.
- Lazy loading, `fetchpriority="high"` on the LCP image, deferred JS.
- Measured locally: FCP ~190 ms, DOMContentLoaded ~140 ms, zero console errors.

---

## 6. Accessibility

Skip link · single H1 · labelled form controls · `aria-expanded` / `aria-pressed` /
`aria-selected` state on every control · `role="dialog"` with focus trapping · visible
focus rings · keyboard operability for tabs, lightbox, sliders and modals ·
`aria-live` form feedback · sufficient colour contrast on the navy/orange palette ·
reduced-motion support.

---

## 7. Replacing the demonstration content

1. **Brand** — edit the logo mark, company name and positioning copy in `index.html`
   (nav, footer, JSON-LD) and `assets/css/styles.css` (colours, type).
2. **Projects** — swap the six `<article class="project-card">` blocks and the
   `PROJECTS` object in `assets/js/main.js`, then update `assets/img/`.
3. **Statistics** — update `data-count` / `data-suffix` values and remove the
   "illustrative demo figure" notes once the figures are real.
4. **Testimonials** — replace the sample quotes, names and monogram initials.
5. **Contact** — replace the placeholder phone, email and address in the top bar,
   footer, NAP panel and JSON-LD, then point the WhatsApp link at the real number.
6. **Enquiry form** — wire `#enquiryForm` to your CRM or a server endpoint; the current
   handler validates and confirms entirely in the browser and sends nothing.
7. **Domain** — update the canonical URL, Open Graph URLs and `sitemap.xml` /
   `robots.txt` to your live domain.

---

## 8. Min Murasu capability mapping

The demo shows, in situ, how Min Murasu delivers for a construction business:

| Capability | Where it is demonstrated |
|---|---|
| Professional contractor website | Whole build — design system, responsive, fast |
| Project portfolio development | `#projects` filterable portfolio + case-study modals |
| Architectural photography & content presentation | Graded WebP/JPEG pipeline in `tools/` |
| Case study creation | `#case-study` deep dive + `#expertise` panel F |
| SEO & local search visibility | JSON-LD, FAQs, city pages, NAP, sitemap |
| Google & Meta lead generation | `#contact` enquiry form + WhatsApp hand-off |
| LinkedIn content marketing | `#expertise` panel G post previews |
| WhatsApp enquiry automation | Sticky button + form-to-WhatsApp prefill |
| CRM & pipeline integration | `#marketing-system` enquiry-to-opportunity pipeline |
| Digital performance reporting | `#marketing-system` outcome metrics + source attribution |

Min Murasu appears only in a subtle footer credit and in this README — the site reads
as a real contractor's site throughout.

---

## 9. Tooling (optional, not required to run the site)

```bash
python3 tools/fetch_commons2.py    # re-fetch open-licensed source photography
python3 tools/process_images.py    # crop, grade and export optimised web images
python3 tools/shoot.py 1440 900    # screenshot sections for visual QA
python3 tools/qa.py                # interaction, accessibility and link audit
```

`tools/qa.py` verifies: mobile navigation reachability, filters, tabs, the comparison
slider, lightbox keyboard navigation, case-study and video modals, accordions, form
validation and submission, internal link integrity, image alt coverage and form labels.
