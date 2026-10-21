#!/usr/bin/env python3
"""Baixa fotos de publicações do Instagram (_data/ig_posts.json) e junta às de avaliações em <slug>/photos.json."""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
import fetch_photos as fp

HERE = os.path.dirname(os.path.abspath(__file__))
st = json.load(open(os.path.join(HERE, "ig_status.json")))
posts = json.load(open(os.path.join(HERE, "_data", "ig_posts.json")))
by_user = {}
for p in posts:
    by_user.setdefault((p.get("ownerUsername") or "").lower(), []).append(p)

def urls_of(p):
    imgs = [u for u in (p.get("images") or []) if u] or [p.get("displayUrl")]
    return [u for u in imgs[:4] if u]

def fetch_raw(u):
    import io, urllib.request
    from PIL import Image
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=40).read())).convert("RGB")
    except Exception:
        return None

def run(slug, o):
    user = o.get("primary")
    base = os.path.join(HERE, slug)
    if not user or not os.path.isdir(base): return slug, 0, 0
    src = os.path.join(base, "_src"); os.makedirs(src, exist_ok=True)
    cands = []
    for p in sorted(by_user.get(user.lower(), []), key=lambda p: p.get("timestamp") or "", reverse=True):
        for u in urls_of(p): cands.append(u)
    cands = list(dict.fromkeys(cands))[:70]
    with ThreadPoolExecutor(8) as ex: ims = list(ex.map(fetch_raw, cands))
    kept, hashes = [], []
    for im in ims:
        if im is None or min(im.size) < 480: continue
        hh = fp.ahash(im)
        if any((hh != o2).sum() < 7 for o2 in hashes): continue
        sharp, bright, ff, nf = fp.analyse(im)
        if bright < 38 or sharp < 25: continue
        hashes.append(hh)
        kept.append(dict(im=im, q=min(sharp, 600) / 600 * 0.6 + min(min(im.size), 1400) / 1400 * 0.4 + 0.1, faces=nf, h="".join("1" if b else "0" for b in hh)))
    kept.sort(key=lambda k: -k["q"])
    kept = kept[:30]
    pj = os.path.join(base, "photos.json")
    meta = [m for m in (json.load(open(pj)) if os.path.exists(pj) else []) if not m["file"].startswith("img/i")]
    for i, k in enumerate(kept, 1):
        im = k["im"]; im.thumbnail((1400, 1400))
        fn = f"i{i:02d}.jpg"; im.save(os.path.join(src, fn), quality=78, optimize=True, progressive=True)
        meta.append(dict(file=f"img/{fn}", hash=k["h"], who="@" + user, aspect=round(im.size[0] / im.size[1], 3), q=round(k["q"], 3), faces=k["faces"], w=im.size[0], h=im.size[1]))
    json.dump(meta, open(pj, "w"), ensure_ascii=False, indent=1)
    return slug, len(cands), len(kept)

if __name__ == "__main__":
    want = set(sys.argv[1:])
    for s, o in st.items():
        if o["status"] == "tem site" or s == "don-alberttoni-barbearia": continue
        if want and s not in want: continue
        r = run(s, o)
        print(f"{r[0]:48s} ig=@{o.get('primary')} candidatas {r[1]:3d} -> mantidas {r[2]:2d}")
