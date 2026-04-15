# Design System Specification — Crestline SaaS

## Typography Scale

Base size: **16px**. Scale ratio: **1.25** (Major Third).

Generate a 9-step type scale with these step names (in order):
`xs`, `sm`, `base`, `lg`, `xl`, `2xl`, `3xl`, `4xl`, `5xl`

**Calculation rule:** Each step value in pixels is `16 × 1.25^n` where:
- `xs` = n=-2 (i.e. 16 ÷ 1.25²)
- `sm` = n=-1
- `base` = n=0 (exactly 16px)
- `lg` = n=1
- `xl` = n=2
- `2xl` = n=3
- `3xl` = n=4
- `4xl` = n=5
- `5xl` = n=6

**Rounding rule:** Round each value to the **nearest integer** (standard rounding, not floor/ceil).

Output these as CSS custom properties inside a `:root {}` block in a file named `tokens.css`.
The property names must follow the pattern `--font-size-<step>` (e.g. `--font-size-xs`, `--font-size-base`).
Values must include the `px` unit (e.g. `10px`, `16px`, `20px`).

## Spacing Scale (8-point grid)

Generate a spacing scale using an **8-point grid** system.
Produce steps 1 through 10 (integers), where step N has value `N × 8px`.

Property names: `--space-<N>` (e.g. `--space-1` through `--space-10`).
Values must be exact multiples of 8 (e.g. `8px`, `16px`, ..., `80px`).

Add these spacing tokens to the same `:root {}` block in `tokens.css`.

## Fluid Typography

For the following 4 type sizes, generate a fluid CSS `clamp()` expression.
The fluid formula uses a **320px–1280px** viewport range.

The formula for a fluid value between `min_px` and `max_px`:
```
preferred_vw = (max_px - min_px) / (1280 - 320) × 100
preferred_rem = min_px / 16 - preferred_vw × 320 / (100 × 16)
result = clamp(<min_rem>rem, <preferred_rem>rem + <preferred_vw>vw, <max_rem>rem)
```

Where all rem values are rounded to **4 decimal places**.

Generate fluid values for:
| Name         | min_px | max_px |
|--------------|--------|--------|
| --fluid-h1   | 32     | 64     |
| --fluid-h2   | 28     | 48     |
| --fluid-h3   | 24     | 36     |
| --fluid-body | 16     | 18     |

Add these as `--fluid-h1`, `--fluid-h2`, `--fluid-h3`, `--fluid-body` custom properties in the same `:root {}` block.

## Breakpoints

Add these breakpoints as CSS custom properties (unitless integers represent pixel widths):
- `--bp-sm`: 480
- `--bp-md`: 640
- `--bp-lg`: 768
- `--bp-xl`: 1024
- `--bp-2xl`: 1280

Values must be plain integers (no `px` unit) for JavaScript interop.

## Deliverable

Produce a single file `tokens.css` at the workspace root containing a single `:root {}` block with all the above properties in this section order:
1. Font size tokens (`--font-size-*`)
2. Spacing tokens (`--space-*`)
3. Fluid typography tokens (`--fluid-*`)
4. Breakpoint tokens (`--bp-*`)

No other CSS rules, no comments outside the `:root {}` block, and no duplicate property names.
