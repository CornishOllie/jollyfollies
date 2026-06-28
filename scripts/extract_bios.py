#!/usr/bin/env python3
"""Extract the About-page character bios (Ollie, Jenny, DINO) from the archive.

Pulls the intro paragraph and the interview Q&A, verbatim, into src/data/bios.json.
"""
import re, html, os, json

ARCHIVE = "../jollyfollies-archive/www.jollyfollies.com/About Us"
OUT = "src/data/bios.json"

FILES = [
    ("Ollie", "Ollie.htm"),
    ("Jenny", "Jenny.htm"),
    ("DINO", "Dino.html"),
]

def clean_body(path):
    t = open(path, encoding="latin-1", errors="replace").read()
    rs = re.findall(r'InstanceBeginEditable name=".*?".*?-->(.*?)<!--\s*InstanceEndEditable', t, re.S)
    src = max(rs, key=lambda r: len(re.sub(r'<[^>]+>', '', r))) if rs else t
    src = re.sub(r'(?is)<(script|style).*?</\1>', '', src)
    src = re.sub(r'(?is)<br\s*/?>', '\n', src)
    src = re.sub(r'(?is)</(p|div|td|tr|h\d)>', '\n', src)
    txt = html.unescape(re.sub(r'<[^>]+>', '', src))
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = "\n".join(l.strip() for l in txt.splitlines())
    txt = re.sub(r'\n{2,}', '\n', txt).strip()
    return txt

def parse(name, txt):
    # drop boilerplate header lines
    lines = [l for l in txt.splitlines() if l.strip()]
    drop = re.compile(r"(VSO blog|wish to raise|Help us|donating|Last|Updated|Big Trip|^\d|parent\.frames|^Likes$|^Dislikes$)", re.I)
    lines = [l for l in lines if not drop.search(l)]
    full = "\n".join(lines)

    intro = ""
    m = re.search(r'Who (?:is|Are)[^\n]*\n(.*?)(?=\nThe .*Interview|\Z)', full, re.S)
    if m:
        intro = re.sub(r'\s+', ' ', m.group(1)).strip()

    qa = []
    iv = re.search(r'The .*?Interview(.*)', full, re.S)
    body = re.sub(r'\s+', ' ', (iv.group(1) if iv else full)).strip()
    # split before each interview question (they all start with an interrogative)
    chunks = re.split(r'(?=(?:Why|What|Where|When|How|Who|Which|Are|Do|Does|Is|Will)\b[^?]{0,90}\?)', body)
    for c in chunks:
        c = c.strip()
        if "?" not in c:
            continue
        q, a = c.split("?", 1)
        a = re.sub(r'\s*(October|November|September)\s+\d.*$', '', a).strip()  # drop trailing "Last Updated" date
        if q.strip() and a.strip():
            qa.append({"q": q.strip() + "?", "a": a.strip()})
    return {"name": name, "intro": intro, "qa": qa}

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bios = []
    for name, fn in FILES:
        p = os.path.join(ARCHIVE, fn)
        if os.path.exists(p):
            bios.append(parse(name, clean_body(p)))
    json.dump(bios, open(OUT, "w"), indent=2, ensure_ascii=False)
    for b in bios:
        print(f"{b['name']}: intro {len(b['intro'])} chars, {len(b['qa'])} Q&A")

if __name__ == "__main__":
    main()
