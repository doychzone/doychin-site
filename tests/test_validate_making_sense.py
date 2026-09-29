import tempfile
import unittest
from pathlib import Path

from scripts.validate_making_sense import validate


def write_issue(root: Path, slug: str) -> Path:
    issue_dir = root / slug
    issue_dir.mkdir()
    (issue_dir / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <title>Example | Making Sense</title>
  <meta name="description" content="Example description">
  <link rel="canonical" href="https://doychin.com/making-sense/{slug}/">
</head>
<body><main>Example</main></body>
</html>
""",
        encoding="utf-8",
    )
    return issue_dir


class ValidateMakingSenseTests(unittest.TestCase):
    def test_legacy_issues_keep_their_image_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            for slug in (
                "issue-zero",
                "the-secret-power-of-your-minimum",
                "who-will-pick-up-when-you-call",
                "your-workout-is-not-the-whole-day",
            ):
                with self.subTest(slug=slug):
                    issue_dir = write_issue(Path(temp_dir), slug)
                    self.assertEqual(validate(issue_dir), [])

    def test_new_issue_still_requires_an_editorial_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            issue_dir = write_issue(Path(temp_dir), "new-issue")

            self.assertEqual(
                validate(issue_dir),
                ["missing local editorial image", "article contains no <img> element"],
            )


if __name__ == "__main__":
    unittest.main()
