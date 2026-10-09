"""Add a folder of photos (e.g. a shared Google Photos album) as a gallery.

    python3 scripts/add_album.py <folder> <slug> "<Name>" <entry_clean> <start> <end>

Optimises each photo the same way build_galleries.py does (full 1500px, thumb
600px) into public/diary-media/<slug>/, then adds or replaces the album in
src/data/galleries.json and links it to the diary entry. Photo dates are left
out when the camera clock can't be trusted; start/end give the album's span.
"""
import json, os, sys, glob
from PIL import Image, ImageOps

MAXW, THUMB = 1500, 600
folder, slug, name, entry_clean, start, end = sys.argv[1:7]
out = f"public/diary-media/{slug}"; os.makedirs(f"{out}/thumb", exist_ok=True)
photos = []
for src in sorted(glob.glob(os.path.join(folder, "*.jpg"))):
    fn = os.path.basename(src)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    full = im.copy(); full.thumbnail((MAXW, MAXW)); full.save(f"{out}/{fn}", "JPEG", quality=82, optimize=True)
    th = im.copy(); th.thumbnail((THUMB, THUMB)); th.save(f"{out}/thumb/{fn}", "JPEG", quality=80, optimize=True)
    photos.append({"src": f"/diary-media/{slug}/{fn}", "thumb": f"/diary-media/{slug}/thumb/{fn}", "date": None})

g = json.load(open("src/data/galleries.json"))
entry = next((os.path.basename(p)[:-3] for p in glob.glob(f"src/content/diary/*-{entry_clean}.md")), None)
title = None
if entry:
    for line in open(f"src/content/diary/{entry}.md"):
        if line.startswith("title:"): title = line.split(":", 1)[1].strip().strip("'\""); break
album = {"name": name, "slug": slug, "count": len(photos), "start": start, "end": end,
         "entry": entry, "entry_clean": entry_clean, "entry_title": title, "photos": photos}
g["albums"] = [a for a in g["albums"] if a["slug"] != slug] + [album]
eg = g.setdefault("entryGalleries", {})
eg[entry_clean] = [s for s in eg.get(entry_clean, []) if s != slug] + [slug]
json.dump(g, open("src/data/galleries.json", "w"), indent=2, ensure_ascii=False)
print(f"{slug}: {len(photos)} photos -> {entry_clean}")
