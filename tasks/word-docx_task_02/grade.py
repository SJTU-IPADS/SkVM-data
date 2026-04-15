"""
Grade function for word-docx_task_02.

Checks reviewed.docx produced by the agent from draft.docx. Uses zipfile +
lxml to inspect OOXML directly, and python-docx for paragraph-level checks.

Review policy:
  - Alice Chen's insertions must be KEPT (accepted)
  - Alice Chen's deletions must be ENACTED (deleted text gone)
  - Bob Torres's insertions must be REMOVED (rejected)
  - Bob Torres's deletions must be REVERTED (original text restored)
  - No revision markup (w:ins, w:del, w:commentRangeStart) in final document
  - Bookmark "intro-anchor" must survive
  - Footnote text must survive
"""
from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.04,
        "description": "reviewed.docx exists at the workspace root — the agent produced the required output file.",
    },
    {
        "id": "valid-ooxml",
        "weight": 0.05,
        "description": "reviewed.docx is a valid OOXML ZIP package containing word/document.xml — it opens without errors.",
    },
    {
        "id": "no-revision-markup",
        "weight": 0.18,
        "description": "word/document.xml contains no tracked-change elements (w:ins, w:del, w:commentRangeStart). The review must be fully resolved — no markup surviving in the delivered document.",
    },
    {
        "id": "alice-ins-kept",
        "weight": 0.15,
        "description": "Alice Chen's insertion 'and approved by the steering committee' appears as plain text in the document — her change was accepted, not removed.",
    },
    {
        "id": "alice-del-enacted",
        "weight": 0.15,
        "description": "The word 'automatically' does not appear in the document AND 'by the cache manager' does — Alice's deletion was enacted (the deleted word is gone, her replacement is kept).",
    },
    {
        "id": "bob-ins-removed",
        "weight": 0.12,
        "description": "Bob Torres's insertion 'and real-time sync' does NOT appear in the document — his change was rejected, so the document must read 'batch import.' without the extra phrase.",
    },
    {
        "id": "bob-del-reverted",
        "weight": 0.15,
        "description": "Bob Torres's deletion of 'Q3' was reverted: the document reads 'deprecated by Q3.' not 'deprecated by Q4.' — original text restored.",
    },
    {
        "id": "bookmark-preserved",
        "weight": 0.08,
        "description": "Bookmark 'intro-anchor' survives in word/document.xml (w:bookmarkStart w:name='intro-anchor') — bookmarks must be preserved through tracked-change resolution per the skill's reference-stability rules.",
    },
    {
        "id": "footnote-preserved",
        "weight": 0.08,
        "description": "The footnote text 'Applies to API versions 1.x through 2.3.' survives in word/footnotes.xml — footnotes live in a separate part and must not be lost during document manipulation.",
    },
]

_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}"


def _load_xml(workspace: str, part: str):
    """Return (xml_bytes, error_str). xml_bytes is None on failure."""
    path = Path(workspace) / "reviewed.docx"
    if not path.exists():
        return None, "reviewed.docx not found"
    try:
        with zipfile.ZipFile(str(path)) as zf:
            if part not in zf.namelist():
                return None, f"{part} not in reviewed.docx"
            return zf.read(part), None
    except zipfile.BadZipFile:
        return None, "reviewed.docx is not a valid zip/OOXML file"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _doc_text(workspace: str) -> str | None:
    """Extract plain text from word/document.xml (ignoring delText)."""
    xml, err = _load_xml(workspace, "word/document.xml")
    if xml is None:
        return None
    try:
        from lxml import etree
        root = etree.fromstring(xml)
        # Collect all w:t (plain text), skip w:delText which should be absent
        texts = []
        for t in root.iter(f"{{{W}}}t"):
            texts.append(t.text or "")
        return " ".join(texts)
    except Exception:
        return None


