"""Anima o PSD do Stopper Digital Assai e entrega MP4 384x1920, H.264, sem audio.
Uso:  python animate_psd.py arquivo.psd saida.mp4
Requer: pip install psd-tools scipy numpy pillow   e   ffmpeg no PATH.
O PSD original e 1080x1920; aqui as camadas sao REPOSICIONADAS num layout vertical 384x1920.
O mapeamento vale para o PSD 01.psd (20 camadas, ordem de baixo para cima)."""
import glob, math, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from psd_tools import PSDImage

W, H, FPS, T = 384, 1920, 30, 15.0

def export_layers(psd_path, outdir):
    i = 0
    def go(layers):
        nonlocal i
        for l in layers:
            if l.kind == 'curves': continue
            if l.is_group(): go(l); continue
            im = l.composite()
            if im is None: continue
            im.convert('RGBA').save(f"{outdir}/{i:02d}.png")
            i += 1
    psd = PSDImage.open(psd_path)
    go(psd)
    # Fundo: o PSD usa modos de mesclagem que o psd-tools nao reproduz (circulos/brilho), entao
    # montamos o fundo: textura escura limpa do BG repetida em espelho + canto vermelho recriado.
    import numpy as np
    bg = psd.composite(layer_filter=lambda l: l.name == 'BG').convert('RGB')
    patch = bg.crop((300, 880, 684, 1190))                      # trecho escuro sem circulos
    flip = patch.transpose(Image.FLIP_TOP_BOTTOM)
    base = Image.new('RGB', (W, H))
    for k in range(7):
        base.paste(patch if k % 2 == 0 else flip, (0, k * patch.height))
    tri = Image.open(f"{outdir}/09.png").getchannel('A')        # mascara do triangulo (Rectangle 2)
    tri = tri.resize((int(tri.width*.5), int(tri.height*.5)), Image.BILINEAR)
    tw, th = tri.size
    yy, xx = np.mgrid[0:th, 0:tw].astype(float)
    k = np.clip((xx/tw)*.5 + (yy/th)*.5, 0, 1)[..., None]       # vermelho -> laranja
    col = np.array([210, 25, 20]) * (1-k) + np.array([255, 120, 20]) * k
    d = np.sqrt((xx-90)**2 + (yy-35)**2)[..., None]             # brilho central
    col = np.clip(col + np.clip(1-d/110, 0, 1) * np.array([60, 130, 40]), 0, 255)
    corner = Image.fromarray(col.astype('uint8')).convert('RGBA')
    corner.putalpha(tri)
    base = base.convert('RGBA'); base.alpha_composite(corner, (0, 0))
    base.save(f"{outdir}/00.png")
    for k in (9, 10, 14):                                        # absorvidos no fundo
        Image.new('RGBA', (1, 1), (0, 0, 0, 0)).save(f"{outdir}/{k:02d}.png")
    return i

# camada: (x, y, escala) do canto superior esquerdo ja escalado, no canvas 384x1920
def group(src, s=.62, ox=-10, oy=32):  # grupo NOVO: posicao original -> canvas
    return (ox + src[0]*s, oy + src[1]*s, s)
PLACE = {
 0: (0, 0, 1.0),                # fundo montado
 10: (0, 0, 1.0), 9: (0, 0, 1.0),  # absorvidos no fundo
 2: (-40, 600, .44),             # tabua com carne (sangra na direita)
 4: (10, 300, .46),              # pack barbecue
 6: (30, 835, .5),               # CANISTER
 7: (6, 875, .48),               # BIFINHOS
 5: (60, 1025, .75),             # tagline
 1: (-205, 1410, .46),            # tabua/calabresa (sangra na direita)
 3: (10, 1120, .5),              # pack calabresa
 8: (48, 1810, .85),             # logo
 14: group((-111, -93)), 15: group((75, 71)), 13: group((64, 154)), 16: group((85, 182)),
 11: group((108, 240)), 12: group((137, 253)), 17: group((100, 96)), 18: group((347, 129)), 19: group((63, 356)),
}
def pulse(t, t0, period, dur):
    # pulso periodico: 0 -> 1 -> 0 durante `dur` s, repetido a cada `period` s a partir de t0
    if t < t0: return 0.0
    u = (t - t0) % period
    return math.sin(math.pi * u / dur) if u < dur else 0.0
def clamp(x): return max(0, min(1, x))
def out_cubic(t): return 1-(1-t)**3
def out_back(t, c=1.70158):
    t -= 1; return 1+(c+1)*t**3+c*t**2
