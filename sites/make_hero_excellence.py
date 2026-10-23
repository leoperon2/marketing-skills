#!/usr/bin/env python3
"""Capa do Excellence Studio: foto da parede com o letreiro dourado (_fontes/excellence-parede.jpg, recorte de print, sem pessoas) num arco,
sobre marfim com linhas douradas (eco das telas geométricas do salão). Saída: excellence-studio/img/hero.jpg (1920x900) e hero-m.jpg (900x1300).
Para uma foto melhor, troque _fontes/excellence-parede.jpg e rode de novo."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "excellence-studio", "img")
foto = Image.open(os.path.join(HERE, "_fontes", "excellence-parede.jpg")).convert("RGB").filter(ImageFilter.UnsharpMask(1.2, 60, 2))
IV1 = np.array([252, 248, 240], np.float32); IV2 = np.array([243, 233, 214], np.float32); GOLD = (186, 140, 40)

def lattice(img, x0, x1, H, seed):
    """Trama de losangos (eco das telas douradas), com fade para a esquerda."""
    W = img.size[0]; ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); st = 96
    for k in range(-H, W + H, st):
        d.line([(k, 0), (k + H, H)], fill=GOLD + (255,), width=2); d.line([(k, H), (k + H, 0)], fill=GOLD + (255,), width=2)
    a = np.asarray(ov, np.float32); x = np.arange(W)[None, :]; f = np.clip((x - x0) / max(x1 - x0, 1), 0, 1) ** 1.4
    a[..., 3] *= f * .30; ov = Image.fromarray(a.astype("uint8"), "RGBA"); img.alpha_composite(ov)

def forma(w, h, preenche=True, borda=3, off=(0, 0), tam=None):
    """Arco: meia-lua em cima, lados retos embaixo."""
    t = tam or (w + 80, h + 80); im = Image.new("L", t, 0); d = ImageDraw.Draw(im); r = w / 2; ox, oy = off
    if preenche:
        d.pieslice((ox, oy, ox + w, oy + w), 180, 360, fill=255); d.rectangle((ox, oy + r, ox + w, oy + h), fill=255)
    else:
        d.arc((ox, oy, ox + w, oy + w), 180, 360, fill=255, width=borda); d.line((ox, oy + r, ox, oy + h), fill=255, width=borda); d.line((ox + w, oy + r, ox + w, oy + h), fill=255, width=borda)
    return im

def arco(canvas, x, y, w, h):
    f = foto.resize((w, int(w * foto.size[1] / foto.size[0])), Image.LANCZOS)
    if f.size[1] < h: f = f.resize((int(f.size[0] * h / f.size[1]), h), Image.LANCZOS)
    f = f.crop(((f.size[0] - w) // 2, 0, (f.size[0] - w) // 2 + w, h)).convert("RGBA")
    W, H = canvas.size
    sm = Image.new("L", (W, H), 0); sm.paste(forma(w, h, True, off=(0, 0), tam=(w + 2, h + 2)).point(lambda v: 150 if v else 0), (x, y + 26))
    sh = Image.new("RGBA", (W, H), (70, 50, 10, 0)); sh.putalpha(sm.filter(ImageFilter.GaussianBlur(24)))
    canvas = Image.alpha_composite(canvas, sh)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rm = Image.new("L", (W, H), 0); rm.paste(forma(w, h, False, 3, tam=(w + 2, h + 2)), (x + 22, y - 12))
    gold = Image.new("RGBA", (W, H), GOLD + (255,)); gold.putalpha(rm); canvas = Image.alpha_composite(canvas, gold)
    mk = forma(w, h, True, tam=(w, h)); canvas.paste(f, (x, y), mk); return canvas

def fundo(W, H):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); t = np.clip(x / W * .8 + y / H * .2, 0, 1)[..., None]
    return Image.fromarray(np.clip(IV1 * (1 - t) + IV2 * t, 0, 255).astype("uint8")).convert("RGBA")

# fundo: só marfim + trama dourada (o arco é uma camada à parte, posicionada por CSS)
for nome, W, H, x0, x1, sd in (("hero.jpg", 1920, 900, 700, 1500, 11), ("hero-m.jpg", 900, 1300, 0, 600, 12)):
    c = fundo(W, H); lattice(c, x0, x1, H, sd)
    n = np.random.default_rng(sd).normal(0, 2, (H, W, 1)).astype(np.float32)
    Image.fromarray(np.clip(np.asarray(c.convert("RGB"), np.float32) + n, 0, 255).astype("uint8")).save(os.path.join(D, nome), quality=90)

# arco.webp: foto no arco + contorno dourado deslocado + sombra, com fundo transparente
aw, ah = 620, 457; pad = 50
base = Image.new("RGBA", (aw + 2 * pad, ah + pad + 120), (0, 0, 0, 0)); base = arco(base, pad - 12, pad - 6, aw, ah)
base.save(os.path.join(D, "arco.webp"), quality=90); print("arco", base.size)
print("ok")
