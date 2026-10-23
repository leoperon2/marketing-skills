#!/usr/bin/env python3
"""Capa da Tayz Bessa Studio: monograma dourado (logo.jpg) dentro de espelhos redondos com halo dourado, sobre preto com verde-musgo.
Saída: tayz-bessa-studio/img/hero.jpg (1920x900) e hero-m.jpg (900x1300). Os espelhos redondos com luz dourada são a assinatura do salão."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "tayz-bessa-studio", "img")
logo = Image.open(os.path.join(D, "logo.jpg")).convert("RGB")
GOLD = (207, 169, 94); MOSS = (40, 74, 50)

def mono(size):
    """Monograma dourado com fundo transparente (luminância vira alfa)."""
    g = logo.resize((size, size), Image.LANCZOS); a = np.asarray(g, np.float32)
    lum = a.max(axis=2); alpha = np.clip((lum - 18) / 120, 0, 1)
    rgba = np.dstack([a, alpha * 255]).astype("uint8"); return Image.fromarray(rgba, "RGBA")

def espelho(canvas, cx, cy, r, w=5):
    """Espelho redondo: vidro escuro, aro dourado e halo de luz."""
    W, H = canvas.size
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD + (210,), width=w * 5)
    canvas = Image.alpha_composite(canvas, halo.filter(ImageFilter.GaussianBlur(26)))
    vidro = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dv = ImageDraw.Draw(vidro)
    dv.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(16, 20, 16, 235))
    inner = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(inner).ellipse((cx - r * .72, cy - r * .72, cx + r * .72, cy + r * .72), fill=MOSS + (60,))
    canvas = Image.alpha_composite(canvas, vidro); canvas = Image.alpha_composite(canvas, inner.filter(ImageFilter.GaussianBlur(r * .25)))
    aro = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(aro).ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD + (255,), width=w)
    return Image.alpha_composite(canvas, aro)

def cena(W, H, grande, pequenos, seed):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32); base[:] = (10, 9, 8)
    cx, cy, _ = grande
    verde = np.clip(1 - np.sqrt((x - cx * 1.08) ** 2 + (y - cy * .9) ** 2) / (W * .55), 0, 1) ** 1.7
    for i, c in enumerate(MOSS): base[..., i] += verde * (c * 1.1)
    ouro = np.clip(1 - np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (grande[2] * 1.9), 0, 1) ** 2.2
    for i, c in enumerate(GOLD): base[..., i] += ouro * (c * .22)
    img = Image.fromarray(np.clip(base, 0, 255).astype("uint8")).convert("RGBA")
    for (px, py, pr) in pequenos: img = espelho(img, px, py, pr, 4)
    img = espelho(img, cx, cy, grande[2], 6)
    m = mono(int(grande[2] * 1.9)); img.alpha_composite(m, (int(cx - m.width / 2), int(cy - m.height / 2)))
    rng = np.random.default_rng(seed); n = rng.normal(0, 5, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(np.asarray(img.convert("RGB"), np.float32) + n, 0, 255).astype("uint8"))

# Se existir a foto de capa fornecida (_fontes/tayz-hero.jpg), ela vira a capa; senão cai na capa de marca (espelhos + monograma) abaixo.
FOTO = os.path.join(HERE, "_fontes", "tayz-hero.jpg")
if os.path.exists(FOTO):
    ph = Image.open(FOTO).convert("RGB"); w, h = ph.size
    def escurece_esq(img, ate, forca):
        a = np.asarray(img, np.float32); W = a.shape[1]; x = np.linspace(0, 1, W)[None, :, None]
        f = 1 - forca * np.clip(1 - x / ate, 0, 1) ** 1.2; return Image.fromarray(np.clip(a * f, 0, 255).astype("uint8"))
    escurece_esq(ph, .62, .52).save(os.path.join(D, "hero.jpg"), quality=90)
    # celular (900x1300): recorte de trança e mãos, colado embaixo; o topo vira um degradê escuro para o texto
    rec = ph.crop((700, 0, 1400, h)).resize((900, int(h * 900 / 700)), Image.LANCZOS)
    cv = Image.new("RGB", (900, 1300), (14, 11, 9)); top = 1300 - rec.size[1]
    topo = np.asarray(rec.crop((0, 0, 900, 4)).resize((900, 1)), np.float32).mean(axis=(0, 1))
    g = np.linspace(0, 1, max(top, 1))[:, None, None]; faixa = (np.array([14, 11, 9], np.float32) * (1 - g) + topo * g) * np.ones((1, 900, 1), np.float32)
    if top > 0: cv.paste(Image.fromarray(np.clip(faixa, 0, 255).astype("uint8")), (0, 0))
    cv.paste(rec, (0, top))
    a = np.asarray(cv, np.float32); y = np.linspace(0, 1, 1300)[:, None, None]
    cv = Image.fromarray(np.clip(a * (1 - .45 * np.clip(1 - y / .55, 0, 1) ** 1.1), 0, 255).astype("uint8"))  # topo mais escuro: contraste do texto
    cv.save(os.path.join(D, "hero-m.jpg"), quality=90)
    print("ok (foto)"); raise SystemExit

cena(1920, 900, (1400, 450, 270), [(1010, 700, 120), (1760, 190, 105)], 3).save(os.path.join(D, "hero.jpg"), quality=88)
cena(900, 1300, (450, 960, 290), [(770, 760, 95), (120, 1170, 75)], 4).save(os.path.join(D, "hero-m.jpg"), quality=88)
print("ok")
