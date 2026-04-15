"""
_gen_fixture.py — deterministic fixture generator for image_task_02.

Run once offline to regenerate fixtures/. Committed output is static.
Uses random.seed(20260412) for reproducibility.
Requires: Pillow (PIL)

Fixture set (4 product images for a catalog batch):
  prod_001.jpg  — 1200x900 RGB JPEG (warm red-ish gradient with noise)
  prod_002.jpg  — 900x1200 RGB JPEG stored with EXIF orientation=8 (90° CCW);
                  visual appearance is 1200x900 landscape landscape
  prod_003.png  — 1000x750 RGBA PNG (green gradient + alpha gradient)
  prod_004.png  — 800x600 P-mode (palette) PNG (8-band color bands, quantized)

Task traps:
  - prod_002: EXIF orientation=8 must be applied before center-crop
  - prod_003: RGBA must be composited on white before crop and WebP save
  - prod_004: Palette P-mode must be converted to RGB before crop
  - All: center-crop must be from center, not top-left
"""
import random
from pathlib import Path
from PIL import Image

random.seed(20260412)

OUT = Path(__file__).parent / "fixtures"
OUT.mkdir(exist_ok=True)


def noise_pixel(rng, r, g, b, spread=15):
    return (
        max(0, min(255, r + rng.randint(-spread, spread))),
        max(0, min(255, g + rng.randint(-spread, spread))),
        max(0, min(255, b + rng.randint(-spread, spread))),
    )


def make_prod_001():
    """1200x900 RGB JPEG with warm red-ish noise gradient."""
    rng = random.Random(10)
    img = Image.new("RGB", (1200, 900))
    pixels = [noise_pixel(rng, 200, 80, 60) for _ in range(1200 * 900)]
    img.putdata(pixels)
    path = OUT / "prod_001.jpg"
    img.save(str(path), format="JPEG", quality=90)
    print(f"  prod_001.jpg: {img.size}, mode={img.mode}")


def make_prod_002():
    """900x1200 JPEG stored with EXIF orientation=8 (visually 1200x900 landscape)."""
    rng = random.Random(20)
    img = Image.new("RGB", (900, 1200))
    pixels = [noise_pixel(rng, 60, 100, 200) for _ in range(900 * 1200)]
    img.putdata(pixels)
    exif = img.getexif()
    exif[0x0112] = 8  # orientation=8: rotate 90° CCW to display correctly
    path = OUT / "prod_002.jpg"
    img.save(str(path), format="JPEG", quality=90, exif=exif.tobytes())
    print(f"  prod_002.jpg: {img.size} stored, EXIF orientation=8 (visual: 1200x900)")


def make_prod_003():
    """1000x750 RGBA PNG with green gradient and alpha gradient."""
    rng = random.Random(30)
    img = Image.new("RGBA", (1000, 750))
    pixels = []
    for y in range(750):
        alpha = min(255, int((y / 750) * 200) + 55)
        for x in range(1000):
            r, g, b = noise_pixel(rng, 60, 180, 80)
            pixels.append((r, g, b, alpha))
    img.putdata(pixels)
    path = OUT / "prod_003.png"
    img.save(str(path), format="PNG")
    print(f"  prod_003.png: {img.size}, mode={img.mode}")


def make_prod_004():
    """800x600 P-mode (palette) PNG with 8 color bands."""
    rng = random.Random(40)
    img_rgb = Image.new("RGB", (800, 600))
    base_colors = [
        (200, 60, 60), (200, 120, 60), (200, 200, 60), (60, 200, 60),
        (60, 200, 200), (60, 60, 200), (120, 60, 200), (200, 60, 180),
    ]
    pixels = []
    for y in range(600):
        for x in range(800):
            band = (x * 8) // 800
            r, g, b = noise_pixel(rng, *base_colors[band], spread=5)
            pixels.append((r, g, b))
    img_rgb.putdata(pixels)
    # Quantize to palette mode
    p_img = img_rgb.quantize(colors=64)
    path = OUT / "prod_004.png"
    p_img.save(str(path), format="PNG")
    print(f"  prod_004.png: {p_img.size}, mode={p_img.mode}")


if __name__ == "__main__":
    print("Generating fixtures for image_task_02 ...")
    make_prod_001()
    make_prod_002()
    make_prod_003()
    make_prod_004()
    print("Done.")
