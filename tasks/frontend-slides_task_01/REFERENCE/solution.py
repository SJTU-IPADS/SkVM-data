"""
Reference solution for frontend-slides_task_01.

Reads deck_spec.json from cwd and produces:
  - presentation.html  (self-contained, no external deps, 6 .slide elements
                        with correct ids, viewport CSS, nav dots, JS nav)
  - deck_manifest.json (slide_count=6, slide_ids=[...], output_file)

Run from the workspace dir: python3 REFERENCE/solution.py
"""
from __future__ import annotations
import json
from pathlib import Path

SPEC_PATH = Path("deck_spec.json")


def load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text())


def build_html(spec: dict) -> str:
    slides = spec["slides"]
    slide_ids = [s["id"] for s in slides]
    n = len(slides)

    slide_html_parts = []
    for slide in slides:
        sid = slide["id"]
        stype = slide["type"]

        if stype == "title":
            inner = f"""
      <div class="slide-content title-content">
        <h1>{slide['heading']}</h1>
        <p class="subtitle">{slide['subheading']}</p>
        <p class="tagline">{slide.get('tagline','')}</p>
      </div>"""
        elif stype == "content":
            bullets_html = "\n".join(f"<li>{b}</li>" for b in slide.get("bullets", []))
            inner = f"""
      <div class="slide-content">
        <h2>{slide['heading']}</h2>
        <ul>{bullets_html}</ul>
      </div>"""
        elif stype == "feature-grid":
            cards_html = ""
            for card in slide.get("cards", []):
                cards_html += f"""<div class="card"><h3>{card['title']}</h3><p>{card['description']}</p></div>\n"""
            inner = f"""
      <div class="slide-content">
        <h2>{slide['heading']}</h2>
        <div class="card-grid">{cards_html}</div>
      </div>"""
        elif stype == "cta":
            inner = f"""
      <div class="slide-content cta-content">
        <h2>{slide['heading']}</h2>
        <p class="cta-body">{slide.get('body','')}</p>
        <button id="{slide.get('cta_id','cta-button')}" class="cta-btn">{slide.get('cta_label','Get Started')}</button>
      </div>"""
        else:
            inner = f"<div class='slide-content'><h2>{slide.get('heading','')}</h2></div>"

        slide_html_parts.append(f'  <section class="slide" id="{sid}">{inner}\n  </section>')

    slides_html = "\n".join(slide_html_parts)

    dots_html = "\n".join(
        f'    <span class="dot" data-index="{i}"></span>'
        for i in range(n)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{spec.get('title', 'Presentation')}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 100%; height: 100%;
    overflow: hidden;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #0f1117;
    color: #e8eaf0;
  }}
  .presentation {{
    width: 100%; height: 100vh;
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
    top: 0; left: 0;
    width: 100%;
    opacity: 0;
    transform: translateX(100%);
    transition: transform 0.4s ease, opacity 0.4s ease;
    background: #0f1117;
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
    max-width: 900px;
    padding: 40px;
    width: 100%;
  }}
  .title-content {{ text-align: center; }}
  h1 {{ font-size: clamp(2rem, 5vw, 4rem); font-weight: 700; color: #ffffff; margin-bottom: 16px; }}
  h2 {{ font-size: clamp(1.5rem, 3.5vw, 2.5rem); font-weight: 600; color: #ffffff; margin-bottom: 24px; }}
  h3 {{ font-size: 1.1rem; font-weight: 600; color: #a0c4ff; margin-bottom: 8px; }}
  .subtitle {{ font-size: clamp(1rem, 2vw, 1.4rem); color: #a0b4cc; margin-bottom: 12px; }}
  .tagline {{ font-size: 1rem; color: #6b8caa; letter-spacing: 0.1em; }}
  ul {{ list-style: none; padding: 0; }}
  ul li {{
    padding: 12px 16px;
    margin-bottom: 8px;
    border-left: 3px solid #4a9eff;
    background: rgba(74, 158, 255, 0.06);
    font-size: clamp(0.9rem, 1.8vw, 1.1rem);
    line-height: 1.5;
  }}
  .card-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-top: 8px;
  }}
  .card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 20px;
  }}
  .card p {{ font-size: 0.9rem; color: #8899aa; line-height: 1.5; }}
  .cta-content {{ text-align: center; }}
  .cta-body {{ font-size: 1.1rem; color: #a0b4cc; margin: 16px 0 32px; }}
  #cta-button {{
    display: inline-block;
    background: #4a9eff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 16px 40px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s ease;
  }}
  #cta-button:hover {{ background: #2b7fe0; }}

  /* Navigation dots */
  .nav-dots {{
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    z-index: 100;
  }}
  .dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: rgba(255,255,255,0.25);
    cursor: pointer;
    transition: background 0.2s;
  }}
  .dot.active {{ background: #4a9eff; }}

  /* Entrance animation */
  @keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  .slide.active .slide-content {{
    animation: fadeSlideIn 0.5s ease forwards;
  }}

  @media (max-height: 600px) {{
    h1 {{ font-size: 1.8rem; }}
    h2 {{ font-size: 1.4rem; }}
    .slide-content {{ padding: 20px; }}
  }}
  @media (max-width: 600px) {{
    .card-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="presentation" id="presentation">
{slides_html}
</div>
<nav class="nav-dots" aria-label="Slide navigation">
{dots_html}
</nav>
<script>
(function() {{
  var slides = document.querySelectorAll('.slide');
  var dots = document.querySelectorAll('.dot');
  var current = 0;
  var total = slides.length;

  function goTo(idx) {{
    if (idx < 0 || idx >= total) return;
    slides[current].classList.remove('active');
    slides[current].classList.add('prev');
    dots[current].classList.remove('active');
    current = idx;
    slides[current].classList.remove('prev');
    slides[current].classList.add('active');
    dots[current].classList.add('active');
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

  // Dot click
  dots.forEach(function(dot, i) {{
    dot.addEventListener('click', function() {{ goTo(i); }});
  }});

  // Initialise first slide
  goTo(0);
}})();
</script>
</body>
</html>
"""
    return html


def build_manifest(spec: dict) -> dict:
    slides = spec["slides"]
    return {
        "slide_count": len(slides),
        "slide_ids": [s["id"] for s in slides],
        "output_file": "presentation.html",
    }


def main() -> None:
    spec = load_spec()
    html = build_html(spec)
    Path("presentation.html").write_text(html, encoding="utf-8")
    manifest = build_manifest(spec)
    Path("deck_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Written presentation.html ({len(html)} bytes) and deck_manifest.json")


if __name__ == "__main__":
    main()
