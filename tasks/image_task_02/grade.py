"""
grade.py for image_task_02.

Contract: returns a list of criterion records per grade-py-protocol.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Checks (9 criteria, weights sum to 1.0):
  1. output/ directory exists
  2. all 4 WebP files present: prod_001.webp, prod_002.webp, prod_003.webp, prod_004.webp
  3. file count in output/ is exactly 4
  4. all outputs are valid WebP format
  5. all outputs are exactly 600x400 pixels (center-crop + EXIF correctness)
  6. prod_002 specifically 600x400 (EXIF orientation=8 trap: stored 900x1200, visual 1200x900)
  7. no alpha channel in any output (palette P-mode and RGBA must be composited)
  8. watermark present in lower-right region (white pixels in bottom-right 20%x45%)
  9. output naming uses source stems (prod_001/002/003/004) with .webp extension

Archetypes hit:
  - Archetype 1 (under-specified step): center-crop must be from center, not top-left
  - Archetype 3 (multi-step coordination): EXIF + mode convert + crop + watermark + WebP
  - Archetype 4 (known-edge-case): prod_002 EXIF orientation=8, prod_004 palette P-mode
  - Archetype 5 (stateful invariant): 4 files, all 600x400, watermark in bounds
"""
from __future__ import annotations
import os
from pathlib import Path

EXPECTED_FILES = {"prod_001.webp", "prod_002.webp", "prod_003.webp", "prod_004.webp"}
TARGET_W, TARGET_H = 600, 400


def _load_image(path: Path):
    try:
        from PIL import Image
        img = Image.open(str(path))
        img.load()
        return img, None
    except Exception as e:
        return None, str(e)


def _has_watermark_pixels(img) -> bool:
    """Check for white-ish pixels in the lower-right corner (bottom 20%, right 45%)."""
    try:
        import numpy as np
        arr = np.array(img.convert("RGB"))
        h, w = arr.shape[:2]
        region = arr[int(h * 0.80):, int(w * 0.55):]
        white = (region[:, :, 0] > 230) & (region[:, :, 1] > 230) & (region[:, :, 2] > 230)
        return int(white.sum()) >= 5
    except Exception:
        return False


