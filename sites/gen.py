#!/usr/bin/env python3
"""Gera um site por negócio a partir do modelo da Don Alberttoni.
Uso: python3 gen.py [slug ...]   (sem argumentos, gera todos)
Entrada: _data/*.json (Apify), <slug>/photos.json + <slug>/img/pNN.jpg, vetoes.json
Saída:   <slug>/index.html, <slug>/img/(hero|gN).jpg, manifest.json"""
import glob, html, json, os, re, shutil, sys, unicodedata
from fetch_photos import clean_name, slugify

HERE = os.path.dirname(os.path.abspath(__file__))
esc = lambda s: html.escape(str(s), quote=True)
LEOSUMIU = "https://leoperon2.github.io/vintage-riders-prototipo/leosumiu"
DON = open(os.path.join(HERE, "don-alberttoni", "index.html"), encoding="utf-8").read()
CSS_MAIN = DON[DON.index("  * { box-sizing"):DON.index("</style>")]
JS_GALLERY = DON[DON.index("<script>\n(function () {\n  var reduce"):]

# ---------------------------------------------------------------- temas
def T(bg, surface, ink, soft, wood, woodink, accent, accentink, salmon, line):
    return dict(bg=bg, surface=surface, ink=ink, inksoft=soft, wood=wood, woodink=woodink, accent=accent, accentink=accentink, salmon=salmon, line=line)

THEMES = {
 "barber": dict(fonts="family=Alfa+Slab+One&family=Work+Sans:wght@400;500;600", display='"Alfa Slab One", "Rockwell", Georgia, serif', body='"Work Sans", system-ui, sans-serif',
   stripe="repeating-linear-gradient(115deg, var(--accent) 0 26px, var(--surface) 26px 52px, var(--salmon) 52px 78px, var(--surface) 78px 104px)", extra="",
   variants=[
    (T("#dfeaee","#f3f8fa","#2a1b14","#5a4a41","#3a2418","#f3e9e1","#9b2c1f","#fff6f2","#e7b3a0","#b9ced6"), T("#1b130f","#26190f","#f1e7df","#c2b0a3","#0f0a07","#f1e7df","#e0654f","#1b130f","#b9735f","#4a3628")),
    (T("#e4e9e2","#f4f7f2","#1d2a22","#4b5a50","#22332a","#eef2ea","#b5472a","#fff7f2","#d9a66b","#bccabd"), T("#121a15","#1b261f","#e6eee6","#a9b9ac","#0b100d","#e6eee6","#e0794f","#121a15","#a9824a","#2f4236")),
    (T("#e7e5ee","#f6f5fa","#231f33","#57536b","#2a2540","#eeecf6","#a8322d","#fff5f4","#d6a0a0","#c7c3d8"), T("#17141f","#211d2e","#ece9f6","#b0abc6","#0e0c14","#ece9f6","#e5675f","#17141f","#a86f6f","#383350"))]),
 "tattoo": dict(fonts="family=Pirata+One&family=Work+Sans:wght@400;500;600", display='"Pirata One", "Georgia", serif', body='"Work Sans", system-ui, sans-serif',
   stripe="repeating-linear-gradient(90deg, var(--accent) 0 3px, var(--wood) 3px 18px)", extra="h1,h2,h3{letter-spacing:.02em} .hero h1{font-size:clamp(46px,8vw,92px)}",
   variants=[
    (T("#e8e2d6","#f3eee4","#14100e","#54493f","#14100e","#efe9df","#c0392b","#ffffff","#b8a67f","#c9bfae"), T("#100d0b","#1a1613","#efe9df","#b3a798","#070605","#efe9df","#e5584a","#100d0b","#8a7a58","#342d27")),
    (T("#e3e6df","#f1f3ed","#101512","#4a544d","#101512","#e8ece4","#2f8f6b","#ffffff","#b0b79a","#c2c9bb"), T("#0d110f","#161c19","#e8ece4","#a7b2a9","#060807","#e8ece4","#4fc08f","#0d110f","#7a8466","#2b332e")),
    (T("#e6e0ea","#f3eff6","#16101a","#58495f","#16101a","#efe8f3","#7a3fb0","#ffffff","#b9a3c9","#cbbfd4"), T("#110d14","#1b1520","#efe8f3","#b5a6bd","#08060a","#efe8f3","#a56be0","#110d14","#85709a","#352b3d"))]),
 "burger": dict(fonts="family=Bowlby+One&family=Work+Sans:wght@400;500;600", display='"Bowlby One", "Arial Black", sans-serif', body='"Work Sans", system-ui, sans-serif',
   stripe="conic-gradient(var(--accent) 25%, var(--salmon) 0 50%, var(--accent) 0 75%, var(--salmon) 0) 0 0 / 28px 28px", extra=".hero h1{font-size:clamp(36px,6.4vw,66px)}",
   variants=[
    (T("#ffe8a3","#fff6d6","#2b1408","#6b4a2c","#2b1408","#ffe8a3","#c8281e","#fff4ee","#ff9f1c","#e6c978"), T("#1c1008","#2a1a0e","#ffe8a3","#cfae78","#0f0803","#ffe8a3","#ee5a46","#1c1008","#d98a14","#4a3220")),
    (T("#f7e2b8","#fff3d9","#241408","#6a4c2c","#241408","#f7e2b8","#2f7d32","#f4fff3","#ffb703","#e2c88f"), T("#171008","#251a0d","#f7e2b8","#c9ab78","#0c0803","#f7e2b8","#5cbd60","#171008","#d99a02","#46341d"))]),
 "salon": dict(fonts="family=Bodoni+Moda:wght@500;700&family=DM+Sans:wght@400;500;600", display='"Bodoni Moda", "Didot", Georgia, serif', body='"DM Sans", system-ui, sans-serif',
   stripe="radial-gradient(circle, var(--accent) 3px, transparent 3.6px) 0 0 / 24px 14px, var(--salmon)", extra="h1,h2,h3{font-weight:500}",
   variants=[
    (T("#f4e4e8","#fbf1f3","#2e1620","#6b4756","#3a1a2b","#fbe9ee","#a2335a","#fff2f6","#e7a9bb","#e0c3cb"), T("#1d0f16","#2a1621","#f7e6ec","#c7a3b2","#12080d","#f7e6ec","#e0709a","#1d0f16","#a35c75","#432533")),
    (T("#ebe4f2","#f6f2fa","#2a1d3a","#5f5073","#33224a","#f1eaf9","#7b3fb5","#fbf5ff","#d3b1ec","#d3c6e2"), T("#17101f","#221731","#efe7f8","#b7a6cd","#0d0813","#efe7f8","#b27de0","#17101f","#7d5da0","#382a4d"))]),
 "pet": dict(fonts="family=Fredoka:wght@500;600&family=Nunito:wght@400;600;700", display='"Fredoka", "Trebuchet MS", sans-serif', body='"Nunito", system-ui, sans-serif',
   stripe="radial-gradient(circle, var(--wood) 3px, transparent 3.6px) 0 0 / 22px 14px, var(--salmon)", extra="h1,h2,h3{font-weight:600}",
   variants=[
    (T("#def2ee","#f2fbf9","#12302f","#3f625f","#12474a","#e6faf6","#0f8b8d","#ffffff","#ffc857","#b6dcd6"), T("#0d1d1d","#142a2a","#dff4f0","#9ec4be","#071212","#dff4f0","#38c0c2","#0d1d1d","#c79a2e","#24413f")),
    (T("#ffeacc","#fff6e6","#3b2208","#7a5630","#5a3410","#ffeacc","#e0701a","#ffffff","#7ecbc0","#f0cf9c"), T("#1f1408","#2d1d0d","#ffeacc","#d1b083","#120b04","#ffeacc","#f58f3c","#1f1408","#3d8f84","#4a3320"))]),
 "auto": dict(fonts="family=Anton&family=Barlow:wght@400;500;600", display='"Anton", "Impact", sans-serif', body='"Barlow", system-ui, sans-serif',
   stripe="repeating-linear-gradient(-45deg, var(--salmon) 0 16px, var(--wood) 16px 32px)", extra="h1,h2,h3{text-transform:uppercase;letter-spacing:.015em} body{font-size:18px}",
   variants=[
    (T("#e4e7ea","#f3f5f6","#15191d","#4a5560","#20262c","#eef0f2","#d9500b","#ffffff","#f2b84b","#c3cad0"), T("#101417","#1a2024","#e8ecef","#9ba7b0","#080a0c","#e8ecef","#ff7a2e","#101417","#c28f2e","#2d363d")),
    (T("#e3e8ee","#f2f5f9","#10161f","#4a5668","#17202e","#eaeff6","#1d5fd0","#ffffff","#f2c14b","#c0cada"), T("#0d1118","#161d28","#e6ecf5","#9aa8bd","#070a0f","#e6ecf5","#5a96f0","#0d1118","#c29a35","#283244"))]),
 "clinic": dict(fonts="family=Playfair+Display:wght@500;700&family=Work+Sans:wght@400;500;600", display='"Playfair Display", Georgia, serif', body='"Work Sans", system-ui, sans-serif',
   stripe="linear-gradient(90deg, var(--salmon), var(--accent), var(--salmon))", extra="h1,h2,h3{font-weight:500}",
   variants=[(T("#e3ece6","#f3f8f4","#172a21","#4c6256","#1f3a30","#edf5f0","#3d7a5c","#ffffff","#b9d4c2","#bfd2c6"), T("#0f1a15","#17261f","#e3efe8","#a2bbac","#08100c","#e3efe8","#6ec198","#0f1a15","#5b8a73","#2a4035"))]),
}

