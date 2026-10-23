#!/usr/bin/env python3
"""Monta a capa da Jennifer Benke a partir do retrato de perfil (logo.jpg, 320 px): selo circular sobre fundo escuro com brilho rosa e grão.
Saída: jennifer-benke-tattoo-studio/img/hero.jpg (1920x900, desktop) e hero-m.jpg (900x1300, celular). Trocar logo.jpg por uma foto maior e rodar de novo."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "jennifer-benke-tattoo-studio", "img")
src = Image.open(os.path.join(D, "logo_src.jpg" if os.path.exists(os.path.join(D, "logo_src.jpg")) else "logo.jpg")).convert("RGB")
ROSE = (229, 154, 176)

def cena(W, H, cx, cy, diam, seed):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32); base[:] = (11, 8, 12)
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    glow = np.clip(1 - d / (diam * 1.25), 0, 1) ** 2.2
    for i, c in enumerate(ROSE): base[..., i] += glow * (c * 0.33)
    fundo = Image.fromarray(np.clip(base, 0, 255).astype("uint8"))
    p = src.resize((diam, diam), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 90, 2))
    m = Image.new("L", (diam, diam), 0); ImageDraw.Draw(m).ellipse((2, 2, diam - 3, diam - 3), fill=255)
    fundo.paste(p, (int(cx - diam / 2), int(cy - diam / 2)), m.filter(ImageFilter.GaussianBlur(1.2)))
    anel = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(anel)
    for k, a in ((1.12, 70), (1.26, 38), (1.42, 20)):
        r = diam * k / 2; dr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ROSE + (a,), width=1)
    fundo = Image.alpha_composite(fundo.convert("RGBA"), anel).convert("RGB")
    rng = np.random.default_rng(seed); n = rng.normal(0, 5.5, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(np.asarray(fundo, np.float32) + n, 0, 255).astype("uint8"))

cena(1920, 900, 1420, 470, 470, 1).save(os.path.join(D, "hero.jpg"), quality=88)
cena(900, 1300, 450, 960, 560, 2).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
