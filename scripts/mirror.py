#!/usr/bin/env python3
"""
Mirror walkerbldgcorp.com pages into 11ty templates.
- Downloads all CSS/JS/font/image assets referenced by the live HTML.
- Rewrites all absolute URLs (walkerbldgcorp.com + bk2.03c.myftpupload.com staging) to local /assets/* paths.
- Saves the resulting HTML as Nunjucks templates under src/content/pages/.
"""
import os, re, sys, hashlib, urllib.parse, urllib.request, pathlib

ROOT = pathlib.Path("/Users/albertvolkman/Sites/walkerbldgcorp.com")
ASSETS = ROOT / "src" / "assets" / "vendor"
PAGES_DIR = ROOT / "src" / "content" / "pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)

LIVE_HOSTS = ("walkerbldgcorp.com", "bk2.03c.myftpupload.com")
PAGES = [
    ("home", "https://walkerbldgcorp.com/"),
    ("about", "https://walkerbldgcorp.com/about/"),
    ("services", "https://walkerbldgcorp.com/services/"),
    ("equipment", "https://walkerbldgcorp.com/equipment/"),
    ("careers", "https://walkerbldgcorp.com/careers/"),
    ("contact", "https://walkerbldgcorp.com/contact/"),
]

NAV_REWRITES = {
    "https://bk2.03c.myftpupload.com/": "/",
    "https://walkerbldgcorp.com/": "/",
}

# Cache for downloaded assets: original-url -> local-path-relative-to-/assets/
asset_map: dict[str, str] = {}
visited: set[str] = set()


def download(url: str) -> bytes | None:
    if url.startswith("//"):
        url = "https:" + url
    if url.startswith("/"):
        url = "https://walkerbldgcorp.com" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except Exception as e:
        print(f"  ! failed: {url}  ({e})", file=sys.stderr)
        return None


SUBDIRS = {"css": "css", "js": "js", "font": "fonts", "img": "img", "video": "video", "audio": "audio"}


def local_path_for(url: str, kind: str) -> tuple[pathlib.Path, str]:
    """Pick a local filesystem path + URL path for an asset URL."""
    parsed = urllib.parse.urlparse(url)
    base_name = os.path.basename(parsed.path) or "index"
    name, ext = os.path.splitext(base_name)
    if not ext:
        ext = "." + kind
    qhash = ""
    if parsed.query:
        qhash = "-" + hashlib.md5(parsed.query.encode()).hexdigest()[:6]
    fname = f"{name}{qhash}{ext}"
    subdir = SUBDIRS[kind]
    local_fs = ASSETS / subdir / fname
    local_url = f"/assets/vendor/{subdir}/{fname}"
    return local_fs, local_url


def ensure_asset_kind(url: str, kind: str) -> str | None:
    """Wrapper for ensure_asset() that accepts video/audio kinds too."""
    return ensure_asset(url, kind)


def ensure_asset(url: str, kind: str) -> str | None:
    """Download an asset (if not already) and return its local URL path."""
    if url in asset_map:
        return asset_map[url]
    if url in visited:
        return None
    visited.add(url)

    abs_url = url
    if abs_url.startswith("//"):
        abs_url = "https:" + abs_url
    parsed = urllib.parse.urlparse(abs_url)
    if parsed.scheme not in ("http", "https") and parsed.netloc:
        return None

    data = download(abs_url)
    if data is None:
        return None

    fs, local_url = local_path_for(abs_url, kind)
    fs.parent.mkdir(parents=True, exist_ok=True)

    # For CSS files, rewrite nested url(...) references to local
    if kind == "css":
        text = data.decode("utf-8", errors="replace")
        text = rewrite_css(text, abs_url)
        data = text.encode("utf-8")

    fs.write_bytes(data)
    asset_map[abs_url] = local_url
    print(f"  + {abs_url}\n    -> {local_url}")
    return local_url