def grade(transcript, workspace_path: str):
    cwd = workspace_path
    doc_path = Path(cwd) / "reviewed.docx"

    results = []

    # ---- file-exists ---------------------------------------------------------
    exists = doc_path.exists()
    results.append({
        "id": "file-exists",
        "score": 1.0 if exists else 0.0,
        "weight": 0.04,
        "description": CRITERIA[0]["description"],
        **({"details": "reviewed.docx not found at workspace root"} if not exists else {}),
    })

    # ---- valid-ooxml ---------------------------------------------------------
    xml_doc, xml_err = _load_xml(cwd, "word/document.xml")
    valid = xml_doc is not None
    results.append({
        "id": "valid-ooxml",
        "score": 1.0 if valid else 0.0,
        "weight": 0.05,
        "description": CRITERIA[1]["description"],
        **({"details": xml_err} if not valid else {}),
    })

    # ---- no-revision-markup --------------------------------------------------
    if xml_doc is not None:
        xml_str = xml_doc.decode("utf-8", errors="replace")
        found_markup = []
        for pattern in (r"<w:ins[\s>/]", r"<w:del[\s>/]", r"<w:commentRangeStart"):
            if re.search(pattern, xml_str):
                found_markup.append(pattern.split("[")[0].lstrip("<"))
        no_markup = len(found_markup) == 0
    else:
        no_markup = False
        found_markup = ["could not read document.xml"]
    results.append({
        "id": "no-revision-markup",
        "score": 1.0 if no_markup else 0.0,
        "weight": 0.18,
        "description": CRITERIA[2]["description"],
        **({"details": f"revision markup still present: {found_markup}"} if not no_markup else {}),
    })

    # ---- get plain text once -------------------------------------------------
    plain_text = _doc_text(cwd) or ""

    # ---- alice-ins-kept ------------------------------------------------------
    alice_ins_phrase = "and approved by the steering committee"
    alice_ins_ok = alice_ins_phrase in plain_text
    results.append({
        "id": "alice-ins-kept",
        "score": 1.0 if alice_ins_ok else 0.0,
        "weight": 0.15,
        "description": CRITERIA[3]["description"],
        **({"details": f"phrase not found in document text: {alice_ins_phrase!r}"} if not alice_ins_ok else {}),
    })

    # ---- alice-del-enacted ---------------------------------------------------
    # "automatically" gone, "by the cache manager" present
    auto_gone = "automatically" not in plain_text
    cache_mgr_present = "by the cache manager" in plain_text
    alice_del_ok = auto_gone and cache_mgr_present
    det = []
    if not auto_gone:
        det.append("'automatically' still present (should have been deleted by Alice's change)")
    if not cache_mgr_present:
        det.append("'by the cache manager' not found (Alice's replacement missing)")
    results.append({
        "id": "alice-del-enacted",
        "score": 1.0 if alice_del_ok else 0.0,
        "weight": 0.15,
        "description": CRITERIA[4]["description"],
        **({"details": "; ".join(det)} if det else {}),
    })

    # ---- bob-ins-removed -----------------------------------------------------
    bob_ins_phrase = "real-time sync"
    bob_ins_removed = bob_ins_phrase not in plain_text
    results.append({
        "id": "bob-ins-removed",
        "score": 1.0 if bob_ins_removed else 0.0,
        "weight": 0.12,
        "description": CRITERIA[5]["description"],
        **({"details": f"Bob's inserted phrase still present: {bob_ins_phrase!r}"} if not bob_ins_removed else {}),
    })

    # ---- bob-del-reverted ----------------------------------------------------
    # Document should say "Q3" not "Q4" (Bob's Q4 insertion removed, Q3 restored)
    has_q3 = "Q3" in plain_text
    has_q4_wrong = "Q4" in plain_text
    bob_del_ok = has_q3 and not has_q4_wrong
    det2 = []
    if not has_q3:
        det2.append("'Q3' not found — original text was not restored")
    if has_q4_wrong:
        det2.append("'Q4' still present — Bob's insertion was not removed")
    results.append({
        "id": "bob-del-reverted",
        "score": 1.0 if bob_del_ok else 0.0,
        "weight": 0.15,
        "description": CRITERIA[6]["description"],
        **({"details": "; ".join(det2)} if det2 else {}),
    })

    # ---- bookmark-preserved --------------------------------------------------
    bm_ok = False
    bm_detail = None
    if xml_doc is not None:
        xml_str = xml_doc.decode("utf-8", errors="replace")
        if 'w:name="intro-anchor"' in xml_str or "w:name='intro-anchor'" in xml_str:
            bm_ok = True
        else:
            bm_detail = "bookmarkStart with name='intro-anchor' not found in word/document.xml"
    else:
        bm_detail = "could not read document.xml"
    results.append({
        "id": "bookmark-preserved",
        "score": 1.0 if bm_ok else 0.0,
        "weight": 0.08,
        "description": CRITERIA[7]["description"],
        **({"details": bm_detail} if not bm_ok else {}),
    })

    # ---- footnote-preserved --------------------------------------------------
    fn_xml, fn_err = _load_xml(cwd, "word/footnotes.xml")
    fn_ok = False
    fn_detail = None
    if fn_xml is not None:
        fn_str = fn_xml.decode("utf-8", errors="replace")
        if "Applies to API versions 1.x through 2.3." in fn_str:
            fn_ok = True
        else:
            fn_detail = "footnote text 'Applies to API versions 1.x through 2.3.' not found in word/footnotes.xml"
    else:
        fn_detail = fn_err or "word/footnotes.xml missing"
    results.append({
        "id": "footnote-preserved",
        "score": 1.0 if fn_ok else 0.0,
        "weight": 0.08,
        "description": CRITERIA[8]["description"],
        **({"details": fn_detail} if not fn_ok else {}),
    })

    return results
