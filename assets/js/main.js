/* =========================================================
   STRUCTURA CONSTRUCTIONS — interaction layer
   Vanilla JS, no dependencies. Progressive enhancement.
   ========================================================= */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------------
     1. Hero entrance + sticky header + scroll progress
  --------------------------------------------------------- */
  window.addEventListener("load", function () {
    document.body.classList.add("is-ready");
  });

  var nav = $("#nav");
  var progress = $("#scrollProgress");
  var toTop = $("#toTop");
  var ticking = false;

  function onScroll() {
    var y = window.pageYOffset || document.documentElement.scrollTop;
    var docH = document.documentElement.scrollHeight - window.innerHeight;

    if (nav) nav.classList.toggle("is-stuck", y > 12);
    if (progress) progress.style.width = (docH > 0 ? (y / docH) * 100 : 0) + "%";
    if (toTop) toTop.classList.toggle("is-visible", y > 700);

    /* subtle hero parallax */
    if (!reduceMotion) {
      var media = $(".hero__media img");
      if (media && y < window.innerHeight * 1.2) {
        media.style.transform = "scale(1.1) translate3d(0," + (y * 0.12).toFixed(1) + "px,0)";
      }
    }
    ticking = false;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  }

  /* ---------------------------------------------------------
     2. Mobile navigation
  --------------------------------------------------------- */
  var burger = $("#navBurger");
  var mobileNav = $("#mobileNav");

  function setMobileNav(open) {
    if (!burger || !mobileNav) return;
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    burger.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
    mobileNav.classList.toggle("is-open", open);
    document.body.classList.toggle("is-locked", open);
    nav && nav.classList.toggle("is-open", open);
  }

  if (burger) {
    burger.addEventListener("click", function () {
      setMobileNav(burger.getAttribute("aria-expanded") !== "true");
    });
  }
  $$("#mobileNav a").forEach(function (link) {
    link.addEventListener("click", function () { setMobileNav(false); });
  });

  /* ---------------------------------------------------------
     3. Scroll reveal + animated counters
  --------------------------------------------------------- */
  var revealTargets = $$("[data-reveal]");

  if ("IntersectionObserver" in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var siblings = el.parentElement ? $$("[data-reveal]", el.parentElement) : [];
        var idx = siblings.indexOf(el);
        el.style.transitionDelay = (idx > 0 ? Math.min(idx, 8) * 75 : 0) + "ms";
        el.classList.add("is-visible");
        revealObserver.unobserve(el);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });

    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add("is-visible"); });
  }

  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduceMotion) { el.textContent = String(target) + suffix; return; }
    var duration = 1500;
    var start = null;

    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(target * eased)) + suffix;
      if (p < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  var counters = $$("[data-count]");
  if ("IntersectionObserver" in window) {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        animateCount(entry.target);
        countObserver.unobserve(entry.target);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { countObserver.observe(el); });
  } else {
    counters.forEach(animateCount);
  }

  /* ---------------------------------------------------------
     4. Scrollspy for navigation
  --------------------------------------------------------- */
  var navLinks = $$(".nav__link");
  var sectionIds = navLinks.map(function (l) { return l.getAttribute("href"); })
    .filter(function (h) { return h && h.indexOf("#") === 0; });

  if ("IntersectionObserver" in window && sectionIds.length) {
    var spyObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (link) {
          link.classList.toggle("is-active", link.getAttribute("href") === "#" + entry.target.id);
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });

    sectionIds.forEach(function (id) {
      var sec = document.querySelector(id);
      if (sec) spyObserver.observe(sec);
    });
  }

  /* ---------------------------------------------------------
     5. Service cards — learn more toggle
  --------------------------------------------------------- */
  $$(".service-card__more").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var card = btn.closest(".service-card");
      var open = card.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.childNodes[0].nodeValue = open ? "Show less" : "Learn more";
    });
  });

  /* ---------------------------------------------------------
     6. Portfolio filters
  --------------------------------------------------------- */
  var filterButtons = $$(".filter");
  var projectCards = $$("#portfolioGrid .project-card");
  var projectCount = $("#projectCount");

  filterButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var filter = btn.getAttribute("data-filter");
      filterButtons.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });

      var visible = 0;
      projectCards.forEach(function (card) {
        var match = filter === "all" || card.getAttribute("data-category") === filter;
        card.classList.toggle("is-hidden", !match);
        if (match) {
          visible++;
          card.classList.remove("is-entering");
          void card.offsetWidth;
          card.classList.add("is-entering");
        }
      });
      if (projectCount) projectCount.textContent = visible < 10 ? "0" + visible : String(visible);
    });
  });

  /* ---------------------------------------------------------
     7. Content engine tabs
  --------------------------------------------------------- */
  var engineTabs = $$("#engineTabs .engine-tab");
  var enginePanels = $$("#enginePanels .engine-panel");

  function activateTab(tab) {
    engineTabs.forEach(function (t) {
      var selected = t === tab;
      t.setAttribute("aria-selected", selected ? "true" : "false");
      t.setAttribute("tabindex", selected ? "0" : "-1");
    });
    enginePanels.forEach(function (p) {
      var on = p.id === tab.getAttribute("aria-controls");
      p.hidden = !on;
      p.classList.toggle("is-active", on);
    });
  }

  engineTabs.forEach(function (tab, index) {
    tab.setAttribute("tabindex", index === 0 ? "0" : "-1");
    tab.addEventListener("click", function () { activateTab(tab); });
    tab.addEventListener("keydown", function (e) {
      var next = null;
      if (e.key === "ArrowDown" || e.key === "ArrowRight") next = engineTabs[(index + 1) % engineTabs.length];
      if (e.key === "ArrowUp" || e.key === "ArrowLeft") next = engineTabs[(index - 1 + engineTabs.length) % engineTabs.length];
      if (e.key === "Home") next = engineTabs[0];
      if (e.key === "End") next = engineTabs[engineTabs.length - 1];
      if (next) { e.preventDefault(); activateTab(next); next.focus(); }
    });
  });

  /* ---------------------------------------------------------
     8. Before / after comparison slider
  --------------------------------------------------------- */
  $$(".ba").forEach(function (ba) {
    var range = $("input[type=range]", ba);
    if (!range) return;
    function update() {
      ba.style.setProperty("--pos", range.value + "%");
    }
    range.addEventListener("input", update);
    update();
  });

  /* ---------------------------------------------------------
     9. Accordions (FAQ + case study)
  --------------------------------------------------------- */
  function wireAccordion(container, itemSelector, btnSelector, exclusive) {
    if (!container) return;
    $$(itemSelector, container).forEach(function (item) {
      var btn = $(btnSelector, item);
      if (!btn) return;
      btn.addEventListener("click", function () {
        var isOpen = item.classList.contains("is-open");
        if (exclusive && !isOpen) {
          $$(itemSelector, container).forEach(function (other) {
            other.classList.remove("is-open");
            var ob = $(btnSelector, other);
            if (ob) ob.setAttribute("aria-expanded", "false");
          });
        }
        item.classList.toggle("is-open", !isOpen);
        btn.setAttribute("aria-expanded", !isOpen ? "true" : "false");
      });
    });
  }
  wireAccordion($("#faqList"), ".faq-item", ".faq-item__btn", true);
  wireAccordion($("#caseAccordion"), ".case-item", ".case-item__btn", true);

  /* ---------------------------------------------------------
     10. Modal plumbing (focus trap + escape)
  --------------------------------------------------------- */
  var openModal = null;
  var lastFocused = null;

  function trapFocus(e, modal) {
    var focusables = $$("a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex='-1'])", modal)
      .filter(function (el) { return el.offsetParent !== null; });
    if (!focusables.length) return;
    var first = focusables[0], last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function showModal(modal) {
    if (!modal) return;
    lastFocused = document.activeElement;
    modal.classList.add("is-open");
    document.body.classList.add("is-locked");
    openModal = modal;
    var focusTarget = $("[data-close]", modal) || modal;
    window.setTimeout(function () { focusTarget.focus(); }, 60);
  }

  function hideModal() {
    if (!openModal) return;
    openModal.classList.remove("is-open");
    document.body.classList.remove("is-locked");
    if (lastFocused && lastFocused.focus) lastFocused.focus();
    openModal = null;
  }

  $$(".modal").forEach(function (modal) {
    $$("[data-close]", modal).forEach(function (btn) {
      btn.addEventListener("click", hideModal);
    });
    modal.addEventListener("click", function (e) {
      if (e.target === modal) hideModal();
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (openModal) { hideModal(); return; }
      setMobileNav(false);
    }
    if (openModal && e.key === "Tab") trapFocus(e, openModal);
  });

  /* ---------------------------------------------------------
     11. Lightbox gallery
  --------------------------------------------------------- */
  var lb = $("#lightbox");
  var lbImage = $("#lbImage");
  var lbCaption = $("#lbCaption");
  var lbCounter = $("#lbCounter");
  var lbGroup = [];

  function renderLightbox(index) {
    if (!lbGroup.length) return;
    var i = (index + lbGroup.length) % lbGroup.length;
    var item = lbGroup[i];
    lbImage.src = item.src;
    lbImage.alt = item.caption || "Project image";
    lbCaption.textContent = item.caption || "";
    lbCounter.textContent = (i + 1) + " / " + lbGroup.length;
  }

  $$(".js-lightbox").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var groupName = btn.closest("[data-lightbox-group]");
      var scope = groupName || btn.parentElement;
      lbGroup = $$(".js-lightbox", scope).map(function (el) {
        return { src: el.getAttribute("data-src"), caption: el.getAttribute("data-caption") || "" };
      });
      var idx = lbGroup.findIndex(function (item) { return item.src === btn.getAttribute("data-src"); });
      renderLightbox(idx < 0 ? 0 : idx);
      showModal(lb);
    });
  });

  if ($("#lbNext")) $("#lbNext").addEventListener("click", function () { renderLightbox(currentIndex() + 1); });
  if ($("#lbPrev")) $("#lbPrev").addEventListener("click", function () { renderLightbox(currentIndex() - 1); });

  function currentIndex() {
    if (!lbGroup.length) return 0;
    for (var i = 0; i < lbGroup.length; i++) {
      if (lbGroup[i].src === lbImage.getAttribute("src")) return i;
    }
    return 0;
  }

  if (lb) {
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); renderLightbox(currentIndex() + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); renderLightbox(currentIndex() - 1); }
    });
  }

  /* ---------------------------------------------------------
     12. Project case-study data + modal
  --------------------------------------------------------- */
  var PROJECTS = {
    villa: {
      title: "Premium Residential Villa",
      category: "Residential · Completed",
      meta: "Coimbatore, Tamil Nadu · 4,800 sq.ft. · 14 months (sample)",
      desc: "A four-bedroom residence on a sloping plot. A reinforced raft bridges variable founding depth, a post-tensioned ground slab holds the plinth level without deep fill, and the cantilevered first floor was cast monolithically with the transfer beam.",
      specs: [
        ["Structure", "RCC frame + PT slab"],
        ["Foundation", "Reinforced raft"],
        ["Programme", "14 months (sample)"],
        ["Area", "4,800 sq.ft."]
      ],
      images: [
        ["assets/img/project-villa.jpg", "Completed villa — evening elevation with reflecting pool."],
        ["assets/img/case-design.jpg", "Structural drawing set — plans, sections and elevations."],
        ["assets/img/service-residential.jpg", "Frame stage — RCC columns with brick infill during construction."],
        ["assets/img/case-detail-2.jpg", "Finished interior joinery and staircase detail."]
      ]
    },
    office: {
      title: "Commercial Office Complex",
      category: "Commercial · Completed",
      meta: "Chennai, Tamil Nadu · 2 blocks + retail podium · 26 months (sample)",
      desc: "Two nine-storey office blocks over a shared retail podium, delivered with a steel-concrete composite frame, unitised glazing and phased occupancy handover across three tenant tranches.",
      specs: [
        ["Structure", "Composite steel + RCC"],
        ["Façade", "Unitised glazing"],
        ["Programme", "26 months (sample)"],
        ["Blocks", "2 + retail podium"]
      ],
      images: [
        ["assets/img/project-office.jpg", "Office complex plaza and curtain wall at blue hour."],
        ["assets/img/gallery-1.jpg", "Residential tower elevation used as a secondary project view."],
        ["assets/img/service-commercial.jpg", "Curtain wall installation during the envelope phase."],
        ["assets/img/case-structure.jpg", "Structural framing and reinforcement detail."]
      ]
    },
    warehouse: {
      title: "Industrial Warehouse & Logistics Hub",
      category: "Industrial · Ongoing",
      meta: "Hosur, Tamil Nadu · 220,000 sq.ft. · phased delivery (sample)",
      desc: "A distribution facility with clear-span portal frames, heavy-duty racking floors, 24 loading bays and a truck circulation loop planned around peak-hour dispatch windows.",
      specs: [
        ["Structure", "Pre-engineered portal"],
        ["Floor", "Heavy-duty racking slab"],
        ["Bays", "24 loading docks"],
        ["Area", "220,000 sq.ft."]
      ],
      images: [
        ["assets/img/project-warehouse.jpg", "Completed logistics warehouse with loading apron."],
        ["assets/img/gallery-2.jpg", "Warehouse facade and yard circulation."],
        ["assets/img/service-industrial.jpg", "Excavation and foundation works in progress."],
        ["assets/img/service-infrastructure.jpg", "Crane erection on the industrial structure."]
      ]
    },
    apartment: {
      title: "Apartment Development",
      category: "Residential · Ongoing",
      meta: "Coimbatore, Tamil Nadu · 3 blocks · 48 units per block (sample)",
      desc: "Three blocks over a shared basement, delivered with prefabricated bathroom pods and staged façade panels to compress the external finishing programme.",
      specs: [
        ["Structure", "RCC frame + AAC infill"],
        ["Pods", "Prefabricated bathrooms"],
        ["Units", "48 per block"],
        ["Programme", "22 months (sample)"]
      ],
      images: [
        ["assets/img/project-apartment.jpg", "Completed apartment development with podium landscaping."],
        ["assets/img/gallery-1.jpg", "Residential tower elevation."],
        ["assets/img/service-residential.jpg", "Frame stage with engineer on site."],
        ["assets/img/case-detail-1.jpg", "Night elevation with warm lighting."]
      ]
    },
    institutional: {
      title: "Institutional Academic Building",
      category: "Commercial · Completed",
      meta: "Coimbatore District, Tamil Nadu · academic block · 19 months (sample)",
      desc: "A block with seminar halls, a library stack and workshop studios, designed for long spans, heavy book loads and a shaded circulation spine.",
      specs: [
        ["Structure", "Long-span RCC + steel roof"],
        ["Uses", "Seminar, library, workshops"],
        ["Ventilation", "Naturally ventilated spine"],
        ["Programme", "19 months (sample)"]
      ],
      images: [
        ["assets/img/project-institutional.jpg", "Completed institutional building with vertical facade fins."],
        ["assets/img/case-design.jpg", "Architectural drawing set for the academic block."],
        ["assets/img/case-detail-2.jpg", "Interior staircase and circulation detail."],
        ["assets/img/service-planning.jpg", "Elevation drawings used in the design review."]
      ]
    },
    road: {
      title: "Infrastructure & Road Development",
      category: "Infrastructure · Completed",
      meta: "South India · 11 km corridor · 16 months (sample)",
      desc: "An eleven-kilometre four-lane corridor with a grade-separated junction, cross-drainage, kerbs and safety furniture, delivered with traffic management kept live throughout.",
      specs: [
        ["Length", "11 km, four-lane"],
        ["Junctions", "Grade separated"],
        ["Drainage", "Cross-drainage network"],
        ["Programme", "16 months (sample)"]
      ],
      images: [
        ["assets/img/project-road.jpg", "Completed highway interchange from the air."],
        ["assets/img/service-infrastructure.jpg", "Crane and structural erection on site."],
        ["assets/img/before-site.jpg", "The site before construction began."],
        ["assets/img/gallery-2.jpg", "Yard and apron civil works."]
      ]
    }
  };

  var caseModal = $("#caseModal");
  var caseImg = $("#caseModalImg");
  var caseTitle = $("#caseModalTitle");
  var caseCat = $("#caseModalCat");
  var caseMeta = $("#caseModalMeta");
  var caseDesc = $("#caseModalDesc");
  var caseSpecs = $("#caseModalSpecs");
  var caseThumbs = $("#caseModalThumbs");

  function openCase(key) {
    var p = PROJECTS[key];
    if (!p || !caseModal) return;
    caseTitle.textContent = p.title;
    caseCat.textContent = p.category;
    caseMeta.textContent = p.meta;
    caseDesc.textContent = p.desc;
    caseSpecs.innerHTML = p.specs.map(function (s) {
      return '<dl class="spec"><dt>' + s[0] + '</dt><dd>' + s[1] + "</dd></dl>";
    }).join("");
    caseImg.src = p.images[0][0];
    caseImg.alt = p.title + " — " + p.images[0][1];

    caseThumbs.innerHTML = "";
    p.images.forEach(function (img, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-current", i === 0 ? "true" : "false");
      b.setAttribute("aria-label", "View image " + (i + 1) + ": " + img[1]);
      var im = document.createElement("img");
      im.src = img[0];
      im.alt = img[1];
      im.loading = "lazy";
      b.appendChild(im);
      b.addEventListener("click", function () {
        caseImg.src = img[0];
        caseImg.alt = p.title + " — " + img[1];
        $$("button", caseThumbs).forEach(function (x) { x.setAttribute("aria-current", "false"); });
        b.setAttribute("aria-current", "true");
      });
      caseThumbs.appendChild(b);
    });
    showModal(caseModal);
  }

  $$(".js-case-open").forEach(function (btn) {
    btn.addEventListener("click", function () {
      openCase(btn.getAttribute("data-project"));
    });
  });

  /* ---------------------------------------------------------
     13. Video modal (demonstration reel placeholder)
  --------------------------------------------------------- */
  var videoModal = $("#videoModal");
  var videoImg = $("#videoImg");
  var videoBar = $("#videoBar");
  var videoTimecode = $("#videoTimecode");
  var videoTimer = null;

  function stopVideo() {
    if (videoTimer) { window.clearInterval(videoTimer); videoTimer = null; }
    if (videoBar) videoBar.style.width = "0%";
    if (videoTimecode) videoTimecode.textContent = "00:00 / 01:24";
  }

  $$(".js-video").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var src = btn.getAttribute("data-src");
      var title = btn.getAttribute("data-title") || "Construction progress film";
      var desc = btn.getAttribute("data-desc") || "";
      videoImg.src = src;
      videoImg.alt = title;
      $("#videoModalTitle").textContent = title;
      $("#videoModalDesc").textContent = desc;
      stopVideo();
      showModal(videoModal);
    });
  });

  var videoPlay = $("#videoPlay");
  if (videoPlay) {
    videoPlay.addEventListener("click", function () {
      if (videoTimer) {
        stopVideo();
        videoPlay.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
        return;
      }
      videoPlay.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 5h3v14H7zM14 5h3v14h-3z"/></svg>';
      var progress = 0;
      var totalSec = 84;
      videoTimer = window.setInterval(function () {
        progress += 1.6;
        if (videoBar) videoBar.style.width = Math.min(progress, 100) + "%";
        if (videoTimecode) {
          var curSec = Math.floor((Math.min(progress, 100) / 100) * totalSec);
          var m = Math.floor(curSec / 60);
          var s = curSec % 60;
          videoTimecode.textContent = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s) + " / 01:24";
        }
        if (progress >= 100) {
          stopVideo();
          videoPlay.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
        }
      }, 120);
    });
  }

  /* ---------------------------------------------------------
     14. Enquiry form validation
  --------------------------------------------------------- */
  var form = $("#enquiryForm");
  var formStatus = $("#formStatus");
  var formSuccess = $("#formSuccess");

  function fieldOf(input) { return input.closest(".field"); }

  function validateField(input) {
    var wrap = fieldOf(input);
    if (!wrap) return true;
    var value = (input.value || "").trim();
    var valid = true;

    if (input.hasAttribute("required") && !value) valid = false;
    else if (input.type === "email" && value && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) valid = false;
    else if (input.type === "tel" && value && !/^[+()\-\s0-9]{8,16}$/.test(value)) valid = false;
    else if (input.minLength > 0 && value && value.length < input.minLength) valid = false;

    wrap.classList.toggle("has-error", !valid);
    input.setAttribute("aria-invalid", valid ? "false" : "true");
    return valid;
  }

  if (form) {
    var fields = $$("input, select, textarea", form);

    fields.forEach(function (input) {
      input.addEventListener("blur", function () { validateField(input); });
      input.addEventListener("input", function () {
        var wrap = fieldOf(input);
        if (wrap && wrap.classList.contains("has-error")) validateField(input);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstInvalid = null;
      var ok = true;

      fields.forEach(function (input) {
        var valid = validateField(input);
        if (!valid && !firstInvalid) firstInvalid = input;
        ok = ok && valid;
      });

      if (!ok) {
        if (formStatus) {
          formStatus.className = "form-status form-status--err is-visible";
          formStatus.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16h.01"/></svg><span>Please correct the highlighted fields and submit again.</span>';
        }
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      if (formStatus) { formStatus.className = "form-status"; formStatus.innerHTML = ""; }

      var ref = "SC-2026-" + String(Math.floor(1000 + Math.random() * 9000));
      var refEl = $("#refNumber");
      if (refEl) refEl.textContent = ref;

      form.style.display = "none";
      if (formSuccess) formSuccess.classList.add("is-visible");
    });
  }

  var resetBtn = $("#resetForm");
  if (resetBtn && form && formSuccess) {
    resetBtn.addEventListener("click", function () {
      form.reset();
      $$(".field", form).forEach(function (f) { f.classList.remove("has-error"); });
      form.style.display = "";
      formSuccess.classList.remove("is-visible");
      var first = $("#f-name");
      if (first) first.focus();
    });
  }

  var waBtn = $("#whatsappEnquiry");
  if (waBtn) {
    waBtn.addEventListener("click", function () {
      var name = ($("#f-name") && $("#f-name").value) || "";
      var project = ($("#f-type") && $("#f-type").value) || "construction project";
      var location = ($("#f-location") && $("#f-location").value) || "";
      var text = "Hi STRUCTURA CONSTRUCTIONS, I would like to discuss a " + project + " project" + (location ? " in " + location : "") + (name ? ". My name is " + name : "") + ".";
      window.open("https://wa.me/910000000000?text=" + encodeURIComponent(text), "_blank", "noopener");
    });
  }

  /* ---------------------------------------------------------
     15. Misc
  --------------------------------------------------------- */
  /* Placeholder links (sample social profiles) should not jump the page */
  $$('a[href="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) { e.preventDefault(); });
  });

  var yearEl = $("#year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* Smooth in-page anchors with sticky-nav offset */
  $$('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var id = link.getAttribute("href");
      if (!id || id === "#" || id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var offset = (nav ? nav.offsetHeight : 70) + 10;
      var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top: top, behavior: reduceMotion ? "auto" : "smooth" });
      if (history.replaceState) history.replaceState(null, "", id);
    });
  });

  /* ---------------------------------------------------------
     Theme Toggle (Dark / Light mode switcher with persistence)
  --------------------------------------------------------- */
  function setTheme(theme) {
    if (theme === "light") {
      document.documentElement.setAttribute("data-theme", "light");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    try {
      localStorage.setItem("structura-theme", theme);
    } catch (e) {}

    var metaTheme = $('meta[name="theme-color"]');
    if (metaTheme) {
      metaTheme.setAttribute("content", theme === "light" ? "#F8FAFC" : "#070C14");
    }
  }

  function toggleTheme() {
    var isLight = document.documentElement.getAttribute("data-theme") === "light";
    setTheme(isLight ? "dark" : "light");
  }

  var themeBtns = $$("#themeToggle, #themeToggleMobile");
  themeBtns.forEach(function (btn) {
    btn.addEventListener("click", toggleTheme);
  });

  /* ---------------------------------------------------------
     16. BNI Demo Banner Dismissal
  --------------------------------------------------------- */
  var demoBanner = $("#demoBanner");
  var closeDemoBanner = $("#closeDemoBanner");
  if (closeDemoBanner && demoBanner) {
    closeDemoBanner.addEventListener("click", function () {
      demoBanner.style.display = "none";
    });
  }

  /* ---------------------------------------------------------
     17. Clickable Service Areas (Direct Location Selection)
  --------------------------------------------------------- */
  $$(".capability--clickable").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var city = btn.getAttribute("data-city");
      var locField = $("#f-location");
      if (locField) {
        locField.value = city;
        validateField(locField);
      }
      var target = $("#contact");
      if (target) {
        var offset = (nav ? nav.offsetHeight : 70) + 10;
        var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: top, behavior: reduceMotion ? "auto" : "smooth" });
      }
      var typeSelect = $("#f-type");
      if (typeSelect) {
        window.setTimeout(function () { typeSelect.focus(); }, 400);
      }
    });
  });

  /* ---------------------------------------------------------
     18. Interactive Construction Cost Estimator
  --------------------------------------------------------- */
  var calcArea = $("#calcArea");
  var calcAreaDisplay = $("#calcAreaDisplay");
  var calcCostValue = $("#calcCostValue");
  var calcTimeValue = $("#calcTimeValue");
  var calcBreakStruct = $("#calcBreakStruct");
  var calcBreakFinish = $("#calcBreakFinish");
  var calcBreakMEP = $("#calcBreakMEP");
  var calcBreakMgmt = $("#calcBreakMgmt");
  var applyEstimateBtn = $("#applyEstimateBtn");
  var currentRate = 2550;
  var currentTierName = "Premium Architectural";

  function formatIndianCurrency(amount) {
    var lakhs = amount / 100000;
    if (lakhs >= 100) {
      return "₹" + (lakhs / 100).toFixed(2) + " Cr";
    }
    return "₹" + lakhs.toFixed(1) + " L";
  }

  function updateEstimator() {
    if (!calcArea) return;
    var sqft = parseInt(calcArea.value, 10) || 2500;
    if (calcAreaDisplay) {
      calcAreaDisplay.textContent = sqft.toLocaleString("en-IN") + " sq.ft";
    }

    var baseCost = sqft * currentRate;
    var low = baseCost * 0.94;
    var high = baseCost * 1.08;

    if (calcCostValue) {
      calcCostValue.textContent = formatIndianCurrency(low) + " – " + formatIndianCurrency(high);
    }

    if (calcTimeValue) {
      var monthsLow = 10, monthsHigh = 12;
      if (sqft > 2000 && sqft <= 4000) { monthsLow = 12; monthsHigh = 14; }
      else if (sqft > 4000 && sqft <= 8000) { monthsLow = 14; monthsHigh = 18; }
      else if (sqft > 8000) { monthsLow = 18; monthsHigh = 24; }
      calcTimeValue.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-2px;margin-right:4px"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Estimated timeline: <b>' + monthsLow + ' – ' + monthsHigh + ' months</b>';
    }

    if (calcBreakStruct) calcBreakStruct.textContent = formatIndianCurrency(baseCost * 0.45);
    if (calcBreakFinish) calcBreakFinish.textContent = formatIndianCurrency(baseCost * 0.30);
    if (calcBreakMEP) calcBreakMEP.textContent = formatIndianCurrency(baseCost * 0.15);
    if (calcBreakMgmt) calcBreakMgmt.textContent = formatIndianCurrency(baseCost * 0.10);
  }

  if (calcArea) {
    calcArea.addEventListener("input", function () {
      $$(".calc-preset").forEach(function (p) {
        p.classList.toggle("is-active", p.getAttribute("data-val") === calcArea.value);
      });
      updateEstimator();
    });
  }

  $$(".calc-preset").forEach(function (btn) {
    btn.addEventListener("click", function () {
      $$(".calc-preset").forEach(function (b) { b.classList.remove("is-active"); });
      btn.classList.add("is-active");
      if (calcArea) {
        calcArea.value = btn.getAttribute("data-val");
        updateEstimator();
      }
    });
  });

  $$(".calc-tier-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      $$(".calc-tier-btn").forEach(function (b) { b.classList.remove("is-active"); });
      btn.classList.add("is-active");
      currentRate = parseInt(btn.getAttribute("data-rate"), 10) || 2550;
      currentTierName = $("strong", btn) ? $("strong", btn).textContent.trim() : "Custom";
      updateEstimator();
    });
  });

  if (applyEstimateBtn) {
    applyEstimateBtn.addEventListener("click", function () {
      var sqft = calcArea ? calcArea.value : "2500";
      var costTxt = calcCostValue ? calcCostValue.textContent : "";
      var reqText = "Estimated for " + sqft + " sq.ft (" + currentTierName + " specification) — approx " + costTxt + ". Please provide a detailed elemental bill of quantities.";

      var reqField = $("#f-requirements");
      if (reqField) {
        reqField.value = reqText;
      }

      var budgetSelect = $("#f-budget");
      if (budgetSelect) {
        var baseAmount = (parseInt(sqft, 10) || 2500) * currentRate;
        if (baseAmount < 2500000) budgetSelect.value = "Under ₹25 lakh";
        else if (baseAmount <= 7500000) budgetSelect.value = "₹25 – 75 lakh";
        else if (baseAmount <= 20000000) budgetSelect.value = "₹75 lakh – 2 crore";
        else if (baseAmount <= 50000000) budgetSelect.value = "₹2 – 5 crore";
        else if (baseAmount <= 150000000) budgetSelect.value = "₹5 – 15 crore";
        else budgetSelect.value = "Above ₹15 crore";
      }

      var formCard = $(".form-card");
      if (formCard) {
        var offset = (nav ? nav.offsetHeight : 70) + 10;
        var top = formCard.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: top, behavior: reduceMotion ? "auto" : "smooth" });
      }

      var nameField = $("#f-name");
      if (nameField) {
        window.setTimeout(function () { nameField.focus(); }, 400);
      }
    });
  }

  updateEstimator();
})();
