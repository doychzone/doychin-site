#!/usr/bin/env python3
"""Generate a review-ready Making Sense issue from an approved package."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote


REQUIRED_FIELDS = (
    "issue_number",
    "title",
    "subtitle",
    "slug",
    "publication_date",
    "read_time",
    "meta_description",
    "og_description",
    "image_alt",
    "body_file",
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def fail(message: str) -> None:
    raise ValueError(message)


def load_spec(path: Path) -> dict:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Cannot read issue package {path}: {exc}")

    missing = [field for field in REQUIRED_FIELDS if not spec.get(field)]
    if missing:
        fail(f"Missing required fields: {', '.join(missing)}")
    if not SLUG_RE.fullmatch(str(spec["slug"])):
        fail("slug must contain only lowercase letters, numbers and hyphens")
    try:
        publication_date = date.fromisoformat(str(spec["publication_date"]))
    except ValueError:
        fail("publication_date must use YYYY-MM-DD")
    if publication_date.weekday() != 2:
        fail("publication_date must be a Wednesday")

    kit = spec.get("kit", {})
    if not all(kit.get(field) for field in ("subject", "preview_text", "teaser")):
        fail("kit must include subject, preview_text and teaser")
    if len(kit["teaser"]) not in range(2, 5):
        fail("kit.teaser must contain 2 to 4 short paragraphs")
    if not isinstance(kit.get("cta"), str) or not kit["cta"].strip():
        fail("kit.cta must be a non-empty string")

    buffer = spec.get("buffer", {})
    if not buffer or not all(isinstance(value, str) and value.strip() for value in buffer.values()):
        fail("buffer must contain at least one non-empty channel draft")
    return spec


def human_date(raw: str) -> str:
    parsed = date.fromisoformat(raw)
    return f"{parsed.strftime('%A, %B')} {parsed.day}, {parsed.year}"


def short_date(raw: str) -> str:
    parsed = date.fromisoformat(raw)
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_sources(sources: list[dict]) -> str:
    if not sources:
        return ""
    items = []
    for source in sources:
        title = esc(source.get("title", "Source"))
        url = esc(source.get("url", ""))
        note = esc(source.get("note", ""))
        suffix = f", {note}" if note else ""
        items.append(
            f'  <li><a href="{url}" target="_blank" rel="noopener">{title}</a>{suffix}</li>'
        )
    return '<div class="sources"><strong>Sources</strong><ol>\n' + "\n".join(items) + "\n</ol></div>"


def render_article(spec: dict, image_name: str, body_html: str) -> str:
    slug = spec["slug"]
    canonical = f"https://www.doychin.com/making-sense/{slug}"
    title = esc(spec["title"])
    subtitle = esc(spec["subtitle"])
    image_url = f"{canonical}/{esc(image_name)}"
    source_block = render_sources(spec.get("sources", []))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | Making Sense</title>
<meta name="description" content="{esc(spec['meta_description'])}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{esc(spec['og_description'])}"><meta property="og:image" content="{image_url}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Libre+Baskerville:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/making-sense/making-sense.css">
</head>
<body>
<nav class="site-nav" aria-label="Primary navigation"><div class="wrap nav-inner"><a class="brand" href="/">Doychin<span> Karshovski</span></a><div class="nav-links"><a href="/">Home</a><a href="/#about">About</a><a href="/#ahead">Stay Ahead</a><a class="nav-primary" href="/making-sense" aria-current="page">Making Sense</a><a class="nav-cta" href="mailto:doych@doychzone.com?subject=Website%20Inquiry">Contact</a></div></div></nav>
<header class="article-hero" style="position:relative;overflow:hidden"><img src="/making-sense/{esc(slug)}/{esc(image_name)}" alt="{esc(spec['image_alt'])}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"><div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.72),rgba(0,0,0,.16))"></div><div class="hero-copy hero-inner" style="position:relative"><div class="kicker">Making Sense</div><h1>{title}</h1><p class="dek">{subtitle}</p><div class="meta"><span>{esc(human_date(spec['publication_date']))}</span><span>{esc(spec['read_time'])}</span></div></div></header>
<main class="article">
{body_html.strip()}

<div class="reader-response">
  <p><strong>Was this useful?</strong></p>
  <p>Did it help you make a little more sense of the noise and lead you to action?</p>
  <p><a href="mailto:doych@doychzone.com?subject=Making%20Sense%20%E2%80%94%20{quote(str(spec['title']))}">Reply and tell me.</a> I read every reply.</p>
  <p>If you know someone who would find this useful, please forward it to them.</p>
</div>
<div class="subscribe-cta subscribe-cta-article"><div class="subscribe-copy"><h2>One focused idea every Wednesday.</h2><p>Health, longevity and human performance without the noise. Subscribe to receive Making Sense by email.</p></div><div class="subscribe-form"><script async data-uid="eb7e3ea366" src="https://making-sense.kit.com/eb7e3ea366/index.js"></script></div></div>
<div class="signoff">Stay curious. But do what makes sense.<strong>Doych ☂️</strong></div>
{source_block}
<div class="disclaimer">Making Sense shares educational information, not individual medical advice.</div>
<div class="archive-cta"><div><strong>Making Sense</strong><br><span style="color:var(--muted)">One subject at a time. Less noise. More clarity. In under five minutes.</span></div><a class="btn" href="/making-sense">See all articles</a></div>
</main>
</body></html>
'''


def render_featured(spec: dict) -> str:
    return f'''<a class="featured-hero" href="/making-sense/{esc(spec['slug'])}" style="background-image:linear-gradient(90deg,rgba(0,0,0,.72),rgba(0,0,0,.16)),url('/making-sense/{esc(spec['slug'])}/{esc(spec['image_filename'])}')">
  <div class="hero-copy hero-inner">
    <div class="kicker">Latest · {esc(short_date(spec['publication_date']))}</div>
    <h1>{esc(spec['title'])}</h1>
    <p class="dek">{esc(spec['subtitle'])}</p>
    <div class="meta"><span>{esc(spec['read_time'])} →</span></div>
  </div>
</a>'''


def archive_card_from_featured(featured: str) -> str:
    def extract(pattern: str, default: str = "") -> str:
        match = re.search(pattern, featured, flags=re.DOTALL)
        return match.group(1).strip() if match else default

    href = extract(r'href="([^"]+)"')
    kicker = extract(r'<div class="kicker">(.*?)</div>')
    kicker = re.sub(r"^Latest(?: issue)?\s*·\s*", "", kicker)
    kicker = re.sub(r"^Issue (?:Zero|\d+)\s*·\s*", "", kicker)
    title = extract(r"<h1>(.*?)</h1>")
    dek = extract(r'<p class="dek">(.*?)</p>')
    read_time = extract(r'<div class="meta"><span>(.*?)</span>')
    if not all((href, kicker, title, dek, read_time)):
        fail("Could not read the current featured issue from making-sense/index.html")
    return f'      <a class="issue-card" href="{href}"><div class="issue-num">{kicker}</div><h2>{title}</h2><p>{dek}</p><div class="read">{read_time}</div></a>'


def update_hub(hub_path: Path, spec: dict) -> None:
    hub = hub_path.read_text(encoding="utf-8")
    match = re.search(r'<a class="featured-hero".*?</a>', hub, flags=re.DOTALL)
    if not match:
        fail("Current featured issue was not found in making-sense/index.html")
    old_featured = match.group(0)
    new_href = f'/making-sense/{spec["slug"]}'
    if new_href in hub:
        fail(f"Hub already contains {new_href}")
    hub = hub[: match.start()] + render_featured(spec) + hub[match.end() :]
    old_card = archive_card_from_featured(old_featured)
    archive_marker = '<div class="section-label" id="archive-label">Previous articles</div>'
    marker_pos = hub.find(archive_marker)
    grid_pos = hub.find('<div class="issue-grid">', marker_pos)
    if marker_pos < 0 or grid_pos < 0:
        fail("Previous articles grid was not found in making-sense/index.html")
    insert_at = grid_pos + len('<div class="issue-grid">')
    hub = hub[:insert_at] + "\n" + old_card + hub[insert_at:]
    hub_path.write_text(hub, encoding="utf-8")


def render_distribution(spec: dict) -> str:
    canonical = f"https://www.doychin.com/making-sense/{spec['slug']}"
    kit = spec["kit"]
    lines = [
        f"# Distribution package - {spec['title']}",
        "",
        "## Kit email",
        "",
        f"**Subject:** {kit['subject']}",
        "",
        f"**Preview text:** {kit['preview_text']}",
        "",
        *[f"{paragraph}\n" for paragraph in kit["teaser"]],
        f"**CTA:** [{kit['cta']}]({canonical})",
        "",
        "## Buffer drafts",
        "",
    ]
    for channel, copy in spec["buffer"].items():
        lines.extend((f"### {channel}", "", copy.replace("{{canonical_url}}", canonical), ""))
    lines.extend(("## Release gate", "", "Keep Kit and Buffer paused until the production URL has been verified.", ""))
    return "\n".join(lines)


def generate(repo: Path, spec_path: Path, image_path: Path, update_archive: bool) -> tuple[Path, Path]:
    spec = load_spec(spec_path)
    if image_path.suffix.lower() not in IMAGE_SUFFIXES or not image_path.is_file():
        fail("--image must point to an existing JPG, PNG, WebP or AVIF file")
    body_path = (spec_path.parent / spec["body_file"]).resolve()
    if not body_path.is_file():
        fail(f"body_file does not exist: {body_path}")
    body_html = body_path.read_text(encoding="utf-8")
    if not re.search(r"<(p|h2|blockquote|div)\b", body_html):
        fail("body_file must contain article HTML")
    if re.search(r"<(script|iframe)\b|\son[a-z]+\s*=", body_html, flags=re.IGNORECASE):
        fail("body_file must not contain scripts, iframes or inline event handlers")

    image_name = image_path.name
    spec["image_filename"] = image_name
    issue_dir = repo / "making-sense" / spec["slug"]
    if issue_dir.exists():
        fail(f"Issue directory already exists: {issue_dir}")
    issue_dir.mkdir(parents=True)
    shutil.copy2(image_path, issue_dir / image_name)
    (issue_dir / "index.html").write_text(render_article(spec, image_name, body_html), encoding="utf-8")

    package_dir = repo / "publishing" / "making-sense"
    package_dir.mkdir(parents=True, exist_ok=True)
    package_path = package_dir / f"{spec['slug']}.md"
    package_path.write_text(render_distribution(spec), encoding="utf-8")
    if update_archive:
        update_hub(repo / "making-sense" / "index.html", spec)
    return issue_dir, package_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="Approved issue package JSON")
    parser.add_argument("--image", required=True, type=Path, help="Approved editorial image")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--update-hub", action="store_true", help="Promote the issue on the Making Sense archive page")
    args = parser.parse_args()
    try:
        issue_dir, package = generate(args.repo.resolve(), args.spec.resolve(), args.image.resolve(), args.update_hub)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Created {issue_dir}")
    print(f"Created {package}")
    print("Next: run validation, review the diff, then open a draft pull request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
