#!/usr/bin/env python3
"""Copia cada site de demonstração para o repositório público de demos (um diretório por cliente, nome não adivinhável).
Uso: python3 publish.py [/caminho/do/clone/demos]   (padrão: /home/user/demos)
Gera urls.json (chave do lead -> URL pública), lido pelo build.py. O sal fica em .salt (fora do git): mesma URL a cada republicação."""
import csv, hashlib, json, os, re, secrets, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SITES = os.path.join(HERE, "..", "sites")
DEST = sys.argv[1] if len(sys.argv) > 1 else "/home/user/demos"
BASE = "https://leoperon2.github.io/demos/"
import build  # reaproveita a lista de leads (e slugify) sem gerar o HTML
salt_f = os.path.join(HERE, ".salt")
if not os.path.exists(salt_f): open(salt_f, "w").write(secrets.token_hex(16))
salt = open(salt_f).read().strip()
urls = {}
for d in os.listdir(DEST):
    if re.search(r"-[a-z0-9]{6}$", d) and os.path.isdir(os.path.join(DEST, d)): shutil.rmtree(os.path.join(DEST, d))
for l in build.leads:
    slug = build.slugify(build.clean_name(l["nomeCompleto"]))
    slug = {"don-alberttoni-barbearia": "don-alberttoni"}.get(slug, slug)  # pasta do modelo feito à mão
    src = os.path.join(SITES, slug)
    if not os.path.exists(os.path.join(src, "index.html")): print("sem site:", l["nome"]); continue
    tok = hashlib.sha256((salt + slug).encode()).hexdigest()[:6]
    pasta = f"{slug[:30].strip('-')}-{tok}"
    out = os.path.join(DEST, pasta)
    os.makedirs(out, exist_ok=True)
    if os.path.isdir(os.path.join(src, "img")): shutil.copytree(os.path.join(src, "img"), os.path.join(out, "img"))
    h = open(os.path.join(src, "index.html"), encoding="utf-8").read()
    h = re.sub(r"(<title>[^\n]*</title>\n)", r'\1<meta name="robots" content="noindex, nofollow">\n', h, count=1)
    # fora do Artifact ninguém injeta o esqueleto: sem esta tag o celular renderiza a 980 px e encolhe tudo
    h = '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + h
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(h)
    urls[l["key"]] = BASE + pasta + "/"
open(os.path.join(DEST, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
open(os.path.join(DEST, ".nojekyll"), "w").write("")
open(os.path.join(DEST, "index.html"), "w").write('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>.</title>')
json.dump(urls, open(os.path.join(HERE, "urls.json"), "w"), indent=1, ensure_ascii=False)
print(len(urls), "sites copiados para", DEST)
