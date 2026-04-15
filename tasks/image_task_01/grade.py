"""
grade.py for image_task_01.

Contract: returns a list of criterion records per grade-py-protocol.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Checks:
  1. output/ directory exists
  2. all three output files present: photo_a.jpg, banner_b.jpg, icon_c.jpg
  3. file count in output/ is exactly 3
  4. all outputs are valid JPEG format
  5. all outputs are exactly 800x600 pixels
  6. photo_a.jpg specifically 800x600 (catches failure to apply EXIF orientation=6)
  7. no alpha channel in any output (PNG alpha must be composited on white)

Archetypes hit:
  - Archetype 1 (under-specified step): prompt pins exact 800x600 + LANCZOS + quality=85
  - Archetype 2 (common-default-wrong): JPEG conversion silently drops alpha (SKILL.md trap)
  - Archetype 4 (known-edge-case): EXIF orientation must be applied before resize
  - Archetype 5 (stateful invariant): file count == 3, all exactly 800x600
"""
from __future__ import annotations
import os
from pathlib import Path

TARGET_W, TARGET_H = 800, 600
EXPECTED_FILES = {"photo_a.jpg", "banner_b.jpg", "icon_c.jpg"}


def _load_image(path: Path):
    """Open an image and return (img, error_str). Returns (None, err) on failure."""
    try:
        from PIL import Image
        img = Image.open(str(path))
        img.load()  # force decode
        return img, None
    except Exception as e:
        return None, str(e)


def grade(transcript, workspace_path: str):
    ws = Path(workspace_path)
    out_dir = ws / "output"

    # ── 1. output/ directory exists ──────────────────────────────────────────
    dir_exists = out_dir.is_dir()

    # ── 2. all three files present ───────────────────────────────────────────
    present = set()
    all_in_output = []
    if dir_exists:
        for f in out_dir.iterdir():
            all_in_output.append(f.name)
            if f.name in EXPECTED_FILES:
                present.add(f.name)
    files_present = (present == EXPECTED_FILES)
    file_count = len(all_in_output)

    # ── per-file checks ──────────────────────────────────────────────────────
    per_file: dict[str, dict] = {}
    for fname in sorted(EXPECTED_FILES):
        fpath = out_dir / fname
        if not fpath.exists():
            per_file[fname] = {"exists": False}
            continue
        img, err = _load_image(fpath)
        if img is None:
            per_file[fname] = {"exists": True, "is_jpeg": False, "correct_size": False,
                               "no_alpha": False, "err": err}
            continue
        per_file[fname] = {
            "exists": True,
            "is_jpeg": img.format == "JPEG",
            "correct_size": (img.width == TARGET_W and img.height == TARGET_H),
            "no_alpha": img.mode not in ("RGBA", "LA"),
            "size": (img.width, img.height),
            "mode": img.mode,
        }

    def _all(key):
        return all(d.get(key, False) for d in per_file.values())

    def _bad(key):
        return [fn for fn, d in per_file.items() if not d.get(key, False)]

    records = []

    # 1. output dir
    records.append({
        "id": "output-dir-exists",
        "score": 1.0 if dir_exists else 0.0,
        "weight": 0.05,
        "description": "A directory named 'output' exists at the workspace root containing the processed images.",
        **({"details": "output/ directory not found at workspace root."} if not dir_exists else {}),
    })

    # 2. all three files present
    missing = EXPECTED_FILES - present
    records.append({
        "id": "all-files-present",
        "score": 1.0 if files_present else 0.0,
        "weight": 0.10,
        "description": "All three output files are present in output/: photo_a.jpg, banner_b.jpg, icon_c.jpg — each named exactly as specified with the .jpg extension (PNG inputs get the .jpg extension, not .png).",
        **({"details": f"Missing files: {sorted(missing)}"} if missing else {}),
    })

    # 3. file count == 3
    count_ok = (file_count == 3)
    records.append({
        "id": "file-count-exactly-3",
        "score": 1.0 if count_ok else 0.0,
        "weight": 0.05,
        "description": "output/ contains exactly 3 files — one per input image — enforcing the invariant that file count equals input count with no extras dropped or added.",
        **({"details": f"Expected 3 files in output/, found {file_count}: {sorted(all_in_output)}"} if not count_ok else {}),
    })

    # 4. all outputs are valid JPEG
    all_jpeg = _all("is_jpeg")
    bad_jpeg = _bad("is_jpeg")
    records.append({
        "id": "all-outputs-are-jpeg",
        "score": 1.0 if all_jpeg else 0.0,
        "weight": 0.10,
        "description": "All three output files are valid JPEG files, not PNG or other format. The task requires converting all inputs (including PNG sources) to JPEG.",
        **({"details": f"Non-JPEG output(s): {bad_jpeg}"} if not all_jpeg else {}),
    })

    # 5. all outputs exactly 800x600
    all_sized = _all("correct_size")
    bad_sized = _bad("correct_size")
    size_details = None
    if not all_sized:
        parts = [f"{fn}: got {per_file[fn].get('size', 'n/a')} expected (800, 600)" for fn in bad_sized]
        size_details = "; ".join(parts)
    records.append({
        "id": "all-outputs-800x600",
        "score": 1.0 if all_sized else 0.0,
        "weight": 0.25,
        "description": "All three output images are exactly 800×600 pixels. This catches EXIF orientation errors on photo_a.jpg (stored as 1600×2400, EXIF orientation=6, visual 2400×1600) and incorrect resizing on banner/icon inputs.",
        **({"details": size_details} if size_details else {}),
    })

    # 6. photo_a specifically 800x600 (EXIF orientation trap, higher weight)
    photo_data = per_file.get("photo_a.jpg", {})
    photo_ok = photo_data.get("correct_size", False)
    records.append({
        "id": "photo-a-exif-orientation-applied",
        "score": 1.0 if photo_ok else 0.0,
        "weight": 0.20,
        "description": "photo_a.jpg output is 800×600 (not 400×600, 600×400, or 600×800), proving that EXIF orientation=6 was applied before resizing. The raw stored image is 1600×2400 (portrait); without orientation correction the visual appears rotated and the resize produces wrong dimensions.",
        **({"details": f"photo_a.jpg actual size: {photo_data.get('size', 'missing')} — expected (800, 600); EXIF orientation was likely not applied before resize."} if not photo_ok else {}),
    })

    # 7. no alpha channels in any output (white-composite trap)
    all_no_alpha = _all("no_alpha")
    bad_alpha = _bad("no_alpha")
    alpha_details = None
    if not all_no_alpha:
        parts = [f"{fn}: mode={per_file[fn].get('mode', 'n/a')}" for fn in bad_alpha]
        alpha_details = f"Outputs still have alpha channel — PNG inputs must be composited on white (#FFFFFF) before JPEG conversion: {'; '.join(parts)}"
    records.append({
        "id": "no-alpha-in-output",
        "score": 1.0 if all_no_alpha else 0.0,
        "weight": 0.25,
        "description": "No output file has an alpha channel (mode must be RGB, not RGBA/LA). JPEG cannot store transparency; banner_b.png and icon_c.png have alpha channels and must be composited on a white background before saving as JPEG — silently saving RGBA as JPEG either fails or discards alpha.",
        **({"details": alpha_details} if alpha_details else {}),
    })

    # Verify weight sum at author time
    total_w = sum(r["weight"] for r in records)
    assert abs(total_w - 1.0) < 1e-3, f"CRITERIA weights sum to {total_w}, expected 1.0"

    return records
