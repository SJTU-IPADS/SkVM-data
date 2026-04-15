# Brand Brief — Nexus Financial

**Brand color anchor:** `#1A56DB` (Nexus Blue)

**Style:** modern

**Brand context:** Nexus Financial is a B2B SaaS platform for financial operations.
The brand values precision, trust, and approachability.

## Requirements

Generate a complete color token JSON file named `tokens.json` at the workspace root.

The token file must include:

### Color palette structure

Produce a 9-step scale (steps 50, 100, 200, 300, 400, 500, 600, 700, 800, 900) for each of these palettes:
- `color.brand.primary` — derived from the brand anchor `#1A56DB`
- `color.brand.neutral` — a neutral gray family

Each token key must follow the pattern: `color.brand.<palette>.<step>` (e.g., `color.brand.primary.500`).

### Semantic tokens

Define exactly these semantic tokens (keys and their resolved palette token references):
- `color.semantic.action` → must reference `color.brand.primary.500`
- `color.semantic.action-hover` → must reference `color.brand.primary.600`
- `color.semantic.action-text` → must reference `color.brand.primary.900`
- `color.semantic.background` → must reference `color.brand.neutral.50`
- `color.semantic.surface` → must reference `color.brand.neutral.100`
- `color.semantic.border` → must reference `color.brand.neutral.300`
- `color.semantic.text-primary` → must reference `color.brand.neutral.900`
- `color.semantic.text-secondary` → must reference `color.brand.neutral.600`

### WCAG contrast audit

Produce a `contrast-audit.json` file at the workspace root containing an array of objects.
Each object must have:
- `pair` — string in the form `"<foreground-token> on <background-token>"`
- `ratio` — the WCAG 2.1 contrast ratio (rounded to 2 decimal places)
- `aa_normal` — boolean, true if ratio >= 4.5
- `aa_large` — boolean, true if ratio >= 3.0
- `aaa_normal` — boolean, true if ratio >= 7.0

Audit exactly these pairs (in this order):
1. `color.semantic.action-text` on `color.semantic.background`
2. `color.semantic.text-primary` on `color.semantic.background`
3. `color.semantic.text-secondary` on `color.semantic.background`
4. `color.semantic.action-text` on `color.semantic.surface`
5. `color.semantic.text-primary` on `color.semantic.surface`

### Naming convention invariant

Every semantic token's value must be a reference to an existing palette token key (a string that is itself a key in the tokens.json at the top level). The grader will verify that each semantic token's value matches an actual palette key.
