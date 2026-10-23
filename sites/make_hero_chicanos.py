#!/usr/bin/env python3
"""Capa do Los Chicanos: fachada (_fontes/chicanos-fachada.jpg, recorte de print do Instagram, sem pessoas e sem os textos de telefone/preço).
Desktop 1920x900: foto à direita esmaecendo para o preto, brilho dourado. Celular 900x1500: foto embaixo, topo preto para o texto."""
import os, numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "barbearia-los-chicanos", "img")
foto = Image.open(os.path.join(HERE, "_fontes", "chicanos-fachada.jpg")).convert("RGB").filter(ImageFilter.UnsharpMask(1.4, 70, 2))
BG = np.array([10, 9, 8], np.float32); w, h = foto.size
W, H = 1920, 900; cv = np.zeros((H, W, 3), np.float32); cv[:] = BG
fw = 1080; fh = int(h * fw / w); r = np.asarray(foto.resize((fw, fh), Image.LANCZOS), np.float32)
if fh < H: r = np.asarray(foto.resize((int(w * H / h), H), Image.LANCZOS), np.float32); fw = r.shape[1]; fh = H
x0 = W - fw; y0 = 0; sl = r[:H] if fh >= H else r
gx = np.linspace(0, 1, fw)[None, :, None]; a = np.clip(gx / .45, 0, 1) ** 1.3
cv[:, x0:] = BG * (1 - a) + sl[:H, :fw] * a
gl = np.clip(1 - np.sqrt(((np.arange(W)[None, :] - 1500) / 900.) ** 2 + ((np.arange(H)[:, None] - 420) / 560.) ** 2), 0, 1) ** 2
cv += gl[..., None] * np.array([46, 34, 12], np.float32)
n = np.random.default_rng(4).normal(0, 3, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero.jpg"), quality=88)
W, H = 900, 1160; rr = foto.resize((W, int(h * W / w)), Image.LANCZOS); top = H - rr.size[1]
cv = np.zeros((H, W, 3), np.float32); cv[:] = BG; cv[top:] = np.asarray(rr, np.float32)
ramp = np.clip((np.arange(H)[:, None, None] - top) / 260., 0, 1) ** 1.2; cv = BG * (1 - ramp) + cv * ramp
y = np.linspace(0, 1, H)[:, None, None]; cv *= 1 - .4 * np.clip(1 - y / .5, 0, 1) ** 1.1
Image.fromarray(np.clip(cv, 0, 255).astype("uint8")).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
