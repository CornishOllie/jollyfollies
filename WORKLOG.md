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
