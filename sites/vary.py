#!/usr/bin/env python3
"""Varia o layout de cada site para que negócios do mesmo ramo/cidade não fiquem iguais.
Uso: python3 vary.py [slug ...]   (sem argumentos, todos)
Lê <slug>/index.html, remove o bloco anterior (<!--vary:start-->...<!--vary:end-->) e injeta um novo
com fonte, acento, hero, moldura, cabeçalho, galeria, títulos, formas, prova social, faixa, ordem e animação.
Idempotente. Cada ramo (kind) sorteia combinações que maximizam a distância entre sites do mesmo ramo."""
import glob, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"don-alberttoni", "suzana-dias-studio", "marshals-tattoo", "win-hamburgueria", "pet-shop-agropal"}  # modelo e quem já tem site
G = "max(16px, env(safe-area-inset-left, 0px))"

# ---------------------------------------------------------------- fontes de título (a 0 é a original do ramo)
FONTS = {
 "barber": [None, ("Bebas+Neue", "Bebas Neue", "Impact, sans-serif", 400), ("Playfair+Display+SC:wght@700", "Playfair Display SC", "Georgia, serif", 700), ("Abril+Fatface", "Abril Fatface", "Georgia, serif", 400), ("Rye", "Rye", "Georgia, serif", 400)],
 "tattoo": [None, ("Bungee", "Bungee", "Impact, sans-serif", 400), ("Staatliches", "Staatliches", "Impact, sans-serif", 400), ("Rye", "Rye", "Georgia, serif", 400)],
 "burger": [None, ("Lilita+One", "Lilita One", "Arial Black, sans-serif", 400), ("Chango", "Chango", "Arial Black, sans-serif", 400), ("Titan+One", "Titan One", "Arial Black, sans-serif", 400)],
 "salon": [None, ("Cormorant+Garamond:wght@600", "Cormorant Garamond", "Georgia, serif", 600), ("Playfair+Display:wght@600", "Playfair Display", "Georgia, serif", 600), ("Italiana", "Italiana", "Georgia, serif", 400), ("Marcellus", "Marcellus", "Georgia, serif", 400)],
 "pet": [None, ("Baloo+2:wght@700", "Baloo 2", "Trebuchet MS, sans-serif", 700), ("Chewy", "Chewy", "Trebuchet MS, sans-serif", 400), ("Sniglet:wght@800", "Sniglet", "Trebuchet MS, sans-serif", 800)],
 "auto": [None, ("Oswald:wght@600", "Oswald", "Impact, sans-serif", 600), ("Bebas+Neue", "Bebas Neue", "Impact, sans-serif", 400), ("Russo+One", "Russo One", "Impact, sans-serif", 400)],
 "clinic": [None, ("Cormorant+Garamond:wght@600", "Cormorant Garamond", "Georgia, serif", 600), ("DM+Serif+Display", "DM Serif Display", "Georgia, serif", 400), ("Lora:wght@600", "Lora", "Georgia, serif", 600)],
}

# ---------------------------------------------------------------- acentos (claro, escuro): accent, ink, salmon
ACCENTS = [None,
 (("#0f7a73", "#ffffff", "#f2b872"), ("#3cc4b8", "#0d1514", "#c58a3f")),
 (("#b3202f", "#ffffff", "#f0a5ac"), ("#ef6b79", "#1a0d10", "#a85660")),
 (("#3b4fc4", "#ffffff", "#f2c14e"), ("#8a9bff", "#0e1022", "#b8922e")),
 (("#c2570c", "#ffffff", "#e9d27a"), ("#f2873a", "#1a0f06", "#b79a3a")),
 (("#b0287d", "#ffffff", "#f0b6d6"), ("#ee6fba", "#1c0d16", "#a86190")),
 (("#2c7a3f", "#ffffff", "#e3c76b"), ("#58c773", "#0c150e", "#b39a40"))]

IMG = ".hero > figure > img:first-child"
RESET = "border:0; box-shadow:none; outline:0; transform:none;"

