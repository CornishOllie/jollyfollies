#!/usr/bin/env node
/**
 * Photo ingest + optimisation.
 *
 * Drop full-size images into  photos/  then run:  npm run photos
 *
 * Each image is resized (max 1600px on the long edge) and written, optimised,
 * to  public/diary-media/  keeping its base name. Reference it from a diary
 * entry or the gallery by that name, e.g.  ![caption](/diary-media/P1120004.jpg)
 *
 * Tip: name a photo exactly as a "(photo coming soon: NAME)" marker in an entry,
 * run this, then swap that marker line for the image syntax above.
 */
import { readdir, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const SRC = 'photos';
const OUT = 'public/diary-media';
const MAX = 1600;
const exts = new Set(['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.tiff', '.heic']);

if (!existsSync(SRC)) { console.error(`No ${SRC}/ folder — create it and drop images in.`); process.exit(1); }
await mkdir(OUT, { recursive: true });

const files = (await readdir(SRC)).filter((f) => exts.has(path.extname(f).toLowerCase()));
if (!files.length) { console.log(`No images found in ${SRC}/. Drop some in and re-run.`); process.exit(0); }

let done = 0;
for (const f of files) {
  const base = path.basename(f, path.extname(f));
  const out = path.join(OUT, `${base}.jpg`);
  try {
    await sharp(path.join(SRC, f))
      .rotate()                                   // respect EXIF orientation
      .resize({ width: MAX, height: MAX, fit: 'inside', withoutEnlargement: true })
      .jpeg({ quality: 82, mozjpeg: true })
      .toFile(out);
    console.log(`✓ ${f}  ->  ${out}`);
    done++;
  } catch (e) {
    console.error(`✗ ${f}: ${e.message}`);
  }
}
console.log(`\nOptimised ${done}/${files.length} image(s) into ${OUT}/`);
