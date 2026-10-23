#!/usr/bin/env python3
"""Capa da Nina Pet Shop: azul-royal da marca, patinhas, um pet (g9.jpg) num círculo com borda branca e anel rosa, e o logo em selo.
Saída: nina-pet-shop/img/hero.jpg (1920x900) e hero-m.jpg (900x1300). Trocar a foto do pet: mudar PET e o recorte."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "nina-pet-shop", "img")
PET = Image.open(os.path.join(D, "g9.jpg")).convert("RGB"); LOGO = Image.open(os.path.join(D, "logo.jpg")).convert("RGB")
PINK = (232, 69, 139); BLUE1 = (24, 58, 158); BLUE2 = (47, 100, 222)

def pata(d, x, y, s, a):
    col = (255, 255, 255, a)
    d.ellipse((x - s * .55, y - s * .1, x + s * .55, y + s * .75), fill=col)
    for dx, dy, r in ((-.72, -.35, .24), (-.27, -.72, .26), (.27, -.72, .26), (.72, -.35, .24)):
        d.ellipse((x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s), fill=col)

def circulo(img, cx, cy, diam, foto, borda=14):
    W, H = img.size
    anel = Image.new("RGBA", (W, H), (0, 0, 0, 0)); r = diam / 2 + borda + 26
    ImageDraw.Draw(anel).ellipse((cx + 18 - r, cy + 18 - r, cx + 18 + r, cy + 18 + r), fill=PINK + (255,))
    img = Image.alpha_composite(img, anel)
    br = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rb = diam / 2 + borda
    ImageDraw.Draw(br).ellipse((cx - rb, cy - rb, cx + rb, cy + rb), fill=(255, 255, 255, 255)); img = Image.alpha_composite(img, br)
    f = foto.resize((diam, diam), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (diam, diam), 0); ImageDraw.Draw(m).ellipse((1, 1, diam - 2, diam - 2), fill=255)
    img.paste(f, (int(cx - diam / 2), int(cy - diam / 2)), m); return img

def selo(img, cx, cy, diam):
    W, H = img.size; rb = diam / 2 + 10
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - rb, cy - rb + 8, cx + rb, cy + rb + 8), fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
    br = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(br).ellipse((cx - rb, cy - rb, cx + rb, cy + rb), fill=(255, 255, 255, 255)); img = Image.alpha_composite(img, br)
    l = LOGO.resize((diam, diam), Image.LANCZOS).convert("RGBA"); m = Image.new("L", (diam, diam), 0); ImageDraw.Draw(m).ellipse((1, 1, diam - 2, diam - 2), fill=255)
    img.paste(l, (int(cx - diam / 2), int(cy - diam / 2)), m); return img

def cena(W, H, pet, logo, seed, patas):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); t = np.clip((x / W) * .75 + (y / H) * .25, 0, 1)[..., None]
    base = np.array(BLUE1, np.float32) * (1 - t) + np.array(BLUE2, np.float32) * t
    img = Image.fromarray(np.clip(base, 0, 255).astype("uint8")).convert("RGBA")
    pt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(pt)
    for (px, py, s, a) in patas: pata(d, px, py, s, a)
    img = Image.alpha_composite(img, pt)
    img = circulo(img, *pet[:3], PET_FOTO); img = selo(img, *logo)
    rng = np.random.default_rng(seed); n = rng.normal(0, 3, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(np.asarray(img.convert("RGB"), np.float32) + n, 0, 255).astype("uint8"))

w, h = PET.size; PET_FOTO = PET.crop((0, 230, w, 230 + w))
cena(1920, 900, (1410, 450, 560), (1180, 690, 230), 5, [(980, 140, 90, 26), (1700, 120, 70, 22), (1150, 300, 50, 20), (1820, 700, 100, 24), (860, 760, 60, 18)]).save(os.path.join(D, "hero.jpg"), quality=88)
cena(900, 1300, (450, 900, 520), (190, 1070, 190), 6, [(120, 760, 80, 24), (790, 700, 90, 24), (700, 1210, 60, 22), (320, 700, 50, 18)]).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
