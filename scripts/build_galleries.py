#!/usr/bin/env python3
"""Optimise ingested trip photos and wire them into the site as galleries.

- Resizes every ingested photo into public/diary-media/<album-slug>/ (web sizes).
- Maps each album (a trip leg) to the diary entry it best belongs to, using the
  album's EXIF date range against the entries' dates, plus name keywords.
- Writes src/data/galleries.json which the Gallery page and diary entries read.
- Writes manifest/album-entry-map.json — the proposed mapping, easy to hand-edit.

Re-runnable: safe to run again as more album zips are ingested.
"""
import os, re, json, glob
from datetime import datetime
from PIL import Image, ImageOps

INDEX = "photos/photo-index.json"
DIARY = "src/content/diary"
OUT_MEDIA = "public/diary-media"
DATA = "src/data/galleries.json"
MAP = "manifest/album-entry-map.json"
MAXW = 1500
THUMB = 600

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def load_entries():
    """slug -> {date, title} from diary front matter."""
    entries = {}
    for p in sorted(glob.glob(f"{DIARY}/*.md")):
        head = open(p, encoding="utf-8").read().split("---")[1]
        d = re.search(r'date:\s*([\d-]+)', head)
        t = re.search(r"title:\s*'?(.*?)'?\s*$", head, re.M)
        slug = os.path.basename(p)[:-3]
        entries[slug] = {
            "date": d.group(1) if d else None,
            "title": t.group(1) if t else slug,
            "clean": re.sub(r'^\d+-', '', slug),
        }
    return entries

def optimise(src, dest_full, dest_thumb):
    if os.path.exists(dest_full) and os.path.exists(dest_thumb):
        return True
    try:
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    except Exception as e:
        print("   ! skip", os.path.basename(src), e)
        return False
    full = im.copy(); full.thumbnail((MAXW, MAXW))
    full.save(dest_full, "JPEG", quality=82, optimize=True)
    th = im.copy(); th.thumbnail((THUMB, THUMB))
    th.save(dest_thumb, "JPEG", quality=80, optimize=True)
    return True

def map_album_to_entry(album, dates, entries):
    """Pick the entry whose date best matches this album's leg.

    Name keyword first (e.g. 'Goa' -> sprint-to-goa); otherwise the entry whose
    date is nearest the album's midpoint (entries are written up around leg's end,
    so this lands on the entry that narrates the leg).
    """
    ds = sorted(d for d in dates if d)
    if not ds:
        return None
    mid = ds[len(ds) // 2]
    toks = [t for t in re.split(r'[^a-z]+', album.lower()) if len(t) >= 3
            and t not in ("to", "the", "and", "from")]
    for slug, e in entries.items():
        title = (e["title"] + " " + slug).lower()
        if any(t in title for t in toks):
            return slug
    cands = [(abs((datetime.fromisoformat(e["date"]) - datetime.fromisoformat(mid)).days), slug)
             for slug, e in entries.items() if e["date"]]
    return min(cands)[1] if cands else None

def main():
    if not os.path.exists(INDEX):
        print("No photo-index.json — run ingest_trip_photos.py first.")
        return
    index = json.load(open(INDEX))
    entries = load_entries()

    # curated leg -> entry overrides (clean-slug values); resolve to full slug
    overrides = {}
    ovr_path = "manifest/album-entry-overrides.json"
    if os.path.exists(ovr_path):
        clean_to_full = {e["clean"]: slug for slug, e in entries.items()}
        for k, v in json.load(open(ovr_path)).items():
            if k.startswith("_"):
                continue
            if v in clean_to_full:
                overrides[k] = clean_to_full[v]
            elif v in entries:
                overrides[k] = v

    by_album = {}
    for r in index:
        by_album.setdefault(r["album"], []).append(r)

    albums_out = []
    album_entry = {}
    total = 0
    for album, photos in by_album.items():
        aslug = slugify(album)
        d_full = os.path.join(OUT_MEDIA, aslug)
        d_thumb = os.path.join(d_full, "thumb")
        os.makedirs(d_thumb, exist_ok=True)
        photos.sort(key=lambda r: (r["datetime"] or "9999"))
        items = []
        for r in photos:
            base = os.path.splitext(r["file"])[0] + ".jpg"
            full = os.path.join(d_full, base)
            thumb = os.path.join(d_thumb, base)
            if optimise(r["path"], full, thumb):
                items.append({
                    "src": f"/diary-media/{aslug}/{base}",
                    "thumb": f"/diary-media/{aslug}/thumb/{base}",
                    "date": r["date"],
                })
                total += 1
        dates = [p["date"] for p in items]
        mapped = overrides.get(aslug) or map_album_to_entry(album, dates, entries)
        album_entry[aslug] = mapped
        albums_out.append({
            "name": album,
            "slug": aslug,
            "count": len(items),
            "start": min((d for d in dates if d), default=None),
            "end": max((d for d in dates if d), default=None),
            "entry": mapped,
            "entry_clean": entries[mapped]["clean"] if mapped else None,
            "entry_title": entries[mapped]["title"] if mapped else None,
            "photos": items,
        })
        print(f"   {album:32s} {len(items):4d} photos -> {mapped}")

    albums_out.sort(key=lambda a: (a["start"] or "9999"))
    # entry -> [album slugs]
    entry_galleries = {}
    for a in albums_out:
        if a["entry"]:
            entry_galleries.setdefault(a["entry_clean"], []).append(a["slug"])

    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump({"albums": albums_out, "entryGalleries": entry_galleries},
              open(DATA, "w"), indent=2)
    json.dump(album_entry, open(MAP, "w"), indent=2)
    print(f"\nOptimised {total} photos into {OUT_MEDIA}/")
    print(f"Wrote {DATA} ({len(albums_out)} albums) and {MAP}")

if __name__ == "__main__":
    main()
