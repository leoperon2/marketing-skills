#!/usr/bin/env python3
"""Capa do NVZ: retrato de cabelo loiro longo (_fontes/nvz-loira.jpg, recorte de story do próprio Instagram do salão), espelhado para o olhar voltar ao texto,
sobre grafite com brilho rosa. Desktop 1920x900 (foto à direita, esmaece à esquerda); celular 900x1300 (rosto na metade de baixo, topo escuro para o texto).
Também gera img/logo.jpg a partir do print do perfil, se já existir o recorte."""
import os, numpy as np
from PIL import Image, ImageOps, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "new-visuallize-salao-de-beleza-menino-deus", "img")
foto = ImageOps.mirror(Image.open(os.path.join(HERE, "_fontes", "nvz-loira.jpg")).convert("RGB")).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
BG = np.array([19, 17, 21], np.float32); PINK = np.array([224, 74, 138], np.float32); w, h = foto.size
def base(W, H, gx, gy, gr):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); cv = np.zeros((H, W, 3), np.float32); cv[:] = BG
    g = np.clip(1 - np.sqrt((x - gx) ** 2 + (y - gy) ** 2) / gr, 0, 1) ** 2; cv += g[..., None] * PINK * .30; return cv
# desktop: foto com margem escura em cima (o recorte começa na altura dos olhos), esmaecendo em cima e à esquerda
W, H = 1920, 900; cv = base(W, H, 1560, 420, 800)
ph = foto.resize((int(w * 1050 / h), 1050), Image.LANCZOS); pa = np.asarray(ph, np.float32); fw = pa.shape[1]
oy = 90; seg = pa[:H - oy]; x0 = W - fw + 40
fx = np.clip(np.linspace(0, 1, fw)[None, :, None] / .38, 0, 1) ** 1.2; fy = np.clip(np.arange(seg.shape[0])[:, None, None] / 150., 0, 1) ** 1.2
reg = cv[oy:oy + seg.shape[0], x0:x0 + fw]; seg = seg[:, :reg.shape[1]]; fd = (fx * fy)[:, :reg.shape[1]]
cv[oy:oy + seg.shape[0], x0:x0 + reg.shape[1]] = reg * (1 - fd) + seg * fd
n = np.random.default_rng(5).normal(0, 2.5, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero.jpg"), quality=90)
# celular: hero alto (960 px de CSS): texto em cima, rosto e cabelo embaixo, sem sobrepor
W, H = 900, 2100; cv = base(W, H, 450, 1500, 800)
ph = foto.resize((W, int(h * W / w)), Image.LANCZOS); pa = np.asarray(ph, np.float32); off = 880
seg = pa[:H - off]; reg = cv[off:off + seg.shape[0]]
ramp = np.clip(np.arange(seg.shape[0])[:, None, None] / 220., 0, 1) ** 1.2
cv[off:off + seg.shape[0]] = reg * (1 - ramp) + seg * ramp
n = np.random.default_rng(6).normal(0, 2.5, (H, W, 1)).astype(np.float32)
Image.fromarray(np.clip(cv + n, 0, 255).astype("uint8")).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
