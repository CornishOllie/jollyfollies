#!/usr/bin/env python3
"""Safely ingest trip-photo album zips from ~/Downloads.

A zip is treated as a trip album ONLY if it contains several JPGs whose EXIF
capture year falls in 2005-2011. That gate keeps work files, recent phone
clips and Notion exports out, no matter what they're named.

For each trip album it:
  - extracts into photos/_incoming/<Album>/ (multi-part zips merge by name)
  - reads EXIF DateTimeOriginal for every image
and writes photos/photo-index.json: the dated, album-tagged photo set that the
matcher joins to the diary.
"""
import os, re, json, zipfile, tempfile, sys
from datetime import datetime
from PIL import Image, ExifTags

DOWNLOADS = os.path.expanduser("~/Downloads")
INCOMING = "photos/_incoming"
INDEX = "photos/photo-index.json"
DATE_TAG = {v: k for k, v in ExifTags.TAGS.items()}.get("DateTimeOriginal")
DATE_TAG2 = {v: k for k, v in ExifTags.TAGS.items()}.get("DateTime")
MIN_JPG = 3
YEAR_LO, YEAR_HI = 2005, 2011

def album_name(zip_name):
    n = re.sub(r'\.zip$', '', zip_name, flags=re.I)
    n = re.sub(r'-\d+-\d{3}$', '', n)   # strip Google's "-3-001" part suffix
    return n.strip()

def exif_dt(path):
    try:
        ex = Image.open(path)._getexif() or {}
    except Exception:
        return None
    raw = ex.get(DATE_TAG) or ex.get(DATE_TAG2)
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw).strip(), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None

def jpg_members(zf):
    return [m for m in zf.namelist()
            if m.lower().endswith((".jpg", ".jpeg")) and not m.startswith("__MACOSX")]

def looks_like_trip(zip_path):
    """Sample a few JPGs' EXIF years to decide if this is a trip album."""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            jpgs = jpg_members(zf)
            if len(jpgs) < MIN_JPG:
                return False
            hits = 0
            with tempfile.TemporaryDirectory() as td:
                for m in jpgs[:5]:
                    try:
                        zf.extract(m, td)
                        dt = exif_dt(os.path.join(td, m))
                        if dt and YEAR_LO <= dt.year <= YEAR_HI:
                            hits += 1
                    except Exception:
                        pass
            return hits >= 1
    except zipfile.BadZipFile:
        return False

def main():
    os.makedirs(INCOMING, exist_ok=True)
    zips = sorted(f for f in os.listdir(DOWNLOADS) if f.lower().endswith(".zip"))
    trip, ignored = [], []
    for z in zips:
        (trip if looks_like_trip(os.path.join(DOWNLOADS, z)) else ignored).append(z)

    print(f"Trip albums detected: {len(trip)}")
    for z in trip:
        print("   ✓", z)
    print(f"Ignored (not trip photos): {len(ignored)}")

    index = []
    albums = {}
    for z in trip:
        alb = album_name(z)
        dest = os.path.join(INCOMING, alb)
        os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(os.path.join(DOWNLOADS, z)) as zf:
            for m in jpg_members(zf):
                # flatten any internal album folder
                target = os.path.join(dest, os.path.basename(m))
                with zf.open(m) as src, open(target, "wb") as out:
                    out.write(src.read())
        albums.setdefault(alb, dest)

    for alb, dest in albums.items():
        for fn in sorted(os.listdir(dest)):
            if not fn.lower().endswith((".jpg", ".jpeg")):
                continue
            p = os.path.join(dest, fn)
            dt = exif_dt(p)
            index.append({
                "album": alb,
                "file": fn,
                "path": p,
                "datetime": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None,
                "date": dt.strftime("%Y-%m-%d") if dt else None,
            })

    index.sort(key=lambda r: (r["datetime"] or "9999"))
    json.dump(index, open(INDEX, "w"), indent=2)

    # per-album date ranges
    print("\nAlbums ingested:")
    by_alb = {}
    for r in index:
        by_alb.setdefault(r["album"], []).append(r["date"])
    for alb, dates in by_alb.items():
        ds = [d for d in dates if d]
        rng = f"{min(ds)} … {max(ds)}" if ds else "no EXIF dates"
        print(f"   {alb:32s} {len(dates):4d} photos   {rng}")
    print(f"\nTotal photos indexed: {len(index)}  ->  {INDEX}")
    if ignored:
        print("\nIgnored zips:", ", ".join(ignored[:8]), "..." if len(ignored) > 8 else "")

if __name__ == "__main__":
    main()
