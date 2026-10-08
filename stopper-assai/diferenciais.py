"""Cena 'Diferenciais': textos refeitos em Montserrat, cada frase no MAIOR tamanho que cabe em 384 px.
Gera os itens (camadas 21..) como PNGs com transparencia, ja no tamanho final (escala 1.0).
Para editar textos, mexa em ITEMS: cada item = lista de linhas; cada linha = lista de (texto, estilo).
Estilos: 'n' texto branco, 'h' destaque (caixa amarela + texto azul)."""
import os
from PIL import Image, ImageDraw, ImageFont

W = 384
MARGIN = 14                        # margem lateral
PAD = 6                            # folga lateral da caixa amarela
MAX_FS, LH_RATIO = 76, 1.2         # maior fonte permitida; altura de linha = fonte * 1.2
Y_TOP, Y_BOTTOM, MAX_GAP = 530, 1510, 100   # faixa vertical dos textos (px) e espaco maximo entre itens
YELLOW, BLUE, WHITE = (255, 200, 0), (20, 40, 215), (255, 255, 255)
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

ITEMS = [
    [[("Ingredientes", 'n')], [("selecionados", 'h')]],
    [[("Carne", 'h')], [("in natura", 'h')]],
    [[("+ Energia", 'h')]],
    [[("Ideal para", 'h')], [("treinos", 'h')], [("e recompensas", 'n')]],
    [[("Sem corantes", 'n')], [("Sem conservantes", 'n')], [("Sem glúten", 'n')], [("Sem transgênicos", 'n')]],
]
WEIGHT = {'n': 'SemiBold', 'h': 'Bold'}

def _font(st, size): return ImageFont.truetype(f"{FONTS}/Montserrat-{WEIGHT[st]}.ttf", size)

def _line_width(line, size):
    return sum(_font(st, size).getlength(t) for t, st in line)

def _fit(lines):
    """Maior tamanho de fonte (px) em que a linha mais larga ainda cabe."""
    avail = W - 2*MARGIN - 2*PAD
    size = MAX_FS
    while size > 12 and max(_line_width(l, size) for l in lines) > avail: size -= 1
    return size

def _render_item(lines, S=2):
    size = _fit(lines); lh = round(size * LH_RATIO); h = lh * len(lines) + 8
    im = Image.new('RGBA', (W*S, h*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, line in enumerate(lines):
        y = 4 + li * lh
        x = MARGIN + PAD
        for t, st in line:
            f = _font(st, size * S); w = f.getlength(t) / S
            if st == 'h':
                d.rectangle([(x - PAD)*S, (y + 2)*S, (x + w + PAD)*S, (y + lh - 2)*S], fill=YELLOW)
            d.text((x*S, (y + (lh - size)/2 - size*0.12)*S), t, font=f, fill=BLUE if st == 'h' else WHITE)
            x += w
    return im.resize((W, h), Image.LANCZOS), size

def build(outdir):
    """Grava 21.png.. e devolve ({camada: (x, y, escala)}, [tamanhos de fonte])."""
    rend = [_render_item(it) for it in ITEMS]
    total = sum(im.height for im, _ in rend)
    gap = min(MAX_GAP, (Y_BOTTOM - Y_TOP - total) / (len(rend) - 1))
    y = Y_TOP + ((Y_BOTTOM - Y_TOP) - (total + gap * (len(rend) - 1))) / 2
    place = {}
    for k, (im, size) in enumerate(rend):
        im.save(f"{outdir}/{21+k}.png"); place[21 + k] = (0, round(y), 1.0); y += im.height + gap
    return place, [s for _, s in rend]
