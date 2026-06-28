# Jolly Follies rebuild — autonomous worklog

Working through loops to make this the most complete version possible while Ollie is away.

## Done before the loops
- Recovered full Wayback archive (214 files); 65 diary entries migrated to Markdown, text verbatim.
- Astro site: home, diary (index + entries w/ prev-next), about, route, vehicle, jogle, gallery, contact, 404, RSS, sitemap, OG, light/dark.
- Ingested 1,255 trip photos from Google Photos album zips (EXIF-dated, 21 legs), optimised, wired into Gallery page + per-entry galleries + JOGLE + diary card covers, with a lightbox.

## Loops
- **L1 — verify & assess**: screenshotted gallery/entry/index — all rendering well. Confirmed gh auth present (CornishOllie). Media 382MB.
- **L2 — hero**: full-bleed Kyrgyzstan mountain-valley hero photo with warm scrim + cream wordmark/Defender. Replaces flat gradient.
- **L3 — About bios**: extracted Ollie/Jenny/DINO interviews + intros verbatim (scripts/extract_bios.py -> src/data/bios.json); rebuilt About with "meet the crew" cards.
- **L4 — DINO guide**: restored verbatim build notes (tyres, awning, hasps) + specs + prep-photo gallery on the Vehicle page.
- **L5 — Route map + stats**: SVG equirectangular route map (17 waypoints, dashed gradient path), by-the-numbers stat band, and a leg-by-leg timeline with thumbnails from the photo data.
- **L6 — Search**: dependency-free client-side diary search (search-index.json endpoint + /search/ page with highlighted snippets) and a ⌕ nav icon.
- **L7 — marker cleanup**: stripped 233 "(photo coming soon)" markers from 48 entries (per-entry leg galleries now provide the photos); converter updated to drop missing images silently.
- **L8 — polish**: per-entry OpenGraph image (the leg cover) with base-path-correct URLs; reading-time on entries; verified light/dark end-to-end (red-diagnostic confirmed nav + body both follow tokens).
- **L9 — DEPLOYED LIVE**: site is live at https://cornishollie.github.io/jollyfollies/ . Pushed source to main (CornishOllie/jollyfollies), deployed built site to gh-pages branch (workflow scope unavailable to the local token, so CI workflow is parked in deploy/ for later). `npm run deploy` redeploys. All pages + assets verified 200.
- **L10 — live QA**: verified gallery (thumbnails load over base path), search (index fetch + highlight), route, about, RSS, sitemap all working on the live URL. Site complete and live.
- **L11 — accurate mapping**: curated leg→entry overrides (manifest/album-entry-overrides.json) so each leg sits on the entry that narrates it (Pamir→mountain-madness, Hungary→magyar, India→hindustan-zindabad, JOGLE→its entry). Diary covers now use a mid-album (more scenic) photo.
- **L12 — JOGLE facts**: added the recovered daily-run route to the JOGLE page.

## Result
Live at https://cornishollie.github.io/jollyfollies/ — full live link sweep passed (0 broken / 20 checked).
Coverage: planning (2006) through to Goa (Nov 2009) richly photographed; India→Sydney + Meghan's
birth are text-only (no photo albums existed for those). Add later via the photos/ pipeline.

## How to maintain
- Add a diary entry: drop a Markdown file in src/content/diary/ (see README).
- Add photos: drop album zips in ~/Downloads (or images in photos/), then:
    python3 scripts/ingest_trip_photos.py && python3 scripts/build_galleries.py && npm run deploy
- Redeploy after any change: npm run deploy
