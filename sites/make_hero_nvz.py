#!/usr/bin/env python3
"""Capa do New Visuallize (NVZ): logo rosa em selo branco sobre grafite com halos rosa (clima preto, cinza e rosa do Instagram deles).
Saída: new-visuallize-salao-de-beleza-menino-deus/img/hero.jpg (1920x900) e hero-m.jpg (900x1300). Usa img/logo.jpg (600 px, recorte do perfil)."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "new-visuallize-salao-de-beleza-menino-deus", "img")
logo = Image.open(os.path.join(D, "logo.jpg")).convert("RGB"); PINK = (214, 56, 120)
def cena(W, H, cx, cy, d, seed):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); base = np.zeros((H, W, 3), np.float32); base[:] = (20, 18, 22)
    g = np.clip(1 - np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (d * 1.5), 0, 1) ** 2.1
    for i, c in enumerate(PINK): base[..., i] += g * c * .36
    img = Image.fromarray(np.clip(base, 0, 255).astype("uint8")).convert("RGBA")
    an = Image.new("RGBA", (W, H), (0, 0, 0, 0)); da = ImageDraw.Draw(an)
    for k, a in ((1.14, 200), (1.30, 90), (1.50, 45), (1.74, 22)):
        r = d * k / 2; da.ellipse((cx - r, cy - r, cx + r, cy + r), outline=PINK + (a,), width=3 if k < 1.2 else 1)
    img = Image.alpha_composite(img, an)
    r = d / 2; sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - r, cy - r + 14, cx + r, cy + r + 14), fill=(0, 0, 0, 160))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(20)))
    l = logo.resize((d, d), Image.LANCZOS).convert("RGBA"); m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((1, 1, d - 2, d - 2), fill=255)
    img.paste(l, (int(cx - d / 2), int(cy - d / 2)), m)
    n = np.random.default_rng(seed).normal(0, 3, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(np.asarray(img.convert("RGB"), np.float32) + n, 0, 255).astype("uint8"))
cena(1920, 900, 1400, 450, 470, 3).save(os.path.join(D, "hero.jpg"), quality=88)
cena(900, 1300, 450, 940, 520, 4).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
