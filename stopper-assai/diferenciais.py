"""Cena 'Diferenciais': textos refeitos em tamanho grande (Montserrat) para caber legivel em 384 px de largura.
Gera titulo (camada 20) e os itens (camadas 21..) como PNGs com transparencia, ja no tamanho final (escala 1.0).
Para editar textos/tamanhos, mexa em ITEMS e nas constantes abaixo."""
import os
from PIL import Image, ImageDraw, ImageFont

W = 384
MARGIN = 14                      # margem lateral
FS, FS_SUB, LH = 44, 34, 54      # tamanho do texto, do subtexto, altura da linha
Y_TOP, Y_BOTTOM = 220, 1740      # faixa vertical (px) onde os 9 itens sao distribuidos
YELLOW, BLUE, WHITE = (255, 200, 0), (20, 40, 215), (255, 255, 255)
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# (texto, estilo): 'n' normal, 'h' destaque (caixa amarela + texto azul), 's' subtexto menor
ITEMS = [
    [("Ingredientes ", 'n'), ("selecionados", 'h')],
    [("Carne in natura", 'h')],
    [("Energia ", 'h'), ("para brincar e treinar", 'n')],
    [("Ideal para treinos ", 'h'), ("e recompensas", 'n')],
    [("Sem corantes nem conservantes", 'n')],
    [("Sem glúten ", 'n'), ("mais digestível", 's')],
    [("Sem transgênicos", 'n')],
]

def _font(w, size): return ImageFont.truetype(f"{FONTS}/Montserrat-{w}.ttf", size)
FONT = {'n': _font('SemiBold', FS), 'h': _font('Bold', FS), 's': _font('SemiBold', FS_SUB)}

def _layout(runs, maxw):
    """Quebra as palavras em linhas: cada linha = lista de (palavra, estilo, x)."""
    words = [(w, st) for txt, st in runs for w in txt.split()]
    lines, cur, x = [], [], 0
    sp = FONT['n'].getlength(' ')
    for w, st in words:
        wl = FONT[st].getlength(w)
        if cur and (x + wl > maxw or (st == 's' and cur[-1][1] != 's')):
            lines.append(cur); cur, x = [], 0
        cur.append((w, st, x)); x += wl + sp
    lines.append(cur)
    return lines

def _render_item(runs, S=2):
    maxw = W - 2*MARGIN
    lines = _layout(runs, maxw)
    h = LH * len(lines) + 8
    im = Image.new('RGBA', (W*S, h*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, line in enumerate(lines):
        y = li * LH + 4
        # caixa de destaque contigua por linha
        i = 0
        while i < len(line):
            if line[i][1] == 'h':
                j = i
                while j + 1 < len(line) and line[j+1][1] == 'h': j += 1
                x0 = line[i][2]; x1 = line[j][2] + FONT['h'].getlength(line[j][0])
                d.rectangle([(MARGIN + x0 - 6)*S, (y + 2)*S, (MARGIN + x1 + 6)*S, (y + LH - 2)*S], fill=YELLOW)
                i = j + 1
            else: i += 1
        for w, st, x in line:
            col = BLUE if st == 'h' else WHITE
            dy = 5 if st == 's' else 0
            f = ImageFont.truetype(FONT[st].path, FONT[st].size * S)
            d.text(((MARGIN + x)*S, (y + 3 + dy)*S), w, font=f, fill=col)
    return im.resize((W, h), Image.LANCZOS)

def build(outdir):
    """Grava 20.png..29.png e devolve {camada: (x, y, escala)} para o PLACE."""
    S = 2
    title = Image.new('RGBA', (W*S, 100*S), (0, 0, 0, 0)); d = ImageDraw.Draw(title)
    f = _font('ExtraBold', 56*S); tw = f.getlength("Diferenciais")
    d.text(((W*S - tw)/2, 8*S), "Diferenciais", font=f, fill=WHITE)
    d.rectangle([(W*S/2 - 50*S), 86*S, (W*S/2 + 50*S), 92*S], fill=YELLOW)
    title.resize((W, 100), Image.LANCZOS).save(f"{outdir}/20.png")
    items = [_render_item(r) for r in ITEMS]
    gap = (Y_BOTTOM - Y_TOP - sum(i.height for i in items)) / (len(items) - 1)
    place, y = {20: (0, 70, 1.0)}, Y_TOP
    for k, im in enumerate(items):
        im.save(f"{outdir}/{21+k}.png"); place[21 + k] = (0, round(y), 1.0); y += im.height + gap
    return place, gap
