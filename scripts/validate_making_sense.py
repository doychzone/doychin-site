#!/usr/bin/env python3
"""Validate a Making Sense issue directory before preview approval."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class IssueParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.description = ""
        self.canonical = ""
        self.images: list[tuple[str, str | None]] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs}
        tag = tag.lower()

        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = (values.get("name") or "").lower()
            content = values.get("content") or ""
            if name == "description":
                self.description = content.strip()
            if name == "robots" and "noindex" in content.lower():
                self.noindex = True
        elif tag == "link":
            rel = (values.get("rel") or "").lower().split()
            if "canonical" in rel:
                self.canonical = (values.get("href") or "").strip()
        elif tag == "img":
            self.images.append(((values.get("src") or "").strip(), values.get("alt")))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def validate(issue_dir: Path) -> list[str]:
    errors: list[str] = []
    index_file = issue_dir / "index.html"

    if not index_file.is_file():
        return [f"{issue_dir}: missing index.html"]

    parser = IssueParser()
    parser.feed(index_file.read_text(encoding="utf-8"))

    if not parser.title:
        errors.append("missing non-empty <title>")
    if not parser.description:
        errors.append("missing non-empty meta description")
    if not parser.canonical:
        errors.append("missing canonical link")
    else:
        parsed = urlparse(parser.canonical)
        expected_path = f"/making-sense/{issue_dir.name}/"
        if parsed.scheme != "https" or parsed.path.rstrip("/") + "/" != expected_path:
            errors.append(
                f"canonical must be an HTTPS URL with path {expected_path}; "
                f"found {parser.canonical!r}"
            )

    if parser.noindex:
        errors.append("production issue must not contain robots noindex")

    local_assets = [
        path
        for path in issue_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif"}
    ]
    if not local_assets:
        errors.append("missing local editorial image")

    if not parser.images:
        errors.append("article contains no <img> element")
    for src, alt in parser.images:
        if not src:
            errors.append("image has an empty src")
        if alt is None or not alt.strip():
            errors.append(f"image {src or '[unknown]'} is missing descriptive alt text")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_making_sense.py ISSUE_DIR [ISSUE_DIR ...]", file=sys.stderr)
        return 2

    failed = False
    for raw_dir in sys.argv[1:]:
        issue_dir = Path(raw_dir)
        errors = validate(issue_dir)
        if errors:
            failed = True
            print(f"::error title=Making Sense validation failed::{issue_dir}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK: {issue_dir}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
