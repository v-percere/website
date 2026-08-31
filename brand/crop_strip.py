"""Find the lit band inside the letterboxed generation and crop it to the
LinkedIn banner aspect ratio."""

import sys

from PIL import Image

SRC = sys.argv[1]
DST = sys.argv[2]
# 0.0 keeps the top of the band (the HUD panel row), 1.0 keeps the bottom.
BIAS = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
# LinkedIn Page covers are uploaded at 4200x700 (6:1); 1128x191 is only the
# size the page renders them at, and uploading that small is rejected.
TARGET_W, TARGET_H = 4200, 700
TARGET_AR = TARGET_W / TARGET_H

img = Image.open(SRC).convert("RGB")
w, h = img.size
gray = img.convert("L")
px = gray.load()

# Row brightness, sampled across the width.
step = max(1, w // 256)
rows = []
for y in range(h):
    total = 0
    n = 0
    for x in range(0, w, step):
        total += px[x, y]
        n += 1
    rows.append(total / n)

peak = max(rows)
threshold = peak * 0.18
lit = [y for y, v in enumerate(rows) if v > threshold]
top, bottom = lit[0], lit[-1]

# The thin glowing HUD borders sit below the detection threshold, so give the
# top a little headroom rather than trusting the measured edge exactly.
top = max(0, top - 8)
bottom -= 2
band_h = bottom - top
band_w = w

print(f"source {w}x{h}  band y={top}..{bottom} ({band_w}x{band_h}, ar={band_w/band_h:.2f})")

if band_w / band_h > TARGET_AR:
    # Band is wider than the target: keep full height, trim the sides evenly.
    crop_h = band_h
    crop_w = round(band_h * TARGET_AR)
    x0 = (band_w - crop_w) // 2
    box = (x0, top, x0 + crop_w, top + crop_h)
else:
    # Band is taller than the target: keep full width, trim top and bottom.
    crop_w = band_w
    crop_h = round(band_w / TARGET_AR)
    extra = band_h - crop_h
    y0 = top + int(extra * BIAS)
    box = (0, y0, crop_w, y0 + crop_h)

print(f"crop box {box}")
out = img.crop(box).resize((TARGET_W, TARGET_H), Image.LANCZOS)
out.save(DST)
print(f"wrote {DST} {out.size[0]}x{out.size[1]}")
