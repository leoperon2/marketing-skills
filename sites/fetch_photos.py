#!/usr/bin/env python3
"""Baixa e seleciona fotos das avaliações de cada negócio.
Uso: python3 fetch_photos.py _data/b1.json _data/b2.json
Gera sites/<slug>/img/p01.jpg... e sites/<slug>/photos.json (credito, proporção, qualidade)."""
import hashlib, io, json, os, re, sys, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor
import cv2, numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") if hasattr(cv2, "CascadeClassifier") else None
PROFILE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml") if hasattr(cv2, "CascadeClassifier") else None


def clean_name(t):
    t = re.sub(r"\([^)]*\)", "", t)
    t = t.split(" | ")[0]
    t = re.sub(r"\s*-\s*(Curitiba|Goiânia|Porto Alegre|Belo Horizonte)\s*$", "", t)
    return re.sub(r"\s+", " ", t).strip(" -")


def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:48]


def sized(url, w=1400):
    return url.rsplit("=", 1)[0] + f"=w{w}" if "googleusercontent" in url and "=" in url.rsplit("/", 1)[-1] else url


def fetch(url):
    try:
        req = urllib.request.Request(sized(url), headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=40).read())).convert("RGB")
    except Exception:
        return None


def ahash(im):
    g = np.asarray(im.convert("L").resize((8, 8)), dtype=np.float32)
    return (g > g.mean()).flatten()


def analyse(im):
    w, h = im.size
    s = 640 / max(w, h)
    small = cv2.cvtColor(np.asarray(im.resize((max(1, int(w * s)), max(1, int(h * s))))), cv2.COLOR_RGB2GRAY)
    sharp = cv2.Laplacian(small, cv2.CV_64F).var()
    bright = float(small.mean())
    faces = (list(FACE.detectMultiScale(small, 1.15, 5, minSize=(40, 40))) + list(PROFILE.detectMultiScale(small, 1.15, 6, minSize=(40, 40)))) if FACE is not None else []
    face_frac = max([fw / small.shape[1] for (_, _, fw, _) in faces] or [0])
    return sharp, bright, face_frac, len(faces)


def process(place):
    slug = slugify(clean_name(place["title"]))
    out = os.path.join(HERE, slug, "_src")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith("p"): os.remove(os.path.join(out, f))
    cands = []
    for r in sorted(place.get("reviews") or [], key=lambda r: -(r.get("likesCount") or 0)):
        for u in r.get("reviewImageUrls") or []:
            cands.append((u, r.get("name") or "cliente"))
    cands = cands[:70]
    with ThreadPoolExecutor(8) as ex:
        ims = list(ex.map(lambda c: fetch(c[0]), cands))
    kept, hashes = [], []
    for (u, who), im in zip(cands, ims):
        if im is None or min(im.size) < 480:
            continue
        hh = ahash(im)
        if any((hh != o).sum() < 7 for o in hashes):
            continue
        sharp, bright, ff, nf = analyse(im)
        if bright < 38 or sharp < 25:
            continue
        hashes.append(hh)
        q = min(sharp, 600) / 600 * 0.6 + min(min(im.size), 1400) / 1400 * 0.4
        kept.append(dict(im=im, who=who, q=q, faces=nf, h="".join("1" if b else "0" for b in hh)))
    kept.sort(key=lambda k: -k["q"])
    kept = kept[:30]
    meta = []
    for i, k in enumerate(kept, 1):
        im = k["im"]
        im.thumbnail((1400, 1400))
        fn = f"p{i:02d}.jpg"
        im.save(os.path.join(out, fn), quality=78, optimize=True, progressive=True)
        meta.append(dict(file=f"img/{fn}", hash=k["h"], who=k["who"], aspect=round(im.size[0] / im.size[1], 3), q=round(k["q"], 3), faces=k["faces"], w=im.size[0], h=im.size[1]))
    json.dump(meta, open(os.path.join(HERE, slug, "photos.json"), "w"), ensure_ascii=False, indent=1)
    return slug, len(cands), len(meta)


if __name__ == "__main__":
    places = []
    for f in sys.argv[1:]:
        places += json.load(open(f, encoding="utf-8"))
    for p in places:
        slug, nc, nk = process(p)
        print(f"{slug:44s} candidatas {nc:3d} -> mantidas {nk:2d}")
