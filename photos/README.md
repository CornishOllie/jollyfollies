# photos/ — the ingest folder

Drop full-size photos in here, then run:

```bash
npm run photos
```

Each image is resized (max 1600px long edge), optimised, and written to
`public/diary-media/` keeping its base name. Originals in this folder are **not**
committed (see `.gitignore`) — they are your working copies.

## Attaching a photo to a diary entry

1. Name the photo to match a placeholder in the entry, e.g. an entry that shows
   `(photo coming soon: P1120004.JPG)` wants a file called `P1120004.jpg`.
2. Drop it in `photos/` and run `npm run photos`.
3. In `src/content/diary/<entry>.md`, replace the marker line with:
   ```markdown
   ![A short caption](/diary-media/P1120004.jpg)
   ```

## Adding a photo to the gallery

Drop + optimise as above, then add an entry to the `recovered` array in
`src/pages/gallery.astro`:

```js
{ src: '/diary-media/P1120004.jpg', alt: 'A short caption' }
```

That's it — `npm run build` picks everything up.
