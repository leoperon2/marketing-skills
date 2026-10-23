#!/usr/bin/env python3
"""Capa do Black Rooster Ink: manga fechada (lobo, mulher, lua e águia; _fontes/br-manga.jpg, recorte de reel do estúdio) à direita, esmaecendo para o preto.
Desktop 1920x900; celular 900x1500 (manga embaixo, topo preto para o texto)."""
import os, numpy as np
from PIL import Image, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "black-rooster-ink", "img")
f = Image.open(os.path.join(HERE, "_fontes", "br-manga.jpg")).convert("RGB"); f = ImageEnhance.Contrast(f).enhance(1.08).filter(ImageFilter.UnsharpMask(1.4, 70, 2)); w, h = f.size
BG = np.array([9, 8, 8], np.float32); RED = np.array([200, 40, 36], np.float32)
def base(W, H, gx, gy, gr):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); cv = np.zeros((H, W, 3), np.float32); cv[:] = BG
    g = np.clip(1 - np.sqrt((x - gx) ** 2 + (y - gy) ** 2) / gr, 0, 1) ** 2; cv += g[..., None] * RED * .22; return cv
W, H = 1920, 900; cv = base(W, H, 1500, 450, 700)
ph = f.resize((int(w * 1200 / h), 1200), Image.LANCZOS); pa = np.asarray(ph, np.float32)[150:150 + H]; fw = pa.shape[1]; x0 = W - fw - 120
fx = np.clip(np.linspace(0, 1, fw)[None, :, None] / .30, 0, 1) ** 1.2 * np.clip((1 - np.linspace(0, 1, fw)[None, :, None]) / .15, 0, 1)
cv[:, x0:x0 + fw] = cv[:, x0:x0 + fw] * (1 - fx) + pa * fx
n = np.random.default_rng(3).normal(0, 2.5, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero.jpg"), quality=90)
W, H = 900, 2100; cv = base(W, H, 450, 1500, 800)
ph = f.resize((W, int(h * W / w)), Image.LANCZOS); pa = np.asarray(ph, np.float32); off = 960; seg = pa[:H - off]
r = np.clip(np.arange(seg.shape[0])[:, None, None] / 220., 0, 1) ** 1.2
cv[off:off + seg.shape[0]] = cv[off:off + seg.shape[0]] * (1 - r) + seg * r
Image.fromarray(np.clip(cv, 0, 255).astype("uint8")).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