HERO = [  # 0 padrão (texto à esquerda, foto à direita)
 "",
 "@media (min-width: 821px) { .hero { grid-template-columns: 1fr 1.05fr; } .hero > figure { order: -1; } }",
 f""".hero {{ position: relative; display: block; min-height: clamp(500px, 62vw, 640px); padding: 0; margin-top: 28px; }}
 .hero > figure {{ position: absolute; inset: 0; margin: 0; border-radius: var(--hrad); }}
 {IMG} {{ width: 100%; height: 100%; aspect-ratio: auto; {RESET} border-radius: var(--hrad); filter: brightness(.5) saturate(1.1); }}
 .hero > div:first-child {{ position: relative; z-index: 2; min-height: inherit; max-width: 640px; padding: clamp(28px, 6vw, 64px); display: flex; flex-direction: column; justify-content: flex-end; color: #fff; }}
 .hero h1 {{ color: #fff; }} .hero .eyebrow, .hero .lede, .hero .score {{ color: rgba(255,255,255,.88); }} .hero .score strong {{ color: #fff; }} .hero .stars {{ color: var(--salmon); }}
 .hero .btn.ghost {{ color: #fff; border-color: #fff; }}
 .hero img.logo-stamp, .hero .seal {{ left: auto; right: 28px; bottom: -30px; }}
 @media (max-width: 820px) {{ .hero {{ min-height: 540px; }} .hero > div:first-child {{ padding-bottom: 76px; }} .hero img.logo-stamp, .hero .seal {{ right: 14px; }} }}""",
 f""".hero {{ grid-template-columns: 1fr; text-align: center; gap: 44px; padding-bottom: 76px; }}
 .hero > div:first-child {{ display: flex; flex-direction: column; align-items: center; }} .hero .lede {{ margin-inline: auto; }} .hero .cta, .hero .score {{ justify-content: center; }}
 {IMG} {{ aspect-ratio: 16 / 9; }}
 .hero img.logo-stamp, .hero .seal {{ left: 50%; margin-left: -68px; bottom: -40px; }} @media (max-width: 820px) {{ .hero img.logo-stamp, .hero .seal {{ left: 50%; margin-left: -52px; }} }}""",
 f""".hero {{ grid-template-columns: 1fr; gap: 56px; padding-top: 28px; }} .hero > figure {{ order: -1; margin-bottom: 8px; }}
 {IMG} {{ aspect-ratio: 21 / 9; }} @media (max-width: 820px) {{ {IMG} {{ aspect-ratio: 4 / 3; }} }}
 .hero > div:first-child {{ max-width: 760px; }} .hero h1 {{ font-size: clamp(36px, 6vw, 62px); }}""",
 f"""@media (min-width: 821px) {{ .hero {{ grid-template-columns: 1.2fr .8fr; }} }}
 {IMG} {{ aspect-ratio: 4 / 5; max-height: 560px; {RESET} border-radius: 999px 999px 18px 18px; }}
 .hero img.logo-stamp, .hero .seal {{ left: auto; right: 6px; }}""",
]
HERO.append("""html { overflow-x: clip; }
 .hero { position: relative; display: block; width: 100vw; margin: 0 calc(50% - 50vw); padding: 0; min-height: clamp(540px, 84vh, 800px); overflow: hidden; --hp: 0; }
 .hero > figure { position: absolute; inset: 0; margin: 0; }
 IMG { width: 100%; height: 100%; aspect-ratio: auto; object-fit: cover; border: 0; box-shadow: none; outline: 0; filter: brightness(.92);
   transform: translate3d(0, calc(var(--hp) * 7%), 0) scale(calc(1.04 + var(--hp) * .1)); transform-origin: 50% 20%; will-change: transform;
   -webkit-mask-image: linear-gradient(to bottom, #000 68%, transparent 100%); mask-image: linear-gradient(to bottom, #000 68%, transparent 100%); }
 .hero > div:first-child { position: relative; z-index: 2; min-height: inherit; padding: clamp(56px, 10vh, 110px) max(16px, calc((100vw - 1080px) / 2)); display: flex; flex-direction: column; justify-content: flex-end; color: #fff;
   opacity: calc(1 - var(--hp) * 1.15); transform: translate3d(0, calc(var(--hp) * -56px), 0); }
 .hero > div:first-child > * { max-width: 620px; }
 .hero h1 { color: #fff; font-size: clamp(44px, 8vw, 96px); text-shadow: 0 2px 24px rgba(0,0,0,.45); } .hero .eyebrow, .hero .lede, .hero .score { color: rgba(255,255,255,.9); } .hero .score strong { color: #fff; } .hero .stars { color: var(--salmon); }
 .hero .btn.ghost { color: #fff; border-color: #fff; }
 .hero img.logo-stamp, .hero .seal { left: auto; right: max(16px, calc((100vw - 1080px) / 2)); bottom: 44px; }
 .stripe { display: none; }
 @media (max-width: 820px) {
   .hero { min-height: 590px; margin-bottom: -18px; } IMG { object-position: var(--foco, 50% 50%); -webkit-mask-image: linear-gradient(to bottom, #000 86%, transparent 100%); mask-image: linear-gradient(to bottom, #000 86%, transparent 100%); }
   main.wrap:has(#casa) > #fotos { padding-top: 6px !important; } main.wrap:has(#casa) > #casa { padding-top: 24px; }
   .hero > div:first-child { justify-content: flex-start; padding-top: 30px; padding-bottom: 0; }
   .hero > div:first-child > * { max-width: 100%; }
   .hero .eyebrow { font-size: 10.5px; letter-spacing: .1em; opacity: .72; margin-bottom: 10px; text-wrap: balance; }
   .hero h1 { font-size: clamp(46px, 14.5vw, 68px); line-height: 1; margin-bottom: 14px; }
   .hero .lede { font-size: 15px; line-height: 1.45; color: rgba(255,255,255,.78); max-width: 32ch; margin: 0 0 18px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
   .hero .cta { display: none; }
   .hero .score { margin-top: 4px; gap: 10px; font-size: 13px; } .hero .score strong { font-size: 24px; } .hero .stars { font-size: 13px; letter-spacing: 2px; }
   .hero img.logo-stamp, .hero .seal { width: 100px; height: 100px; border-width: 4px; box-shadow: 0 4px 0 var(--salmon); bottom: 18px; right: 16px; }
 }
 @media (prefers-reduced-motion: reduce) { .hero > div:first-child { opacity: 1 !important; transform: none !important; } .hero > figure > img:first-child { transform: scale(1.04) !important; } }""".replace("IMG", IMG))
