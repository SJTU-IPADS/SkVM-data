"""
Reference solution for frontend-slides_task_02.

Reads talk_outline.json from cwd and produces:
  - talk.html       (self-contained, dark theme, 6 slides with ids, speaker
                     notes as HTML comments, slide counter, wheel+keyboard nav)
  - talk_manifest.json

Run from workspace: python3 REFERENCE/solution.py
"""
from __future__ import annotations
import json
from pathlib import Path

OUTLINE_PATH = Path("talk_outline.json")


def load_outline() -> dict:
    return json.loads(OUTLINE_PATH.read_text())


def build_slide(slide: dict) -> str:
    sid = slide["id"]
    stype = slide["type"]
    note = slide.get("speaker_note", "")
    note_comment = f"\n    <!-- SPEAKER NOTE: {note} -->" if note else ""

    if stype == "cover":
        inner = f"""
    <div class="slide-content cover-content">
      <h1>{slide['heading']}</h1>
      <p class="subheading">{slide.get('subheading', '')}</p>
    </div>{note_comment}"""
    elif stype == "agenda":
        items_html = "".join(f"<li>{item}</li>" for item in slide.get("items", []))
        inner = f"""
    <div class="slide-content">
      <h2>{slide['heading']}</h2>
      <ol class="agenda-list">{items_html}</ol>
    </div>{note_comment}"""
    elif stype == "content":
        bullets_html = "".join(f"<li>{b}</li>" for b in slide.get("bullets", []))
        inner = f"""
    <div class="slide-content">
      <h2>{slide['heading']}</h2>
      <ul class="bullet-list">{bullets_html}</ul>
    </div>{note_comment}"""
    elif stype == "cta":
        inner = f"""
    <div class="slide-content cta-content">
      <h2>{slide['heading']}</h2>
      <p class="cta-body">{slide.get('body', '')}</p>
    </div>{note_comment}"""
    else:
        inner = f"""
    <div class="slide-content"><h2>{slide.get('heading','')}</h2></div>{note_comment}"""

    return f'  <section class="slide" id="{sid}">{inner}\n  </section>'


def build_html(outline: dict) -> str:
    slides = outline["slides"]
    n = len(slides)

    slides_html = "\n".join(build_slide(s) for s in slides)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{outline.get('talk_title', 'Talk')}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 100%;
    height: 100%;
    overflow: hidden;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #0a0a0f;
    color: #e0e4f0;
  }}
  .presentation {{
    width: 100%;
    height: 100vh;
    overflow: hidden;
    position: relative;
  }}
  .slide {{
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    background: #0a0a0f;
    opacity: 0;
    transform: translateX(100%);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;
  }}
  .slide.active {{
    opacity: 1;
    transform: translateX(0);
  }}
  .slide.prev {{
    transform: translateX(-100%);
    opacity: 0;
  }}
  .slide-content {{
    max-width: 860px;
    width: 100%;
    padding: 48px;
  }}
  .cover-content {{ text-align: center; }}
  h1 {{
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 700;
    color: #f0f4ff;
    margin-bottom: 20px;
    line-height: 1.2;
  }}
  h2 {{
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 600;
    color: #f0f4ff;
    margin-bottom: 28px;
    border-bottom: 2px solid #2a2a4a;
    padding-bottom: 12px;
  }}
  .subheading {{
    font-size: clamp(1rem, 2vw, 1.25rem);
    color: #7a8ab0;
    margin-top: 8px;
  }}
  .bullet-list, .agenda-list {{
    list-style: none;
    padding: 0;
  }}
  .bullet-list li, .agenda-list li {{
    padding: 14px 20px;
    margin-bottom: 10px;
    border-left: 3px solid #3a5aff;
    background: rgba(58, 90, 255, 0.07);
    font-size: clamp(0.9rem, 1.6vw, 1.05rem);
    line-height: 1.6;
    color: #c8d4f0;
  }}
  .cta-content {{ text-align: center; }}
  .cta-body {{
    font-size: clamp(1rem, 2vw, 1.3rem);
    color: #8090b0;
    margin-top: 20px;
    line-height: 1.6;
  }}
  /* Slide counter */
  .slide-counter {{
    position: fixed;
    bottom: 24px;
    right: 32px;
    font-size: 0.85rem;
    color: #4a5a80;
    font-variant-numeric: tabular-nums;
    z-index: 100;
  }}
  /* Speaker note: hidden visually, embedded as HTML comment in DOM */
  @media (max-height: 600px) {{
    .slide-content {{ padding: 24px; }}
    h1 {{ font-size: 1.8rem; }}
    h2 {{ font-size: 1.3rem; }}
  }}
  @media (max-width: 640px) {{
    .slide-content {{ padding: 24px; }}
  }}
</style>
</head>
<body>
<div class="presentation" id="presentation">
{slides_html}
</div>
<div class="slide-counter" id="slide-counter">1 / {n}</div>
<script>
(function() {{
  var slides = document.querySelectorAll('.slide');
  var counter = document.getElementById('slide-counter');
  var current = 0;
  var total = slides.length;
  var throttleWheel = false;

  function goTo(idx) {{
    if (idx < 0 || idx >= total) return;
    slides[current].classList.remove('active');
    slides[current].classList.add('prev');
    current = idx;
    slides.forEach(function(s, i) {{
      s.classList.remove('prev');
      s.classList.remove('active');
    }});
    slides[current].classList.add('active');
    counter.textContent = (current + 1) + ' / ' + total;
  }}

  function next() {{ goTo(current + 1); }}
  function prev() {{ goTo(current - 1); }}

  // Keyboard navigation
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {{
      e.preventDefault(); next();
    }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{
      e.preventDefault(); prev();
    }}
  }});

  // Mouse-wheel navigation (throttled)
  document.addEventListener('wheel', function(e) {{
    e.preventDefault();
    if (throttleWheel) return;
    throttleWheel = true;
    if (e.deltaY > 0) {{ next(); }} else {{ prev(); }}
    setTimeout(function() {{ throttleWheel = false; }}, 600);
  }}, {{ passive: false }});

  // Init
  goTo(0);
}})();
</script>
</body>
</html>
"""
    return html


def build_manifest(outline: dict) -> dict:
    slides = outline["slides"]
    return {
        "slide_count": len(slides),
        "slide_ids": [s["id"] for s in slides],
        "has_speaker_notes": True,
        "output_file": outline.get("output_file", "talk.html"),
    }


def main() -> None:
    outline = load_outline()
    html = build_html(outline)
    out_file = outline.get("output_file", "talk.html")
    Path(out_file).write_text(html, encoding="utf-8")
    manifest = build_manifest(outline)
    Path("talk_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Written {out_file} ({len(html)} bytes) and talk_manifest.json")


if __name__ == "__main__":
    main()
