import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_making_sense import generate, load_spec


HUB = '''<!doctype html><html><body>
<a class="featured-hero" href="/making-sense/old-issue">
  <div class="hero-copy hero-inner">
    <div class="kicker">Latest · September 23, 2026</div>
    <h1>Old Issue</h1><p class="dek">Old subtitle.</p>
    <div class="meta"><span>About a 4 minute read →</span></div>
  </div>
</a>
<div class="section-label" id="archive-label">Previous articles</div>
<div class="issue-grid"></div>
</body></html>'''


def valid_spec() -> dict:
    return {
        "issue_number": 6,
        "title": "New Issue",
        "subtitle": "New subtitle.",
        "slug": "new-issue",
        "publication_date": "2026-09-30",
        "read_time": "About a 5 minute read",
        "meta_description": "Meta description.",
        "og_description": "Social description.",
        "image_alt": "Editorial image description",
        "body_file": "body.html",
        "sources": [],
        "kit": {
            "subject": "Subject",
            "preview_text": "Preview",
            "teaser": ["First short paragraph.", "Second short paragraph."],
            "cta": "Read the full issue",
        },
        "buffer": {"LinkedIn": "Read this: {{canonical_url}}"},
    }


class GeneratorTests(unittest.TestCase):
    def test_generates_issue_distribution_and_archive_update(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "making-sense").mkdir()
            (repo / "making-sense" / "index.html").write_text(HUB, encoding="utf-8")
            spec_path = repo / "issue.json"
            spec_path.write_text(json.dumps(valid_spec()), encoding="utf-8")
            (repo / "body.html").write_text("<p>Final article.</p>", encoding="utf-8")
            image = repo / "approved.jpg"
            image.write_bytes(b"test image")

            issue_dir, package = generate(repo, spec_path, image, True)

            article = (issue_dir / "index.html").read_text(encoding="utf-8")
            hub = (repo / "making-sense" / "index.html").read_text(encoding="utf-8")
            distribution = package.read_text(encoding="utf-8")
            self.assertIn("https://www.doychin.com/making-sense/new-issue", article)
            self.assertIn('alt="Editorial image description"', article)
            self.assertIn('<div class="kicker">Making Sense</div>', article)
            self.assertNotIn("Issue 6", article)
            self.assertIn('/making-sense/new-issue', hub)
            self.assertIn('/making-sense/old-issue', hub)
            self.assertIn("Latest · September 30, 2026", hub)
            self.assertIn('<div class="issue-num">September 23, 2026</div>', hub)
            self.assertIn("Read the full issue", distribution)
            self.assertIn("https://www.doychin.com/making-sense/new-issue", distribution)

    def test_rejects_long_kit_teaser(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "issue.json"
            spec = valid_spec()
            spec["kit"]["teaser"] = ["one", "two", "three", "four", "five"]
            path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "2 to 4"):
                load_spec(path)

    def test_rejects_non_wednesday_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "issue.json"
            spec = valid_spec()
            spec["publication_date"] = "2026-09-29"
            path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Wednesday"):
                load_spec(path)

    def test_rejects_existing_issue_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "making-sense" / "new-issue").mkdir(parents=True)
            spec_path = repo / "issue.json"
            spec_path.write_text(json.dumps(valid_spec()), encoding="utf-8")
            (repo / "body.html").write_text("<p>Final article.</p>", encoding="utf-8")
            image = repo / "approved.jpg"
            image.write_bytes(b"test image")
            with self.assertRaisesRegex(ValueError, "already exists"):
                generate(repo, spec_path, image, False)


if __name__ == "__main__":
    unittest.main()