COPY = {
 "barber": dict(gal="Por dentro", gsub="Fotos enviadas por clientes no Google Maps.", final="Sua cadeira está reservada?", fsub="Chame a equipe e marque o seu horário.", wa="Chamar no WhatsApp", cat="Barbearia"),
 "tattoo": dict(gal="Trabalhos", gsub="Tatuagens e piercings enviados por clientes no Google Maps.", final="Sua próxima tattoo começa aqui", fsub="Conte a ideia ao estúdio e peça um orçamento.", wa="Pedir orçamento", cat="Estúdio de tatuagem"),
 "burger": dict(gal="No prato", gsub="Fotos enviadas por clientes no Google Maps.", final="Bateu a fome?", fsub="Peça o seu pelo WhatsApp ou passe por lá.", wa="Pedir no WhatsApp", cat="Hamburgueria"),
 "salon": dict(gal="Resultados", gsub="Fotos enviadas por clientes no Google Maps.", final="Hora de cuidar de você", fsub="Marque o seu horário com a equipe.", wa="Agendar no WhatsApp", cat="Salão de beleza"),
 "pet": dict(gal="Os clientes de quatro patas", gsub="Fotos enviadas por clientes no Google Maps.", final="Seu pet merece esse cuidado", fsub="Fale com a equipe e combine o melhor horário.", wa="Chamar no WhatsApp", cat="Pet shop"),
 "auto": dict(gal="Na oficina", gsub="Fotos enviadas por clientes no Google Maps.", final="Seu carro em boas mãos", fsub="Chame no WhatsApp e peça um orçamento.", wa="Pedir orçamento", cat="Oficina"),
 "clinic": dict(gal="Resultados", gsub="Fotos enviadas por clientes no Google Maps.", final="Cuide de você com calma", fsub="Marque uma conversa com a equipe.", wa="Agendar no WhatsApp", cat="Beleza e estética"),
}

