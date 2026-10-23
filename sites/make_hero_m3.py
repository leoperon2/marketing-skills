#!/usr/bin/env python3
"""Capa da M3 Motos: foto do motor aberto (img/g15.jpg, engrenagens e cobre) à direita esmaecendo para o preto, com brilho verde-limão da marca.
Desktop 1920x900; celular 900x1160 (foto embaixo, topo preto para o texto). Trocar a foto: mudar FOTO."""
import os, numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "m3-motos-pilarzinho", "img")
FOTO = os.path.join(D, "g15.jpg"); foto = Image.open(FOTO).convert("RGB").filter(ImageFilter.UnsharpMask(1.4, 70, 2))
BG = np.array([9, 10, 8], np.float32); LIME = np.array([166, 208, 60], np.float32)
W, H = 1920, 900; cv = np.zeros((H, W, 3), np.float32); cv[:] = BG
r = np.asarray(foto.resize((1000, 1000), Image.LANCZOS), np.float32)[50:950]; x0 = W - 1000
a = np.clip(np.linspace(0, 1, 1000)[None, :, None] / .5, 0, 1) ** 1.3
cv[:, x0:] = BG * (1 - a) + r * a * .92
gl = np.clip(1 - np.sqrt(((np.arange(W)[None, :] - 1250) / 800.) ** 2 + ((np.arange(H)[:, None] - 500) / 500.) ** 2), 0, 1) ** 2.2
cv += gl[..., None] * LIME * .16
n = np.random.default_rng(8).normal(0, 3, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero.jpg"), quality=88)
W, H = 900, 1160; rr = foto.resize((W, W), Image.LANCZOS); top = H - W
cv = np.zeros((H, W, 3), np.float32); cv[:] = BG; cv[top:] = np.asarray(rr, np.float32) * .92
ramp = np.clip((np.arange(H)[:, None, None] - top) / 240., 0, 1) ** 1.2; cv = BG * (1 - ramp) + cv * ramp
Image.fromarray(np.clip(cv, 0, 255).astype("uint8")).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
