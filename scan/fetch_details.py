#!/usr/bin/env python3
"""Baixa detalhes completos (avaliações em texto e fotos de avaliações) de negócios do top50.csv.
Uso: APIFY_TOKEN=... python3 fetch_details.py <inicio> <fim> <max_reviews> <saida.json>"""
import csv, json, os, sys, time, urllib.parse, urllib.request
t = os.environ["APIFY_TOKEN"]
a, b, mr, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rows = list(csv.DictReader(open("top50.csv", encoding="utf-8")))[a:b]

def call(m, p, body=None, **q):
    q["token"] = t
    r = urllib.request.Request(f"https://api.apify.com/v2{p}?{urllib.parse.urlencode(q)}",
        data=json.dumps(body).encode() if body is not None else None, method=m, headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=120))

inp = {"startUrls": [{"url": r["maps"]} for r in rows], "language": "pt-BR", "maxReviews": mr, "reviewsSort": "mostRelevant",
       "scrapeContacts": True, "maxImages": 0, "maxCrawledPlacesPerSearch": 1}
rid = call("POST", "/acts/compass~crawler-google-places/runs", inp)["data"]["id"]
while True:
    d = call("GET", f"/actor-runs/{rid}")["data"]
    if d["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"): break
    time.sleep(10)
time.sleep(5)
d = call("GET", f"/actor-runs/{rid}")["data"]
items = call("GET", f"/datasets/{d['defaultDatasetId']}/items", clean="true", format="json")
json.dump(items, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(d["status"], "lugares:", len(items), "custo US$", d.get("usageTotalUsd"),
      "fotos em avaliações:", sum(len(r.get("reviewImageUrls") or []) for p in items for r in p.get("reviews", [])))
