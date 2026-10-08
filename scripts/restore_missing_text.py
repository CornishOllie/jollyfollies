"""Restore paragraphs that convert_diary.py dropped (found 2026-10-08).

The replica's parse of the archived pages (../jollyfollies-replica/src/data/
original-entries.json) kept text the first conversion missed, often opening
paragraphs. For each entry, any paragraph or heading (not the dateline, which the page already shows) present in the archive
but absent here is inserted before the next block that is present (or after
the last one). Run fix_typos.py afterwards. Prints what it inserted.
"""
import json, re, pathlib, difflib, sys

ORIG = json.load(open("../jollyfollies-replica/src/data/original-entries.json"))

def norm(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s); s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*_#>`\\]", "", s); return re.sub(r"\W+", " ", s).lower().strip()

def words(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s); s = re.sub(r"\]\([^)]*\)", "]", s)
    return re.findall(r"[a-z0-9]+", s.lower())

def shingles(w, n=3): return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}

def present(text, body_shingles):
    """Missing blocks share almost none of their 3-word runs with the entry
    (0-6% when checked); present ones share far more, typo fixes and all."""
    sh = shingles(words(text))
    return len(words(text)) < 4 or len(sh & body_shingles) / max(1, len(sh)) >= 0.6

DATELINE = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\b", re.I)

def locate(text, body):
    """Index in raw markdown where this block's text starts, or -1."""
    words = re.findall(r"[A-Za-z0-9']+", text)
    for n in (8, 6, 4):
        for start in range(0, min(6, max(1, len(words) - n))):
            pat = r"\W+".join(map(re.escape, words[start:start + n]))
            m = re.search(pat, body)
            if m:
                return body.rfind("\n\n", 0, m.start()) + 2 if body.rfind("\n\n", 0, m.start()) >= 0 else 0
    return -1

dry = "--dry" in sys.argv
total = 0
for p in sorted(pathlib.Path("src/content/diary").glob("*.md")):
    slug = p.stem[4:]
    if slug not in ORIG: continue
    head, fm, body = p.read_text().split("---", 2)
    blocks = [b for b in ORIG[slug]["blocks"] if b["type"] in ("p", "h") and b.get("text", "").strip()]
    bs = shingles(words(body))
    title = norm(ORIG[slug].get("title", ""))
    blocks = [b for b in blocks if not (b["type"] == "h" and (DATELINE.match(b["text"].strip()) or norm(b["text"]) == title))]
    flags = [present(b["text"], bs) for b in blocks]
    inserts = []
    for i, b in enumerate(blocks):
        if flags[i]: continue
        text = b["text"].strip()
        md = ("## " + text) if b["type"] == "h" else text
        pos = -1
        for j in range(i + 1, len(blocks)):           # before the next block we do have
            if flags[j]:
                pos = locate(blocks[j]["text"], body)
                if pos >= 0: break
        if pos < 0:
            for j in range(i - 1, -1, -1):            # else after the last one we have
                if flags[j]:
                    k = locate(blocks[j]["text"], body)
                    if k >= 0:
                        e = body.find("\n\n", k); pos = len(body) if e < 0 else e + 2
                        break
        if pos < 0: pos = len(body)
        inserts.append((pos, i, md))
    for pos, i, md in sorted(inserts, key=lambda x: (-x[0], -x[1])):
        body = body[:pos] + md + "\n\n" + body[pos:]
    body = re.sub(r"\n{3,}", "\n\n", body)
    if inserts:
        total += len(inserts)
        print(f"{slug}: +{len(inserts)}  " + " | ".join(m[:50] for _, _, m in sorted(inserts, key=lambda x: x[1])))
        if not dry: p.write_text(head + "---" + fm + "---" + body)
print("inserted", total, "(dry run)" if dry else "")
