"""Give every photo-less entry a picture (2026-10-09), from manifest/added-images.json.

Three kinds, always labelled so nobody mistakes them for photos from the post:
  own      - our own photo from elsewhere on the site; caption says what/when
  commons  - a freely licensed Wikimedia Commons photo; caption credits author,
             licence and source, as the licence requires
  drawing  - an illustration drawn for the site (sources in illustrations-src/)
"header" images go at the top of the entry (after an opening heading);
"slot" images go where the 2009 post had a photo with that caption.
"""
import json, re, pathlib

ORIG = json.load(open("../jollyfollies-replica/src/data/original-entries.json"))
A = json.load(open("manifest/added-images.json"))

def caption(v):
    if v["kind"] == "own": return v.get("caption", "")
    if v["kind"] == "drawing": return f"Illustration: {v['desc']}"
    return f"Illustration: {v['desc']}. Photo: {v['artist']}, {v['license']}, via [Wikimedia Commons]({v['page']})"

def block(v, alt):
    cap = caption(v)
    return f"![{alt}]({v['file']})\n\n" + (f"*{cap}*\n\n" if cap else "")

def anchor(text, body):
    words = re.findall(r"[A-Za-z0-9']+", text)
    for n in (8, 6, 4):
        for s in range(0, min(6, max(1, len(words) - n))):
            m = re.search(r"\W+".join(map(re.escape, words[s:s + n])), body)
            if m:
                k = body.rfind("\n\n", 0, m.start()); return k + 2 if k >= 0 else 0
    return -1

def entry(slug): return next(pathlib.Path("src/content/diary").glob(f"*-{slug}.md"))
done = 0
for slug, v in A["header"].items():
    p = entry(slug); head, fm, body = p.read_text().split("---", 2)
    if v["file"] in body: continue
    body = body.lstrip("\n")
    m = re.match(r"(#+ [^\n]*\n\n)", body)
    pre = m.group(1) if m else ""
    alt = v.get("caption") or v.get("desc") or ""
    body = "\n" + pre + block(v, alt) + body[len(pre):]
    p.write_text(head + "---" + fm + "---" + body); done += 1
for v in A["slot"]:
    p = entry(v["slug"]); head, fm, body = p.read_text().split("---", 2)
    if v["file"] in body: continue
    blocks = ORIG[v["slug"]]["blocks"]
    bi = next(i for i, b in enumerate(blocks) if b["type"] == "photo" and (b.get("caption") or "").strip() == v["caption"])
    pos = next((k for b in blocks[bi + 1:] if b["type"] in ("p", "h") and len(b.get("text", "")) > 15 for k in [anchor(b["text"], body)] if k >= 0), len(body))
    body = body[:pos] + ("\n" if pos and body[pos - 1] != "\n" else "") + block(v, v["caption"]) + body[pos:]
    p.write_text(head + "---" + fm + "---" + re.sub(r"\n{3,}", "\n\n", body)); done += 1
print("added", done)
