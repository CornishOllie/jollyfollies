#!/usr/bin/env python3
"""Build a 'photos to find' spreadsheet from the archived pages.

For every photo the original site placed (ignoring buttons/banners/logos), record
where it sat and what it showed, so the originals can be hunted down in Google Photos:
  page, date, section, caption, original filename, the text just before and after it,
  the likely trip leg (by date), and whether we already have it.
Outputs manifest/photos-to-find.csv (opens in Excel / Google Sheets).
"""
import re, os, html, csv, json, glob

ARCHIVE = "../jollyfollies-archive/www.jollyfollies.com"
OUT = "manifest/photos-to-find.csv"
GAL = "src/data/galleries.json"

FURNITURE = re.compile(r'(button|block|banner|logo|side_view|nav|counter|subscribe|'
                       r'spacer|bullet|arrow|header|footer|smalllogo|whatsnew|'
                       r'diary_home|board|extralabs|blogger|ggpht|hit|vso|rss|lighthouse)', re.I)
IMG_EXT = re.compile(r'\.(jpe?g|png|gif)$', re.I)
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January","February","March","April","May","June","July",
     "August","September","October","November","December"], 1)}

def regions(text):
    return re.findall(r'InstanceBeginEditable name=".*?".*?-->(.*?)<!--\s*InstanceEndEditable', text, re.S)

def entry_date(text):
    for body in regions(text):
        t = html.unescape(re.sub(r'<[^>]+>', ' ', body))
        m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', t)
        if m and m.group(2).lower() in MONTHS:
            return f"{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return ""

def load_legs():
    if not os.path.exists(GAL):
        return [], {}
    albums = json.load(open(GAL))["albums"]
    legs = [(a["start"], a["end"], a["name"]) for a in albums if a.get("start")]
    by_entry = {a["entry_clean"]: a["name"] for a in albums if a.get("entry_clean")}
    return legs, by_entry

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def leg_for(date, legs):
    if not date:
        return ""
    for s, e, name in legs:
        if s <= date <= (e or s):
            return name
    # nearest by start
    near = min(legs, key=lambda l: abs(_d(l[0]) - _d(date)), default=None)
    return near[2] + " (near)" if near else ""

def _d(s):
    y, m, d = map(int, s.split("-")); return y * 10000 + m * 100 + d

def section_titles(body):
    """Blue/bold sub-headings used as section markers (e.g. Wroclaw, Krakow)."""
    return body

def main():
    legs, leg_by_entry = load_legs()
    have = set()
    for d in ("public/diary-media", "public/images"):
        for root, _, files in os.walk(d):
            for f in files:
                have.add(f.lower())

    rows = []
    for path in sorted(glob.glob(f"{ARCHIVE}/Diary/*.htm*")) + \
                sorted(glob.glob(f"{ARCHIVE}/*.htm*")) + \
                sorted(glob.glob(f"{ARCHIVE}/*/*.htm*")):
        fn = os.path.basename(path)
        text = open(path, encoding="latin-1", errors="replace").read()
        is_diary = "/Diary/" in path.replace("\\", "/")
        title = re.sub(r'^\d+_', '', re.sub(r'\.html?$', '', fn)).replace('_', ' ').strip()
        if is_diary:
            title = title.title()
        date = entry_date(text) if is_diary else ""
        rs = regions(text)
        body = max(rs, key=lambda r: len(re.sub(r'<[^>]+>', '', r)), default="") if rs else text
        body = re.sub(r'(?is)<(script|style).*?</\1>', '', body)

        # tokenize: replace imgs with sentinels, track headings
        imgs = []
        def repl(m):
            imgs.append(m.group(0)); return f" \x00{len(imgs)-1}\x00 "
        marked = re.sub(r'(?is)<img[^>]*>', repl, body)
        # mark blue/bold sub-headings so we can recover the section
        marked = re.sub(r'(?is)<font[^>]*color=["\']?#?0{0,2}[03]{0,2}[0-9a-f]*["\']?[^>]*>(.*?)</font>',
                        lambda m: f" \x01{re.sub(r'<[^>]+>','',m.group(1)).strip()}\x01 ", marked)
        plain = html.unescape(re.sub(r'<[^>]+>', ' ', marked))
        plain = re.sub(r'[ \t]+', ' ', plain)

        for i, tag in enumerate(imgs):
            src = re.search(r'src="([^"]+)"', tag)
            alt = re.search(r'alt="([^"]*)"', tag)
            if not src:
                continue
            srcv = html.unescape(src.group(1)).split('?')[0]
            base = os.path.basename(srcv)
            if not IMG_EXT.search(base) or FURNITURE.search(srcv):
                continue
            caption = html.unescape(alt.group(1)).strip() if alt and alt.group(1).strip() else \
                      re.sub(r'\.[a-z]+$', '', base, flags=re.I).replace('_', ' ')
            tok = f'\x00{i}\x00'
            idx = plain.find(tok)
            before_raw = plain[:idx]
            after_raw = plain[idx + len(tok):]
            # nearest section heading (last \x01...\x01 before the image)
            secs = re.findall(r'\x01(.*?)\x01', before_raw)
            section = secs[-1].strip() if secs else ""
            clean = lambda s: re.sub(r'[\x00\x01]\d*', ' ', re.sub(r'\x00\d+\x00|\x01.*?\x01', ' ', s)).strip()
            before = clean(before_raw)[-220:].strip()
            after = clean(after_raw)[:220].strip()
            rows.append({
                "Page": title,
                "Date": date,
                "Section": section,
                "Caption / subject": caption,
                "Original filename": base,
                "Likely trip leg": leg_by_entry.get(slugify(title)) or leg_for(date, legs),
                "Context before": before,
                "Context after": after,
                "Already recovered": "yes" if base.lower() in have else "",
            })

    # de-dup by (page, filename)
    seen = set(); uniq = []
    for r in rows:
        k = (r["Page"], r["Original filename"])
        if k not in seen:
            seen.add(k); uniq.append(r)

    cols = ["Page", "Date", "Section", "Caption / subject", "Original filename",
            "Likely trip leg", "Context before", "Context after", "Already recovered"]
    os.makedirs("manifest", exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in uniq:
            w.writerow(r)

    missing = sum(1 for r in uniq if not r["Already recovered"])
    print(f"Wrote {OUT}")
    print(f"  {len(uniq)} photo slots total, {missing} still to find, {len(uniq)-missing} already recovered")
    print(f"  with a caption: {sum(1 for r in uniq if r['Caption / subject'])}; "
          f"with surrounding context: {sum(1 for r in uniq if r['Context before'] or r['Context after'])}")

if __name__ == "__main__":
    main()
