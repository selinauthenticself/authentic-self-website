#!/usr/bin/env python3
"""Builds the static site from src/ into site/.

Each file in src/pages starts with a comment holding its settings, e.g.
<!-- {"path": "/about", "title": "...", "description": "..."} -->
Pages are written to site/<path>/index.html so every URL stays exactly
the same as on the Squarespace site (good for Google rankings).

Images: {{IMG}} in a page is replaced by IMAGE_BASE. While images still
live on Squarespace it points at their CDN. After running
scripts/download-images.sh, build with:  python3 build.py --local-images
"""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "site"
SITE_URL = "https://www.authenticselfhypnotherapy.com.au"
CDN = "https://images.squarespace-cdn.com/content/v1/6724c7a0bca70a27ee2e67bd/"
PREVIEW = "--preview" in sys.argv
IMAGE_BASE = "/assets/images/" if "--local-images" in sys.argv else CDN
# Images that live outside the main Squarespace image library. With --local-images
# they are served from src/assets/images/extra/ (download-images.sh fetches them).
EXTRA_IMAGES = {
    "https://images.squarespace-cdn.com/content/v2/namespaces/memberAccountAvatars/libraries/6622558cf609b2707cf08b56/de0d8d40-f5d4-4c82-b78b-dc9f5a1181ee/CroppedSydneyPhotoshoot.png": "extra/selin-author.png",
    "https://static1.squarespace.com/static/6724c7a0bca70a27ee2e67bd/6724c7a4bca70a27ee2e682b/6724c7a4bca70a27ee2e6830/1755424047224/unsplash-image-OD2z4Pn4LXQ.jpg": "extra/low-self-worth.jpg",
    "https://images.squarespace-cdn.com/content/v1/5ec321c2af33de48734cc929/fbbf3ea4-50af-4722-8e53-3173298dae20/cover+image.jpg": "extra/testimonials-cover.jpg",
}

# The journaling prompts PDF from the Thank You page
GUIDE = "/assets/JournalingPromptsWebsite.pdf"  # stored with the site in src/assets/

# Your original fonts, Sofia Pro (headings) and Sweet Sans Pro (text), come from
# your Adobe Fonts web project "Authentic Self". The menu uses Avenir Next /
# DM Sans to match Bloom Yoga Ballina.
ADOBE_FONTS_ID = "hfx0nru"

# Contact form: Web3Forms access key for info@authenticselfhypnotherapy.com.au
# (create one free at https://web3forms.com - the key arrives by email).
WEB3FORMS_ACCESS_KEY = "52ffef0f-b6fe-453b-80e9-9fab325dd59b"

NAV = [("About Selin", "/about"), ("Packages", "/#offerings"), ("Book Now", "/private-sessions"),
       ("Testimonials", "/testimonials"), ("Contact", "/contact"), ("Blog", "/blog")]


