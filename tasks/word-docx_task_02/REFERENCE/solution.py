"""
Reference solution for word-docx_task_02.

Reads draft.docx (which has tracked changes from two reviewers) and produces
reviewed.docx at the workspace root with:
  - Alice Chen's changes accepted  (her insertions kept, her deletions enacted)
  - Bob Torres's changes rejected  (his insertions removed, his deletions reverted)
  - No revision markup remaining in word/document.xml
  - Bookmark "intro-anchor" preserved
  - Footnote text preserved

Strategy: manipulate OOXML directly via lxml. For each paragraph, walk the
child elements and:
  - For w:ins by Alice: unwrap (keep children runs as plain siblings)
  - For w:del by Alice: remove the element (deletion is enacted)
  - For w:ins by Bob:   remove the element (insertion is rejected)
  - For w:del by Bob:   unwrap del runs but convert w:delText → w:t (restore original)
"""
from __future__ import annotations
import os
import sys
import copy
import zipfile
import io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def qn(tag: str) -> str:
    ns, local = tag.split(":", 1)
    return f"{{{W}}}{local}"


ALICE = "Alice Chen"
BOB = "Bob Torres"


def accept_alice_reject_bob(doc_xml_bytes: bytes) -> bytes:
    """Transform document.xml according to the review policy."""
    root = etree.fromstring(doc_xml_bytes)

    def get_author(elem) -> str:
        return elem.get(qn("w:author"), "")

    def convert_del_text_to_t(elem):
        """Convert all w:delText inside this element to w:t (restoring deleted text)."""
        for dt in elem.iter(qn("w:delText")):
            dt.tag = qn("w:t")

    def process_paragraph(p):
        """
        Process all w:ins and w:del inside a paragraph, replacing them in-place.
        We collect a new list of children, replacing tracked-change wrappers
        with their resolved content.
        """
        # We need to modify the children list while iterating, so collect ops first.
        to_process = list(p)  # snapshot current children
        # Build a map of (element -> replacement_list)
        # We'll reconstruct p's children from scratch.
        new_children = []

        for child in to_process:
            tag = etree.QName(child.tag).localname if child.tag != etree.Comment else None
            if tag == "ins":
                author = get_author(child)
                if author == ALICE:
                    # Accept Alice's insertion: unwrap → keep the runs
                    for run in list(child):
                        new_children.append(copy.deepcopy(run))
                elif author == BOB:
                    # Reject Bob's insertion: remove it entirely
                    pass  # don't append
                else:
                    # Unknown author: keep as-is
                    new_children.append(copy.deepcopy(child))
            elif tag == "del":
                author = get_author(child)
                if author == ALICE:
                    # Accept Alice's deletion: remove the deleted text (don't restore it)
                    pass  # don't append
                elif author == BOB:
                    # Reject Bob's deletion: restore the original text
                    child_copy = copy.deepcopy(child)
                    convert_del_text_to_t(child_copy)
                    # Unwrap the w:del wrapper, keeping its run children
                    for run in list(child_copy):
                        new_children.append(run)
                else:
                    new_children.append(copy.deepcopy(child))
            else:
                new_children.append(copy.deepcopy(child))

        # Replace p's children
        for child in list(p):
            p.remove(child)
        for child in new_children:
            p.append(child)

    # Walk all paragraphs in the body
    body = root.find(qn("w:body"))
    if body is not None:
        for p in body.findall(qn("w:p")):
            process_paragraph(p)

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def main():
    workspace = os.environ.get("WORKSPACE", os.getcwd())
    src = os.path.join(workspace, "draft.docx")
    dst = os.path.join(workspace, "reviewed.docx")

    if not os.path.exists(src):
        print(f"ERROR: {src} not found", file=sys.stderr)
        sys.exit(1)

    with zipfile.ZipFile(src, "r") as zin:
        names = zin.namelist()
        files = {name: zin.read(name) for name in names}

    # Transform document.xml
    if "word/document.xml" in files:
        files["word/document.xml"] = accept_alice_reject_bob(files["word/document.xml"])

    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)

    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
