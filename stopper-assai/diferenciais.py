"""Extrai titulo + 9 itens de 'Diferenciais Competitivos' do PSD como PNGs com transparencia.
Os destaques usam modo Exclusion; compomos sobre preto e sobre branco e recuperamos o alfa."""
import numpy as np
from PIL import Image
from psd_tools import PSDImage

CUTS = [340, 485, 635, 735, 835, 935, 1080, 1235, 1380, 1590]   # limites verticais entre os 9 itens (PSD 1080x1920)

def _render(psd, backdrop):
    out = np.full((psd.height, psd.width, 3), backdrop, dtype=float)
    def over(layer, mode):
        im = layer.composite()
        if im is None: return
        im = np.asarray(im.convert('RGBA'), dtype=float) / 255
        x0, y0 = max(layer.left, 0), max(layer.top, 0)
        sx, sy = x0 - layer.left, y0 - layer.top
        h = min(im.shape[0] - sy, psd.height - y0); w = min(im.shape[1] - sx, psd.width - x0)
        if h <= 0 or w <= 0: return
        src = im[sy:sy+h, sx:sx+w]; a = src[..., 3:4]; cs = src[..., :3]
        cb = out[y0:y0+h, x0:x0+w]
        blended = cb + cs - 2*cb*cs if mode == 'exclusion' else cs
        out[y0:y0+h, x0:x0+w] = (1-a)*cb + a*blended
    for l in psd:
        if l.name == 'Diferenciais Competitivos' or l.name.startswith('Elaborado'): over(l, 'normal')
    for l in psd:
        if l.name.startswith('Rectangle 1'): over(l, 'exclusion')
    return out

def export(psd_path, outdir):
    psd = PSDImage.open(psd_path)
    b, w = _render(psd, 0.0), _render(psd, 1.0)
    alpha = np.clip(1 - (w - b).mean(axis=2), 0, 1)
    color = np.where(alpha[..., None] > 1e-3, b / np.maximum(alpha[..., None], 1e-3), 0)
    rgba = np.dstack([np.clip(color, 0, 1), alpha])
    full = Image.fromarray((rgba * 255).astype('uint8'), 'RGBA')
    sizes = []
    def save(box, n):
        part = full.crop(box); bb = part.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
        part = part.crop(bb); part.save(f"{outdir}/{n:02d}.png"); sizes.append(part.size)
    save((0, 60, 1080, 300), 20)                                  # titulo
    for i in range(9):
        save((0, CUTS[i], 1080, CUTS[i+1]), 21 + i)               # itens 1..9
    return sizes
