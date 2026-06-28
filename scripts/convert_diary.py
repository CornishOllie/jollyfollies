#!/usr/bin/env python3
"""Convert archived Dreamweaver diary HTML into Markdown posts (text preserved verbatim).

Reads the Wayback archive's Diary/*.html, extracts the date + body from the
InstanceEditable regions, and writes src/content/diary/NNN-slug.md with front matter.
Only the markup is normalised; the wording (period charm, typos and all) is untouched.
"""
import re, os, html, sys

ARCHIVE = "../jollyfollies-archive/www.jollyfollies.com/Diary"
OUT = "src/content/diary"
MEDIA_SRC = "../jollyfollies-archive/www.jollyfollies.com"
MEDIA_OUT = "public/diary-media"

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January","February","March","April","May","June","July",
     "August","September","October","November","December"], 1)}

SMALL = {"a","an","and","the","of","to","in","on","at","for","by","is","it","be","we","got","but"}

def humanize(slug):
    words = slug.replace("_", " ").split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i != 0 and lw in SMALL:
            out.append(lw)
        elif w.isupper() or any(c.isdigit() for c in w):
            out.append(w)
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)

def editable_regions(text):
    return re.findall(
        r'InstanceBeginEditable name="(.*?)".*?-->(.*?)<!--\s*InstanceEndEditable',
        text, re.S)

def find_date(regions):
    pat = re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})')
    for _, body in regions:
        txt = html.unescape(re.sub(r'<[^>]+>', ' ', body))
        m = pat.search(txt)
        if m and m.group(2).lower() in MONTHS:
            d, mon, y = int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3))
            return f"{y:04d}-{mon:02d}-{d:02d}"
    return None

def html_to_md(frag, existing_media):
    """Minimal, verbatim-preserving HTML->Markdown for a diary body fragment."""
    s = frag
    s = re.sub(r'(?is)<(script|style).*?</\1>', '', s)
    # images: keep only those whose file actually survived in the archive
    def img_sub(m):
        src = re.search(r'src="([^"]+)"', m.group(0))
        alt = re.search(r'alt="([^"]*)"', m.group(0))
        if not src:
            return ''
        base = os.path.basename(html.unescape(src.group(1)).split('?')[0])
        alt_t = html.unescape(alt.group(1)) if alt else ''
        if base in existing_media:
            return f'\n\n![{alt_t}](/diary-media/{base})\n\n'
        # missing images are dropped; per-entry leg galleries provide the photos
        return ''
    s = re.sub(r'(?is)<img[^>]*>', img_sub, s)
    # links
    s = re.sub(r'(?is)<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',
               lambda m: f'[{re.sub(r"<[^>]+>","",m.group(2)).strip()}]({html.unescape(m.group(1))})', s)
    # emphasis
    s = re.sub(r'(?is)<(b|strong)>(.*?)</\1>', lambda m: f'**{m.group(2).strip()}**', s)
    s = re.sub(r'(?is)<(i|em)>(.*?)</\1>', lambda m: f'*{m.group(2).strip()}*', s)
    # headings
    s = re.sub(r'(?is)<h[1-6][^>]*>(.*?)</h[1-6]>', lambda m: f'\n\n## {re.sub(r"<[^>]+>","",m.group(1)).strip()}\n\n', s)
    # list items
    s = re.sub(r'(?is)<li[^>]*>(.*?)</li>', lambda m: f'\n- {re.sub(r"<[^>]+>","",m.group(1)).strip()}', s)
    # breaks & paragraphs -> newlines
    s = re.sub(r'(?is)<br\s*/?>', '\n', s)
    s = re.sub(r'(?is)</p>', '\n\n', s)
    s = re.sub(r'(?is)<p[^>]*>', '\n\n', s)
    # strip any remaining tags
    s = re.sub(r'(?is)<[^>]+>', '', s)
    s = html.unescape(s)
    # tidy whitespace, keep paragraph breaks
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(MEDIA_OUT, exist_ok=True)
    existing_media = set()
    for root, _, files in os.walk(MEDIA_SRC):
        for f in files:
            if f.lower().endswith((".jpg",".jpeg",".png",".gif")):
                existing_media.add(f)

    files = sorted(f for f in os.listdir(ARCHIVE) if f.lower().endswith((".html",".htm")))
    posts, no_date = [], []
    for fn in files:
        m = re.match(r'(\d+)_(.*)\.html?$', fn, re.I)
        if not m:
            continue
        num = int(m.group(1)); slug_raw = m.group(2)
        text = open(os.path.join(ARCHIVE, fn), encoding="latin-1").read()
        regions = editable_regions(text)
        date = find_date(regions)
        # body = the largest editable region by text length
        body_region = max(regions, key=lambda r: len(re.sub(r'<[^>]+>','',r[1])), default=("",""))[1]
        body_md = html_to_md(body_region, existing_media)
        title = humanize(slug_raw)
        slug = f"{num:03d}-" + re.sub(r'[^a-z0-9]+','-', slug_raw.lower()).strip('-')
        orig = f"http://www.jollyfollies.com/Diary/{fn}"
        if not date:
            no_date.append(fn)
        posts.append((num, slug, title, date, orig, body_md))

    # backfill any missing dates by interpolating from neighbours (keeps chronological order)
    posts.sort(key=lambda p: p[0])
    for i, p in enumerate(posts):
        if p[3] is None:
            prev = next((q[3] for q in reversed(posts[:i]) if q[3]), None)
            nxt = next((q[3] for q in posts[i+1:] if q[3]), None)
            posts[i] = (p[0], p[1], p[2], prev or nxt or "2006-01-01", p[4], p[5])

    for num, slug, title, date, orig, body in posts:
        # drop a leading bold line that just repeats the title (rendered separately)
        norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
        first, _, rest = body.partition("\n")
        if first.startswith("**") and norm(first) == norm("**" + title + "**"):
            body = rest.lstrip("\n")
        fm = (f"---\n"
              f"title: {title!r}\n"
              f"date: {date}\n"
              f"order: {num}\n"
              f"original_url: {orig!r}\n"
              f"---\n\n")
        open(os.path.join(OUT, slug + ".md"), "w", encoding="utf-8").write(fm + body + "\n")

    print(f"Wrote {len(posts)} diary posts to {OUT}")
    print(f"Dates parsed from source: {len(posts)-len(no_date)}; backfilled: {len(no_date)}")
    if no_date:
        print("Backfilled (no date in archive):", ", ".join(no_date[:20]))

if __name__ == "__main__":
    main()
