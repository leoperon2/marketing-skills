#!/usr/bin/env python3
"""Nina Pet Shop: gera (1) fundo azul com patinhas (hero.jpg desktop 1920x1100, hero-m.jpg celular 900x1300) e (2) pet.webp, o círculo do pet
com borda branca e anel rosa (fundo transparente). O círculo e o logo são posicionados por CSS (vary.py) para atravessar a emenda entre o azul e a próxima seção.
Trocar a foto do pet: mudar PET e o recorte."""
import os, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "nina-pet-shop", "img")
PET = Image.open(os.path.join(D, "g9.jpg")).convert("RGB")
PINK = (232, 69, 139); BLUE1 = (24, 58, 158); BLUE2 = (47, 100, 222)

def pata(d, x, y, s, a):
    col = (255, 255, 255, a)
    d.ellipse((x - s * .55, y - s * .1, x + s * .55, y + s * .75), fill=col)
    for dx, dy, r in ((-.72, -.35, .24), (-.27, -.72, .26), (.27, -.72, .26), (.72, -.35, .24)):
        d.ellipse((x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s), fill=col)

def fundo(W, H, patas, seed):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); t = np.clip((x / W) * .75 + (y / H) * .25, 0, 1)[..., None]
    base = np.array(BLUE1, np.float32) * (1 - t) + np.array(BLUE2, np.float32) * t
    img = Image.fromarray(np.clip(base, 0, 255).astype("uint8")).convert("RGBA")
    pt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(pt)
    for p in patas: pata(d, *p)
    img = Image.alpha_composite(img, pt)
    n = np.random.default_rng(seed).normal(0, 3, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(np.asarray(img.convert("RGB"), np.float32) + n, 0, 255).astype("uint8"))

fundo(1920, 1100, [(140, 180, 100, 26), (520, 760, 70, 20), (1000, 120, 90, 24), (1340, 900, 80, 22), (1780, 200, 110, 26), (300, 480, 50, 18), (1650, 640, 60, 20)], 5).save(os.path.join(D, "hero.jpg"), quality=88)
fundo(900, 1300, [(110, 150, 80, 24), (780, 230, 90, 24), (700, 760, 60, 20), (150, 700, 55, 20), (420, 1180, 70, 22), (820, 1120, 60, 20)], 6).save(os.path.join(D, "hero-m.jpg"), quality=88)

w, h = PET.size; foto = PET.crop((0, 230, w, 230 + w)).resize((800, 800), Image.LANCZOS)
S = 960; c = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(c); cx = cy = 470
d.ellipse((cx + 22 - 448, cy + 22 - 448, cx + 22 + 448, cy + 22 + 448), fill=PINK + (255,))
d.ellipse((cx - 418, cy - 418, cx + 418, cy + 418), fill=(255, 255, 255, 255))
m = Image.new("L", (800, 800), 0); ImageDraw.Draw(m).ellipse((1, 1, 798, 798), fill=255)
c.paste(foto.convert("RGBA"), (cx - 400, cy - 400), m)
c.save(os.path.join(D, "pet.webp"), quality=88)
print("ok", os.path.getsize(os.path.join(D, "pet.webp")) // 1024, "KB")
