# Authentic Self Hypnotherapy — website

A copy of www.authenticselfhypnotherapy.com.au as plain HTML/CSS, built from
the Squarespace site in November 2026. **Not published anywhere.** The
Squarespace site is still the live one.

## Review it

Open `site/index.html` in your browser and click around. Images, the
Google Reviews widget and the Acuity booking calendars load from the live
services, so you need to be online.

## Edit and rebuild

- Page content: `src/pages/*.html` (one file per page; settings line at the top)
- Blog post text: `src/posts/*.html`
- Colours, fonts, spacing: `src/assets/styles.css`
- Header, footer, newsletter: `build.py`

```
python3 build.py --preview   # review build (relative links, hidden from Google)
python3 build.py             # launch build (clean URLs, sitemap.xml)
```

All URLs are the same as on Squarespace, so Google rankings and existing links carry over.

The journaling prompts guide (Thank You page download) is stored with the site
at `src/assets/JournalingPromptsWebsite.pdf`.

## How publishing works

The site is hosted on GitHub Pages from the repository
`selinauthenticself/authentic-self-website`. Every change pushed to the `main`
branch is built and published automatically (see `.github/workflows/deploy.yml`).
The first run also saves any images still on Squarespace into `src/assets/images/`.

## Before launch

1. **Images:** run `bash scripts/download-images.sh`, then build with
   `--local-images`. Until then, images still load from Squarespace's servers
   and would stop working once Squarespace is cancelled.
2. **Videos:** done. All 6 videos (home page + 5 testimonials) are stored with the
   site in `src/assets/videos/`, compressed for the web.
3. **Contact form + newsletter:** they need a form service (e.g. Formspree,
   Netlify Forms, MailerLite). Right now they show a "not connected yet" message.
   The newsletter on the current site isn't working either: it shows
   "needs a storage option".
4. **Fonts:** your original Sofia Pro (headings) and Sweet Sans Pro (text),
   loaded from your Adobe Fonts web project `hfx0nru`. Keep your Adobe
   membership active or these fonts stop loading. The menu uses Avenir Next /
   DM Sans (free), matching Bloom Yoga Ballina.
5. **Hosting:** e.g. Netlify, Cloudflare Pages or GitHub Pages; then point
   the domain's DNS there.

## Not copied (Squarespace template leftovers)

`/services` and `/shop` (and its 3 products) contain placeholder template text
and aren't linked from the site.
