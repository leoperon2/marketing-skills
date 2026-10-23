#!/usr/bin/env python3
"""Capa do Aure Art Studio a partir da foto da sala (_fontes/aure-sala.jpg, recorte de print do Instagram, sem pessoas).
Desktop (1920x900): foto à direita esmaecendo para o preto; celular (900x1300): foto embaixo, topo escurecido para o texto.
Se tiver a foto original em alta resolução, troque _fontes/aure-sala.jpg e rode de novo."""
import os, numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "aure-art-studio-tattoo-piercing-em-goiania", "img")
foto = Image.open(os.path.join(HERE, "_fontes", "aure-sala.jpg")).convert("RGB").filter(ImageFilter.UnsharpMask(1.6, 70, 2))
BG = np.array([12, 10, 8], np.float32); w, h = foto.size

# desktop
W, H = 1920, 900; cv = np.zeros((H, W, 3), np.float32); cv[:] = BG
x0 = 860; y0 = 300; rec = np.asarray(foto.crop((0, y0, w, y0 + H)).resize((w, H)), np.float32); wx = min(w, W - x0)
gx = np.clip(np.linspace(0, 1, wx), 0, 1)[None, :, None]; a = np.clip(gx / .42, 0, 1) ** 1.3          # esmaece os 42% da esquerda
cv[:, x0:x0 + wx] = BG * (1 - a) + rec[:, :wx] * a
gl = np.clip(1 - np.sqrt(((np.arange(W)[None, :] - 1350) / 900.) ** 2 + ((np.arange(H)[:, None] - 380) / 520.) ** 2), 0, 1) ** 2   # brilho quente do neon
cv += gl[..., None] * np.array([60, 36, 12], np.float32)
n = np.random.default_rng(7).normal(0, 3, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero.jpg"), quality=88)

# celular
W, H = 900, 1500; r = foto.resize((W, int(h * W / w)), Image.LANCZOS); top = H - r.size[1]
cv = np.zeros((H, W, 3), np.float32); cv[:] = BG; ra = np.asarray(r, np.float32); t = max(top, 0)
cv[t:t + min(H, r.size[1])] = ra[max(0, -top):max(0, -top) + (H - t)]
rampa = np.clip((np.arange(H)[:, None, None] - top) / 260., 0, 1) ** 1.2   # borda superior da foto some no preto
cv = BG * (1 - rampa) + cv * rampa
y = np.linspace(0, 1, H)[:, None, None]; cv *= 1 - .45 * np.clip(1 - y / .5, 0, 1) ** 1.1
Image.fromarray(np.clip(cv, 0, 255).astype("uint8")).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
