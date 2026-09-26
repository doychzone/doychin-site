# Making Sense publishing contract

This repository is the technical source of truth for the canonical Making Sense web publication.

## Production system

- Repository: `doychzone/doychin-site`
- Production branch: `main`
- Vercel project: `doychin-site`
- Issue path: `making-sense/<slug>/index.html`
- Issue assets: stored inside the same issue directory
- Public canonical path: `/making-sense/<slug>/`
- Timezone: `Europe/Sofia`

## Required issue package

Every new issue pull request must contain:

- `making-sense/<slug>/index.html`
- at least one local editorial image in the issue directory
- a permanent canonical URL
- a non-empty meta description
- a title
- descriptive image alt text
- the approved publication date
- an update to the Making Sense hub when the issue should appear in the archive

## Editorial approvals

The pull request description records these gates:

- article approved
- image approved for public use
- Vercel Preview checked on desktop
- Vercel Preview checked on mobile
- links and images checked
- canonical metadata checked
- Kit teaser prepared
- Buffer copy prepared

A pull request is not ready to merge while any required gate remains unchecked.

## Agent boundaries

- Claude prepares the editorial draft.
- Grok returns red-team observations and channel-specific social options.
- ChatGPT packages the issue, prepares metadata, Kit teaser and Buffer copy, and performs QA.
- GrokBot or another repository agent creates the branch, files and pull request.
- Repository agents must not push directly to `main`, merge their own pull request or promote a deployment without the required approval.

## Distribution rule

The Vercel page is the only canonical web publication.

Kit sends a short teaser email with one primary call to action linking to the canonical page. Kit must not publish a duplicate public post.

Buffer posts must use the verified production URL. Drafts may be created earlier, but scheduling or publishing waits until the production health check succeeds.

## Release rule

A Vercel Preview is created from the issue branch. Production remains unchanged until the pull request is approved and released during the Tuesday publication window.

If the production page fails verification, Kit and Buffer remain paused.