def kind_of(cat, name):
    c = (cat + " " + name).lower()
    if "tatu" in c or "piercing" in c or "tattoo" in c: return "tattoo"
    if "hambur" in c or "burger" in c or "gastrobar" in c or "restaurante" in c: return "burger"
    if "barbearia" in c: return "barber"
    if "pet" in c: return "pet"
    if any(k in c for k in ("oficina", "mecânic", "mecanic", "autopeça", "usinagem", "motos", "auto center")): return "auto"
    if "saúde e beleza" in c or "estética" in c or "clínica" in c or "clinica" in c: return "clinic"
    return "salon"

# ---------------------------------------------------------------- utilidades de texto
def short_name(n):
    p = [x for x in re.split(r"\s+", (n or "").strip()) if x]
    if not p: return "Cliente"
    if len(p) > 1 and p[1][:1].isalpha(): return f"{p[0]} {p[1][0].upper()}."
    return p[0]

EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F\u200d\u2B50\u2B06\u2705]+")

def nemoji(t):
    return re.sub(r"\s{2,}", " ", EMOJI.sub("", t or "")).strip()

def credit(who):
    return f"Instagram {who}" if (who or "").startswith("@") else f"Foto de {first_name(who)}"

def first_name(n):
    p = (n or "").split()
    w = p[0] if p else ""
    if not re.fullmatch(r"[A-Za-zÀ-ÿ'\-]{2,14}", w): return "cliente"
    return w.title() if w.isupper() else w[:1].upper() + w[1:]

def clean_owner(t, city=""):
    paras = []
    for p in [x.strip() for x in re.split(r"\n\s*\n", nemoji(t or "")) if x.strip()]:
        words = re.findall(r"\w+", p.lower())
        grams = [" ".join(words[i:i + 3]) for i in range(len(words) - 2)]
        spam = p.count("#") >= 2 or (grams and max(grams.count(g) for g in set(grams)) >= 3) or (city and p.lower().count(city.lower()) >= 3)
        if not spam and len(p) > 25: paras.append(p)
    return "\n\n".join(paras)

def fmt_phone(p):
    d = re.sub(r"\D", "", p or "")
    d = d[2:] if d.startswith("55") and len(d) > 11 else d
    if len(d) == 11: return f"({d[:2]}) {d[2:7]}-{d[7:]}", True
    if len(d) == 10: return f"({d[:2]}) {d[2:6]}-{d[6:]}", False
    return (p or ""), False

def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", t or "") if s.strip()]

def good_text(t):
    return t and not re.search(r"https?://|www\.|@\w|\d{4,}", t)

BAD_TAG = {"certeza", "vez", "dia", "pessoal", "lugar", "tempo", "gente", "pessoas", "coisa", "cliente", "clientes", "parabéns", "sempre", "muito", "ótimo", "excelente", "perfeito", "melhor", "bom", "boa", "super", "nota", "recomendo", "nunca", "voltar", "indico"}
GOOD_TAG = {"atendimento", "ambiente", "preço", "qualidade", "equipe", "profissional", "profissionais", "resultado", "limpeza", "música", "cuidado", "capricho", "corte", "barba", "estúdio", "higiene", "localização", "sabor", "carne", "hambúrguer", "pão", "batata", "molho", "cerveja", "entrega", "banho", "tosa", "animais", "orçamento", "prazo", "serviço", "oficina", "confiança", "honestidade", "cabelo", "unhas", "maquiagem", "escova", "tratamento", "pele", "espaço", "cardápio", "porção", "variedade", "agendamento", "pontualidade", "simpatia", "arte", "traço", "desenho", "tatuagem", "tatuador", "cor", "cores", "cabeleireira", "cabelereira", "atenção", "cuidadoso", "carinho", "pet", "mecânico", "peças", "diagnóstico", "projeto", "acabamento", "conforto", "decoração", "estrutura"}

def tag_cards(place):
    reviews = [r for r in place.get("reviews") or [] if (r.get("stars") or 0) >= 4 and good_text(r.get("text"))]
    tags = [t for t in place.get("reviewsTags") or [] if t["title"].lower() not in BAD_TAG and t["count"] >= 3]
    ordered = [t for t in tags if t["title"].lower() in GOOD_TAG] + [t for t in tags if t["title"].lower() not in GOOD_TAG and t["title"].isalpha() and len(t["title"]) >= 6 and t["title"] == t["title"].lower() and t["count"] >= 5]
    cards, used = [], set()
    for t in ordered:
        w = t["title"]
        best = None
        for r in sorted(reviews, key=lambda r: -(r.get("likesCount") or 0)):
            for s in sentences(r.get("text")):
                s = nemoji(s)
                if s not in used and re.search(rf"\b{re.escape(w)}", s, re.I) and 28 <= len(s) <= 120:
                    best = s; used.add(s); break
            if best: break
        cards.append((w[:1].upper() + w[1:], t["count"], best))
        if len(cards) == 4: break
    return cards

def pick_quotes(place, n=5):
    rs = [r for r in place.get("reviews") or [] if (r.get("stars") or 0) >= 5 and good_text(r.get("text")) and 45 <= len(r["text"].strip()) <= 300]
    rs.sort(key=lambda r: (-(r.get("likesCount") or 0), -len(r["text"])))
    out, seen = [], set()
    for r in rs:
        k = (r.get("name") or "")
        if k in seen: continue
        seen.add(k); out.append(r)
        if len(out) == n: break
    return out