# n: (inicio, duracao, dx, dy, escala0, easing)
A = {1:(.5,.8,300,0,1,out_cubic), 2:(.15,.7,-250,0,1,out_cubic), 3:(.6,.8,-150,200,.8,out_back), 4:(.3,.8,150,-200,.8,out_back),
 5:(1.8,.4,0,30,1,out_cubic), 6:(1.1,.4,-60,0,1,out_cubic), 7:(1.3,.5,0,0,1.5,out_back), 8:(2.1,.4,0,0,.8,out_cubic),
 9:(0,.5,0,0,1,out_cubic), 10:(0,.5,0,0,1,out_cubic),
 17:(.9,.4,0,0,.3,out_back), 15:(1.0,.4,-150,0,1,out_cubic), 13:(1.15,.4,-150,0,1,out_cubic), 16:(1.3,.4,-150,0,1,out_cubic),
 11:(1.45,.4,-150,0,1,out_cubic), 12:(1.55,.35,0,0,.5,out_back), 18:(1.2,.4,120,0,1,out_cubic), 19:(1.6,.4,-120,0,1,out_cubic), 14:(1.0,.5,0,0,.6,out_cubic)}
S1_OUT = (6.0, .6)   # cena 1 (produtos) sai em 6,0 s; fundo (0) e logo (8) permanecem
SCENE1 = {3,5,6,7,11,12,13,15,16,17,18,19}   # somem na troca de cena; 1,2,4 (embalagem/tabuas) se movem
MOVE_T = (6.0, .8)   # inicio e duracao da transicao das embalagens/tabuas para a cena 2
MOVE = {4: (18, 10, .44), 2: (-50, 330, .36), 1: (-150, 1540, .42)}   # destino (x, y, escala) na cena 2
A.update({21+i: (7.2+i*.65,.4,-40,0,1,out_cubic) for i in range(9)})
FADE = {21,22,23,24,25,26,27,28,29,5,6,7,8,9,10,17,15,13,16,11,12,18,19,14}

def run(layerdir, out):
    img = {int(os.path.basename(f)[:2]): Image.open(f).convert('RGBA') for f in sorted(glob.glob(layerdir+'/*.png'))}
    p = subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',out], stdin=subprocess.PIPE)
    for fr in range(int(T*FPS)):
        t = fr/FPS
        cv = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        for n in sorted(img):
            im = img[n]; x, y, bs = PLACE[n]
            if n in MOVE:
                k = clamp((t - MOVE_T[0]) / MOVE_T[1]); k = k*k*(3 - 2*k)
                x, y, bs = (x + (MOVE[n][0]-x)*k, y + (MOVE[n][1]-y)*k, bs + (MOVE[n][2]-bs)*k)
            w, h = im.size; w, h = w*bs, h*bs
            s = 1.0; dx = dy = 0; a = 1.0
            if n in A:
                st, d, ax, ay, s0, e = A[n]; k = e(clamp((t-st)/d))
                dx, dy, s = ax*(1-k), ay*(1-k), s0+(1-s0)*k
                a = clamp((t-st)/(d*.7)) if n in FADE else (clamp((t-st)/.2) if n in (1,2,3,4) else 1)
            if t > 1.4:
                ph = t*math.pi
                if n == 3: dy += 5*math.sin(ph+1)
                if n == 4: dy += 5*math.sin(ph)
                if n == 7: s *= 1+.012*math.sin(ph)
                if n == 7: s *= 1+.05*pulse(t, 4.0, 3.0, .7)
                if n == 17: s *= 1+.03*math.sin(ph*1.5)+.08*pulse(t, 5.5, 3.0, .7)
                if n == 8: s *= 1+.07*pulse(t, 6.0, 4.0, .8)
            if n == 14 and t > 1.5: a *= .6+.4*math.sin(t*2*math.pi/1.3)**2
            if n == 0: s = 1+.05*t/T
            if n in SCENE1: a *= 1 - clamp((t - S1_OUT[0]) / S1_OUT[1])
            if a <= 0: continue
            sc = bs*s
            im2 = im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))), Image.BILINEAR)
            if a < 1:
                im2.putalpha(im2.getchannel('A').point(lambda v: int(v*a)))
            ox, oy = int(x+w/2+dx-im2.width/2), int(y+h/2+dy-im2.height/2)
            sx, sy = max(0, -ox), max(0, -oy)
            ex, ey = min(im2.width, W-ox), min(im2.height, H-oy)
            if ex > sx and ey > sy:
                cv.alpha_composite(im2.crop((sx, sy, ex, ey)), dest=(ox+sx, oy+sy))
        p.stdin.write(cv.convert('RGB').tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    # uso: animate_psd.py produtos.psd saida.mp4   (a cena 'Diferenciais' e gerada por diferenciais.py)
    psd, out = sys.argv[1], sys.argv[-1]
    tmp = tempfile.mkdtemp()
    n = export_layers(psd, tmp)
    assert n == 20, f"esperava 20 camadas, achei {n}; o mapeamento foi feito para o PSD 01.psd"
    import diferenciais
    place, _ = diferenciais.build(tmp)
    PLACE.update(place)
    run(tmp, out)