SCRIPT_BLEED = """<script>(function(){function init(){var h=document.querySelector('.hero');if(!h)return;var t=0;function f(){t=0;var p=Math.min(Math.max(window.scrollY/Math.max(h.offsetHeight,1),0),1);h.style.setProperty('--hp',p.toFixed(3));}window.addEventListener('scroll',function(){if(!t)t=requestAnimationFrame(f);},{passive:true});f();}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();})();</script>"""
NEEDS_FIG = {1, 2, 3, 4, 5, 6}

FRAME = [
 "",
 f"{IMG} {{ border: 0; border-radius: 22px; box-shadow: 0 22px 44px -18px rgba(0,0,0,.45); }}",
 f"{IMG} {{ border: 10px solid #fff; border-bottom-width: 38px; box-shadow: 0 14px 30px -10px rgba(0,0,0,.4); transform: rotate(-2.2deg); }}",
 f"{IMG} {{ border: 0; box-shadow: none; outline: 3px solid var(--accent); outline-offset: 12px; }}",
 f"{IMG} {{ border: 0; box-shadow: -14px 14px 0 var(--accent); }}",
]

HEADER = [
 "",
 "header.bar { background: var(--surface); color: var(--ink); border-bottom: 2px solid var(--line); } body::before { background: var(--surface); }",
 "header.bar { background: var(--accent); color: var(--accent-ink); } body::before { background: var(--accent); } .bar .btn { background: var(--accent-ink); color: var(--accent); border-color: var(--accent-ink); } .brand img { border-color: var(--accent-ink); }",
 ".bar-in { display: grid; grid-template-columns: 1fr auto 1fr; } nav { order: 1; justify-self: start; } .brand { order: 2; justify-self: center; } .bar .btn { order: 3; justify-self: end; } @media (max-width: 820px) { .bar-in { display: flex; } .brand { order: 0; } .bar .btn { order: 0; } }",
]

