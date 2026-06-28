#!/usr/bin/env python3
"""Build the master manifest of every photo the site wants but doesn't have.

Scans the Wayback archive for image references, ignores site furniture
(buttons/banners), and records for each real photo:
  - filename + a human caption (derived from the descriptive original name)
  - which page references it, and (for diary entries) the entry date + slug
  - the original archive path and whether we already hold the file locally

Output:
  manifest/photo-manifest.json   machine-readable, drives the matching step
  manifest/photo-manifest.csv    human-readable shopping list
The date attached to each photo is the key the Google Photos EXIF dates join to.
"""
import re, os, json, html, csv

ARCHIVE = "../jollyfollies-archive/www.jollyfollies.com"
DIARY = os.path.join(ARCHIVE, "Diary")
OUT = "manifest"
HAVE_DIR = "public/diary-media"
LOCAL_IMAGES = "public/images"

FURNITURE = re.compile(r'(button|block|banner|logo|side_view|home_button|nav|counter|'
                       r'subscribe|spacer|bullet|arrow|header|footer|smalllogo|'
                       r'whatsnew|diary_home|board|extralabs|blogger|ggpht|hit-counter)', re.I)
IMG_EXT = re.compile(r'\.(jpe?g|png|gif)$', re.I)
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January","February","March","April","May","June","July",
     "August","September","October","November","December"], 1)}

def editable_regions(text):
    return re.findall(r'InstanceBeginEditable name=".*?".*?-->(.*?)<!--\s*InstanceEndEditable', text, re.S)

def entry_date(text):
    pat = re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})')
    for body in editable_regions(text):
        t = html.unescape(re.sub(r'<[^>]+>', ' ', body))
        m = pat.search(t)
        if m and m.group(2).lower() in MONTHS:
            return f"{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return None

def caption_from(name):
    """Turn an original filename into a human caption, when it's descriptive."""
    stem = re.sub(IMG_EXT, '', name)
    stem = html.unescape(stem)
    # camera-style names carry no meaning -> no caption
    if re.match(r'^(P\d{6,}|DSC\w*\d+|DSCN\d+|IMG_?\d+|PICT\d+|\d+)$', stem):
        return None
    stem = re.sub(r'[_]+', ' ', stem).strip()
    return stem or None

def have_local(base):
    for d in (HAVE_DIR, LOCAL_IMAGES):
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower() == base.lower():
                    return True
    return False

def scan_file(path, rel):
    text = open(path, encoding="latin-1", errors="replace").read()
    is_diary = "/Diary/" in path.replace("\\", "/")
    date = entry_date(text) if is_diary else None
    slug = None
    if is_diary:
        m = re.match(r'(\d+)_(.*)\.html?$', os.path.basename(path), re.I)
        if m:
            slug = f"{int(m.group(1)):03d}-" + re.sub(r'[^a-z0-9]+', '-', m.group(2).lower()).strip('-')
    refs = re.findall(r'(?:src|href)="([^"]+)"', text, re.I)
    out = []
    seen = set()
    for r in refs:
        r = html.unescape(r)
        clean = r.split('?')[0]
        if not IMG_EXT.search(clean):
            continue
        base = os.path.basename(clean)
        if FURNITURE.search(r) or base in seen:
            continue
        seen.add(base)
        out.append({
            "filename": base,
            "caption": caption_from(base),
            "archive_path": clean,
            "page": rel,
            "page_type": "diary" if is_diary else "page",
            "entry_slug": slug,
            "entry_date": date,
            "have_local": have_local(base),
        })
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for root, _, files in os.walk(ARCHIVE):
        for fn in files:
            if fn.lower().endswith((".htm", ".html")):
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, ARCHIVE)
                rows.extend(scan_file(p, rel))

    # de-dup across pages: one record per filename, keep best (dated diary) context
    by_name = {}
    for r in rows:
        k = r["filename"].lower()
        cur = by_name.get(k)
        better = (r["entry_date"] is not None and (cur is None or cur["entry_date"] is None))
        if cur is None or better:
            if cur:  # preserve list of referencing pages
                r["also_on"] = cur.get("also_on", []) + [cur["page"]]
            by_name[k] = r
        else:
            cur.setdefault("also_on", []).append(r["page"])

    photos = sorted(by_name.values(), key=lambda r: (r["entry_date"] or "9999", r["filename"]))

    have = sum(1 for p in photos if p["have_local"])
    dated = sum(1 for p in photos if p["entry_date"])
    captioned = sum(1 for p in photos if p["caption"])

    json.dump({
        "summary": {
            "total_photos": len(photos),
            "have_locally": have,
            "missing": len(photos) - have,
            "with_entry_date": dated,
            "with_caption": captioned,
        },
        "photos": photos,
    }, open(os.path.join(OUT, "photo-manifest.json"), "w"), indent=2)

    with open(os.path.join(OUT, "photo-manifest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "caption", "entry_date", "entry_slug", "have_local", "page"])
        for p in photos:
            w.writerow([p["filename"], p["caption"] or "", p["entry_date"] or "",
                        p["entry_slug"] or "", "yes" if p["have_local"] else "", p["page"]])

    print(f"Photos wanted by the site : {len(photos)}")
    print(f"  already have locally     : {have}")
    print(f"  missing (need from you)  : {len(photos)-have}")
    print(f"  carry an entry date      : {dated}")
    print(f"  carry a usable caption   : {captioned}")
    print(f"\nWritten: {OUT}/photo-manifest.json  and  {OUT}/photo-manifest.csv")

if __name__ == "__main__":
    main()