def pull_quote(place):
    cands = []
    for r in place.get("reviews") or []:
        if (r.get("stars") or 0) < 5 or not good_text(r.get("text")): continue
        for s in sentences(r["text"]):
            if 40 <= len(s) <= 105 and s[-1] in ".!" and not s.lower().startswith(("sou ", "fui ", "fiz ")):
                cands.append(((r.get("likesCount") or 0), len(s), nemoji(s).rstrip(), r.get("name")))
    cands.sort(key=lambda c: (-c[0], -c[1]))
    return cands[0] if cands else None

# ---------------------------------------------------------------- horários
DAYS = {"segunda": 1, "terça": 2, "terca": 2, "quarta": 3, "quinta": 4, "sexta": 5, "sábado": 6, "sabado": 6, "domingo": 0}
DAY_LABEL = {1: "Segunda", 2: "Terça", 3: "Quarta", 4: "Quinta", 5: "Sexta", 6: "Sábado", 0: "Domingo"}

def tmin(s, ampm_hint=None):
    m = re.match(r"\s*(\d{1,2})(?::(\d{2}))?\s*([AaPp][Mm])?", s)
    if not m: return None
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or ampm_hint or "").lower()
    if ap == "pm" and h < 12: h += 12
    if ap == "am" and h == 12: h = 0
    return h * 60 + mi

def parse_hours(oh):
    out = {}
    for e in oh or []:
        d = None
        for k, v in DAYS.items():
            if e["day"].lower().startswith(k): d = v
        if d is None: continue
        s = e["hours"].strip()
        low = s.lower()
        if "fechado" in low or "closed" in low: out[d] = []; continue
        if "24" in low: out[d] = [[0, 1440]]; continue
        ranges = []
        for part in s.split(","):
            sides = re.split(r"\s+(?:to|às|as|–|-)\s+", part.strip())
            if len(sides) == 2:
                ap = re.search(r"([AaPp][Mm])", sides[1]); ap = ap.group(1) if ap else None
                a, b = tmin(sides[0], ap), tmin(sides[1])
                if a is not None and b is not None: ranges.append([a, b])
        out[d] = ranges
    return out if out else None

def fmt_t(m):
    h, mi = divmod(m % 1440, 60)
    return f"{h}h" if mi == 0 else f"{h}h{mi:02d}"

def hours_text(ranges):
    if not ranges: return None
    if ranges == [[0, 1440]]: return "24 horas"
    return " e ".join(f"{fmt_t(a)} às {fmt_t(b)}" for a, b in ranges)

# ---------------------------------------------------------------- fotos
LAY = {
 9: [("1/3","1/4","tall"),("3/5","1/3","sq"),("5/7","1/4","tall"),("3/5","3/5","sq"),("1/3","4","wide"),("5/7","4","wide"),("1/3","5/7","sq"),("3/5","5/7","sq"),("5/7","5/7","sq")],
 8: [("1/3","1/4","tall"),("3/5","1/3","sq"),("5/7","1/4","tall"),("3/5","3/5","sq"),("1/3","4","wide"),("5/7","4","wide"),("1/4","5/7","wide"),("4/7","5/7","wide")],
 7: [("1/3","1/4","tall"),("3/5","1/3","sq"),("5/7","1/4","tall"),("3","3","sq"),("4","3","sq"),("1/4","4/6","wide"),("4/7","4/6","wide")],
 6: [("1/3","1/4","tall"),("3/5","1/3","sq"),("5/7","1/4","tall"),("3/5","3","wide"),("1/4","4/6","wide"),("4/7","4/6","wide")],
 5: [("1/4","1/3","wide"),("4/7","1/3","wide"),("1/3","3","wide"),("3/5","3","wide"),("5/7","3","wide")],
 4: [("1/4","1/3","wide"),("4/7","1/3","wide"),("1/4","3/5","wide"),("4/7","3/5","wide")],
 3: [("1/4","1/4","sq"),("4/7","1/3","wide"),("4/7","3","wide")],
}
TARGET = {"tall": 0.62, "sq": 1.0, "wide": 1.45}
MAXGAL = 18

SPAN = {"s": (1, 1), "v": (1, 2), "b": (2, 2), "w": (2, 1)}

def holes(types, cols):
    """Simula o auto-posicionamento 'dense' do CSS grid e conta células vazias."""
    grid = []
    for t in types:
        w, h = SPAN[t]; w = min(w, cols)
        r = 0
        while True:
            while len(grid) < r + h: grid.append([False] * cols)
            hit = next((c for c in range(cols - w + 1) if all(not grid[r + i][c + j] for i in range(h) for j in range(w))), None)
            if hit is not None:
                for i in range(h):
                    for j in range(w): grid[r + i][hit + j] = True
                break
            r += 1
    return sum(1 for row in grid for x in row if not x)

