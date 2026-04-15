"""
Reference solution for image_task_02.

Steps per image:
1. Apply EXIF orientation (ImageOps.exif_transpose) — handles prod_002.jpg stored as
   900x1200 with EXIF orientation=8 (rotate 90° CCW to display as 1200x900).
2. Convert to RGB — composites RGBA on white, converts palette P-mode to RGB.
3. Center-crop to 600x400 — crop box centered on image midpoint.
4. Add watermark "© Catalog 2026" in lower-right corner (white text, dark shadow, 10px margin).
5. Save as WebP quality=80 to output/<stem>.webp.

Source → Output:
  prod_001.jpg (1200x900 RGB)         → output/prod_001.webp
  prod_002.jpg (900x1200, EXIF=8)     → output/prod_002.webp  (visual 1200x900)
  prod_003.png (1000x750 RGBA)        → output/prod_003.webp
  prod_004.png (800x600, palette P)   → output/prod_004.webp
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

WORKSPACE = Path(".")
OUTPUT_DIR = WORKSPACE / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_W, TARGET_H = 600, 400
WEBP_QUALITY = 80
WATERMARK_TEXT = "© Catalog 2026"
WATERMARK_MARGIN = 10

SOURCES = [
    ("prod_001.jpg", "prod_001.webp"),
    ("prod_002.jpg", "prod_002.webp"),
    ("prod_003.png", "prod_003.webp"),
    ("prod_004.png", "prod_004.webp"),
]

for src_name, dst_name in SOURCES:
    img = Image.open(WORKSPACE / src_name)

    # Step 1: Apply EXIF orientation
    img = ImageOps.exif_transpose(img)

    # Step 2: Convert to RGB (handle palette, RGBA, LA, etc.)
    if img.mode == "P":
        img = img.convert("RGBA")
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "LA":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Step 3: Center-crop to 600x400
    w, h = img.size
    left = (w - TARGET_W) // 2
    top = (h - TARGET_H) // 2
    right = left + TARGET_W
    bottom = top + TARGET_H
    img = img.crop((left, top, right, bottom))

    # Step 4: Add watermark in lower-right corner
    draw = ImageDraw.Draw(img)
    # Try to load a system font, fall back to default
    font = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
    ]:
        try:
            font = ImageFont.truetype(font_path, 20)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = TARGET_W - text_w - WATERMARK_MARGIN
    y = TARGET_H - text_h - WATERMARK_MARGIN

    # Dark shadow for contrast, white text on top
    draw.text((x + 1, y + 1), WATERMARK_TEXT, fill=(0, 0, 0), font=font)
    draw.text((x, y), WATERMARK_TEXT, fill=(255, 255, 255), font=font)

    # Step 5: Save as WebP quality=80
    out_path = OUTPUT_DIR / dst_name
    img.save(str(out_path), format="WEBP", quality=WEBP_QUALITY)
    print(f"  {src_name} -> output/{dst_name}: {img.size}")

print("Done.")
