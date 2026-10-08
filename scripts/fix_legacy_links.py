"""Repoint or remove links the 2009 HTML carried into the diary Markdown.

Only link targets change; the diary's words stay as written.
- NNN_name.html (old entry-to-entry links) -> /diary/<slug>/ by entry number
- [![img](src)](../Images/...) click-to-enlarge wrappers -> the image alone
- [](...) empty links left where an image was dropped -> removed
- old Gallery page -> /gallery/
- targets that no longer exist (Videos page, Spending.xls, ../Images photos,
  a truncated "02" link) -> plain text
- www.cbtkyrgyzstan.kg -> http://www.cbtkyrgyzstan.kg
Run from the repo root: python3 scripts/fix_legacy_links.py
"""
import re, pathlib

DIARY = pathlib.Path("src/content/diary")
by_num = {p.name[:3]: p.stem[4:] for p in DIARY.glob("*.md")}
DEAD = ("../Images/", "../blog/", "../Gallery/Videos.html", "../Spending.xls")

def entry_link(m):
    text, num = m.group(1), m.group(2)
    return f"[{text}](/diary/{by_num[num]}/)" if num in by_num else text

changed = 0
for p in sorted(DIARY.glob("*.md")):
    s = orig = p.read_text()
    s = re.sub(r"\[(!\[[^\]]*\]\([^)]*\))\]\(\.\./[^)]*\)", r"\1", s)          # unwrap images
    s = re.sub(r"\[\]\((?:\.\./)[^)]*\)", "", s)                                # empty links
    s = re.sub(r"\[([^\]]*)\]\((\d{3})_[^)]*\.html\)", entry_link, s)            # entry links
    s = s.replace("](../Gallery/Gallery.html)", "](/gallery/)")
    s = s.replace("](www.cbtkyrgyzstan.kg)", "](http://www.cbtkyrgyzstan.kg)")
    s = re.sub(r"\[([^\]]*)\]\((?:%s)[^)]*\)" % "|".join(map(re.escape, DEAD)), r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\(02\)", r"\1", s)
    if s != orig:
        p.write_text(s); changed += 1
print(f"updated {changed} entries")
