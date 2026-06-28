# Jolly Follies

**Live: https://cornishollie.github.io/jollyfollies/**

A modern restoration of **jollyfollies.com** — the travel diary of an overland drive
from Land's End, Cornwall to Sydney, Australia in a 1990s Land Rover Defender 110
("DINO"), in aid of VSO. The original was hand-built in Dreamweaver as a teenager;
the live site lapsed and survived only in the Internet Archive. This rebuild keeps
the identity and the words, and replaces the plumbing with a fast, responsive,
maintainable static site.

> **The words are kept verbatim.** Diary text was migrated from the archive exactly
> as written — period charm and the odd typo included. Only broken markup was fixed.

## Stack

- [Astro](https://astro.build) static site (zero JS shipped except a tiny theme/menu toggle)
- Markdown content collection for the diary (`src/content/diary/`)
- Light/dark theme, RSS feed, sitemap, OpenGraph/Twitter cards, 404 page
- Deployed to GitHub Pages via GitHub Actions

## Project layout

```
src/
  content/diary/        # one Markdown file per diary entry (the source of truth)
  content/config.ts     # diary front-matter schema
  layouts/BaseLayout.astro
  components/            # Header, Footer, DiaryCard, DefenderLogo (SVG)
  pages/                # index, about, route, vehicle, jogle, gallery, contact, 404
    diary/index.astro   # the diary index (grouped by year)
    diary/[...slug].astro  # an individual entry, with prev/next
    rss.xml.js          # the feed
  styles/global.css     # design tokens (palette pulled from the original) + base styles
public/
  images/               # brand + recovered photos
  diary-media/          # optimised photos referenced by entries (generated)
photos/                 # drop full-size photos here, then `npm run photos`
scripts/
  convert_diary.py      # re-generate diary Markdown from the Wayback archive
  optimize-photos.mjs   # resize + optimise photos into public/diary-media/
```

## Develop locally

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # static output to dist/
npm run preview    # serve the built site
```

Requires Node 20+.

## Add a diary entry

Create `src/content/diary/NNN-a-short-slug.md`:

```markdown
---
title: 'A Memorable Day'
date: 2009-06-14
order: 70
original_url: 'http://www.jollyfollies.com/Diary/...'   # optional
---

Your words here. Plain Markdown. Paragraphs, **bold**, *italic*, [links](https://…).
```

- The URL is `/diary/a-short-slug/` (the leading `NNN-` is stripped).
- Entries are ordered by `date` (newest first); `order` is a tiebreaker.
- It appears automatically on the home page, the diary index, and in the RSS feed.

## Add photos

```bash
# 1. drop full-size images into photos/
# 2. optimise them into public/diary-media/
npm run photos
```

Then reference one in an entry:

```markdown
![A short caption](/diary-media/P1120004.jpg)
```

Many entries contain `(photo coming soon: NAME)` markers where an image used to be.
Name your photo to match, run `npm run photos`, and swap the marker line for the
image syntax above. See `photos/README.md` for the gallery convention too.

## Re-running the archive conversion

The diary Markdown was generated from the Wayback archive (kept in
`../jollyfollies-archive/`). To regenerate:

```bash
npm run convert
```

## Deploy (GitHub Pages)

The site is already live at **https://cornishollie.github.io/jollyfollies/**, served
from the `gh-pages` branch. To redeploy after changes:

```bash
npm run deploy        # builds and force-pushes dist/ to the gh-pages branch
```

### Switching to CI deploys (optional, recommended)

This was deployed via the `gh-pages` branch because the local `gh` token lacked the
`workflow` scope. To use GitHub Actions instead (auto-deploy on push to `main`):

1. `gh auth refresh -s workflow`
2. `mkdir -p .github/workflows && mv deploy/github-pages-workflow.yml .github/workflows/deploy.yml`
3. Commit and push, then set **Settings → Pages → Source: GitHub Actions**.

### URLs and the `site` / `base` config

`astro.config.mjs` currently sets `site: 'https://jollyfollies.com'` with no `base`.

- **Custom domain (jollyfollies.com):** keep it as-is. Add a `public/CNAME` file
  containing `jollyfollies.com`, and point your DNS at GitHub Pages
  (an `ALIAS`/`ANAME` to `<user>.github.io`, or the four Pages A records). Set the
  custom domain in **Settings → Pages**.
- **Default github.io project URL:** set
  `site: 'https://<user>.github.io'` and `base: '/jollyfollies'` in
  `astro.config.mjs`. All internal links already respect `base`, so they will adjust.

A ready-to-use `public/CNAME` is included but commented in the README — create it
when the domain is registered.

## Provenance

- Source: Internet Archive (Wayback Machine), full snapshot in
  `../jollyfollies-archive/` (also zipped as `../jollyfollies-archive.zip`).
- 65 diary entries recovered (dates 2006–2010); a handful of original photos
  survived, most are being restored from the photo library.
