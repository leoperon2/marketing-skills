#!/usr/bin/env python3
"""Monta o filme de venda da CB500 (vertical 1080x1920). Edite SEGMENTOS/ANUNCIO e rode de novo."""
import os, subprocess, sys
from PIL import Image, ImageOps, ImageDraw, ImageFont

UP = "/root/.claude/uploads/33cb7b6d-e62a-5fc9-a95d-a66865712c79/"
OUT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(OUT, "work"); os.makedirs(WORK, exist_ok=True)
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONTB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
W, H, FPS = 1080, 1920, 30
MUSICA = UP + "086e2356-adeus_macbook.mp4"   # trilha do VT do MacBook (troque se quiser)

# ---- dados do anúncio (edite) ----
ANUNCIO = ["HONDA CB500 · 1998", "+24 MIL KM", "R$ ______", "(__) _____-____"]

IMG = {i: UP + f for i, f in enumerate("""082c8b46 d3825ebd f742e4f1 591ef5e7 cf700bf0 db8b4092
849f57eb a57691ce f7b03197 f6cd01e2 f99b9937""".split(), 1)}
IMG = {k: v + "-image.jpg" for k, v in IMG.items()}

# foto, duração, fy (corte vertical 0-1), zoom ini->fim, foco x ini->fim, foco y ini->fim, texto
SEG = [
 (3, 4.4, .45, 1.00,1.22, .5,.62, .5,.45, ["Quase trinta.", "E ainda arranco suspiros."]),
 (9, 4.0, .30, 1.22,1.00, .2,.7, .5,.5, ["É verdade.", "Dou inveja nas novinhas."]),
 (11,4.0, .50, 1.00,1.25, .3,.4, .3,.45, ["Vivi bons momentos.", "Colecionei histórias."]),
 (1, 4.4, .30, 1.00,1.30, .5,.45, .4,.5, ["Os anos passaram.", "A vontade de acelerar, não."]),
 (2, 4.0, .55, 1.00,1.20, .8,.4, .5,.5, ["Já cruzei estradas,", "fiquei sem gasolina..."]),
 (8, 5.0, .35, 1.00,1.25, .2,.5, .5,.55, ["Teve uma vez que até","peguei carona. Faltou","energia pra continuar.","(risos)"]),
 (10,4.0, .40, 1.25,1.00, .3,.5, .6,.5, ["Mas faz tempo que não", "tomo banho de chuva."]),
 ("CARD", 3.6, ["MUITO PRAZER.", "HONDA CB500.", "NASCI EM 1998."]),
 (7, 4.0, .45, 1.00,1.22, .3,.6, .5,.5, ["Sou uma garota","bem conservada,","cheia de charme"]),
 (5, 4.0, .40, 1.00,1.30, .6,.2, .6,.7, ["e com uma voz que", "ninguém confunde."]),
 (4, 5.2, .30, 1.25,1.00, .7,.4, .5,.5, ["E sabe de uma coisa?", "Ainda tenho muita", "estrada pela frente."]),
 (3, 4.0, .45, 1.25,1.00, .6,.5, .45,.5, ["Bora me levar", "pra passear?"]),
 ("END", 5.0, ANUNCIO),
]

def txt_png(lines, path, big=False, center=False):
    im = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(im)
    def track(s, f, sp):
        return sum(d.textlength(c, font=f) + sp for c in s) - sp
    def draw(s, f, x, y, sp, fill):
        for c in s:
            d.text((x+3, y+3), c, font=f, fill=(0,0,0,150)) if fill[3] == 255 and not center else None
            d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
    if center:
        sizes = [(FONTB, 52, 8)] + [(FONT, 40, 6)] * (len(lines)-1)
        if len(lines) == 3 and big: sizes = [(FONTB, 66, 12)] * 3
        total = sum(s[1]*1.9 for s in sizes); y = H/2 - total/2
        for s, (fp, sz, sp) in zip(lines, sizes):
            f = ImageFont.truetype(fp, sz); draw(s, f, (W - track(s, f, sp))/2, y, sp, (255,255,255,255)); y += sz*1.9
    else:
        f = ImageFont.truetype(FONTB, 50); sp = 6; y = H - 330 - len(lines)*84
        for s in lines:
            draw(s.upper(), f, 80, y, sp, (255,255,255,255)); y += 84
    im.save(path)

def sh(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

grad = Image.new("RGBA", (W, H), (0,0,0,0)); gp = grad.load()
for y in range(H):
    a = int(max(0, (y - H*0.55) / (H*0.45)) ** 1.5 * 190)
    for x in range(0, W, 1): gp[x, y] = (0,0,0,a)
grad.save(f"{WORK}/grad.png")

clips = []
for n, s in enumerate(SEG):
    out = f"{WORK}/c{n:02d}.mp4"; clips.append(out)
    if s[0] in ("CARD", "END"):
        p = f"{WORK}/t{n:02d}.png"; txt_png(s[2], p, big=(s[0]=="CARD"), center=True)
        dur = s[1]
        sh(["ffmpeg","-y","-f","lavfi","-i",f"color=c=black:s={W}x{H}:r={FPS}:d={dur}","-loop","1","-t",str(dur),"-i",p,
            "-filter_complex",f"[1]format=rgba,fade=t=in:st=0.3:d=0.6:alpha=1,fade=t=out:st={dur-0.5}:d=0.5:alpha=1[t];[0][t]overlay,format=yuv420p",
            "-r",str(FPS),"-c:v","libx264","-crf","18",out]); continue
    k, dur, fy, z0, z1, x0, x1, y0, y1, lines = s
    im = ImageOps.exif_transpose(Image.open(IMG[k]).convert("RGB"))
    iw, ih = im.size; ch = int(iw*16/9); top = int(max(0, ih-ch)*fy)
    im = im.crop((0, top, iw, top+min(ch, ih))).resize((2160, 3840), Image.LANCZOS)
    base = f"{WORK}/p{n:02d}.png"; im.save(base)
    p = f"{WORK}/t{n:02d}.png"; txt_png(lines, p)
    N = int(dur*FPS)
    z = f"{z0}+({z1}-{z0})*on/{N}"
    fx = f"({x0}+({x1}-{x0})*on/{N})"; fyy = f"({y0}+({y1}-{y0})*on/{N})"
    zp = f"zoompan=z='{z}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fyy}':d={N}:s={W}x{H}:fps={FPS}"
    sh(["ffmpeg","-y","-i",base,"-i",f"{WORK}/grad.png","-loop","1","-t",str(dur),"-i",p,
        "-filter_complex",
        f"[0]{zp},format=rgba[v];[v][1]overlay[g];[2]format=rgba,fade=t=in:st=0.4:d=0.5:alpha=1,fade=t=out:st={dur-0.5}:d=0.4:alpha=1[t];[g][t]overlay,fade=t=in:st=0:d=0.2,format=yuv420p",
        "-t",str(dur),"-r",str(FPS),"-c:v","libx264","-crf","18",out])

lst = f"{WORK}/list.txt"; open(lst,"w").write("".join(f"file '{c}'\n" for c in clips))
total = sum(s[1] for s in SEG)
sh(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-i",MUSICA,
    "-filter_complex",f"[1:a]atrim=0:{total},afade=t=in:d=1,afade=t=out:st={total-2.5}:d=2.5[a]",
    "-map","0:v","-map","[a]","-t",str(total),"-c:v","libx264","-crf","24","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
    os.path.join(OUT, "cb500_filme_venda.mp4")])
print("ok", total)