def rewrite_css(text: str, css_url: str) -> str:
    """Find url(...) references in a CSS file, download them, rewrite to local paths."""
    def fix(match):
        raw = match.group(1).strip("\"'")
        if raw.startswith("data:") or raw.startswith("#"):
            return match.group(0)
        abs_ref = urllib.parse.urljoin(css_url, raw)
        # determine kind
        lower = abs_ref.lower().split("?")[0]
        if any(lower.endswith(ext) for ext in (".woff", ".woff2", ".ttf", ".otf", ".eot")):
            kind = "font"
        elif any(lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")):
            kind = "img"
        else:
            return match.group(0)
        local = ensure_asset(abs_ref, kind)
        if not local:
            return match.group(0)
        # URL inside CSS file at /assets/vendor/css/x.css needs ../font/foo
        # but using site-absolute local URL is safer
        return f"url({local})"

    return re.sub(r"url\(([^)]+)\)", fix, text)


def process_html(slug: str, page_url: str):
    print(f"\n== {slug} ({page_url}) ==")
    raw = download(page_url)
    if raw is None:
        print(f"  !! could not download page")
        return
    html = raw.decode("utf-8", errors="replace")

    # 1. Stylesheets: <link rel="stylesheet" href="...">
    def rewrite_link(m):
        url = m.group(1)
        if any(h in url for h in LIVE_HOSTS):
            local = ensure_asset(url, "css")
            if local:
                return m.group(0).replace(url, local)
        return m.group(0)
    html = re.sub(r'<link[^>]+rel=[\'"]stylesheet[\'"][^>]+href=[\'"]([^\'"]+)[\'"][^>]*>', rewrite_link, html)
    # also handle href before rel
    html = re.sub(r'<link[^>]+href=[\'"]([^\'"]+\.css[^\'"]*)[\'"][^>]+rel=[\'"]stylesheet[\'"][^>]*>', rewrite_link, html)

    # 2. Scripts: <script src="...">
    def rewrite_script(m):
        url = m.group(1)
        if any(h in url for h in LIVE_HOSTS):
            local = ensure_asset(url, "js")
            if local:
                return m.group(0).replace(url, local)
        return m.group(0)
    html = re.sub(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', rewrite_script, html)

    # 3. Images: src= and srcset= attributes
    def rewrite_img_src(m):
        url = m.group(1)
        if any(h in url for h in LIVE_HOSTS):
            local = ensure_asset(url, "img")
            if local:
                return m.group(0).replace(url, local)
        return m.group(0)
    html = re.sub(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', rewrite_img_src, html)

    # srcset list
    def rewrite_srcset(m):
        srcset = m.group(1)
        parts = [p.strip() for p in srcset.split(",")]
        out = []
        for p in parts:
            tokens = p.split()
            if not tokens: continue
            url = tokens[0]
            if any(h in url for h in LIVE_HOSTS):
                local = ensure_asset(url, "img")
                if local:
                    tokens[0] = local
            out.append(" ".join(tokens))
        return f'srcset="{", ".join(out)}"'
    html = re.sub(r'srcset=[\'"]([^\'"]+)[\'"]', rewrite_srcset, html)

    # 4. <link rel="icon" / "apple-touch-icon" / "preload" as="image" / "preload" as="font">
    def rewrite_link_other(m):
        url = m.group(1)
        if any(h in url for h in LIVE_HOSTS):
            lower = url.lower().split("?")[0]
            if any(lower.endswith(ext) for ext in (".png",".jpg",".jpeg",".gif",".svg",".webp",".ico")):
                kind = "img"
            elif any(lower.endswith(ext) for ext in (".woff",".woff2",".ttf",".otf",".eot")):
                kind = "font"
            else:
                return m.group(0)
            local = ensure_asset(url, kind)
            if local: return m.group(0).replace(url, local)
        return m.group(0)
    html = re.sub(r'<link[^>]+href=[\'"]([^\'"]+)[\'"]', rewrite_link_other, html)

    # 5. CSS files referenced via inline <style> blocks may contain url(...)
    def rewrite_inline_style_block(m):
        css = m.group(1)
        # treat inline style as if its base is the page URL
        return f"<style{m.group(0)[6:m.group(0).find('>')+1]-0}"  # placeholder; we'll do real below
    # simpler: regex over url() patterns in the whole document
    def fix_inline_url(m):
        raw = m.group(1).strip("\"'")
        if raw.startswith("data:") or raw.startswith("#") or raw.startswith("/assets/"):
            return m.group(0)
        if not any(h in raw for h in LIVE_HOSTS) and not raw.startswith("http"):
            return m.group(0)
        abs_ref = raw if raw.startswith("http") else urllib.parse.urljoin(page_url, raw)
        if not any(h in abs_ref for h in LIVE_HOSTS):
            return m.group(0)
        lower = abs_ref.lower().split("?")[0]
        if any(lower.endswith(ext) for ext in (".png",".jpg",".jpeg",".gif",".svg",".webp")):
            kind = "img"
        elif any(lower.endswith(ext) for ext in (".woff",".woff2",".ttf",".otf",".eot")):
            kind = "font"
        else:
            return m.group(0)
        local = ensure_asset(abs_ref, kind)
        return f"url({local})" if local else m.group(0)
    html = re.sub(r"url\(([^)]+)\)", fix_inline_url, html)

    # 6a. <video src>, <source src>, <audio src>, <track src> tags
    def rewrite_media_src(m):
        url = m.group(2)
        if any(h in url for h in LIVE_HOSTS):
            lower = url.lower().split("?")[0]
            if any(lower.endswith(ext) for ext in (".mp4", ".webm", ".mov", ".m4v")):
                kind = "video"
            elif any(lower.endswith(ext) for ext in (".mp3", ".ogg", ".wav", ".m4a")):
                kind = "audio"
            else:
                return m.group(0)
            local = ensure_asset_kind(url, kind)
            if local:
                return m.group(0).replace(url, local)
        return m.group(0)
    html = re.sub(r'<(video|source|audio|track)[^>]+src=[\'"]([^\'"]+)[\'"]', rewrite_media_src, html)

    # 6b. Elementor stores video background URLs inside data-settings JSON
    # (HTML-encoded as &quot; and with escaped slashes). Catch both forms.
    def rewrite_encoded_video(m):
        url = m.group(0)
        # un-escape backslash-slashes if present
        plain = url.replace("\\/", "/")
        if not any(h in plain for h in LIVE_HOSTS):
            return url
        local = ensure_asset_kind(plain, "video")
        if not local:
            return url
        # re-apply the same escape style we found
        return local.replace("/", "\\/") if "\\/" in url else local
    html = re.sub(
        r"https:(?:\\?/){2}(?:bk2\.03c\.myftpupload\.com|walkerbldgcorp\.com)(?:\\?/[^\"'\s<>}]+)+\.(?:mp4|webm|mov|m4v|mp3|ogg|wav|m4a)",
        rewrite_encoded_video,
        html,
    )

    # 7. Nav: replace any walkerbldgcorp.com / bk2 absolute links to relative
    for src_host, repl in NAV_REWRITES.items():
        html = html.replace(src_host, repl)

    # 7. Strip GoDaddy WSIMG analytics block (third-party tracking, won't work on CF Pages).
    html = re.sub(
        r"<script>\s*'undefined'\s*===\s*typeof\s+_trfq.*?img1\.wsimg\.com/traffic-assets/[^>]+></script>",
        "<!-- GoDaddy WSIMG analytics removed -->",
        html,
        flags=re.DOTALL,
    )

    # 8. Strip wp-emoji loader (references s.w.org CDN; site has no emoji content).
    html = re.sub(
        r'<script id="wp-emoji-settings"[^>]*>.*?</script>\s*<script type="module">.*?</script>',
        "<!-- wp-emoji loader removed -->",
        html,
        flags=re.DOTALL,
    )

    # 9. Save as Nunjucks template
    permalink = "/" if slug == "home" else f"/{slug}/"
    frontmatter = (
        "---\n"
        f"permalink: {permalink}\n"
        f"eleventyExcludeFromCollections: false\n"
        "---\n"
    )
    out_path = PAGES_DIR / f"{slug}.njk"
    out_path.write_text(frontmatter + html)
    print(f"  => wrote {out_path}")


def main():
    for slug, url in PAGES:
        try:
            process_html(slug, url)
        except Exception as e:
            print(f"!! {slug} failed: {e}", file=sys.stderr)
            raise
    print(f"\nDone. {len(asset_map)} assets cached.")
    # Format the freshly-written page templates so they stay in line with the repo's Prettier config.
    print("\nFormatting page templates with Prettier...")
    import subprocess
    subprocess.run(
        ["npx", "prettier", "--write", "src/content/pages/"],
        cwd=ROOT,
        check=False,
    )


if __name__ == "__main__":
    main()