def plan_mosaic(photos, seed):
    """Sorteia o formato de cada foto (vertical, dobro, panorâmica, pequena) até encaixar sem buracos em 4 e 2 colunas."""
    import random
    n = len(photos)
    rnd = random.Random(seed)
    def allowed(p):
        a = p["aspect"]
        if a < 0.78: return ["v", "v", "v", "s", "b"]
        if a > 1.5: return ["w", "s", "b"]
        return ["s", "s", "b"] + (["v"] if a < 1.0 else []) + (["w"] if a > 1.2 else [])
    for need_b in (True, False):
        for _ in range(9000):
            order = list(range(n)); rnd.shuffle(order)
            types = [rnd.choice(allowed(photos[i])) for i in order]
            nb = types.count("b")
            if nb > max(1, n // 5) or (need_b and nb == 0) or types[0] == "w": continue
            if holes(types, 4) == 0 and holes(types, 2) == 0:
                return [(types[k], photos[order[k]]) for k in range(n)]
    return None

def choose_photos(slug):
    base = os.path.join(HERE, slug)
    meta = json.load(open(os.path.join(base, "photos.json"))) if os.path.exists(os.path.join(base, "photos.json")) else []
    vh = json.load(open(os.path.join(HERE, "vetoes_hash.json"))).get(slug, []) if os.path.exists(os.path.join(HERE, "vetoes_hash.json")) else []
    ham = lambda a, b: sum(x != y for x, y in zip(a, b))
    meta = [m for m in meta if not any(ham(m.get("hash", ""), v) < 7 for v in vh)]
    strict = [m for m in meta if not (m.get("tf", 0) > 0.02 or m.get("tn", 0) >= 2)]
    meta = strict if len(strict) >= 14 else [m for m in meta if not (m.get("tf", 0) > 0.04 or m.get("tn", 0) >= 4)]
    if not meta: return None, []
    pool = sorted(meta, key=lambda m: -m["q"])
    hero = next((m for m in pool if 0.95 <= m["aspect"] <= 1.9), pool[0])
    rest = [m for m in pool if m is not hero][:MAXGAL]
    for n in range(len(rest), 2, -1):
        pl = plan_mosaic(rest[:n], slug)
        if pl: return hero, pl
    return hero, []

# ---------------------------------------------------------------- página
def build(place, idx):
    nome = clean_name(place["title"])
    slug = slugify(nome)
    base = os.path.join(HERE, slug)
    kind = kind_of(place.get("categoryName") or "", nome)
    th = THEMES[kind]; cp = COPY[kind]
    light, dark = th["variants"][idx % len(th["variants"])]
    hero, gal = choose_photos(slug)

    # imagens finais
    img_dir = os.path.join(base, "img")
    src_dir = os.path.join(base, "_src")
    if not os.path.isdir(src_dir): os.rename(img_dir, src_dir)
    keep = {}
    if hero: keep["hero.jpg"] = hero["file"]
    for k, (_, m) in enumerate(gal, 1): keep[f"g{k}.jpg"] = m["file"]
    tmp = os.path.join(base, "_img")
    if os.path.isdir(tmp): shutil.rmtree(tmp)
    os.makedirs(tmp)
    for dst, src in keep.items(): shutil.copy(os.path.join(src_dir, os.path.basename(src)), os.path.join(tmp, dst))
    has_logo = os.path.exists(os.path.join(src_dir, "logo.jpg"))
    if has_logo: shutil.copy(os.path.join(src_dir, "logo.jpg"), os.path.join(tmp, "logo.jpg"))
    if os.path.isdir(img_dir): shutil.rmtree(img_dir)
    os.rename(tmp, img_dir)

    cidade = place.get("city") or ""; bairro = place.get("neighborhood") or ""
    nota = place.get("totalScore") or 0; nrev = place.get("reviewsCount") or 0
    notas = f"{nota:.1f}".replace(".", ",")
    cat = (place.get("categoryName") or cp["cat"]).replace("colocação de piercing", "piercing")
    phone_txt, is_mobile = fmt_phone(place.get("phone"))
    digits = re.sub(r"\D", "", place.get("phone") or "")
    wa = f"https://wa.me/{digits if digits.startswith('55') else '55' + digits}" if is_mobile else None
    insta = next((u for u in (place.get("instagrams") or []) if not re.search(r"avec|wix|linktree|facebook|instagram\.com/(p|reel|explore)", u)), None)
    insta_user = re.sub(r".*instagram\.com/", "", insta).strip("/").split("?")[0] if insta else None
    booking = None
    for u in [b.get("url") for b in place.get("bookingLinks") or []] + [place.get("servicesLink"), place.get("reserveTableUrl")]:
        if u and not re.search(r"whatsapp|wa\.me|wa\.link|instagram|linktr\.ee|facebook|fb\.com", u):
            booking = u; break
    maps = f"https://www.google.com/maps/search/?api=1&query={re.sub(' ', '%20', nome)}&query_place_id={place.get('placeId')}"
    owner = clean_owner(place.get("ownerDescription") or place.get("description") or "", cidade)

    cta = []
    if booking: cta.append(("Agendar online", booking, True))
    if wa: cta.append((cp["wa"], wa, not cta))
    if insta and len(cta) < 2: cta.append(("Ver no Instagram", insta, not cta))
    if not cta: cta.append(("Como chegar", maps, True))
    cta_html = "".join(f'<a class="btn{"" if p else " ghost"}" href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>' for t, u, p in cta[:2])
    nav_cta = cta[0]

    lede = ""
    if owner:
        ss = sentences(owner)
        lede = ss[0]
        for s in ss[1:]:
            if len(lede) + len(s) < 190: lede += " " + s
            else: break
    if not lede or len(lede) < 30:
        lede = f"{cat} em {bairro or cidade}. {nrev} clientes avaliaram no Google, com nota média {notas}."
    if len(lede) > 230: lede = lede[:227].rsplit(" ", 1)[0] + "…"

    cards = tag_cards(place)
    pq = pull_quote(place)
    quotes = pick_quotes(place)
    dist = place.get("reviewsDistribution") or {}
    total = sum(dist.get(k, 0) for k in ("oneStar", "twoStar", "threeStar", "fourStar", "fiveStar")) or 1
    hours = parse_hours(place.get("openingHours"))

    # ---- seções
    nav = ['<a href="#casa">Sobre</a>']
    if gal: nav.append('<a href="#fotos">Fotos</a>')
    if quotes: nav.append('<a href="#clientes">Clientes</a>')
    nav.append('<a href="#horarios">Contato</a>' if not hours else '<a href="#horarios">Horários</a>')

    seal = f'<div class="seal" id="stamp" aria-label="Nota {notas} no Google"><b>{notas}</b><span>no Google</span></div>'
    stamp = f'<img class="logo-stamp" id="stamp" src="img/logo.jpg" alt="Logo de {esc(nome)}" width="136" height="136">' if has_logo else seal
    hero_html = (f'<figure><img src="img/hero.jpg" alt="Foto de {esc(nome)}" width="{hero["w"]}" height="{hero["h"]}">{stamp}</figure>' if hero else "")
    badge = f'<img class="logo-badge" src="img/logo.jpg" alt="Logo de {esc(nome)}" width="96" height="96">' if (has_logo and not hero) else ""

    about_paras = ""
    if owner:
        for p in [x.strip() for x in re.split(r"\n\s*\n", owner) if x.strip()][:3]:
            about_paras += f"<p>{esc(p)}</p>"
    else:
        extra = ""
        if cards: extra = " Entre os pontos mais citados nas avaliações estão " + ", ".join(c[0].lower() for c in cards[:3]) + "."
        local = f"em {bairro}, {cidade}" if bairro else f"em {cidade}"
        about_paras = f"<p>{esc(nome)} fica {esc(local)}. Os clientes dão nota {notas} em {nrev} avaliações no Google.{esc(extra)}</p>"
    cards_html = ""
    if cards:
        cards_html = '<ul class="services">' + "".join(
            f'<li class="svc"><b>{esc(t)}</b><span>{esc(s) if s else ""}{"" if s else f"citado em {n} avaliações"}</span></li>' for t, n, s in cards) + "</ul>"
        cards_html += '<p class="sub" style="margin:14px 0 0;font-size:15px">Temas mais citados pelos clientes nas avaliações do Google.</p>'
    pull_html = ""
    if pq:
        pull_html = f'<p class="pull">“{esc(pq[2])}”<br><span style="font:500 15px var(--font-body);color:var(--ink-soft)">{esc(short_name(pq[3]))}, em avaliação no Google</span></p>'
    about_cls = "about" if pull_html else "about one"
    sec_about = f'''<section id="casa">
    <div class="{about_cls}">
      <div>
        <h2>Conheça {esc(nome) if len(nome) < 28 else "o lugar"}</h2>
        {about_paras}
        {cards_html}
      </div>
      {pull_html}
    </div>
  </section>'''

    sec_gal = ""
    if gal:
        tiles = "".join(
            f'      <button class="tile {t}" type="button" aria-label="Ampliar foto {k}"><span class="ph"><img src="img/g{k}.jpg" alt="Foto de {esc(nome)}" loading="lazy"></span><span class="cap"></span></button>\n'
            for k, (t, m) in enumerate(gal, 1))
        sec_gal = f'''<section id="fotos" style="padding-top:0">
    <h2>{esc(cp["gal"])}</h2>
    <p class="sub">{esc(cp["gsub"])} Toque numa foto para ampliar e passe de uma para outra.</p>
    <div class="mosaic" id="mosaic">
{tiles}    </div>
  </section>'''
    lay_css = ""

    sec_proof = ""
    if quotes:
        bars = "".join(f'<div class="bar-row"><span>{s} ★</span><div class="track"><div class="fill" style="width:{100 * dist.get(k, 0) / total:.1f}%"></div></div><span>{dist.get(k, 0)}</span></div>'
                        for s, k in ((5, "fiveStar"), (4, "fourStar"), (3, "threeStar"), (2, "twoStar"), (1, "oneStar")))
        qs = ""
        for r in quotes:
            reply = r.get("responseFromOwnerText")
            rep = f'<div class="reply"><strong>Resposta do estabelecimento:</strong> {esc(reply[:200])}</div>' if reply and good_text(reply) else ""
            go = f'<a class="rv-go" href="{esc(r["reviewUrl"])}" target="_blank" rel="noopener" aria-label="Ver esta avaliação no Google">Ver no Google ↗</a>' if r.get("reviewUrl") else ""
            qs += f'<blockquote><p>{esc(r["text"].strip())}</p><cite>{esc(short_name(r.get("name")))}</cite>{go}{rep}</blockquote>'
        sec_proof = f'''<div class="proof" id="clientes">
  <div class="wrap">
    <section>
      <p class="eyebrow">Avaliações no Google</p>
      <h2>O que os clientes dizem</h2>
      <div class="proof-top">
        <div class="big">{notas}</div>
        <div class="bars" role="img" aria-label="Distribuição das {total} avaliações por estrelas">{bars}</div>
      </div>
      <div class="quotes">{qs}</div>
    </section>
  </div>
</div>'''

    # horários e contato
    hours_card = ""
    if hours:
        lis = ""
        for d in (1, 2, 3, 4, 5, 6, 0):
            if d not in hours: continue
            t = hours_text(hours[d])
            lis += f'<li data-d="{d}"><span>{DAY_LABEL[d]}</span>' + (f"<span>{t}</span>" if t else '<span class="closed">Fechado</span>') + "</li>"
        hours_card = f'<div class="card"><h3>Horário</h3><span class="status" id="status" hidden></span><ul class="hours" id="hours">{lis}</ul>' + tags_html(place) + "</div>"
    addr = place.get("address") or ""
    street = place.get("street") or addr.split(" - ")[0]
    contact = f'<p style="margin:0 0 6px">{"WhatsApp" if is_mobile else "Telefone"}: <button class="copy" id="copy" type="button">{esc(phone_txt)}</button> <span id="copied" aria-live="polite" style="font-size:14px;color:var(--ink-soft)"></span></p>' if phone_txt else ""
    if insta: contact += f'<p style="margin:0"><a href="{esc(insta)}" target="_blank" rel="noopener">@{esc(insta_user)}</a> no Instagram</p>'
    where = f'<div class="card"><h3>Onde estamos</h3><address>{esc(addr)}</address><p style="margin:0 0 18px"><a href="{esc(maps)}" target="_blank" rel="noopener">Abrir no Google Maps</a></p><h3 style="margin-top:26px">Contato</h3>{contact}'
    if not hours: where += tags_html(place)
    where += "</div>"
    info_cls = "info" if hours else "info single"
    sec_info = f'<section id="horarios"><h2>{"Horários e endereço" if hours else "Endereço e contato"}</h2><div class="{info_cls}">{hours_card}{where}</div></section>'
    sec_final = f'''<section class="final">
    <h2>{esc(cp["final"])}</h2>
    <p class="sub" style="margin-inline:auto">{esc(cp["fsub"])}</p>
    <div class="cta">{cta_html}</div>
  </section>'''

    css_theme = ":root {\n" + "".join(f"    --{k}: {v};\n" for k, v in {"bg": light["bg"], "surface": light["surface"], "ink": light["ink"], "ink-soft": light["inksoft"], "wood": light["wood"], "wood-ink": light["woodink"], "accent": light["accent"], "accent-ink": light["accentink"], "salmon": light["salmon"], "line": light["line"]}.items()) + f"    --font-display: {th['display']};\n    --font-body: {th['body']};\n    --stripe-bg: {th['stripe']};\n  }}\n"
    dk = "".join(f"--{k}: {v}; " for k, v in {"bg": dark["bg"], "surface": dark["surface"], "ink": dark["ink"], "ink-soft": dark["inksoft"], "wood": dark["wood"], "wood-ink": dark["woodink"], "accent": dark["accent"], "accent-ink": dark["accentink"], "salmon": dark["salmon"], "line": dark["line"]}.items())
    css_theme += f"  @media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {{ {dk}color-scheme: dark; }} }}\n  :root[data-theme=\"dark\"] {{ {dk}color-scheme: dark; }}\n"

    css = CSS_MAIN
    css = re.sub(r"  \.stripe \{ height: 14px; background: repeating[^\n]*\n", "  .stripe { height: 14px; background: var(--stripe-bg); margin-inline: calc(-1 * max(16px, env(safe-area-inset-left, 0px))); }\n", css)
    css = css.replace("    .mosaic .t-a { grid-column: span 2; grid-row: span 2; }", "")
    css = css.replace("  .hero img.stamp {", "  .hero img.stamp-unused {")
    seal_css = '''  .seal { position: absolute; left: -22px; bottom: -34px; width: 124px; height: 124px; border-radius: 50%; background: var(--accent); color: var(--accent-ink); display: grid; place-content: center; text-align: center; border: 6px solid var(--surface); box-shadow: 0 6px 0 var(--salmon); transform: rotate(calc(-8deg + var(--spin, 0deg))); }
  .seal b { font-family: var(--font-display); font-weight: 400; font-size: 38px; line-height: 1; }
  .seal span { font: 600 11px/1.2 var(--font-body); letter-spacing: .08em; text-transform: uppercase; margin-top: 4px; }
  .hero img.logo-stamp { position: absolute; left: -22px; bottom: -34px; width: 136px; height: 136px; aspect-ratio: 1; border-radius: 50%; object-fit: cover; background: #fff; border: 6px solid var(--surface); box-shadow: 0 6px 0 var(--salmon); transform: rotate(calc(-8deg + var(--spin, 0deg))); }
  .logo-badge { display: block; width: 96px; height: 96px; border-radius: 50%; object-fit: cover; margin: 0 0 18px; border: 4px solid var(--surface); box-shadow: 0 4px 0 var(--salmon); }
  .brand img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid var(--salmon); background: #fff; }
  .tile .cap { display: none; }
  .lb figcaption:empty { display: none; }
  @media (max-width: 820px) { .hero img.logo-stamp { width: 104px; height: 104px; left: -6px; bottom: -28px; } }
  .mosaic { grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-rows: 230px; grid-auto-flow: dense; gap: 14px; }
  .mosaic .tile { grid-column: span 1; grid-row: span 1; }
  .mosaic .tile.v { grid-row: span 2; }
  .mosaic .tile.b { grid-column: span 2; grid-row: span 2; }
  .mosaic .tile.w { grid-column: span 2; }
  @media (max-width: 820px) { .mosaic { grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-rows: 188px; gap: 10px; } }
  .about.one { grid-template-columns: minmax(0, 1fr); max-width: 760px; }
  .info.single { grid-template-columns: minmax(0, 1fr); max-width: 560px; }
  .hero:not(:has(figure)) { grid-template-columns: minmax(0, 1fr); max-width: 760px; }
  @media (max-width: 820px) { .seal { width: 96px; height: 96px; left: -6px; bottom: -26px; } .seal b { font-size: 28px; } .seal span { font-size: 9px; } }
'''
    css = css + seal_css + "  " + th["extra"] + "\n  " + lay_css

    hours_json = json.dumps({str(k): v for k, v in (hours or {}).items()})
    js1 = f'''<script>
(function () {{
  var HOURS = {hours_json};
  var parts = new Intl.DateTimeFormat("en-US", {{ timeZone: "America/Sao_Paulo", weekday: "short", hour: "numeric", minute: "numeric", hour12: false }}).formatToParts(new Date());
  var get = function (t) {{ return parts.filter(function (p) {{ return p.type === t; }})[0].value; }};
  var dow = {{ Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }}[get("weekday")];
  var mins = (parseInt(get("hour"), 10) % 24) * 60 + parseInt(get("minute"), 10);
  var li = document.querySelector('#hours li[data-d="' + dow + '"]');
  if (li) li.classList.add("today");
  var s = document.getElementById("status");
  if (s && Object.keys(HOURS).length) {{
    var open = (HOURS[dow] || []).some(function (r) {{ return r[1] > r[0] ? mins >= r[0] && mins < r[1] : mins >= r[0]; }}) ||
      (HOURS[(dow + 6) % 7] || []).some(function (r) {{ return r[1] <= r[0] && mins < r[1]; }});
    s.hidden = false; s.textContent = open ? "Aberto agora" : "Fechado agora"; s.classList.toggle("open", open);
  }}
  var btn = document.getElementById("copy"), out = document.getElementById("copied");
  if (btn) btn.addEventListener("click", function () {{
    var ok = function () {{ out.textContent = "copiado"; setTimeout(function () {{ out.textContent = ""; }}, 2000); }};
    if (navigator.clipboard) navigator.clipboard.writeText({json.dumps(phone_txt)}).then(ok, function () {{}});
  }});
}})();
</script>'''

    lb = DON[DON.index('<div class="progress"'):DON.index('<header class="bar">')]
    fonts = f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?{th["fonts"]}&display=swap" rel="stylesheet">'
    foot_addr = f"{street} · {bairro} · {cidade}" if bairro else f"{street} · {cidade}"
    page = f'''<title>{esc(nome)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{esc(lede[:150])}">
{fonts}
<style>
  /* {kind}: identidade própria por nicho; layout-base do modelo Don Alberttoni */
{css_theme}
{css}</style>

{lb}<header class="bar">
  <div class="bar-in">
    <a class="brand" href="#topo">{'<img src="img/logo.jpg" alt="" width="40" height="40">' if has_logo else ""}{esc(nome if len(nome) <= 24 else nome[:22].rsplit(" ", 1)[0])}</a>
    <nav aria-label="Seções">{"".join(nav)}</nav>
    <a class="btn" href="{esc(nav_cta[1])}" target="_blank" rel="noopener">{esc("Agendar" if nav_cta[0] == "Agendar online" else nav_cta[0].replace("Chamar no WhatsApp", "WhatsApp"))}</a>
  </div>
</header>

<main id="topo" class="wrap">
  <div class="hero">
    <div>
      {badge}
      <p class="eyebrow">{esc(cat)}{" · " + esc(bairro) + ", " + esc(cidade) if bairro else " · " + esc(cidade)}</p>
      <h1>{esc(nome)}</h1>
      <p class="lede">{esc(lede)}</p>
      <div class="cta">{cta_html}</div>
      <div class="score" aria-label="Nota {notas} de 5 no Google, {nrev} avaliações">
        <strong>{notas}</strong>
        <div><span class="stars" aria-hidden="true">★★★★★</span><br>{nrev} avaliações no Google</div>
      </div>
    </div>
    {hero_html}
  </div>
</main>
<div class="stripe" aria-hidden="true"></div>

<main class="wrap">
  {sec_about}
  {sec_gal}
</main>

{sec_proof}

<main class="wrap">
  {sec_info}
  {sec_final}
</main>

<footer>
  <div class="wrap">
    <span style="display:flex;align-items:center;gap:12px">{'<img src="img/logo.jpg" alt="" width="52" height="52" style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:2px solid var(--salmon)">' if has_logo else ""}<strong style="font-family:var(--font-display);font-weight:400">{esc(nome)}</strong></span>
    <p>{esc(foot_addr)}</p>
    <p style="flex-basis:100%;font-size:12px;opacity:.55">Fotos e avaliações públicas do Google Maps e do Instagram. Protótipo sujeito à autorização do estabelecimento. <a href="{LEOSUMIU}?site={slug}" target="_blank" rel="noopener">Plano B do seu site</a></p>
  </div>
</footer>

{js1}
{JS_GALLERY}'''
    open(os.path.join(base, "index.html"), "w", encoding="utf-8").write(page)
    return dict(slug=slug, title=nome, kind=kind, hero=bool(hero), gallery=len(gal), quotes=len(quotes), cards=len(cards), hours=bool(hours), files=sorted(os.listdir(img_dir)), cta=cta[0][0])

def tags_html(place):
    items = []
    for grp, lst in (place.get("additionalInfo") or {}).items():
        if grp in ("Acessibilidade",): continue
        for d in lst:
            for k, v in d.items():
                if v and k not in items and len(k) < 42 and "gratuito" not in k.lower(): items.append(k)
    items = items[:6]
    return '<ul class="tags">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>" if items else ""

if __name__ == "__main__":
    byslug = {}
    for name in ["b1", "b2", "test", "more_a", "more_b", "more_c", "more_d"]:
        f = os.path.join(HERE, "_data", name + ".json")
        if os.path.exists(f):
            for p in json.load(open(f, encoding="utf-8")): byslug[slugify(clean_name(p["title"]))] = p
    places = list(byslug.values())
    want = set(sys.argv[1:])
    manifest = []
    for i, p in enumerate(places):
        slug = slugify(clean_name(p["title"]))
        if want and slug not in want: continue
        if not os.path.isdir(os.path.join(HERE, slug)): continue
        m = build(p, i)
        manifest.append(m)
        print(f'{m["slug"]:46s} {m["kind"]:7s} hero={int(m["hero"])} gal={m["gallery"]} q={m["quotes"]} cards={m["cards"]} hrs={int(m["hours"])} cta={m["cta"]}')
    json.dump(manifest, open(os.path.join(HERE, "manifest.json" if not want else "manifest.partial.json"), "w"), ensure_ascii=False, indent=1)
    import vary; vary.run(want or None)  # variação de layout por ramo (idempotente)
