"""
_gen_fixture.py — generates deterministic fixtures for image_task_01.

Run once offline to regenerate fixtures/. Committed output is static.
Uses random.seed(20260412) for reproducibility.
Requires: Pillow (PIL)

Fixture set:
  photo_a.jpg  — 2400x1600 JPEG with embedded EXIF orientation=6 (90° CW rotated)
                 stored as 1600x2400 pixels; EXIF orientation=6 means "rotate 90° CW to display"
                 so visual size is 2400x1600. Naive resize (ignoring EXIF) produces wrong dims.
  banner_b.png — 800x400 RGBA PNG with semi-transparent blue gradient
  icon_c.png   — 256x256 RGBA PNG with red circle on transparent background

Task: resize all to 800x600 (after applying EXIF), composite alpha on white, save as JPEG.
"""

import random
from pathlib import Path
from PIL import Image

random.seed(20260412)

OUT = Path(__file__).parent / "fixtures"
OUT.mkdir(exist_ok=True)


def make_photo_a():
    """1600x2400 JPEG stored with EXIF orientation=6 (visually 2400x1600 landscape)."""
    rng = random.Random(1)
    img = Image.new("RGB", (1600, 2400))
    pixels = []
    for y in range(2400):
        r = int((y / 2400) * 200) + rng.randint(0, 10)
        g = int((1 - y / 2400) * 180) + rng.randint(0, 10)
        b = 120 + rng.randint(0, 30)
        for x in range(1600):
            pixels.append((min(r, 255), min(g, 255), min(b, 255)))
    img.putdata(pixels)
    exif = img.getexif()
    exif[0x0112] = 6  # Orientation=6: rotate 90° CW
    path = OUT / "photo_a.jpg"
    img.save(str(path), format="JPEG", quality=90, exif=exif.tobytes())
    print(f"  photo_a.jpg: {img.size} stored, EXIF orientation=6 (visual: 2400x1600)")


def make_banner_b():
    """800x400 RGBA PNG with semi-transparent blue gradient."""
    rng = random.Random(2)
    img = Image.new("RGBA", (800, 400), (0, 0, 0, 0))
    pixels = []
    for y in range(400):
        for x in range(800):
            alpha = min(255, int((x / 800) * 200) + rng.randint(0, 30))
            r = 20 + rng.randint(0, 10)
            g = 60 + rng.randint(0, 20)
            b = 180 + rng.randint(0, 40)
            pixels.append((min(r, 255), min(g, 255), min(b, 255), alpha))
    img.putdata(pixels)
    path = OUT / "banner_b.png"
    img.save(str(path), format="PNG")
    print(f"  banner_b.png: {img.size}, mode={img.mode} (has alpha)")


def make_icon_c():
    """256x256 RGBA PNG — red circle on transparent background."""
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    cx, cy, r = 128, 128, 100
    pixels = list(img.getdata())
    for y in range(256):
        for x in range(256):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                pixels[y * 256 + x] = (220, 50, 50, 255)
    img.putdata(pixels)
    path = OUT / "icon_c.png"
    img.save(str(path), format="PNG")
    print(f"  icon_c.png: {img.size}, mode={img.mode} (has alpha)")


if __name__ == "__main__":
    print("Generating fixtures for image_task_01 ...")
    make_photo_a()
    make_banner_b()
    make_icon_c()
    print("Done.")
