import numpy as np
from rapidocr_onnxruntime import RapidOCR
_o = RapidOCR()
def text_stats(path):
    r, _ = _o(path)
    from PIL import Image
    w, h = Image.open(path).size
    area, n = 0.0, 0
    for box, txt, conf in (r or []):
        if float(conf) < 0.6 or len(txt.strip()) < 3: continue
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        area += (max(xs) - min(xs)) * (max(ys) - min(ys)); n += 1
    return area / (w * h), n
