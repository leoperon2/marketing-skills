#!/usr/bin/env python3
"""Capa do Deck 583: o hambúrguer de img/g17.jpg bem grande, com brilho quente, esmaecendo para o marrom-escuro.
Desktop 1920x900 (foto à direita); celular 900x1750 (foto embaixo, topo escuro para o texto). Trocar a foto: mudar FOTO."""
import os, numpy as np
from PIL import Image, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "deck-583", "img")
foto = Image.open(os.path.join(D, "g17.jpg")).convert("RGB")
foto = ImageEnhance.Color(ImageEnhance.Contrast(foto).enhance(1.08)).enhance(1.12).filter(ImageFilter.UnsharpMask(1.4, 70, 2))
BG = np.array([14, 9, 7], np.float32); WARM = np.array([240, 150, 40], np.float32)
def base(W, H, gx, gy, gr):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); cv = np.zeros((H, W, 3), np.float32); cv[:] = BG
    g = np.clip(1 - np.sqrt((x - gx) ** 2 + (y - gy) ** 2) / gr, 0, 1) ** 2; cv += g[..., None] * WARM * .26; return cv
W, H = 1920, 900; cv = base(W, H, 1450, 450, 760); fw = 960
pa = np.asarray(foto.resize((fw, fw), Image.LANCZOS), np.float32)[30:930]; x0 = W - fw + 20
fx = np.clip(np.linspace(0, 1, fw)[None, :, None] / .42, 0, 1) ** 1.25; reg = cv[:, x0:x0 + fw]; pa = pa[:, :reg.shape[1]]; fx = fx[:, :reg.shape[1]]
cv[:, x0:x0 + reg.shape[1]] = reg * (1 - fx) + pa * fx
n = np.random.default_rng(9).normal(0, 2.5, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero.jpg"), quality=90)
W, H = 900, 1750; cv = base(W, H, 450, 1300, 760); pa = np.asarray(foto.resize((W, W), Image.LANCZOS), np.float32); top = H - W
ramp = np.clip(np.arange(W)[:, None, None] / 260., 0, 1) ** 1.2; reg = cv[top:]
cv[top:] = reg * (1 - ramp) + pa * ramp
n = np.random.default_rng(10).normal(0, 2.5, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
