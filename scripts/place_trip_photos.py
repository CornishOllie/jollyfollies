"""Put matched photos back into the trip entries where the 2009 posts had them.

Reads manifest/trip-photo-matches.json (slug, slot, caption, file): exact
filename matches plus photos matched by eye on 2026-10-09 and reviewed.
Each photo goes before the first text block that followed it in the original
post (from the replica's parse of the archive), or after the one before it,
with its original caption underneath. Skips photos already in the entry.
"""
import json, re, pathlib

ORIG = json.load(open("../jollyfollies-replica/src/data/original-entries.json"))
MATCHES = json.load(open("manifest/trip-photo-matches.json"))

def anchor(text, body):
    words = re.findall(r"[A-Za-z0-9']+", text)
    for n in (8, 6, 4):
        for start in range(0, min(6, max(1, len(words) - n))):
            m = re.search(r"\W+".join(map(re.escape, words[start:start + n])), body)
            if m:
                k = body.rfind("\n\n", 0, m.start())
                return k + 2 if k >= 0 else 0
    return -1

by_slug = {}
for m in MATCHES: by_slug.setdefault(m["slug"], []).append(m)
total = 0
for slug, ms in by_slug.items():
    p = next(pathlib.Path("src/content/diary").glob(f"*-{slug}.md"))
    head, fm, body = p.read_text().split("---", 2)
    blocks = ORIG[slug]["blocks"]
    photo_idx = [i for i, b in enumerate(blocks) if b["type"] == "photo"]
    inserts = []
    for m in ms:
        if m["file"] in body: continue
        bi = photo_idx[m["slot"]]
        pos = -1
        for b in blocks[bi + 1:]:
            if b["type"] in ("p", "h") and len(b.get("text", "")) > 15:
                pos = anchor(b["text"], body)
                if pos >= 0: break
        if pos < 0:
            for b in reversed(blocks[:bi]):
                if b["type"] in ("p", "h") and len(b.get("text", "")) > 15:
                    k = anchor(b["text"], body)
                    if k >= 0:
                        e = body.find("\n\n", k); pos = len(body) if e < 0 else e + 2; break
        if pos < 0: pos = len(body)
        cap = m["caption"].strip()
        md = f"![{cap}]({m['file']})\n\n*{cap}*\n\n" if cap else f"![]({m['file']})\n\n"
        inserts.append((pos, m["slot"], md))
    for pos, slot, md in sorted(inserts, key=lambda x: (-x[0], -x[1])):
        body = body[:pos] + md + body[pos:]
    body = re.sub(r"\n{3,}", "\n\n", body)
    p.write_text(head + "---" + fm + "---" + body)
    total += len(inserts); print(f"{slug}: +{len(inserts)}")
print("placed", total)
