import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.generate_making_sense import generate, load_spec


HUB = '''<!doctype html><html><body>
<a class="featured-issue" href="/making-sense/old-issue">
  <img src="/making-sense/old-issue/hero.jpg" alt="Old hero">
  <div class="featured-issue-copy">
    <div class="kicker">Latest · September 23, 2026</div>
    <h2>Old Issue</h2><p>Old subtitle.</p>
    <div class="read">About a 4 minute read →</div>
  </div>
</a>
<div class="section-label" id="recent-label">Previous articles</div>
<div class="recent-grid">
      <a class="recent-card" href="/making-sense/rec-a">
        <img class="recent-card-image" src="/making-sense/rec-a/a.jpg" alt="A">
        <div class="recent-card-body">
          <div class="issue-num">September 16, 2026</div>
          <h2>Recent A</h2>
          <p>Dek A.</p>
        </div>
      </a>
      <a class="recent-card" href="/making-sense/rec-b">
        <div class="recent-card-body">
          <div class="issue-num">September 9, 2026</div>
          <h2>Recent B</h2>
          <p>Dek B.</p>
        </div>
      </a>
      <a class="recent-card" href="/making-sense/rec-c">
        <img class="recent-card-image" src="/making-sense/rec-c/c.jpg" alt="C">
        <div class="recent-card-body">
          <div class="issue-num">September 2, 2026</div>
          <h2>Recent C</h2>
          <p>Dek C.</p>
        </div>
      </a>
</div>
<div class="section-label" id="archive-label">Earlier issues</div>
<div class="issue-list">
      <a class="issue-row" href="/making-sense/older"><span class="issue-row-title">Older Issue</span><span class="issue-row-date">August 19, 2026</span></a>
</div>
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
            self.assertIn("Read the full issue", distribution)
            self.assertIn('class="featured-issue" href="/making-sense/new-issue"', hub)
            self.assertNotIn('class="featured-issue" href="/making-sense/old-issue"', hub)
            recent_hrefs = re.findall(r'class="recent-card" href="([^"]+)"', hub)
            self.assertEqual(recent_hrefs, [
                "/making-sense/old-issue",
                "/making-sense/rec-a",
                "/making-sense/rec-b",
            ])
            self.assertIn("Old subtitle.", hub)
            self.assertEqual(len(re.findall(r'class="recent-card"', hub)), 3)
            issue_list = hub[hub.find('id="archive-label"'):]
            list_hrefs = re.findall(r'class="issue-row" href="([^"]+)"', issue_list)
            self.assertEqual(list_hrefs, ["/making-sense/rec-c", "/making-sense/older"])
            self.assertIn("Recent C", issue_list)
            self.assertIn("September 2, 2026", issue_list)
            self.assertNotIn('class="recent-card" href="/making-sense/rec-c"', hub)
            self.assertNotIn('class="featured-issue" href="/making-sense/rec-a"', hub)
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
