"""One-off typo pass over Ollie's and Jenny's own words (2026-10-08).

Fixes clear misspellings only. Deliberate spellings (stretched words, slang,
jokes like "Ochin Hurrahshaw!", alternative transliterations like Mashad or
Taleban) are left alone, and so are readers' forum comments. Link targets,
front matter other than the text, and file names are never touched.
"""
import re, pathlib, json

FIXES = {
    "acustomed": "accustomed", "alsohonestly": "also honestly", "alll": "all",
    "bussle": "bustle", "catorgorised": "categorised", "conciencous": "conscientious",
    "consciounesses": "consciousnesses", "critisize": "criticise", "daugher": "daughter",
    "lonesom": "lonesome", "sqaure": "square", "surpressed": "suppressed",
    "totaly": "totally", "sauscison": "saucisson", "saucison": "saucisson",
    "caraf": "carafe", "upto": "up to", "angenda": "agenda",
    "Cappadoccia": "Cappadocia", "Dushambe": "Dushanbe", "Chadigarh": "Chandigarh",
    "Karakarom": "Karakoram", "Dehli": "Delhi", "Persepholis": "Persepolis",
    "Bayeaux": "Bayeux", "Ramadam": "Ramadan", "Guiness": "Guinness",
    "Shiitte": "Shiite", "Udapur": "Udaipur", "Bhukara": "Bukhara",
    "Xingjang": "Xinjiang", "Xinjang": "Xinjiang", "Gilget": "Gilgit",
    "Chittral": "Chitral", "Armahdinjad": "Ahmadinejad", "Safronbolu": "Safranbolu",
    "Jolllyfollies": "Jollyfollies", "Uiger": "Uighur", "Mudjahaddin": "Mujahideen",
    "Osbourse": "Osbourne", "Welllhouse": "Wellhouse", "Misouwi": "Mousavi",
}
PAT = re.compile(r"\b(" + "|".join(map(re.escape, FIXES)) + r")\b")
LINK_TARGET = re.compile(r"\]\([^)]*\)|https?://\S+")

def fix_text(s, counts):
    out, last = [], 0
    for m in LINK_TARGET.finditer(s):            # leave link targets untouched
        out.append(PAT.sub(lambda w: (counts.__setitem__(w[1], counts.get(w[1], 0) + 1), FIXES[w[1]])[1], s[last:m.start()]))
        out.append(m.group(0)); last = m.end()
    out.append(PAT.sub(lambda w: (counts.__setitem__(w[1], counts.get(w[1], 0) + 1), FIXES[w[1]])[1], s[last:]))
    return "".join(out)

counts = {}
for p in sorted(pathlib.Path("src/content/diary").glob("*.md")):
    _, fm, body = p.read_text().split("---", 2)
    fm = re.sub(r"^(title:.*)$", lambda m: fix_text(m.group(1), counts), fm, flags=re.M)
    p.write_text("---" + fm + "---" + fix_text(body, counts))
bios = pathlib.Path("src/data/bios.json")
def walk(o):
    if isinstance(o, str): return fix_text(o, counts)
    if isinstance(o, list): return [walk(x) for x in o]
    if isinstance(o, dict): return {k: (v if k in ("photo", "image", "src") else walk(v)) for k, v in o.items()}
    return o
bios.write_text(json.dumps(walk(json.loads(bios.read_text())), indent=2, ensure_ascii=False) + "\n")
print(sum(counts.values()), "fixes:", dict(sorted(counts.items())))
