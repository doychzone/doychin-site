# Making Sense issue generator

The generator turns one approved issue package and one approved editorial image into a review-ready branch. It does not publish, merge, schedule Kit or activate Buffer.

## Inputs

Copy these two files into a working folder:

- `templates/making-sense/issue.example.json`
- `templates/making-sense/body.example.html`

Complete the JSON fields, write the final article body in the HTML file and place the approved image beside them. The Kit section is intentionally a short teaser with one CTA, not a copy of the full article.

## Generate

From the repository root:

```bash
python3 scripts/generate_making_sense.py path/to/issue.json \
  --image path/to/approved-photo.jpg \
  --update-hub
```

This creates:

- `making-sense/<slug>/index.html`
- a copy of the approved image in the issue directory
- `publishing/making-sense/<slug>.md` with Kit and Buffer drafts
- an updated featured issue and archive card in `making-sense/index.html`

## Safety gates

1. Run `python3 scripts/validate_making_sense.py making-sense/<slug>`.
2. Run `python3 -m unittest discover -s tests`.
3. Review the generated files and create a draft pull request.
4. Check the Vercel Preview on desktop and mobile.
5. Merge only in the approved Tuesday release window.
6. Verify the production URL before scheduling Kit or activating Buffer.

The generator stops if the slug is invalid, the issue directory already exists, the image is unsupported, required fields are missing, the Kit teaser is not 2–4 paragraphs, or the archive cannot be updated safely.