GALLERY = [
 "",
 ".mosaic { gap: 4px; } .tile { border-radius: 0; } @media (max-width: 820px) { .mosaic { gap: 4px; } }",
 ".mosaic { gap: 12px; grid-auto-rows: 220px; } .tile { border-radius: 18px; } @media (max-width: 820px) { .mosaic { gap: 8px; grid-auto-rows: 176px; } }",
 ".mosaic { gap: 18px; } .tile { outline: 5px solid var(--surface); outline-offset: -5px; box-shadow: 0 6px 0 var(--salmon); } @media (max-width: 820px) { .mosaic { gap: 12px; } }",
 ".mosaic { gap: 8px; } .tile img { filter: grayscale(.9) contrast(1.05); } .tile:hover img, .tile:focus-visible img { filter: none; } @media (max-width: 820px) { .tile img { filter: grayscale(.5); } }",
]

HEADING = [
 "",
 "h2 { text-transform: uppercase; letter-spacing: .05em; font-size: clamp(26px, 4vw, 36px); } h2::after { content: ''; display: block; width: 64px; height: 4px; background: var(--accent); margin-top: 14px; }",
 "#fotos h2, #fotos .sub, #horarios h2, .proof h2, .proof .eyebrow { text-align: center; margin-inline: auto; } #fotos h2::after, #horarios h2::after, .proof h2::after { content: ''; display: block; width: 48px; height: 3px; background: var(--accent); margin: 14px auto 0; } .proof-top { justify-content: center; }",
 "h2::before { content: ''; display: block; width: 56px; height: 6px; background: var(--accent); margin-bottom: 14px; } .final h2::before { margin-inline: auto; }",
]

SHAPE = [
 "",
 ".btn { border-radius: 999px; } .card, .svc, blockquote { border-radius: 24px; } .status, .tags li { border-radius: 999px; } :root { --hrad: 30px; }",
 ".btn { border-radius: 10px; } .card, .svc, blockquote { border-radius: 12px; } .tags li { border-radius: 8px; } .status { border-radius: 6px; } :root { --hrad: 14px; }",
 ".btn { border-radius: 0; text-transform: uppercase; letter-spacing: .06em; font-size: 15px; } .card, .svc, blockquote { border-width: 2px; }",
]

PROOF = [
 "",
 ".proof { background: var(--surface); color: var(--ink); border-block: 1px solid var(--line); } .proof .eyebrow, blockquote cite { color: var(--accent); } .fill { background: var(--accent); } .track { background: var(--line); } blockquote { border-color: var(--line); background: var(--bg); } .reply { color: var(--ink-soft); border-color: var(--line); }",
 ".proof { background: var(--accent); color: var(--accent-ink); } .proof .eyebrow, blockquote cite { color: var(--accent-ink); opacity: .85; } .fill { background: var(--accent-ink); } .reply { color: var(--accent-ink); }",
 ".quotes { grid-template-columns: 1fr; max-width: 760px; } blockquote { border: 0; border-left: 5px solid var(--salmon); padding: 6px 0 6px 22px; } blockquote p { font-size: 19px; }",
]

