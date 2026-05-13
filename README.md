# Walker Building Corporation

Static HTML mirror of [walkerbldgcorp.com](https://walkerbldgcorp.com/) — original site is WordPress + Elementor. This rebuild serves the same rendered HTML and assets from a static host (Cloudflare Pages), edited via [Tina CMS](https://tina.io/), built with [Eleventy](https://www.11ty.dev/).

## Approach

The six page templates under `src/content/pages/*.njk` are the rendered HTML output of the live WordPress site with all absolute URLs rewritten to local `/assets/vendor/*` paths. All CSS, JS, fonts, and images were mirrored at build-out time.

This produces a pixel-identical replica of the live site, without runtime PHP, MySQL, or WordPress attack surface.

**Tina edits sitewide values in `src/_data/site.json` (phone, email, address, hours).** Page bodies are Elementor-generated HTML and aren't field-editable — structural edits happen by editing the `.njk` files directly (or re-running the mirror).

## Local development

```sh
npm install
npm run dev         # Tina + Eleventy at http://localhost:8080 (admin at /admin/)
npm run build:eleventy   # just the static build (skips Tina)
```

## Project layout

```
src/
├── _data/site.json          ← edited by Tina (sitewide phone/email/address)
├── _headers, _redirects     ← Cloudflare Pages config
├── assets/vendor/           ← mirrored CSS, JS, fonts, images
├── content/pages/*.njk      ← the 6 page templates (rendered Elementor HTML)
├── robots.txt
└── sitemap.njk              ← auto-generated sitemap
tina/config.ts               ← Tina schema (site settings only)
```

## Deployment (Cloudflare Pages)

1. Push repo to GitHub.
2. Cloudflare Pages → connect repo → build command `npm run build`, output dir `public`.
3. Set env vars `NEXT_PUBLIC_TINA_CLIENT_ID` and `TINA_TOKEN` from Tina Cloud.

## Re-mirroring the live site

If the WordPress site changes upstream and you want to pull those changes in, re-run the mirror script:

```sh
python3 /tmp/walker-build.py
npm run build:eleventy
```

The script lives in `scripts/mirror.py` (TODO: move it from /tmp into the repo).

## Notes

- Output is ~36MB on disk (six background-video loops re-encoded to ~1.5 Mbps H.264, no audio, plus Elementor's bundled CSS/JS). All assets are served with `Cache-Control: immutable` via `_headers`.
- The original videos were 1080p / ~22 Mbps / 13–23s. They've been re-encoded at 1.5 Mbps using `libx264 -preset slow -an -movflags +faststart`. To re-mirror and re-encode in one shot: re-run `python3 scripts/mirror.py`, then run the ffmpeg loop in `scripts/encode-videos.sh` (TODO: extract that script).
- The contact form has been rewired to use Cloudflare Pages forms (`data-static-form-name="contact"`). Submissions land in the Cloudflare Pages dashboard. Successful submissions redirect to `/contact/thanks/`.
- Live site references a staging hostname (`bk2.03c.myftpupload.com`) — all such URLs are rewritten during the mirror.
- The mirror script also strips GoDaddy WSIMG analytics scripts and the WordPress emoji loader, so zero third-party assets are loaded by the built site.
