#!/usr/bin/env python3
"""Varia o layout de cada site para que negócios do mesmo ramo/cidade não fiquem iguais.
Uso: python3 vary.py [slug ...]   (sem argumentos, todos)
Lê <slug>/index.html, remove o bloco anterior (<!--vary:start-->...<!--vary:end-->) e injeta um novo
com fonte, acento, hero, moldura, cabeçalho, galeria, títulos, formas, prova social, faixa, ordem e animação.
Idempotente. Cada ramo (kind) sorteia combinações que maximizam a distância entre sites do mesmo ramo."""
import glob, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"suzana-dias-studio", "marshals-tattoo", "win-hamburgueria", "pet-shop-agropal"}  # modelo e quem já tem site
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
 .hero { position: relative; display: block; width: 100vw; margin: 0 calc(50% - 50vw); padding: 0; min-height: clamp(540px, min(84vh, 66vw), 800px); overflow: hidden; --hp: 0; }
 .hero > figure { position: absolute; inset: 0; margin: 0; }
 IMG { width: 100%; height: 100%; aspect-ratio: auto; object-fit: cover; border: 0; box-shadow: none; outline: 0; filter: brightness(.92);
   transform: translate3d(0, calc(var(--hp) * 7%), 0) scale(calc(1.04 + var(--hp) * .1)); transform-origin: 50% 20%; will-change: transform;
   -webkit-mask-image: linear-gradient(to bottom, #000 68%, transparent 100%); mask-image: linear-gradient(to bottom, #000 68%, transparent 100%); }
 .hero > div:first-child { position: relative; z-index: 2; min-height: inherit; padding: clamp(56px, 10vh, 110px) max(28px, 7vw, calc((100vw - 1080px) / 2)); display: flex; flex-direction: column; justify-content: flex-end; color: #fff;
   opacity: calc(1 - var(--hp) * 1.15); transform: translate3d(0, calc(var(--hp) * -56px), 0); }
 .hero > div:first-child > * { max-width: 700px; }
 .hero h1 { color: #fff; font-size: clamp(50px, 9vw, 110px); text-shadow: 0 2px 24px rgba(0,0,0,.45); } .hero .eyebrow, .hero .lede, .hero .score { color: rgba(255,255,255,.9); } .hero .score strong { color: #fff; } .hero .stars { color: var(--salmon); }
 .hero .btn.ghost { color: #fff; border-color: #fff; }
 .hero .eyebrow, .hero .lede, .hero .score { text-shadow: 0 1px 16px rgba(0,0,0,.7); }
 .hero .eyebrow { font-size: 13px; } .hero .lede { font-size: clamp(17px, 2.1vw, 21px); line-height: 1.5; } .hero .btn { min-height: 52px; padding: 0 26px; font-size: 17px; }
 .hero img.logo-stamp, .hero img.stamp, .hero .seal { left: auto; right: max(28px, 7vw, calc((100vw - 1080px) / 2)); bottom: 44px; }
 .stripe { display: none; }
 @media (max-width: 820px) {
   .hero { min-height: 590px; margin-bottom: -18px; } IMG { object-position: var(--foco, 50% 50%); -webkit-mask-image: linear-gradient(to bottom, #000 86%, transparent 100%); mask-image: linear-gradient(to bottom, #000 86%, transparent 100%); }
   main.wrap:has(#casa) > #fotos { padding-top: 6px !important; } main.wrap:has(#casa) > #casa { padding-top: 24px; }
   .hero > div:first-child { justify-content: flex-start; padding-top: 30px; padding-bottom: 0; }
   .hero > div:first-child > * { max-width: 100%; }
   .hero .eyebrow { font-size: 11px; letter-spacing: .1em; opacity: .72; margin-bottom: 10px; text-wrap: balance; }
   .hero h1 { font-size: clamp(48px, 15.5vw, 76px); line-height: 1; margin-bottom: 14px; }
   .hero .lede { font-size: 16.5px; line-height: 1.45; color: rgba(255,255,255,.78); max-width: 32ch; margin: 0 0 18px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
   .hero .cta { display: none; }
   .hero .score { margin-top: 4px; gap: 10px; font-size: 13px; } .hero .score strong { font-size: 24px; } .hero .stars { font-size: 13px; letter-spacing: 2px; }
   .hero img.logo-stamp, .hero img.stamp, .hero .seal { width: 100px; height: 100px; border-width: 4px; box-shadow: 0 4px 0 var(--salmon); bottom: 18px; right: 20px; }
 }
 @media (prefers-reduced-motion: reduce) { .hero > div:first-child { opacity: 1 !important; transform: none !important; } .hero > figure > img:first-child { transform: scale(1.04) !important; } }""".replace("IMG", IMG))
SCRIPT_BLEED = """<script>(function(){function init(){var h=document.querySelector('.hero');if(!h)return;var t=0;function f(){t=0;var p=Math.min(Math.max(window.scrollY/Math.max(h.getBoundingClientRect().height,1),0),1);h.style.setProperty('--hp',p.toFixed(3));}window.addEventListener('scroll',function(){if(!t)t=requestAnimationFrame(f);},{passive:true});f();}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();})();</script>"""
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

GALLERY.append("""#fotos .sub { font-size: 18px; line-height: 1.55; color: var(--ink); opacity: .88; max-width: 52ch; }
 #fotos h2 { font-size: clamp(34px, 6vw, 54px); }
 .mosaic { gap: 10px; }
 .tile { --g: 0; border-radius: 10px; isolation: isolate; box-shadow: 0 0 calc(4px + var(--g) * 34px) calc(var(--g) * 3px) rgb(var(--glow, 255 170 80) / calc(var(--g) * .55)); }
 .tile:hover, .tile:focus-visible { --g: 1 !important; }
 .tile img { filter: grayscale(.3) contrast(1.22) saturate(1.1) brightness(.9) sepia(.15); }
 .tile:hover img, .tile:focus-visible img { filter: grayscale(0) contrast(1.15) saturate(1.2) brightness(1); }
 .tile::before { content: ""; position: absolute; inset: 0; z-index: 1; pointer-events: none; background: rgb(var(--glow, 255 170 80)); mix-blend-mode: soft-light; opacity: .22; }
 .tile .cap { z-index: 3; }
 .tile::after { content: ""; position: absolute; inset: 0; z-index: 2; pointer-events: none; border-radius: inherit;
   background: radial-gradient(130% 100% at 50% 35%, transparent 52%, rgba(8,5,3,.55) 100%), linear-gradient(to top, rgba(18,9,4,.38), transparent 45%);
   box-shadow: inset 0 0 0 1px rgb(var(--glow, 255 170 80) / calc(.22 + var(--g) * .7)), inset 0 0 calc(10px + var(--g) * 26px) rgb(var(--glow, 255 170 80) / calc(.06 + var(--g) * .34)); }""")
SCRIPT_GLOW = """<script>(function(){function init(){var t=[].slice.call(document.querySelectorAll('.tile'));if(!t.length)return;var rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;if(rm){t.forEach(function(e){e.style.setProperty('--g','.3')});return;}var q=0;function f(){q=0;var vh=window.innerHeight;t.forEach(function(e){var r=e.getBoundingClientRect();if(r.bottom<-80||r.top>vh+80){e.style.setProperty('--g','0');return;}var d=Math.abs((r.top+r.bottom)/2-vh*0.5)/(vh*0.5);var g=Math.max(0,1-d);e.style.setProperty('--g',(g*g).toFixed(3));});}window.addEventListener('scroll',function(){if(!q)q=requestAnimationFrame(f);},{passive:true});window.addEventListener('resize',f);f();}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();})();</script>"""

HEADING = [
 "",
 "h2 { text-transform: uppercase; letter-spacing: .05em; font-size: clamp(26px, 4vw, 36px); } h2::after { content: ''; display: block; width: 64px; height: 4px; background: var(--accent); margin-top: 14px; }",
 "#fotos h2, #fotos .sub, #horarios h2, .proof h2, .proof .eyebrow { text-align: center; margin-inline: auto; } #fotos h2::after, #horarios h2::after, .proof h2::after { content: ''; display: block; width: 48px; height: 3px; background: var(--accent); margin: 14px auto 0; } .proof-top { justify-content: center; }",
 "h2::before { content: ''; display: block; width: 56px; height: 6px; background: var(--accent); margin-bottom: 14px; } .final h2::before { margin-inline: auto; }",
]

SHAPE = [
 "",
 ".btn { border-radius: 999px; } .card, .svc, blockquote, .qmore { border-radius: 24px; } .status, .tags li { border-radius: 999px; } :root { --hrad: 30px; }",
 ".btn { border-radius: 10px; } .card, .svc, blockquote, .qmore { border-radius: 12px; } .tags li { border-radius: 8px; } .status { border-radius: 6px; } :root { --hrad: 14px; }",
 ".btn { border-radius: 0; text-transform: uppercase; letter-spacing: .06em; font-size: 15px; } .card, .svc, blockquote { border-width: 2px; }",
]

PROOF = [
 "",
 ".proof { background: var(--surface); color: var(--ink); border-block: 1px solid var(--line); } .proof .eyebrow, blockquote cite { color: var(--accent); } .fill { background: var(--accent); } .track { background: var(--line); } blockquote { border-color: var(--line); background: var(--bg); } .reply { color: var(--ink-soft); border-color: var(--line); }",
 ".proof { background: var(--accent); color: var(--accent-ink); } .proof .eyebrow, blockquote cite { color: var(--accent-ink); opacity: .85; } .fill { background: var(--accent-ink); } .reply { color: var(--accent-ink); }",
 ".quotes { grid-template-columns: 1fr; max-width: 760px; } blockquote { border: 0; border-left: 5px solid var(--salmon); padding: 6px 0 6px 22px; } blockquote p { font-size: 19px; }",
]

PROOF.append("""#clientes .eyebrow { color: var(--accent); }
 .proof { background: var(--surface); color: var(--ink); border-block: 1px solid var(--line); }
 .proof-top { display: flex; flex-wrap: wrap; align-items: center; gap: 22px 36px; margin-bottom: 26px; }
 .big { font-size: clamp(64px, 10vw, 100px); }
 .bars { flex: 1 1 260px; max-width: 440px; font-size: 15px; }
 .fill { background: var(--accent); } .track { background: color-mix(in srgb, var(--ink) 14%, transparent); }
 .quotes { display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 6px 4px 24px; margin-inline: -4px; scrollbar-width: thin; scrollbar-color: var(--accent) transparent; -webkit-overflow-scrolling: touch;
   -webkit-mask-image: linear-gradient(to right, #000 90%, transparent); mask-image: linear-gradient(to right, #000 90%, transparent); }
 .qmore { border-radius: 18px; } blockquote { flex: 0 0 clamp(280px, 80vw, 390px); scroll-snap-align: start; display: flex; flex-direction: column; gap: 16px; border: 1px solid var(--line); border-radius: 18px; padding: 24px 22px 20px; background: var(--bg); position: relative; overflow: hidden; }
 blockquote::before { content: "\\201C"; position: absolute; right: 16px; top: -4px; font: 400 96px/1 var(--font-display); color: var(--accent); opacity: .28; }
 blockquote p { margin: 0; font-size: 18px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 7; -webkit-box-orient: vertical; overflow: hidden; }
 blockquote cite { margin-top: auto; display: flex; align-items: center; gap: 12px; font-style: normal; font-weight: 600; font-size: 15px; color: var(--ink); }
 blockquote cite::after { content: "Google"; margin-left: auto; font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-soft); font-weight: 500; }
 .av { width: 38px; height: 38px; border-radius: 50%; background: var(--accent); color: var(--accent-ink); display: grid; place-items: center; font: 700 17px var(--font-body); flex: none; }
 .reply { font-size: 14px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; color: var(--ink-soft); border-top-color: var(--line); } .reply strong { color: var(--ink); }""")
SCRIPT_AV = """<script>document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('blockquote cite').forEach(function(c){var n=(c.textContent||'').trim();if(!n)return;var s=document.createElement('span');s.className='av';s.textContent=n.charAt(0).toUpperCase();c.insertBefore(s,c.firstChild);});});</script>"""

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

LEGIVEL_CSS = """@media (min-width: 821px) and (max-width: 1279px) {
 body { font-size: 19px; }
 .brand { font-size: 22px; } nav { font-size: 17px; gap: 28px; } .bar .btn { min-height: 44px; font-size: 17px; }
 h2 { font-size: clamp(38px, 5.6vw, 58px); } .sub { font-size: 19px; }
 .about p { font-size: 19px; } .pull { font-size: clamp(28px, 3.8vw, 40px); }
 .svc b { font-size: 25px; } .svc span { font-size: 16.5px; }
 .card { padding: 34px; } .card h3 { font-size: 27px; } .hours li { padding: 11px 0; font-size: 19px; } address { font-size: 19px; } .tags li { font-size: 16px; padding: 6px 14px; } .status { font-size: 16px; }
 .btn { min-height: 52px; font-size: 17px; } .final h2 { font-size: clamp(40px, 6vw, 64px); }
 blockquote { flex-basis: clamp(300px, 36vw, 420px); } blockquote p { font-size: 19px; } blockquote cite { font-size: 16px; }
 .score strong { font-size: 40px; } footer { font-size: 16px; } footer strong { font-size: 20px; }
}"""
INTRO_CSS = """@media (prefers-reduced-motion: no-preference) {
 header.bar { animation: introDown .8s cubic-bezier(.2, .7, .2, 1) both; }
 .hero { animation: introFade 1.3s ease both; }
 .hero > div:first-child > * { animation: introUp .95s cubic-bezier(.2, .7, .2, 1) both; }
 .hero > div:first-child > :nth-child(1) { animation-delay: .25s; } .hero > div:first-child > :nth-child(2) { animation-delay: .38s; } .hero > div:first-child > :nth-child(3) { animation-delay: .5s; } .hero > div:first-child > :nth-child(4) { animation-delay: .62s; } .hero > div:first-child > :nth-child(5) { animation-delay: .74s; }
 .hero img.logo-stamp, .hero .seal { animation: introPop 1s cubic-bezier(.2, .8, .2, 1.2) .8s both; }
}
@keyframes introDown { from { transform: translateY(-100%); } to { transform: none; } }
@keyframes introFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes introUp { from { opacity: 0; transform: translateY(26px); } to { opacity: 1; transform: none; } }
@keyframes introPop { from { opacity: 0; transform: scale(.7) rotate(-14deg); } to { opacity: 1; } }"""
SCRIPT_NUDGE = """<script>(function(){var rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;function nudge(){if(rm||location.hash||window.scrollY>2)return;var dy=Math.round(Math.min(84,Math.max(52,window.innerHeight*0.09))),t0=null,stop=false,dur=1200;function cancel(){stop=true;}['touchstart','wheel','keydown','mousedown'].forEach(function(e){window.addEventListener(e,cancel,{once:true,passive:true});});function ease(p){return p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;}function step(ts){if(stop)return;if(t0===null)t0=ts;var p=Math.min((ts-t0)/dur,1);window.scrollTo({top:Math.round(dy*ease(p)),behavior:'instant'});if(p<1)requestAnimationFrame(step);}setTimeout(function(){requestAnimationFrame(step);},450);}if(document.readyState==='complete')nudge();else window.addEventListener('load',nudge);})();</script>"""
# título e subtítulo da galeria escritos à mão por site (regex: troca só dentro de #fotos; idempotente)
GALERIA_TEXTO = {"barbearia-los-chicanos": ("Aqui é onde o estilo acontece", "Cortes, barba, bigode e o clima da casa.", "Toque numa foto para ampliar"),
    "excellence-studio": ("Beleza que renova a autoestima", "Cabelos, unhas e muito cuidado, direto do salão.", "Toque numa foto para ampliar"),
    "aure-art-studio-tattoo-piercing-em-goiania": ("Cada traço conta uma história", "Tatuagens e piercings feitos aqui, do traço fino ao colorido.", "Toque numa foto para ampliar"),
    "nina-pet-shop": ("Cada pet sai daqui mais lindo e mais feliz", "Alguns dos nossos clientes de quatro patas.", "Toque numa foto para ampliar"),
    "tayz-bessa-studio": ("Sai daqui se sentindo ainda mais você", "Cabelos, mechas e escovas que viram autoestima.", "Toque numa foto para ampliar"),
    "jennifer-benke-tattoo-studio": ("Arte que valoriza a sua pele", "Linhas finas, delicadas e feitas para durar.", "Toque numa foto para ampliar"),
    "don-alberttoni": ("Cada canto tem uma história", "Cadeiras antigas, sinuca, violão, xadrez e um poodle de visita.", "Toque numa foto para ampliar"),
    "charles-tattoo-piercing": ("Toda ideia merece virar pele", "Histórias, homenagens e inspirações que já ganharam traço aqui.", "Toque numa foto para ampliar")}
# seção "sobre" e título das avaliações escritos à mão (só com fatos do perfil e das avaliações; idempotente)
SOBRE_TEXTO = {"barbearia-los-chicanos": dict(
    h2="Corte, barba e bigode, do jeito que você pede.",
    paras=["Barbearia especializada no tratamento de barba e cabelo, na Boa Vista, em Curitiba. Atendimento de primeira, ambiente com personalidade e a família Los Chicanos esperando por você.",
           "Chega, senta e sai na régua."],
    pull=("Cortou do jeito que você pede!", "Avaliação no Google"),
    cards=[("Corte", "Do clássico ao degradê, do jeito que você pede."), ("Barba e bigode", "Aparados, desenhados e bem cuidados."),
           ("Ambiente", "Casa com estilo, boa música e atendimento no capricho."), ("Horário marcado", "Chame no WhatsApp e agende.")],
    nota="", prova="Quem já sentou na cadeira conta"),
  "excellence-studio": dict(
    h2="Seu momento de beleza, com toda a calma.",
    paras=["Salão de beleza completo no Menino Deus, em Porto Alegre. Cabelo, unhas, maquiagem, depilação e estética, com profissionais experientes e qualificados.",
           "Chega, relaxa e deixa a gente cuidar de você."],
    pull=("Salão com profissionalismo e atendimento excelentes.", "Avaliação no Google"),
    cards=[("Cabelo", "Corte, penteado, coloração, mechas e alisamento."), ("Unhas", "Manicure, pedicure e unhas postiças."),
           ("Maquiagem", "Para festas, eventos e noivas."), ("Estética e depilação", "Limpeza de pele, massagem relaxante e depilação.")],
    nota="", prova="Quem já passou por aqui conta"),
  "aure-art-studio-tattoo-piercing-em-goiania": dict(
    h2="Tinta, metal e estilo, dentro do shopping.",
    paras=["Estúdio de tatuagem e piercing em Goiânia, no Shopping Passeio das Águas. Procedimentos seguros, atendimento personalizado e uma equipe de tatuadores e piercers.",
           "Conta a ideia. A gente cuida do resto."],
    pull=("Os furos que fiz com ele foram os primeiros em que a dor foi praticamente zero.", "Avaliação no Google"),
    cards=[("Tatuagem em todos os estilos", "Blackwork, fine line, old school, realismo, ornamental e oriental, além de flash tattoo."), ("Piercing", "Perfurações tradicionais e exóticas, com segurança."),
           ("Lóbulo e cicatrização", "Lóbuloplastia química e laserterapia de apoio à cicatrização."), ("Sala de espera", "Sofás, neon e quadros, para esperar com estilo.")],
    nota="", prova="Quem já passou por aqui conta"),
  "nina-pet-shop": dict(
    h2="Seu pet em boas patas.",
    paras=["Banho e tosa, hotel, táxi dog, rações e acessórios em Belo Horizonte. Aqui o seu pet é tratado com dedicação e carinho, como se fosse da família.",
           "Chega, traz o seu pet e deixa com a gente."],
    pull=("Não tenho palavras para descrever o quanto estou feliz.", "Avaliação no Google"),
    cards=[("Banho e tosa", "O seu pet cheiroso, bonito e bem cuidado.", "banho"), ("Táxi dog", "A gente busca e entrega o seu pet.", "taxi"),
           ("Hotel", "Um lugar de confiança para o seu pet ficar.", "hotel"), ("Rações e acessórios", "Tudo o que o seu pet precisa, na loja.", "loja")],
    nota="", prova="Quem leva o pet pro Nina conta"),
  "tayz-bessa-studio": dict(
    h2="Cuidado que devolve autoestima.",
    paras=["Em Goiânia, a Tayz Bessa transforma cabelo e desperta autoestima. Visagismo, coloração, mechas, escovas e unhas, num estúdio onde dá vontade de ficar.",
           "Chega, relaxa e deixa o resto com a gente."],
    pull=("Uma profissional incrível que transformou meu cabelo e minha autoestima.", "Avaliação no Google"),
    cards=[("Visagismo e corte", "Cortes pensados para o seu rosto e para o seu jeito."), ("Cor e mechas", "Coloração e mechas com cuidado e acabamento."),
           ("Escovas e tratamentos", "Escovas, terapia capilar e alinhamento capilar."), ("Unhas", "Manicure, pedicure, alongamento e nail design.")],
    nota="", prova="Quem já passou por aqui conta"),
  "jennifer-benke-tattoo-studio": dict(
    h2="Delicadeza que fica pra sempre.",
    paras=["Tatuagens delicadas que valorizam a sua pele, em linhas finas, elegantes e atemporais. Estúdio em Porto Alegre desde 2016, com uma tatuadora premiada 8 vezes.",
           "Conta a sua ideia. O resto é traço."],
    pull=("O traço mais fino e mais lindo é o dela.", "Avaliação no Google"),
    cards=[("Fine line e minimalismo", "O traço fino que ela faz, do jeito que você imaginou."), ("Coberturas e reformas", "Dá nova vida pra uma tattoo antiga."),
           ("Cuidados", "Orientação para a sua tattoo cicatrizar bem."), ("Agenda aberta", "Peça o orçamento pelo WhatsApp.")],
    nota="", prova="Quem já passou por aqui conta"),
  "don-alberttoni": dict(
    h2="Barbearia old school, do jeito que o Vinícius gosta.",
    paras=["Desde 2015 no Bom Retiro, em Curitiba: cadeira de couro, vinil rodando, xadrez no tabuleiro de pedra e violão encostado no canto. Aqui o corte vem com café e papo reto.",
           "Chega, senta e deixa a gente cuidar do visual."],
    pull=("Ouvindo vinil, trocando ideia e ainda ir embora com um corte 10/10 é uma raridade.", "Daniel S., em avaliação no Google"),
    cards=[("Corte de cabelo", "Do clássico ao estilo novo, do seu jeito."), ("Barba", "Aparada e desenhada com calma, do jeito antigo."),
           ("Sobrancelha", "O acabamento que completa o corte."), ("Corte infantil", "Com paciência para os pequenos.")],
    nota="Valores e profissionais disponíveis aparecem no agendamento online.", prova="Quem já sentou na cadeira conta"),
  "charles-tattoo-piercing": dict(
    h2="Tem uma ideia na cabeça? Bora tirar do papel.",
    paras=["Mais de 10 anos de tatuagem, piercing e microdermal no Rodoviário. Estúdio limpo, ambiente acolhedor e um atendimento que deixa tranquilo até quem vai fazer a primeira tattoo.",
           "Chega, conta a ideia e leva pra casa uma marca que é só sua."],
    pull=("Fiz minhas primeiras tatuagens, que trabalho incrível, mão super leve.", "Agna C., em avaliação no Google"),
    cards=[("Primeira vez? Fica tranquilo", "Tem cliente contando que foi bem acolhido e saiu tranquilo, mesmo sendo a primeira tattoo."),
           ("Higiene e acolhimento", "Higiene, ambiente e muito acolhimento, nas palavras de quem já foi."),
           ("Tattoo, piercing e micro", "Também faz piercing, até de bioflex, e microdermal."),
           ("Porta aberta o dia todo", "Aberto todos os dias, das 7h às 21h.")],
    nota="Baseado no que os clientes contam no Google e nas informações do perfil.",
    prova="Quem já passou por aqui conta")}
GCTA_CSS = """#fotos .sub { margin-bottom: 16px; }
 .gcta { display: flex; align-items: center; justify-content: center; gap: 14px; margin: 0 auto 30px; font: 500 12.5px/1 "Barlow Condensed", "Arial Narrow", sans-serif; letter-spacing: .26em; text-transform: uppercase; color: #e8c98b; }
 .gcta::before, .gcta::after { content: ""; width: 28px; height: 1px; background: currentColor; opacity: .55; }"""
GCTA_LINK = '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600&display=swap" rel="stylesheet">'
ICONES = {
 "banho": '<svg viewBox="0 0 32 32" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15h24v2.5a7 7 0 0 1-7 7H11a7 7 0 0 1-7-7z"/><path d="M8 15V9.5a3 3 0 0 1 6 0"/><circle cx="20" cy="8" r="1.4"/><circle cx="24" cy="11" r="1.1"/><path d="M9 28l1.5-3.5M23 28l-1.5-3.5"/></svg>',
 "taxi": '<svg viewBox="0 0 32 32" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21v-4l2.2-6.2A3 3 0 0 1 9 9h14a3 3 0 0 1 2.8 1.8L28 17v4z"/><path d="M4 17h24"/><circle cx="10" cy="23.5" r="2.5"/><circle cx="22" cy="23.5" r="2.5"/><path d="M13 5h6"/></svg>',
 "hotel": '<svg viewBox="0 0 32 32" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15 16 5l12 10"/><path d="M7 13v14h18V13"/><path d="M13 27v-7a3 3 0 0 1 6 0v7"/></svg>',
 "loja": '<svg viewBox="0 0 32 32" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 10h19l-1.6 17H8.1z"/><path d="M11 10a5 5 0 0 1 10 0"/><circle cx="12.5" cy="17" r="1.3"/><circle cx="19.5" cy="17" r="1.3"/><path d="M12.5 22.5c1 1.4 2.2 2 3.5 2s2.5-.6 3.5-2"/></svg>'}
ICONES_CSS = """.svc .ic { width: 48px; height: 48px; border-radius: 50%; display: grid; place-items: center; background: color-mix(in srgb, var(--accent) 13%, transparent); color: var(--accent); flex: none; }
 .svc .ic svg { display: block; }"""
SOBRE_CSS = """#casa { position: relative; isolation: isolate; padding-block: 84px 44px; }
 #casa::before { content: ""; position: absolute; inset: -30px calc(50% - 50vw); z-index: -1; pointer-events: none; background: radial-gradient(55% 55% at 22% 35%, rgb(var(--glow, 255 170 80) / .17), transparent 72%); }
 #casa h2 { font-size: clamp(40px, 6.6vw, 70px); line-height: 1.02; margin-bottom: 22px; }
 #casa .about > div > p { font-size: clamp(19px, 2.4vw, 24px); line-height: 1.5; max-width: 36ch; }
 #casa .about > div > p:nth-of-type(2) { color: var(--accent); font-weight: 600; }
 #casa .pull { font-size: clamp(30px, 5vw, 52px); line-height: 1.12; position: relative; padding-top: 30px; }
 #casa .pull::before { content: "\\201C"; position: absolute; top: -28px; left: 50%; transform: translateX(-50%); font: 400 120px/1 var(--font-display); color: var(--accent); opacity: .9; }
 #casa .svc { min-height: 140px; } #casa .svc b { font-size: clamp(21px, 2.6vw, 27px); } #casa .svc span { font-size: 16px; line-height: 1.45; color: var(--ink); opacity: .82; }
 #casa .services { gap: 14px; margin: 26px 0 0; }"""
DM_SITES = {"charles-tattoo-piercing"}  # layout de celular ampliado quando a tela de toque abre a página em ~980 px
# mensagem que já vem preenchida nos botões de WhatsApp (por site)
WA_TEXTO = {"barbearia-los-chicanos": "Fala, pessoal da Los Chicanos, tudo bom? Queria agendar um horário.", "excellence-studio": "Oi, tudo bem? Queria agendar um horário no Excellence.", "aure-art-studio-tattoo-piercing-em-goiania": "Oi, tudo bem? Queria pedir um orçamento de tatuagem.", "nina-pet-shop": "Oi, tudo bem? Queria agendar um banho e tosa para o meu pet.", "tayz-bessa-studio": "Oi, Tayz, tudo bem? Queria agendar um horário.", "charles-tattoo-piercing": "Fala, Charles, tudo bom? Queria te pedir orçamento de uma tattoo.", "don-alberttoni": "Fala, Vinícius, tudo bom? Queria agendar um horário.", "jennifer-benke-tattoo-studio": "Oi, Jennifer, tudo bem? Queria pedir um orçamento de uma tattoo."}
AVAL_LINK = {"barbearia-los-chicanos", "excellence-studio", "aure-art-studio-tattoo-piercing-em-goiania", "nina-pet-shop", "tayz-bessa-studio", "charles-tattoo-piercing", "don-alberttoni", "jennifer-benke-tattoo-studio"}  # "Avaliações no Google" com estrelas e link para as avaliações no Google
AVAL_CSS = """.rev-link { display: inline-flex; flex-direction: column; align-items: center; gap: 7px; text-align: center; color: var(--accent); text-decoration: none; }
 .rev-link .rs { color: #e8c98b; letter-spacing: 4px; font-size: 12px; line-height: 1; }
 .rev-link:hover .rt, .rev-link:focus-visible .rt { text-decoration: underline; text-underline-offset: 5px; }
 .proof-top { justify-content: center; text-align: center; } .proof .bars { text-align: left; }
 a.score { text-decoration: none; color: inherit; } a.score:hover > div, a.score:focus-visible > div { text-decoration: underline; text-underline-offset: 4px; }"""
# textos da capa e do fechamento escritos à mão por site
HERO_TEXTO = {"barbearia-los-chicanos": ("Barbearia · Boa Vista, Curitiba", "Corte, barba e bigode do jeito que você pede. Atendimento de quem entende, num ambiente de respeito e estilo.", "LOS CHICANOS"),
    "excellence-studio": ("Salão de beleza · Menino Deus, Porto Alegre", "Especialistas em elevar a sua autoestima. Cabelo, unhas, maquiagem, depilação e estética, com profissionais experientes."),
    "aure-art-studio-tattoo-piercing-em-goiania": ("Tattoo e piercing · Shopping Passeio das Águas, Goiânia", "Tatuagem e piercing num estúdio dentro do shopping, com uma equipe de tatuadores e piercers. Chega, escolhe o seu estilo e sai com a sua marca.", "AURE ART STUDIO"),
    "nina-pet-shop": ("Banho, tosa e carinho · Candelária, Belo Horizonte", "Banho e tosa, hotel e táxi dog com a dedicação e o carinho que o seu pet merece."),
    "tayz-bessa-studio": ("Cabelo & unhas · Jardim Mariliza, Goiânia", "Visagismo, cabelo e unhas num estúdio de espelhos dourados e muito verde. Aqui o cuidado vira autoestima."),
    "jennifer-benke-tattoo-studio": ("Tattoo fine line · Cristal, Porto Alegre", "Tatuagens delicadas que valorizam a sua pele. Linhas finas, elegantes e atemporais, desde 2016. 8x premiada."),
    "don-alberttoni": ("Barbearia old school desde 2015 · Bom Retiro, Curitiba",
    "Corte, barba e sobrancelha no capricho. Café na mão, vinil rodando e uma casa pra quem curte estilo, moto e tinta na pele.")}
FINAL_TEXTO = {"barbearia-los-chicanos": ("Bora ficar na régua?", "Chame no WhatsApp e escolha o seu horário."),
    "excellence-studio": ("Seu horário de beleza espera por você", "Chame no WhatsApp e escolha o melhor horário."),
    "aure-art-studio-tattoo-piercing-em-goiania": ("Qual é a sua marca?", "Chame no WhatsApp, conte a ideia e peça seu orçamento."),
    "nina-pet-shop": ("Seu pet merece esse carinho", "Agende o banho e tosa pelo WhatsApp e escolha o melhor horário."),
    "tayz-bessa-studio": ("Seu momento começa aqui", "Agende pelo WhatsApp e escolha o melhor horário."),
    "jennifer-benke-tattoo-studio": ("Agenda aberta. Qual é a sua ideia?", "Chame no WhatsApp, conte o que você imagina e peça seu orçamento."),
    "don-alberttoni": ("Sua cadeira tá te esperando", "Marque pelo agendamento online ou chame no WhatsApp. O resto é com a gente.")}
# contraste mínimo em todos os sites (texto miúdo do rodapé e dia de hoje nos horários)
CONTRASTE_CSS = """.hours li.today { color: color-mix(in srgb, var(--accent) 62%, var(--ink)); font-weight: 700; }
 footer p, footer p a { opacity: 1 !important; color: color-mix(in srgb, var(--wood-ink) 90%, transparent); }"""
# último card da lista de avaliações: leva a todas as avaliações no Google (todos os sites)
QMORE_CSS = """.quotes .qmore { display: flex; flex-direction: column; justify-content: center; gap: 10px; flex: 0 0 clamp(250px, 72vw, 330px); scroll-snap-align: start; min-width: 0; padding: 22px; border: 1px solid currentColor; text-decoration: none; color: inherit; }
 .qmore .qm-st { letter-spacing: 3px; font-size: 13px; opacity: .9; } .qmore .qm-t { font-family: var(--font-display); font-size: clamp(22px, 3vw, 28px); line-height: 1.1; } .qmore .qm-s { font-size: 14px; opacity: .8; }
 .qmore .qm-a { margin-top: 6px; font-weight: 600; font-size: 15px; } .qmore:hover .qm-a, .qmore:focus-visible .qm-a { text-decoration: underline; text-underline-offset: 4px; }
 .rv-go { display: inline-block; align-self: flex-start; margin-top: 8px; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; text-decoration: none; color: var(--accent); }
 .rv-go:hover { text-decoration: underline; text-underline-offset: 4px; }"""

def add_qmore(html):
    mp = re.search(r'query_place_id=([^"&]+)', html)
    if not mp or '<div class="quotes">' not in html: return html
    url = "https://search.google.com/local/reviews?placeid=" + mp.group(1)
    mn = re.search(r"(\d[\d.]*) avaliações no Google", html)
    sub = f"{mn.group(1)} avaliações de clientes" if mn else "Avaliações de clientes"
    card = (f'<a class="qmore" href="{url}" target="_blank" rel="noopener"><span class="qm-st" aria-hidden="true">\u2605\u2605\u2605\u2605\u2605</span>'
            f'<span class="qm-t">Veja todas as avaliações no Google</span><span class="qm-s">{sub}</span><span class="qm-a">Abrir no Google \u2197</span></a>')
    return re.sub(r'(<div class="quotes">.*?)(?:<a class="qmore".*?</a>)?(</div>\s*</section>)', lambda m: m.group(1) + card + m.group(2), html, count=1, flags=re.S)

# fonte, paleta e ajustes de CSS feitos à mão por site
FONTE_CUSTOM = {"barbearia-los-chicanos": ("Oswald:wght@500;600;700", "Oswald", "Impact, sans-serif", 600), "excellence-studio": ("Marcellus", "Marcellus", "Georgia, serif", 400), "aure-art-studio-tattoo-piercing-em-goiania": ("Josefin+Sans:wght@400;600;700", "Josefin Sans", "Arial, sans-serif", 600), "tayz-bessa-studio": ("Playfair+Display:wght@500;600;700", "Playfair Display", "Georgia, serif", 600), "jennifer-benke-tattoo-studio": ("Cormorant+Garamond:ital,wght@0,600;0,700;1,600", "Cormorant Garamond", "Georgia, serif", 700)}
# paleta clara por site (vence o modo escuro do aparelho)
TEMA_LIGHT = {"excellence-studio": "--bg: #fbf7ef; --surface: #fffdf8; --ink: #2a2113; --ink-soft: #5a4d37; --wood: #1b1812; --wood-ink: #f8f1e2; --accent: #8f6300; --accent-ink: #ffffff; --salmon: #d9b25a; --line: #e6dcc6;", "nina-pet-shop": "--bg: #fbf5ea; --surface: #fffdf8; --ink: #14215a; --ink-soft: #3a4780; --wood: #1f45b5; --wood-ink: #ffffff; --accent: #c72d73; --accent-ink: #ffffff; --salmon: #ffb3d1; --line: #e6d9c4;"}
LOGO_INJECT = {"nina-pet-shop"}  # coloca o logo (img/logo.jpg) no cabeçalho e no rodapé
TEMA_CUSTOM = {"barbearia-los-chicanos": "--bg: #0b0a09; --surface: #15120f; --ink: #f5eee2; --ink-soft: #bdb09c; --wood: #17110c; --wood-ink: #f5eee2; --accent: #d8a548; --accent-ink: #14100a; --salmon: #f0cd86; --line: #32281d; --glow: 216 165 72;", "aure-art-studio-tattoo-piercing-em-goiania": "--bg: #0c0a08; --surface: #16120e; --ink: #f6efe4; --ink-soft: #bcb09e; --wood: #1a130d; --wood-ink: #f6efe4; --accent: #e0a85e; --accent-ink: #14100a; --salmon: #f1d08f; --line: #33291e; --glow: 224 168 94;", "tayz-bessa-studio": "--bg: #0b0a08; --surface: #14120e; --ink: #f4ede0; --ink-soft: #b9ae98; --wood: #14241a; --wood-ink: #f4ede0; --accent: #cfa95e; --accent-ink: #15110a; --salmon: #e3c887; --line: #2e2a20; --glow: 207 169 94;", "jennifer-benke-tattoo-studio": "--bg: #120d11; --surface: #1c1419; --ink: #f4eaee; --ink-soft: #bfa9b3; --wood: #0a0609; --wood-ink: #f4eaee; --accent: #e59ab0; --accent-ink: #1a0c12; --salmon: #c9a27e; --line: #3a2a32; --glow: 229 154 176;"}
GALERIA_FILTRO = {"barbearia-los-chicanos": "contrast(1.1) saturate(1.05) brightness(.97)", "aure-art-studio-tattoo-piercing-em-goiania": "contrast(1.1) saturate(1.04) brightness(.96)", "tayz-bessa-studio": "contrast(1.06) saturate(1.06) brightness(.98)", "jennifer-benke-tattoo-studio": "contrast(1.08) saturate(1.05) brightness(.97)"}
CSS_EXTRA = {"barbearia-los-chicanos": """.hero img.logo-stamp, .hero .seal { display: none; }
 .hero h1 { text-transform: uppercase; letter-spacing: .06em; font-size: clamp(44px, 6.4vw, 92px); line-height: 1.02; }
 .hero .eyebrow { letter-spacing: .18em; } .hero > div:first-child > .lede { max-width: 25em; }
 @media (min-width: 821px) { .hero > div:first-child { max-width: 52%; } }
 @media (max-width: 820px) { .hero { min-height: 600px; } .hero > figure > img:first-child { content: url("img/hero-m.jpg"); object-position: 50% 100%; }
   .hero h1 { font-size: clamp(40px, 11.6vw, 56px); } .hero .lede { max-width: 30ch; } }""",
  "excellence-studio": """.hero .seal, .hero img.logo-stamp { display: none; }
 #fotos .gcta { color: #8f6300; } #clientes .rev-link .rs { color: #a8730a; }
 html .hero > div:first-child { color: var(--ink); }
 html .hero h1 { color: var(--ink); text-shadow: none; text-transform: uppercase; letter-spacing: .07em; font-size: clamp(40px, 5.6vw, 78px); line-height: 1.05; }
 html .hero .eyebrow { color: #8f6300; opacity: 1; letter-spacing: .16em; font-size: 12px; }
 html .hero .lede, html .hero .score, html .hero .score > div { color: var(--ink-soft); text-shadow: none; opacity: 1; }
 html .hero .score strong { color: var(--ink); } html .hero .stars { color: #a8730a; }
 html .hero .btn.ghost { color: var(--ink); border-color: var(--ink); text-shadow: none; }
 .hero > figure > img:first-child { -webkit-mask-image: none; mask-image: none; filter: none; }
 .hero > div:first-child > .lede { max-width: 25em; }
 .hero { --aw: min(86vw, 440px); }
 .hero::after { content: ""; display: block; position: relative; z-index: 3; width: var(--aw); aspect-ratio: 720 / 627; margin: 28px auto 0; background: url("img/arco.webp") center / contain no-repeat; }
 .hero { padding-bottom: 36px; }
 .hero > figure > img:first-child { content: url("img/hero-m.jpg"); object-position: 50% 50%; }
 @media (max-width: 820px) { html .hero h1 { font-size: clamp(36px, 10.5vw, 52px); } .hero .lede { max-width: 30ch; } .hero { min-height: 0; } }
 @media (min-width: 821px) { .hero { --aw: min(46vw, 600px); min-height: clamp(520px, 46vw, 680px); padding-bottom: 0; }
   .hero > figure > img:first-child { content: url("img/hero.jpg"); }
   .hero > div:first-child { max-width: 52%; padding: 90px max(28px, 7vw) 90px; justify-content: center; }
   .hero::after { position: absolute; right: max(12px, 4vw); top: 50%; transform: translateY(-50%); margin: 0; } }""",
  "aure-art-studio-tattoo-piercing-em-goiania": """.hero img.logo-stamp, .hero .seal { display: none; }
 .hero h1 { text-transform: uppercase; letter-spacing: .09em; font-size: clamp(38px, 5.6vw, 76px); line-height: 1.06; }
 .hero .eyebrow { letter-spacing: .18em; }
 .hero > div:first-child > .lede { max-width: 26em; }
 @media (min-width: 821px) { .hero > div:first-child { max-width: 52%; } }
 @media (max-width: 820px) { .hero { min-height: 700px; } .hero > figure > img:first-child { content: url("img/hero-m.jpg"); object-position: 50% 100%; }
   .hero h1 { font-size: clamp(34px, 9.6vw, 48px); } .hero .lede { max-width: 30ch; } }""",
  "nina-pet-shop": """.hero .seal, .hero img.logo-stamp { display: none; }
 #fotos .gcta { color: #a3225f; } #clientes .rev-link .rs { color: #a86200; }
 .hero .eyebrow { color: #fff; font-size: 12px; } .hero .score, .hero .score > div { color: #fff; } .hero .stars { color: #fff1b8; }
 footer p, footer p a { opacity: 1 !important; color: rgba(255, 255, 255, .92); }
 .hero { --d: min(78vw, 330px); min-height: 0; padding: 36px 0 1px; margin-bottom: calc(var(--d) * .44 + 18px); z-index: 3; overflow: visible; }
 .hero > figure { overflow: hidden; }
 .hero > figure > img:first-child { -webkit-mask-image: none; mask-image: none; content: url("img/hero-m.jpg"); object-position: 50% 50%; }
 .hero > div:first-child { min-height: 0; justify-content: flex-start; padding: 0 max(24px, 7vw); }
 .hero h1 { font-size: clamp(46px, 13vw, 64px); }
 .hero .eyebrow { letter-spacing: .12em; opacity: 1; }
 .hero .lede { color: #fff; opacity: .96; max-width: 30ch; }
 .hero::after { content: ""; display: block; position: relative; z-index: 3; width: var(--d); height: var(--d); margin: 36px auto calc(var(--d) / -2); background: url("img/pet.webp") center / contain no-repeat; filter: drop-shadow(0 14px 22px rgba(10, 24, 90, .38)); }
 .hero::before { content: ""; position: absolute; z-index: 4; width: calc(var(--d) * .4); height: calc(var(--d) * .4); border-radius: 50%; background: #fff url("img/logo.jpg") center / cover; border: 4px solid #fff; box-shadow: 0 8px 18px rgba(10, 24, 90, .38); left: calc(50% - var(--d) * .6); bottom: calc(var(--d) * -.42); }
 @media (min-width: 821px) {
   .hero { --d: min(34vw, 440px); padding: 0 0 1px; }
   .hero > figure > img:first-child { content: url("img/hero.jpg"); }
   .hero > div:first-child { padding: 84px max(28px, 7vw) 96px; max-width: 62%; justify-content: center; }
   .hero h1 { font-size: clamp(54px, 6.4vw, 96px); } .hero .lede { max-width: 24em; font-size: clamp(18px, 1.7vw, 22px); }
   .hero::after { position: absolute; right: max(28px, 8vw); bottom: calc(var(--d) / -2); margin: 0; }
   .hero::before { left: auto; right: calc(max(28px, 8vw) + var(--d) * .8); bottom: calc(var(--d) * -.5); }
 }""",

  "tayz-bessa-studio": """.hero img.logo-stamp { display: none; }
 .hero h1 { font-size: clamp(42px, 5.8vw, 78px); line-height: 1.04; letter-spacing: .035em; }
 .hero .eyebrow { letter-spacing: .2em; } .hero .lede { max-width: 31em; }
 @media (max-width: 820px) { .hero { min-height: 700px; } .hero > figure > img:first-child { content: url("img/hero-m.jpg"); object-position: 50% 100%; }
   .hero h1 { font-size: clamp(40px, 11.5vw, 56px); } .hero .lede { max-width: 30ch; } }""",
  "jennifer-benke-tattoo-studio": """.hero img.logo-stamp { display: none; }
 .hero h1 { font-size: clamp(52px, 8vw, 108px); line-height: 1.02; font-style: italic; }
 .hero .eyebrow { letter-spacing: .2em; }
 @media (max-width: 820px) { .hero { min-height: 700px; } .hero > figure > img:first-child { content: url("img/hero-m.jpg"); object-position: 50% 100%; }
   .hero h1 { font-size: clamp(52px, 15.5vw, 72px); line-height: 1; } .hero .lede { max-width: 30ch; } }"""}
LEGIVEL = {"charles-tattoo-piercing"}  # tipografia maior em telas de 821 a 1279 px
INTRO = {"barbearia-los-chicanos", "excellence-studio", "aure-art-studio-tattoo-piercing-em-goiania", "nina-pet-shop", "tayz-bessa-studio", "charles-tattoo-piercing", "don-alberttoni", "jennifer-benke-tattoo-studio"}    # animação de entrada + pequeno scroll suave ao carregar

DIMS = ["font", "accent", "hero", "frame", "header", "gallery", "heading", "shape", "proof", "stripe", "info", "about", "order", "anim"]
SIZE = dict(font=None, accent=len(ACCENTS), hero=6, frame=len(FRAME), header=len(HEADER), gallery=5, heading=len(HEADING),
            shape=len(SHAPE), proof=4, stripe=len(STRIPE), info=len(INFO), about=len(ABOUT), order=len(ORDER), anim=len(ANIM))


OVERRIDE = {"barbearia-los-chicanos": {"hero": 6, "gallery": 5, "proof": 4, "about": 3, "heading": 2, "anim": 1, "header": 0, "shape": 0},
            "excellence-studio": {"hero": 6, "gallery": 2, "proof": 4, "about": 3, "heading": 2, "anim": 1, "header": 0, "shape": 2},
            "aure-art-studio-tattoo-piercing-em-goiania": {"hero": 6, "gallery": 5, "proof": 4, "about": 3, "heading": 2, "anim": 1, "header": 0, "shape": 0},
            "nina-pet-shop": {"hero": 6, "gallery": 2, "proof": 4, "about": 3, "heading": 2, "anim": 1, "header": 0, "shape": 1, "accent": 0},
            "tayz-bessa-studio": {"hero": 6, "gallery": 5, "proof": 4, "about": 3, "heading": 2, "anim": 1, "header": 0, "shape": 0},
            "jennifer-benke-tattoo-studio": {"hero": 6, "gallery": 5, "proof": 4, "about": 3, "heading": 2, "anim": 1},
            "charles-tattoo-piercing": {"hero": 6, "gallery": 5, "proof": 4, "about": 3}}  # escolhas à mão (capa panorâmica escura)
CAPA_ESCURA = set()
CAPA_CLARA = {"don-alberttoni"}  # foto de capa clara: escurece para o texto branco ler
# sites feitos à mão: ramo e plano fixos (ficam fora do sorteio, para não mudar o layout dos outros do ramo)
PLANO_FIXO = {"don-alberttoni": ("barber", dict(font=0, accent=0, hero=6, frame=0, header=0, gallery=5, heading=2, shape=0, proof=4, stripe=0, info=0, about=3, order=0, anim=1))}
FORCE_DARK = {"barbearia-los-chicanos", "aure-art-studio-tattoo-piercing-em-goiania", "tayz-bessa-studio", "charles-tattoo-piercing", "don-alberttoni", "jennifer-benke-tattoo-studio"}  # sempre tema escuro, ignorando o tema do aparelho
FOCO_MOBILE = {"jennifer-benke-tattoo-studio": "50% 50%", "charles-tattoo-piercing": "67.5% 50%", "don-alberttoni": "44% 50%"}  # ponto de interesse da capa no celular (object-position)  # capa já escura: não escurecer mais no hero em tela cheia

def _rules(inner):
    return re.findall(r"([^{}]+)\{([^{}]*)\}", inner)

def _scoped(inner, prefix):
    out = []
    for sel, dec in _rules(inner):
        ss = [s.strip() for s in sel.split(",")]
        out.append(",".join(prefix + s for s in ss) + "{" + dec + "}")
    return "".join(out)

def _media_blocks(css):
    """[(condição, inner)] das @media de um nível, com contagem de chaves."""
    res = []
    for m in re.finditer(r"@media\s*([^{]+)\{", css):
        i, depth = m.end(), 1
        while i < len(css) and depth:
            depth += {"{": 1, "}": -1}.get(css[i], 0); i += 1
        res.append((m.group(1).strip(), css[m.end():i - 1]))
    return res

def modo_ampliado(page):
    """Telas de toque que abrem a página em ~980 px (modo desktop do navegador do celular): usa o layout de celular ampliado.
    vw/vh viram variáveis (valem 1vw/1vh normalmente e 1vw/zoom no modo ampliado); as @media de celular são espelhadas sob html.dm."""
    def troca(m):
        css = re.sub(r"(\d*\.?\d+)vw", r"calc(\1 * var(--vw))", m.group(2))
        css = re.sub(r"(\d*\.?\d+)vh", r"calc(\1 * var(--vh))", css)
        return m.group(1) + css + m.group(3)
    page = re.sub(r"(<style>)(.*?)(</style>)", troca, page, flags=re.S)
    css_all = "".join(re.findall(r"<style>(.*?)</style>", page, flags=re.S))
    esp = "".join(_scoped(inner, "html.dm ") for cond, inner in _media_blocks(css_all)
                  if (m := re.fullmatch(r"\(max-width:\s*(\d+)px\)", cond)) and 412 <= int(m.group(1)) <= 820)
    base = ("<style>:root { --vw: 1vw; --vh: 1vh; } html.dm { zoom: var(--z); --vw: calc(1vw / var(--z)); --vh: calc(1vh / var(--z)); }</style>"
            "<style>/* espelho das media de celular */" + esp + "</style>")
    topo = ("<script>(function(){var d=document.documentElement,s=Math.min(screen.width,screen.height),w=window.innerWidth;"
            "if(w>820&&s>0&&s<=700&&w/s>1.5){d.classList.add('dm');d.style.setProperty('--z',(w/s).toFixed(3));}})();</script>")
    return page.replace("<!--vary:start-->", "<!--vary:start-->" + topo + base, 1)

def kind_and_info(html):
    m = re.search(r"/\* (\w+): identidade", html)
    return (m.group(1) if m else None), ('<figure><img src="img/' in html), ('id="casa"' in html and "class=\"pull\"" in html)


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
    f = FONTE_CUSTOM.get(slug) or FONTS[kind][c["font"]]
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
        if lst is None: css.append(HERO[hero].replace("brightness(.92)", "brightness(.55) saturate(1.08)") if slug in CAPA_CLARA else HERO[hero]); continue
        if lst[c[key]]: css.append(lst[c[key]])
    extra = (SCRIPT_BLEED if hero == 6 else "") + (SCRIPT_GLOW if c["gallery"] == 5 else "") + (SCRIPT_AV if c["proof"] == 4 else "")
    css.append(QMORE_CSS)
    css.append(CONTRASTE_CSS)
    if slug in GALERIA_FILTRO: css.append(".tile img { filter: " + GALERIA_FILTRO[slug] + "; }")
    if slug in CSS_EXTRA: css.append(CSS_EXTRA[slug])
    if slug in LEGIVEL:
        _c, _in = _media_blocks(LEGIVEL_CSS)[0]
        css.append("@media " + _c + " {" + _scoped(_in, "html:not(.dm) ") + "}")
    if slug in SOBRE_TEXTO: css.append(SOBRE_CSS)
    if slug in SOBRE_TEXTO and any(len(c) > 2 for c in SOBRE_TEXTO[slug]["cards"]): css.append(ICONES_CSS)
    if slug in AVAL_LINK: css.append(AVAL_CSS)
    if slug in GALERIA_TEXTO: css.append(GCTA_CSS); link += GCTA_LINK
    if slug in INTRO: css.append(INTRO_CSS); extra += SCRIPT_NUDGE
    if c["gallery"] == 5:
        _a = ACCENTS[c["accent"]]; _h = (_a[1][0] if _a else "#ffaa50").lstrip("#")
        css.insert(0, ":root { --glow: " + " ".join(str(int(_h[i:i + 2], 16)) for i in (0, 2, 4)) + "; }")
    if hero == 6 and slug in FOCO_MOBILE: css.insert(0, ":root { --foco: " + FOCO_MOBILE[slug] + "; }")
    return "<!--vary:start-->" + link + "<style>\n  /* variação: " + ",".join(f"{d}={c[d]}" for d in DIMS) + " */\n  " + "\n  ".join(css) + "\n</style>" + extra + "<!--vary:end-->"


def run(only=None):
    pages = {}
    for f in sorted(glob.glob(os.path.join(HERE, "*", "index.html"))):
        slug = os.path.basename(os.path.dirname(f))
        if slug in SKIP: continue
        html = re.sub(r"\n*<!--vary:start-->.*?<!--vary:end-->", "", open(f, encoding="utf-8").read(), flags=re.S)
        if slug in GALERIA_TEXTO:
            t, sub, cta = GALERIA_TEXTO[slug]
            html = re.sub(r'(<section id="fotos"[^>]*>\s*<h2>)[^<]*(</h2>\s*<p class="sub">)[^<]*(</p>)(?:\s*<p class="gcta">[^<]*</p>)?', lambda m: m.group(1) + t + m.group(2) + sub + m.group(3) + '<p class="gcta">' + cta + "</p>", html, count=1)
        if slug in SOBRE_TEXTO:
            S = SOBRE_TEXTO[slug]; e = __import__("html").escape
            novo = e(S["h2"]) + "</h2>\n        " + "\n        ".join("<p>" + e(p) + "</p>" for p in S["paras"]) + '\n        <ul class="services">' + "".join('<li class="svc">' + (f'<i class="ic" aria-hidden="true">{ICONES[c[2]]}</i>' if len(c) > 2 else "") + "<b>" + e(c[0]) + "</b><span>" + e(c[1]) + "</span></li>" for c in S["cards"]) + "</ul>" + ('<p class="sub" style="margin:14px 0 0;font-size:15px">' + e(S["nota"]) + "</p>" if S["nota"] else "")
            html = re.sub(r'(<section id="casa">\s*<div class="about[^"]*">\s*<div>\s*<h2>).*?</h2>\s*(?:<p>.*?</p>\s*)+(?:<ul class="services">.*?</ul>\s*(?:<p class="sub"[^>]*>.*?</p>)?)?', lambda m: m.group(1) + novo, html, count=1, flags=re.S)
            html = re.sub(r'<p class="pull">.*?</p>', lambda m: '<p class="pull">\u201c' + e(S["pull"][0]) + '\u201d<br><span style="font:500 15px var(--font-body);color:var(--ink-soft)">' + e(S["pull"][1]) + "</span></p>", html, count=1, flags=re.S)
            html = re.sub(r'(id="clientes">.*?<h2>)[^<]*(</h2>)', lambda m: m.group(1) + e(S["prova"]) + m.group(2), html, count=1, flags=re.S)
        if slug in WA_TEXTO:
            q = __import__("urllib.parse", fromlist=["quote"]).quote(WA_TEXTO[slug], safe="")
            html = re.sub(r'href="(https://wa\.me/\d+)(?:\?text=[^"]*)?"', lambda m: 'href="' + m.group(1) + "?text=" + q + '"', html)
        if slug in AVAL_LINK and (mp := re.search(r'query_place_id=([^"&]+)', html)):
            url = "https://search.google.com/local/reviews?placeid=" + mp.group(1)
            link = f'<a class="rev-link" href="{url}" target="_blank" rel="noopener"><span class="rs" aria-hidden="true">\u2605\u2605\u2605\u2605\u2605</span><span class="rt">Veja as avaliações no Google</span></a>'
            html = re.sub(r'(id="clientes">.*?<p class="eyebrow">)(?:<a class="rev-link".*?</a>|[^<]*)(</p>)', lambda m: m.group(1) + link + m.group(2), html, count=1, flags=re.S)
            html = re.sub(r'<(?:div|a) class="score"( aria-label="[^"]*")?( href="[^"]*" target="_blank" rel="noopener")?>\s*(<strong>.*?</strong>\s*<div>.*?</div>)\s*</(?:div|a)>', lambda m: f'<a class="score" href="{url}" target="_blank" rel="noopener"{m.group(1) or ""}>{m.group(3)}</a>', html, count=1, flags=re.S)
        if slug in HERO_TEXTO:
            eb, ld, *h1t = HERO_TEXTO[slug]
            if h1t: html = re.sub(r"(<h1>)[^<]*(</h1>)", lambda m: m.group(1) + h1t[0] + m.group(2), html, count=1)
            html = re.sub(r'(<div class="hero">\s*<div>\s*<p class="eyebrow">)[^<]*(</p>)', lambda m: m.group(1) + eb + m.group(2), html, count=1)
            html = re.sub(r'(<p class="lede">)[^<]*(</p>)', lambda m: m.group(1) + ld + m.group(2), html, count=1)
        if slug in FINAL_TEXTO:
            ft, fs = FINAL_TEXTO[slug]
            html = re.sub(r'(<section class="final">\s*<h2>)[^<]*(</h2>\s*<p class="sub"[^>]*>)[^<]*(</p>)', lambda m: m.group(1) + ft + m.group(2) + fs + m.group(3), html, count=1)
        html = re.sub(r'\s*<p class="src">.*?</p>', "", html, flags=re.S)  # nunca mostrar a nota "Trechos de avaliações públicas..."
        if slug in LOGO_INJECT and os.path.exists(os.path.join(HERE, slug, "img", "logo.jpg")):
            html = re.sub(r'(<a class="brand" href="#topo">)(?!<img)', lambda m: m.group(1) + '<img src="img/logo.jpg" alt="" width="40" height="40">', html, count=1)
            html = re.sub(r'(<span style="display:flex;align-items:center;gap:12px">)(?!<img)(<strong)', lambda m: m.group(1) + '<img src="img/logo.jpg" alt="" width="52" height="52" style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:2px solid var(--salmon)">' + m.group(2), html, count=1)
        html = add_qmore(html)
        kind, fig, pull = kind_and_info(html)
        if slug in PLANO_FIXO: kind = PLANO_FIXO[slug][0]
        if kind: pages[slug] = (f, html, kind, fig)
    by_kind = {}
    for s, (_, _, k, _) in pages.items():
        if s not in PLANO_FIXO: by_kind.setdefault(k, []).append(s)
    plan = assign(by_kind)
    for s, (_k, p) in PLANO_FIXO.items():
        if s in pages: plan[s] = dict(p)
    for s, o in OVERRIDE.items():
        if s in plan: plan[s].update(o)
    for s, (f, html, k, fig) in pages.items():
        if only and s not in only: continue
        i = html.index("</style>") + len("</style>")
        b = block(k, plan[s], fig, s)
        if s in FORCE_DARK:  # reaplica as variáveis do tema escuro direto no :root (sem depender de prefers-color-scheme)
            dk = "".join(m.group(1) for m in re.finditer(r':root\[data-theme="dark"\] \{([^}]*)\}', html + b))
            b = b.replace("<!--vary:end-->", "<style>:root { " + dk + " }</style><!--vary:end-->")
        if s in TEMA_LIGHT: b = b.replace("<!--vary:end-->", "<style>html:root:root { " + TEMA_LIGHT[s] + " color-scheme: light; }</style><!--vary:end-->")
        if s in TEMA_CUSTOM: b = b.replace("<!--vary:end-->", "<style>:root { " + TEMA_CUSTOM[s] + " }</style><!--vary:end-->")
        page = html[:i] + "\n" + b + html[i:]
        if s in DM_SITES: page = modo_ampliado(page)
        open(f, "w", encoding="utf-8").write(page)
    json.dump({s: dict(kind=pages[s][2], **plan[s]) for s in pages}, open(os.path.join(HERE, "variants.json"), "w"), indent=1, ensure_ascii=False)
    return plan


if __name__ == "__main__":
    plan = run(set(sys.argv[1:]) or None)
    for s, c in sorted(plan.items()): print(f"{s:46s}", " ".join(f"{c[d]}" for d in DIMS))
