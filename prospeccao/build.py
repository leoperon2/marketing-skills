#!/usr/bin/env python3
"""Monta prospeccao.html (arquivo único) a partir de prospeccao.csv + template.html.
Miniaturas: sites/<slug>/img/hero.jpg → 216x144 WebP q38 embutido em base64. Nada passa pelo contexto do Claude."""
import base64, csv, io, json, os, re, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); SITES = os.path.join(HERE, "..", "sites")
import unicodedata

def clean_name(t):  # igual a sites/fetch_photos.py (copiado para não depender do cv2)
    t = re.sub(r"\([^)]*\)", "", t); t = t.split(" | ")[0]
    t = re.sub(r"\s*-\s*(Curitiba|Goiânia|Porto Alegre|Belo Horizonte)\s*$", "", t)
    return re.sub(r"\s+", " ", t).strip(" -")

def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:48]

EXCLUIR = {"Pilgrim Burgers", "Marshals Tattoo", "Pet Shop Agropal", "Suzana Dias Studio", "Win Hamburgueria"}  # já têm site
NICHO = {"burger": "Hamburgueria", "barber": "Barbearia", "tattoo": "Estúdio de tatuagem", "salon": "Salão de beleza", "pet": "Pet shop", "auto": "Oficina e mecânica", "clinic": "Clínica de estética"}
CURTO = {"AURE ART STUDIO tattoo & piercing em goiania": "Aure Art Studio"}

def curto(n):
    if n in CURTO: return CURTO[n]
    n = n.split(" - ")[0].strip()
    return n.title() if n.isupper() else n

def thumb(slug):
    p = next((q for q in (os.path.join(SITES, slug, "img", n) for n in ("hero.jpg", "letreiro.jpg")) if os.path.exists(q)), None)
    if not p: return None
    im = Image.open(p).convert("RGB"); im.thumbnail((432, 288))
    w, h = im.size; tw, th = 216, 144
    s = max(tw / w, th / h); im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    l, t = (im.width - tw) // 2, (im.height - th) // 2; im = im.crop((l, t, l + tw, t + th))
    b = io.BytesIO(); im.save(b, "WEBP", quality=38, method=6)
    Image.open(io.BytesIO(b.getvalue())).verify()
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()

def bairro(slug):
    f = os.path.join(SITES, slug, "index.html")
    if not os.path.exists(f): return ""
    m = re.search(r'<p class="eyebrow">[^<]*?·\s*([^<]*)</p>', open(f, encoding="utf-8").read())
    if not m: return ""
    parts = [x.strip() for x in m.group(1).split(",")]
    return parts[0] if len(parts) > 1 else ""

rows = [r for r in csv.DictReader(open(os.path.join(HERE, "prospeccao.csv"), encoding="utf-8")) if r["negocio"] not in EXCLUIR]
leads = []
for i, r in enumerate(rows):
    slug = slugify(clean_name(r["negocio"])); nome = curto(r["negocio"])
    wa = (r["whatsapp"] or "").strip()
    if wa and not re.fullmatch(r"https://wa\.me/55\d{10,11}", wa): print("WA fora do padrão:", nome, wa); wa = ""
    leads.append(dict(key=slugify(nome + " " + r["cidade"]), ord=i, nome=nome, nomeCompleto=r["negocio"], nicho=r["nicho"], cat=NICHO.get(r["nicho"], r["nicho"]),
        cidade=r["cidade"], bairro=bairro(slug), nota=float(r["nota"]), aval=int(r["avaliacoes"]), maps=r["maps"], wa=wa, tel=r["telefone"],
        demo=r["link_prototipo"], insta=r["instagram"] if "/invites" not in r["instagram"] else "", pronto=(r["site_versao_final"] == "sim"), img=thumb(slug)))
chaves = [l["key"] for l in leads]; assert len(set(chaves)) == len(chaves), "chave duplicada"
js = json.dumps(leads, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("__LEADS__", js)
open(os.path.join(HERE, "prospeccao.html"), "w", encoding="utf-8").write(out)
print(len(leads), "leads;", sum(l["pronto"] for l in leads), "prontos;", "sem miniatura:", [l["nome"] for l in leads if not l["img"]], "| sem WhatsApp:", [l["nome"] for l in leads if not l["wa"]], "| bytes:", len(out.encode()))
