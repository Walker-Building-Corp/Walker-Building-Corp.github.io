# Walker Building Corporation

Hand-built static marketing site. Eleventy v3 + Tina CMS, deployed to Cloudflare Pages.

## Architecture

- **Single CSS file** at `src/assets/css/main.css` (~20KB) with a design system anchored on the brand palette extracted from the original Elementor build.
- **Zero JavaScript bundle** — the only `<script>` on each page is the inline LocalBusiness JSON-LD schema.
- **Composable section partials** in `src/_includes/partials/section-*.njk`. Each page declares its sections via frontmatter; the layout dispatches by type.
- **Markdown content collections** for `services/` and `equipment/`. Tina-editable.
- **Site settings** in `src/_data/site.json` — global phone/email/address/hours used by header, footer, contact form, and JSON-LD.

```
src/
├── _data/
│   ├── site.json              ← Tina-editable: phone, email, address, hours
│   └── year.js                ← provides {{ year }} to footer
├── _includes/
│   ├── layouts/base.njk       ← <head> + SEO + chrome + slot
│   └── partials/
│       ├── header.njk         ← sticky header + top contact strip + nav
│       ├── footer.njk         ← services list + company + contact
│       ├── hero.njk           ← optional video-bg hero
│       ├── sections.njk       ← dispatches sections array by type
│       └── section-*.njk      ← one file per section type
├── content/
│   ├── pages/                 ← 7 page markdowns (frontmatter-driven)
│   ├── services/              ← 4 service markdowns (collection)
│   └── equipment/             ← 4 equipment markdowns (collection)
├── assets/
│   ├── css/main.css           ← single stylesheet
│   ├── fonts/                 ← Bebas Neue + Be Vietnam Pro woff2
│   ├── img/                   ← logos, service/equipment photos
│   └── video/                 ← 6 hero background loops (~18MB)
├── _headers, _redirects       ← Cloudflare Pages config
├── robots.txt
└── sitemap.njk                ← auto-generated sitemap.xml
tina/config.ts                 ← Tina schema (Pages, Services, Equipment, Settings)
```

## Local development

```sh
npm install
npm run dev              # Tina + Eleventy at http://localhost:8080 (admin at /admin/)
npm run build:eleventy   # just the static build (skips Tina)
```

## Page composition (frontmatter)

Each page in `src/content/pages/*.md` is composed from:

1. A `hero` object: `{ video, poster, eyebrow, heading, subhead, ctas, compact }`
2. A `sections` array — each entry has a `type` and optional `heading`/`intro`/`body`/`cta`.

Available section types:

| Type               | Renders                                        |
| ------------------ | ---------------------------------------------- |
| `services-grid`    | card grid pulling from `collections.services`  |
| `services-detail`  | full per-service rows with image + body        |
| `equipment-grid`   | card grid pulling from `collections.equipment` |
| `equipment-detail` | full per-equipment rows                        |
| `about-summary`    | centered prose block + optional CTA            |
| `cta-band`         | full-width primary-color band with single CTA  |
| `contact-form`     | Cloudflare Pages contact form + info column    |
| `careers-form`     | Cloudflare Pages job application form          |

To add a new section type: create `src/_includes/partials/section-<type>.njk`, then add a branch to `partials/sections.njk` and the type to Tina's section options in `tina/config.ts`.

## Forms

`contact` and `careers` form names are wired for Cloudflare Pages forms (`data-static-form-name="contact"` / `"careers"`). Both POST to `/contact/thanks/` on success.

## Linting + formatting

Prettier, ESLint, Stylelint, HTMLHint, with a husky pre-commit hook running `lint-staged`.

```sh
npm run format         # apply Prettier to everything
npm run format:check   # CI-friendly: fail if anything is unformatted
npm run lint           # run all linters
```

`src/_includes/layouts/base.njk` is `.prettierignore`d because it has Jinja interpolation inside the inline JSON-LD `<script>` block (Prettier can't reconcile).

## Deployment (Cloudflare Pages)

1. Push to GitHub `main`.
2. Cloudflare Pages → connect repo, build command `npm run build`, output dir `public`.
3. Env vars: `NEXT_PUBLIC_TINA_CLIENT_ID` and `TINA_TOKEN` from Tina Cloud.
4. Forms auto-detected via the `data-static-form-name` attribute.

## SEO

- LocalBusiness JSON-LD in `base.njk`, sourced from `site.json` (phone, address, geo, hours, areas served).
- Per-page `<title>` and `<meta name="description">`.
- Open Graph + Twitter card tags.
- Canonical URL.
- `sitemap.xml` auto-generated.
- `robots.txt` with sitemap reference.
