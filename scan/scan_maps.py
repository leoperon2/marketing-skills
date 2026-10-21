#!/usr/bin/env python3
"""Varredura do Google Maps via Apify e ranking de candidatos a site.

Uso:
  export APIFY_TOKEN=...
  python3 scan_maps.py run   --niches "barbearia,oficina de motos" --cities "Curitiba/Paraná,Londrina/Paraná" --per-search 60
  python3 scan_maps.py rank  --dataset <datasetId> --top 50

`run` imprime o datasetId; `rank` baixa, filtra, pontua e grava candidatos.csv e top50.csv.
Sem dependências externas.
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request

ACTOR = "compass~crawler-google-places"
API = "https://api.apify.com/v2"
SOCIAL = re.compile(r"(instagram|facebook|fb\.com|linktr|wa\.me|whatsapp|beacons|bio\.link|linkin\.bio|tiktok)", re.I)
TOKEN = os.environ.get("APIFY_TOKEN", "")


def call(method, path, body=None, **q):
    q["token"] = TOKEN
    url = f"{API}{path}?{urllib.parse.urlencode(q)}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def run(a):
    niches = [n.strip() for n in a.niches.split(",") if n.strip()]
    cities = [c.strip() for c in a.cities.split(",") if c.strip()]
    ids = []
    for city in cities:
        inp = {
            "searchStringsArray": niches,
            "city": city.split("/")[0],       # formato "Curitiba/Paraná"; evita polígono de 0 km²
            "state": city.split("/")[1] if "/" in city else "",
            "countryCode": "br",
            "maxCrawledPlacesPerSearch": a.per_search,
            "language": "pt-BR",
            "scrapeContacts": True,       # e-mail e redes sociais do site (add-on pago, confira o preço)
            "maxImages": 0,
            "maxReviews": 0,              # avaliações detalhadas só para os finalistas
            "skipClosedPlaces": True,
        }
        r = call("POST", f"/acts/{ACTOR}/runs", inp)["data"]
        ids.append(r["id"])
        print("started", city, r["id"])
    for rid in ids:
        while True:
            d = call("GET", f"/actor-runs/{rid}")["data"]
            if d["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                print(rid, d["status"], "dataset:", d["defaultDatasetId"], "cost_usd:", d.get("usageTotalUsd"))
                break
            time.sleep(15)


def fetch(dataset):
    out, off = [], 0
    while True:
        chunk = call("GET", f"/datasets/{dataset}/items", clean="true", limit=1000, offset=off, format="json")
        if not chunk:
            return out
        out += chunk
        off += len(chunk)


def mobile(phone):
    d = re.sub(r"\D", "", phone or "")
    d = d[2:] if d.startswith("55") else d
    return len(d) == 11 and d[2] == "9"      # celular BR: DDD + 9 + 8 dígitos (provável WhatsApp)


def first(v):
    return (v[0] if isinstance(v, list) and v else v) or ""


def score(p):
    rev, rating = p.get("reviewsCount") or 0, p.get("totalScore") or 0
    photos = p.get("imagesCount") or 0
    site = (p.get("website") or "").strip()
    has_real_site = bool(site) and not SOCIAL.search(site)
    insta = first(p.get("instagrams"))
    email = first(p.get("emails"))
    wa = mobile(p.get("phone") or p.get("phoneUnformatted"))
    material = min(rev, 150) / 150 * 25 + max(rating - 4.0, 0) / 1.0 * 15 + min(photos, 40) / 40 * 10
    need = 0 if has_real_site else 20
    access = (15 if wa else 0) + (10 if insta else 0) + (5 if email else 0)
    return round(material + need + access, 1), dict(whatsapp=wa, instagram=insta, email=email, has_real_site=has_real_site)


def rank(a):
    seen, rows = set(), []
    items = [p for d in a.dataset.split(",") for p in fetch(d.strip())]
    for p in items:
        pid = p.get("placeId") or p.get("url")
        if pid in seen or p.get("permanentlyClosed") or p.get("temporarilyClosed"):
            continue
        seen.add(pid)
        if (p.get("reviewsCount") or 0) < a.min_reviews or (p.get("totalScore") or 0) < a.min_rating:
            continue
        s, x = score(p)
        if x["has_real_site"] or not (x["whatsapp"] or x["instagram"] or x["email"]):
            continue                              # já tem site, ou não há como falar com o dono
        rows.append(dict(score=s, nome=p.get("title"), categoria=p.get("categoryName"), cidade=p.get("city"),
                         nota=p.get("totalScore"), avaliacoes=p.get("reviewsCount"), fotos=p.get("imagesCount"),
                         telefone=p.get("phone"), whatsapp_provavel=x["whatsapp"], instagram=x["instagram"],
                         email=x["email"], site_atual=p.get("website") or "", maps=p.get("url")))
    rows.sort(key=lambda r: -r["score"])
    for name, subset in (("candidatos.csv", rows), ("top50.csv", rows[:a.top])):
        with open(name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["score"])
            w.writeheader(); w.writerows(subset)
    from collections import Counter
    print("por categoria:", Counter(r["categoria"] for r in rows).most_common(8))
    print(f"{len(seen)} únicos | {len(rows)} candidatos qualificados | top {a.top} em top50.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--niches", required=True); r.add_argument("--cities", required=True)
    r.add_argument("--per-search", type=int, default=60)
    k = sub.add_parser("rank"); k.add_argument("--dataset", required=True); k.add_argument("--top", type=int, default=50)
    k.add_argument("--min-reviews", type=int, default=40); k.add_argument("--min-rating", type=float, default=4.3)
    a = ap.parse_args()
    if not TOKEN:
        sys.exit("defina APIFY_TOKEN")
    run(a) if a.cmd == "run" else rank(a)