def header(path):
    links = "".join(
        f'<a href="{href}"{" aria-current=page" if path.startswith(href) else ""}>{name}</a>'
        for name, href in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="inner">
  <a class="logo" href="/" aria-label="Authentic Self Hypnotherapy home"><img src="{{{{IMG}}}}d3558367-4b30-4348-bc7f-907a6c262d22/logo_txt_brick.png" alt="Authentic Self Hypnotherapy"></a>
  <button class="menu-toggle" aria-label="Open menu" onclick="document.querySelector('.nav').classList.toggle('open')">&#9776;</button>
  <nav class="nav">{links}<a class="btn" href="/strategy">Schedule a Free Chat</a></nav>
</div></header>"""


NEWSLETTER = """<section class="section bg-cream newsletter" id="newsletter"><div class="inner">
  <h2>A Gentle Way to Kickstart Your Hypnosis Journey</h2>
  <p>Sign up below to get my free guide with journaling prompts to help you find your top priority for hypnosis.</p>
  <form class="newsletter-form" action="/thank-you" onsubmit="event.preventDefault(); window.location.href = this.getAttribute('action');">
    <label class="visually-hidden" for="nl-f">First Name</label><input id="nl-f" name="fname" placeholder="First Name" autocomplete="given-name">
    <label class="visually-hidden" for="nl-l">Last Name</label><input id="nl-l" name="lname" placeholder="Last Name" autocomplete="family-name">
    <label class="visually-hidden" for="nl-e">Email Address</label><input id="nl-e" name="email" type="email" placeholder="Email Address" autocomplete="email" required>
    <button class="btn" type="submit">Download</button>
  </form>
</div></section>"""

FOOTER = """<footer class="site-footer"><div class="footer-inner">
  <a class="f-logo" href="/"><img src="{{IMG}}d3558367-4b30-4348-bc7f-907a6c262d22/logo_txt_brick.png" alt="Authentic Self Hypnotherapy" loading="lazy"></a>
  <ul class="f-list">
    <li><svg class="f-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg><span>2/4 Ti-Tree Place, Byron Bay NSW 2481 or Online</span></li>
    <li><svg class="f-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg><a href="/">www.authenticselfhypnotherapy.com.au</a></li>
    <li><svg class="f-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg><a href="mailto:info@authenticselfhypnotherapy.com.au">info@authenticselfhypnotherapy.com.au</a></li>
    <li><svg class="f-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg><a href="tel:+61466480926" aria-label="Click to call 0466 480 926">0466 480 926</a></li>
    <li><svg class="f-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/></svg><a href="https://www.instagram.com/selinonthemind/" target="_blank" rel="noopener">@selinonthemind</a></li>
    <li><svg class="f-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M15.5 8H14a2 2 0 0 0-2 2v11M9.5 13h5"/></svg><a href="https://www.facebook.com/authenticselfhypnotherapy" target="_blank" rel="noopener">Facebook</a></li>
  </ul>
  <div class="f-legal">
    <p class="f-copy">&copy; <span id="f-year">2026</span> Authentic Self Hypnotherapy</p>
    <a href="/terms-and-conditions">Terms and Conditions</a>
  </div>
</div><script>document.getElementById('f-year').textContent=new Date().getFullYear()</script></footer>"""


def layout(meta, body):
    NOINDEX = '\n<meta name="robots" content="noindex">' if PREVIEW else ""
    path = meta["path"]
    desc = meta.get("description", "")
    canonical = SITE_URL + (path if path != "/" else "/")
    ADOBE = f'<link rel="stylesheet" href="https://use.typekit.net/{ADOBE_FONTS_ID}.css">\n' if ADOBE_FONTS_ID else ""
    newsletter = "" if meta.get("no_newsletter") else NEWSLETTER
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">{NOINDEX}
<title>{meta['title']}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500&family=Mulish:wght@400;700&family=Outfit:wght@300&display=swap" rel="stylesheet">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/icons/icon-192.png">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
{ADOBE}<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
{header(path)}
<main id="main">
{body}
</main>
{newsletter}
{FOOTER}
</body>
</html>
"""


def relative_links(html, path):
    """Preview builds use relative links so the site works by double-clicking
    index.html, without a web server."""
    depth = len([p for p in path.strip("/").split("/") if p])
    prefix = "../" * depth

    def fix(m):
        attr, url = m.group(1), m.group(2)
        target, _, frag = url.partition("#")
        if target == "":
            return m.group(0)
        clean = target.strip("/")
        if "." in clean.split("/")[-1]:
            new = prefix + clean
        else:
            new = prefix + (clean + "/" if clean else "") + "index.html"
        return f'{attr}="{new}{"#" + frag if frag else ""}"'
    return re.sub(r'(href|src|action|poster)="(/(?!/)[^"]*)"', fix, html)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    shutil.copy(SRC / "assets" / "icons" / "favicon.ico", OUT / "favicon.ico")
    urls = []
    for page in sorted((SRC / "pages").glob("*.html")):
        text = page.read_text()
        m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->", text, re.S)
        meta = json.loads(m.group(1))
        html = layout(meta, text[m.end():].strip()).replace("{{IMG}}", IMAGE_BASE).replace("{{GUIDE}}", GUIDE).replace("{{FORM_KEY}}", WEB3FORMS_ACCESS_KEY)
        dest = OUT / meta["path"].strip("/") / "index.html" if meta["path"] != "/" else OUT / "index.html"
        if IMAGE_BASE != CDN:
            for url, local in EXTRA_IMAGES.items():
                html = html.replace(url, IMAGE_BASE + local)
        if PREVIEW:
            html = relative_links(html, meta["path"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html)
        if not meta.get("hidden"):
            urls.append(SITE_URL + meta["path"])
        print("built", meta["path"])
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    if not PREVIEW:
        (OUT / "CNAME").write_text("www.authenticselfhypnotherapy.com.au\n")  # custom domain for GitHub Pages
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


if __name__ == "__main__":
    build()
