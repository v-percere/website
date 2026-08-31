"""Export the rendered cover into upload-safe files.

LinkedIn Pages reject anything over 3 MB, so the JPEG quality is stepped down
until it fits with margin. Alpha and colour profiles are stripped because the
uploader is unreliable with both.
"""

import os
import sys

from PIL import Image

SRC = sys.argv[1]
STEM = sys.argv[2]
LIMIT = 3 * 1024 * 1024
BUDGET = int(LIMIT * 0.8)

img = Image.open(SRC).convert("RGB")
print(f"source {img.size[0]}x{img.size[1]}")

png = f"{STEM}.png"
img.save(png, "PNG", optimize=True)
png_bytes = os.path.getsize(png)
print(f"{png}  {png_bytes/1024/1024:.2f} MB  {'ok' if png_bytes < LIMIT else 'OVER 3MB LIMIT'}")
if png_bytes >= LIMIT:
    os.remove(png)
    print(f"  removed {png}: too large to upload")

jpg = f"{STEM}.jpg"
for quality in (95, 92, 90, 87, 84, 80, 75):
    img.save(jpg, "JPEG", quality=quality, optimize=True, progressive=False, subsampling=0)
    size = os.path.getsize(jpg)
    if size <= BUDGET:
        break
print(f"{jpg}  {size/1024/1024:.2f} MB  quality={quality}")