STRIPE = ["", ".stripe { height: 6px; }", ".stripe { display: none; }"]
INFO = [
 "",
 ".card { border: 0; box-shadow: 0 14px 34px -16px rgba(0,0,0,.35); }",
 ".info:not(.single) { grid-template-columns: 1fr; max-width: 680px; margin-inline: auto; }",
]
ABOUT = [
 "",
 ".about:not(.one) > .pull { order: -1; }",
 ".services { grid-template-columns: 1fr; } .svc { min-height: 0; flex-direction: row; align-items: center; border-top: 1px solid var(--line); border-left: 5px solid var(--accent); }",
 ".about:not(.one) { grid-template-columns: 1fr; } .about > .pull { order: -1; text-align: center; border: 0; padding: 0 0 8px; font-size: clamp(26px, 4vw, 40px); max-width: 24ch; margin-inline: auto; }",
]
ORDER = ["", "main.wrap:has(#casa) { display: flex; flex-direction: column; } main.wrap:has(#casa) > #fotos { order: -1; padding-top: 48px !important; }"]
ANIM = [
 "",
 ".js .rv { transform: scale(.92); }",
 "html { overflow-x: clip; } body { overflow-x: clip; } .js .rv { transform: translateX(calc(var(--dir, -1) * 48px)); } .js .rv:nth-child(even) { --dir: 1; }",
 ".js .rv { transform: translateY(72px); filter: blur(8px); transition: opacity .8s ease, transform 1s cubic-bezier(.2, .7, .2, 1), filter .8s; } .js .rv.in { filter: none; }",
]

DIMS = ["font", "accent", "hero", "frame", "header", "gallery", "heading", "shape", "proof", "stripe", "info", "about", "order", "anim"]
SIZE = dict(font=None, accent=len(ACCENTS), hero=6, frame=len(FRAME), header=len(HEADER), gallery=len(GALLERY), heading=len(HEADING),
            shape=len(SHAPE), proof=len(PROOF), stripe=len(STRIPE), info=len(INFO), about=len(ABOUT), order=len(ORDER), anim=len(ANIM))


OVERRIDE = {"charles-tattoo-piercing": {"hero": 6}}  # escolhas à mão (capa panorâmica escura)
CAPA_ESCURA = set()
FORCE_DARK = {"charles-tattoo-piercing"}  # sempre tema escuro, ignorando o tema do aparelho
FOCO_MOBILE = {"charles-tattoo-piercing": "67.5% 50%"}  # ponto de interesse da capa no celular (object-position)  # capa já escura: não escurecer mais no hero em tela cheia

def kind_and_info(html):
    m = re.search(r"/\* (\w+): identidade", html)
    return (m.group(1) if m else None), ('<figure><img src="img/hero.jpg"' in html), ('id="casa"' in html and "class=\"pull\"" in html)


def assign(sites):
    """sites: {kind: [slug,...]} → {slug: {dim: idx}} maximizando a distância mínima dentro de cada ramo."""
    out = {}
    for kind, slugs in sites.items():
        slugs = sorted(slugs); n = len(slugs)
        size = dict(SIZE, font=len(FONTS[kind]))
        best = None
        for seed in range(400):
            rnd = random.Random(f"{kind}:{seed}")
            perms = {d: rnd.sample(range(size[d]), size[d]) for d in DIMS}
            ch = [{d: perms[d][(r + (0 if d == "hero" else rnd.randrange(size[d]))) % size[d]] if d != "hero" else perms[d][r % size[d]] for d in DIMS} for r in range(n)]
            dist = [sum(a[d] != b[d] for d in DIMS) for i, a in enumerate(ch) for b in ch[i + 1:]] or [len(DIMS)]
            score = (min(dist), sum(dist) / len(dist))
            if best is None or score > best[0]: best = (score, ch)
        for s, c in zip(slugs, best[1]): out[s] = c
    return out


