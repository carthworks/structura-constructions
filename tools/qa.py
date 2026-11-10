#!/usr/bin/env python3
"""Interaction QA: exercise the interactive features and capture state."""
import asyncio, json
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8080/index.html"
OUT = "assets/raw/shots"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        results = {}

        # ---------- MOBILE ----------
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_timeout(900)

        # nav overflow check
        overflow = await page.evaluate("""() => {
            const nav = document.querySelector('.nav__inner');
            const burger = document.querySelector('#navBurger');
            const r = burger.getBoundingClientRect();
            return {navScrollW: nav.scrollWidth, navClientW: nav.clientWidth,
                    burgerRight: Math.round(r.right), vw: window.innerWidth,
                    burgerVisible: r.right <= window.innerWidth + 1 && r.width > 0};
        }""")
        results["mobile_nav"] = overflow
        await page.screenshot(path=f"{OUT}/mob-nav.png", clip={"x":0,"y":0,"width":390,"height":140})

        # open mobile menu
        await page.click("#navBurger")
        await page.wait_for_timeout(600)
        results["mobile_menu_open"] = await page.evaluate("""() => ({
            open: document.querySelector('#mobileNav').classList.contains('is-open'),
            expanded: document.querySelector('#navBurger').getAttribute('aria-expanded')
        })""")
        await page.screenshot(path=f"{OUT}/mob-menu.png")
        await page.click("#mobileNav a[href='#projects']")
        await page.wait_for_timeout(900)
        results["mobile_menu_after_click"] = await page.evaluate("""() => ({
            open: document.querySelector('#mobileNav').classList.contains('is-open'),
            scrolled: window.scrollY > 200
        })""")

        # horizontal overflow check across the whole page
        results["h_overflow"] = await page.evaluate("""() => {
            const docW = document.documentElement.clientWidth;
            const bad = [];
            document.querySelectorAll('body *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width > 0 && (r.right > docW + 2 || r.left < -2)) {
                    const cs = getComputedStyle(el);
                    if (cs.position === 'fixed') return;
                    bad.push(el.tagName + '.' + (el.className||'').toString().slice(0,40) + ' right=' + Math.round(r.right));
                }
            });
            return {docW, scrollW: document.documentElement.scrollWidth, offenders: bad.slice(0,8)};
        }""")
        await page.close()

        # ---------- DESKTOP ----------
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda e: errors.append("desktop: " + str(e)))
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_timeout(800)

        # filters
        await page.click(".filter[data-filter='residential']")
        await page.wait_for_timeout(500)
        results["filter_residential"] = await page.evaluate("""() => ({
            visible: [...document.querySelectorAll('#portfolioGrid .project-card')].filter(c=>!c.classList.contains('is-hidden')).length,
            counter: document.querySelector('#projectCount').textContent
        })""")
        await page.screenshot(path=f"{OUT}/qa-filter.png")

        await page.click(".filter[data-filter='all']")
        await page.wait_for_timeout(300)

        # engine tabs
        await page.click("#tab-C")
        await page.wait_for_timeout(600)
        results["tabs"] = await page.evaluate("""() => ({
            cVisible: !document.querySelector('#panel-C').hidden,
            aHidden: document.querySelector('#panel-A').hidden
        })""")
        await page.screenshot(path=f"{OUT}/qa-tabC.png")

        # before/after slider
        await page.click("#tab-B")
        await page.wait_for_timeout(400)
        await page.evaluate("""() => {
            const r = document.querySelector('#baCompare input[type=range]');
            r.value = 72; r.dispatchEvent(new Event('input', {bubbles:true}));
        }""")
        await page.wait_for_timeout(300)
        results["before_after"] = await page.evaluate("""() => ({
            pos: document.querySelector('#baCompare').style.getPropertyValue('--pos')
        })""")
        await page.screenshot(path=f"{OUT}/qa-ba.png")

        # lightbox
        await page.click("#tab-A")
        await page.wait_for_timeout(400)
        await page.click("#panel-A .js-lightbox")
        await page.wait_for_timeout(700)
        results["lightbox"] = await page.evaluate("""() => ({
            open: document.querySelector('#lightbox').classList.contains('is-open'),
            src: document.querySelector('#lbImage').getAttribute('src'),
            counter: document.querySelector('#lbCounter').textContent
        })""")
        await page.screenshot(path=f"{OUT}/qa-lightbox.png")
        await page.keyboard.press("ArrowRight")
        await page.wait_for_timeout(400)
        results["lightbox_next"] = await page.evaluate("() => document.querySelector('#lbCounter').textContent")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)
        results["lightbox_closed"] = await page.evaluate("() => !document.querySelector('#lightbox').classList.contains('is-open')")

        # case study modal
        await page.click(".js-case-open[data-project='warehouse']")
        await page.wait_for_timeout(700)
        results["case_modal"] = await page.evaluate("""() => ({
            open: document.querySelector('#caseModal').classList.contains('is-open'),
            title: document.querySelector('#caseModalTitle').textContent,
            specs: document.querySelectorAll('#caseModalSpecs .spec').length,
            thumbs: document.querySelectorAll('#caseModalThumbs button').length
        })""")
        await page.screenshot(path=f"{OUT}/qa-case-modal.png")
        await page.click("#caseModalThumbs button:nth-child(2)")
        await page.wait_for_timeout(300)
        results["case_modal_thumb"] = await page.evaluate("() => document.querySelector('#caseModalImg').getAttribute('src')")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(400)

        # video modal
        await page.click("#tab-C")
        await page.wait_for_timeout(400)
        await page.click("#panel-C .js-video")
        await page.wait_for_timeout(600)
        results["video_modal"] = await page.evaluate("""() => ({
            open: document.querySelector('#videoModal').classList.contains('is-open'),
            title: document.querySelector('#videoModalTitle').textContent
        })""")
        await page.click("#videoPlay")
        await page.wait_for_timeout(1200)
        results["video_progress"] = await page.evaluate("() => document.querySelector('#videoBar').style.width")
        await page.screenshot(path=f"{OUT}/qa-video.png")
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(400)

        # FAQ accordion
        await page.click("#faqList .faq-item:nth-child(3) .faq-item__btn")
        await page.wait_for_timeout(500)
        results["faq"] = await page.evaluate("""() => ({
            thirdOpen: document.querySelector('#faqList .faq-item:nth-child(3)').classList.contains('is-open'),
            firstOpen: document.querySelector('#faqList .faq-item:nth-child(1)').classList.contains('is-open')
        })""")

        # service learn more
        await page.click(".service-card__more")
        await page.wait_for_timeout(500)
        results["service_toggle"] = await page.evaluate("""() => ({
            open: document.querySelector('.service-card').classList.contains('is-open'),
            label: document.querySelector('.service-card__more').textContent.trim().split('\\n')[0].trim()
        })""")

        # form validation: submit empty
        await page.click("#enquiryForm button[type=submit]")
        await page.wait_for_timeout(500)
        results["form_errors"] = await page.evaluate("""() => ({
            errorFields: document.querySelectorAll('#enquiryForm .field.has-error').length,
            status: document.querySelector('#formStatus').className
        })""")
        await page.screenshot(path=f"{OUT}/qa-form-errors.png")

        # fill and submit
        await page.fill("#f-name", "Test Client")
        await page.fill("#f-company", "Test Developers")
        await page.fill("#f-phone", "+91 98765 43210")
        await page.fill("#f-email", "test@example.com")
        await page.fill("#f-location", "Coimbatore")
        await page.select_option("#f-type", index=1)
        await page.fill("#f-requirements", "Looking for a residential project consultation.")
        await page.click("#enquiryForm button[type=submit]")
        await page.wait_for_timeout(700)
        results["form_success"] = await page.evaluate("""() => ({
            successVisible: document.querySelector('#formSuccess').classList.contains('is-visible'),
            ref: document.querySelector('#refNumber').textContent,
            formHidden: document.querySelector('#enquiryForm').style.display === 'none'
        })""")
        await page.screenshot(path=f"{OUT}/qa-form-success.png")

        # keyboard: skip link + focus visible
        await page.keyboard.press("Tab")
        results["first_tab"] = await page.evaluate("() => document.activeElement.className")

        # link audit
        results["links"] = await page.evaluate("""() => {
            const bad = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const h = a.getAttribute('href');
                if (!h) return;
                if (h.startsWith('#') && h.length > 1) {
                    if (!document.querySelector(h)) bad.push(h);
                } else if (!h.startsWith('http') && !h.startsWith('mailto') && !h.startsWith('tel') && !h.startsWith('https://wa.me')) {
                    bad.push(h);
                }
            });
            return {badInternal: [...new Set(bad)]};
        }""")

        # accessibility basics
        results["a11y"] = await page.evaluate("""() => {
            const imgs = [...document.querySelectorAll('img')];
            const btns = [...document.querySelectorAll('button')];
            const inputs = [...document.querySelectorAll('input,select,textarea')];
            return {
                imgNoAlt: imgs.filter(i => !i.alt).length,
                btnNoLabel: btns.filter(b => !b.textContent.trim() && !b.getAttribute('aria-label')).length,
                inputNoLabel: inputs.filter(i => {
                    if (i.type === 'hidden') return false;
                    return !document.querySelector('label[for="'+i.id+'"]') && !i.getAttribute('aria-label');
                }).length,
                h1: document.querySelectorAll('h1').length,
                landmarks: {
                    header: document.querySelectorAll('header').length,
                    main: document.querySelectorAll('main').length,
                    footer: document.querySelectorAll('footer').length,
                    nav: document.querySelectorAll('nav').length
                }
            };
        }""")
        await page.close()
        await browser.close()
        results["js_errors"] = errors
        print(json.dumps(results, indent=2))

asyncio.run(main())