def grade(transcript, workspace_path: str):
    ws = Path(workspace_path)
    out_dir = ws / "output"

    dir_exists = out_dir.is_dir()

    present = set()
    all_in_output = []
    if dir_exists:
        for f in out_dir.iterdir():
            all_in_output.append(f.name)
            if f.name in EXPECTED_FILES:
                present.add(f.name)
    files_present = (present == EXPECTED_FILES)
    file_count = len(all_in_output)

    per_file: dict[str, dict] = {}
    for fname in sorted(EXPECTED_FILES):
        fpath = out_dir / fname
        if not fpath.exists():
            per_file[fname] = {"exists": False}
            continue
        img, err = _load_image(fpath)
        if img is None:
            per_file[fname] = {"exists": True, "err": err, "is_webp": False,
                               "correct_size": False, "no_alpha": False, "has_watermark": False}
            continue
        per_file[fname] = {
            "exists": True,
            "is_webp": img.format == "WEBP",
            "size": (img.width, img.height),
            "correct_size": (img.width == TARGET_W and img.height == TARGET_H),
            "no_alpha": img.mode not in ("RGBA", "LA"),
            "has_watermark": _has_watermark_pixels(img),
            "mode": img.mode,
        }

    def _all(key):
        return all(d.get(key, False) for d in per_file.values())

    def _bad(key):
        return [fn for fn, d in per_file.items() if not d.get(key, False)]

    records = []

    # 1. output dir exists
    records.append({
        "id": "output-dir-exists",
        "score": 1.0 if dir_exists else 0.0,
        "weight": 0.04,
        "description": "A directory named 'output' exists at the workspace root to receive all processed product images.",
        **({"details": "output/ directory not found."} if not dir_exists else {}),
    })

    # 2. all 4 files present
    missing = EXPECTED_FILES - present
    records.append({
        "id": "all-files-present",
        "score": 1.0 if files_present else 0.0,
        "weight": 0.08,
        "description": "All four output files are present in output/: prod_001.webp, prod_002.webp, prod_003.webp, prod_004.webp — one WebP per input image with the source stem preserved.",
        **({"details": f"Missing: {sorted(missing)}"} if missing else {}),
    })

    # 3. file count == 4
    count_ok = (file_count == 4)
    records.append({
        "id": "file-count-exactly-4",
        "score": 1.0 if count_ok else 0.0,
        "weight": 0.04,
        "description": "output/ contains exactly 4 files — one per source image, no extras — preserving the batch invariant that every input produces exactly one output.",
        **({"details": f"Expected 4 files, found {file_count}: {sorted(all_in_output)}"} if not count_ok else {}),
    })

    # 4. all outputs are WebP
    all_webp = _all("is_webp")
    bad_webp = _bad("is_webp")
    records.append({
        "id": "all-outputs-webp",
        "score": 1.0 if all_webp else 0.0,
        "weight": 0.10,
        "description": "All four output files are valid WebP images. The task requires converting all inputs (JPEG and PNG) to WebP quality=80.",
        **({"details": f"Non-WebP output(s): {bad_webp}"} if not all_webp else {}),
    })

    # 5. all outputs exactly 600x400
    all_sized = _all("correct_size")
    bad_sized = _bad("correct_size")
    size_det = None
    if not all_sized:
        parts = [f"{fn}: got {per_file[fn].get('size', 'n/a')} expected (600, 400)" for fn in bad_sized]
        size_det = "; ".join(parts)
    records.append({
        "id": "all-outputs-600x400",
        "score": 1.0 if all_sized else 0.0,
        "weight": 0.18,
        "description": "All four output images are exactly 600×400 pixels after center-crop, confirming that the crop was applied on the visually-correct pixel grid (including after EXIF orientation) and to the correct dimensions.",
        **({"details": size_det} if size_det else {}),
    })

    # 6. prod_002 specifically 600x400 (EXIF orientation=8 trap)
    p2 = per_file.get("prod_002.webp", {})
    p2_ok = p2.get("correct_size", False)
    records.append({
        "id": "prod002-exif-orientation-applied",
        "score": 1.0 if p2_ok else 0.0,
        "weight": 0.18,
        "description": "prod_002.webp is 600×400 pixels, proving that EXIF orientation=8 was applied before cropping. The raw stored image is 900×1200 (portrait) with EXIF orientation=8 (rotate 90° CCW to display as 1200×900 landscape); without orientation correction the center-crop operates on the wrong pixel grid.",
        **({"details": f"prod_002.webp actual size: {p2.get('size', 'missing')} — expected (600, 400). EXIF orientation=8 was likely not applied before cropping."} if not p2_ok else {}),
    })

    # 7. no alpha in outputs (palette P + RGBA must be composited)
    all_no_alpha = _all("no_alpha")
    bad_alpha = _bad("no_alpha")
    alpha_det = None
    if not all_no_alpha:
        parts = [f"{fn}: mode={per_file[fn].get('mode', 'n/a')}" for fn in bad_alpha]
        alpha_det = f"Alpha channel found — prod_003.png (RGBA) and prod_004.png (palette/P) must be composited on white before saving: {'; '.join(parts)}"
    records.append({
        "id": "no-alpha-in-output",
        "score": 1.0 if all_no_alpha else 0.0,
        "weight": 0.15,
        "description": "No output WebP file retains an alpha channel (mode must be RGB, not RGBA/LA). prod_003.png is RGBA and prod_004.png is a palette-mode PNG that may include transparency; both must be composited on white (#FFFFFF) before cropping and saving.",
        **({"details": alpha_det} if alpha_det else {}),
    })

    # 8. watermark present in lower-right of each output
    all_watermarked = _all("has_watermark")
    bad_wm = _bad("has_watermark")
    records.append({
        "id": "watermark-in-lower-right",
        "score": 1.0 if all_watermarked else 0.0,
        "weight": 0.15,
        "description": "Each output image has watermark text in the lower-right corner region, detectable as white-ish pixels (R>230, G>230, B>230) in the bottom 20% × right 45% of the image. Missing or misplaced watermark (top-left, center, or outside image bounds) fails this criterion.",
        **({"details": f"Watermark not detected in lower-right of: {bad_wm}"} if bad_wm else {}),
    })

    # 9. naming invariant: all stems are prod_001/002/003/004
    expected_stems = {"prod_001", "prod_002", "prod_003", "prod_004"}
    actual_stems = {Path(f).stem for f in all_in_output} if all_in_output else set()
    stems_ok = (expected_stems == actual_stems)
    records.append({
        "id": "output-naming-matches-source-stems",
        "score": 1.0 if stems_ok else 0.0,
        "weight": 0.08,
        "description": "Output filenames use the source stem (prod_001, prod_002, prod_003, prod_004) with .webp extension, preserving per-file identity across the batch pipeline.",
        **({"details": f"Expected stems {sorted(expected_stems)}, found {sorted(actual_stems)}"} if not stems_ok else {}),
    })

    # Verify weight sum at author time
    total_w = sum(r["weight"] for r in records)
    assert abs(total_w - 1.0) < 1e-3, f"CRITERIA weights sum to {total_w}, expected 1.0"

    return records
