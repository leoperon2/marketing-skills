#!/usr/bin/env python3
"""Marca cada foto de <slug>/photos.json com a área de texto detectada por OCR (tf) e nº de blocos (tn)."""
import json, os, glob, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
def work(slug):
    from text_score import text_stats
    pj = os.path.join(HERE, slug, "photos.json")
    meta = json.load(open(pj))
    for m in meta:
        if "tf" in m: continue
        try: m["tf"], m["tn"] = text_stats(os.path.join(HERE, slug, "_src", os.path.basename(m["file"])))
        except Exception: m["tf"], m["tn"] = 0.0, 0
    json.dump(meta, open(pj, "w"), ensure_ascii=False, indent=1)
    return slug, len(meta), sum(1 for m in meta if m["tf"] > 0.04 or m["tn"] >= 4)
if __name__ == "__main__":
    slugs = [os.path.dirname(f).split("/")[-1] for f in sorted(glob.glob(os.path.join(HERE, "*/photos.json")))]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as p:
        for s, n, g in p.imap_unordered(work, slugs): print(f"{s:48s} fotos {n:3d} com texto {g:3d}", flush=True)
