"""
Reference solution for image_task_01.

Steps per image:
1. Apply EXIF orientation (ImageOps.exif_transpose) so pixel layout matches visual orientation.
2. Composite any alpha channel on white (#FFFFFF) before JPEG conversion.
3. Resize to exactly 800x600 using LANCZOS resampling (no aspect-ratio preservation).
4. Save as JPEG quality=85 to output/<stem>.jpg.

Source → Output mapping:
  photo_a.jpg  (stored 1600x2400, EXIF orientation=6 → visual 2400x1600) → output/photo_a.jpg
  banner_b.png (800x400, RGBA)  → output/banner_b.jpg
  icon_c.png   (256x256, RGBA)  → output/icon_c.jpg
"""
import os
from pathlib import Path
from PIL import Image, ImageOps

WORKSPACE = Path(".")
OUTPUT_DIR = WORKSPACE / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_SIZE = (800, 600)
JPEG_QUALITY = 85

SOURCES = [
    ("photo_a.jpg",  "photo_a.jpg"),
    ("banner_b.png", "banner_b.jpg"),
    ("icon_c.png",   "icon_c.jpg"),
]

for src_name, dst_name in SOURCES:
    src_path = WORKSPACE / src_name
    img = Image.open(src_path)

    # Step 1: Apply EXIF orientation so visual orientation matches stored pixels
    img = ImageOps.exif_transpose(img)

    # Step 2: Resize to exactly 800x600 using LANCZOS
    img = img.resize(TARGET_SIZE, Image.LANCZOS)

    # Step 3: Composite on white if the image has an alpha channel
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode == "LA":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Step 4: Save as JPEG
    out_path = OUTPUT_DIR / dst_name
    img.save(str(out_path), format="JPEG", quality=JPEG_QUALITY)
    print(f"  {src_name} -> output/{dst_name}: {img.size}")

print("Done.")