def block(kind, c, has_fig, slug=""):
    hero = c["hero"]
    if hero in NEEDS_FIG and not has_fig: hero = 0 if hero not in (2, 6) else 3
    css = []
    f = FONTS[kind][c["font"]]
    link = ""
    if f:
        link = f'<link href="https://fonts.googleapis.com/css2?family={f[0]}&display=swap" rel="stylesheet">'
        css.append(f':root {{ --font-display: "{f[1]}", {f[2]}; }} h1, h2, h3, .brand, .big, .svc b, .pull, .score strong, .seal b, footer strong {{ font-weight: {f[3]} !important; }}')
    a = ACCENTS[c["accent"]]
    if a:
        (la, li, ls), (da, di, ds) = a
        css.append(f":root {{ --accent: {la}; --accent-ink: {li}; --salmon: {ls}; }}")
        dk = f"--accent: {da}; --accent-ink: {di}; --salmon: {ds};"
        css.append(f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {dk} }} }} :root[data-theme="dark"] {{ {dk} }}')
    css.append("@media (max-width: 460px) { .brand { min-width: 0; overflow: hidden; text-overflow: ellipsis; font-size: 14px; } .bar .btn { padding: 0 12px; font-size: 13px; flex-shrink: 0; } }")
    css.append(":root { --hrad: 0px; }")  # SHAPE sobrescreve depois
    for lst, key in ((SHAPE, "shape"), (FRAME, "frame"), (None, None), (HEADER, "header"), (GALLERY, "gallery"), (HEADING, "heading"), (PROOF, "proof"), (STRIPE, "stripe"), (INFO, "info"), (ABOUT, "about"), (ORDER, "order"), (ANIM, "anim")):
        if lst is None: css.append(HERO[hero].replace("brightness(.5)", "brightness(.9)") if slug in CAPA_ESCURA else HERO[hero]); continue
        if lst[c[key]]: css.append(lst[c[key]])
    extra = SCRIPT_BLEED if hero == 6 else ""
    if hero == 6 and slug in FOCO_MOBILE: css.insert(0, ":root { --foco: " + FOCO_MOBILE[slug] + "; }")
    return "<!--vary:start-->" + link + "<style>\n  /* variação: " + ",".join(f"{d}={c[d]}" for d in DIMS) + " */\n  " + "\n  ".join(css) + "\n</style>" + extra + "<!--vary:end-->"


def run(only=None):
    pages = {}
    for f in sorted(glob.glob(os.path.join(HERE, "*", "index.html"))):
        slug = os.path.basename(os.path.dirname(f))
        if slug in SKIP: continue
        html = re.sub(r"\n*<!--vary:start-->.*?<!--vary:end-->", "", open(f, encoding="utf-8").read(), flags=re.S)
        kind, fig, pull = kind_and_info(html)
        if kind: pages[slug] = (f, html, kind, fig)
    by_kind = {}
    for s, (_, _, k, _) in pages.items(): by_kind.setdefault(k, []).append(s)
    plan = assign(by_kind)
    for s, o in OVERRIDE.items():
        if s in plan: plan[s].update(o)
    for s, (f, html, k, fig) in pages.items():
        if only and s not in only: continue
        i = html.index("</style>") + len("</style>")
        b = block(k, plan[s], fig, s)
        if s in FORCE_DARK:  # reaplica as variáveis do tema escuro direto no :root (sem depender de prefers-color-scheme)
            dk = "".join(m.group(1) for m in re.finditer(r':root\[data-theme="dark"\] \{([^}]*)\}', html + b))
            b = b.replace("<!--vary:end-->", "<style>:root { " + dk + " }</style><!--vary:end-->")
        open(f, "w", encoding="utf-8").write(html[:i] + "\n" + b + html[i:])
    json.dump({s: dict(kind=pages[s][2], **plan[s]) for s in pages}, open(os.path.join(HERE, "variants.json"), "w"), indent=1, ensure_ascii=False)
    return plan


if __name__ == "__main__":
    plan = run(set(sys.argv[1:]) or None)
    for s, c in sorted(plan.items()): print(f"{s:46s}", " ".join(f"{c[d]}" for d in DIMS))
