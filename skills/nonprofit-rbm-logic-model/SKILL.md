---
name: nonprofit-impact-orchestra
description: Generate donor-ready nonprofit project packages for grants, concept notes, logframes, MEAL plans, budgets, safeguarding reviews, and funder adaptation. Use when designing a new project, adapting to a donor call, building RBM logic, or preparing a proposal for submission. Also covers GESI, SDG alignment, risks, compliance scoring, and JSON-ready outputs.
---

# Nonprofit Impact Orchestra

Turn rough nonprofit ideas, donor calls, or draft proposals into donor-ready packages.

## Important Usage Note

`orchestra ...` examples below are **invocation patterns**, not a required local binary.
Use them as mode labels when handling user requests in chat.

## Invocation Patterns

- `orchestra [project description]`
- `orchestra --express [description]`
- `orchestra --concept [description]`
- `orchestra --loi [description]`
- `orchestra --cfp [paste donor call text]`
- `orchestra --review [paste proposal text]`
- `orchestra --peer-review [paste proposal text]`
- `orchestra --donor-fit [description]`
- `orchestra --json [description]`

## Core Rules

1. Be donor-ready; never fake certainty.
2. Preserve realism over grandiosity.
3. Flag weak or unverifiable claims explicitly.
4. Ask only minimum blocking questions.
5. Prefer structured outputs over long prose.
6. Build for implementation, not just approval.
7. Never fabricate baselines, evidence, partner commitments, or donor fit.
8. Never output citations without retrievable source metadata (title/organization, URL or document origin, and date).

## Evidence & Source Policy (Mandatory)

### Confidence Labels
- `[HIGH]` — verified with retrievable source
- `[MEDIUM]` — plausible but incomplete evidence
- `[UNVERIFIED]` — claim needs manual verification

### Source Requirements
For each source in an Evidence Note, include:
- source title or organization,
- URL (or explicit non-URL origin provided by user),
- publication/access date,
- confidence label.

### Source-Limited Mode (Fallback)
If reliable retrieval is unavailable (no web/tool access and no user-provided sources):
1. Do **not** invent sources or links.
2. Replace Evidence Note with `Evidence Needed`.
3. Mark unsupported claims as `[UNVERIFIED]`.
4. Add `owner + due date` for each verification item.

## Decision-Grade Additions (standard/deep mode)

1. Add Evidence Note with 3–8 sources **only when source requirements are met**.
2. For any budget line >10% of total, provide unit-cost assumptions (quantity × unit rate) + rationale.
3. Add Compliance Gates: `Go / Conditional Go / No-Go` before submission.
4. Separate verified baselines from placeholders.
5. Add a 2-week validation sprint (data checks, partner confirmations, budget checks, stop/go trigger).

## Workflow

1. **Parse and scope**: location, target group, problem, impact, budget, duration, partners, donor, output type.
2. **Strategic context**: drivers, stakeholders, risks, assumptions, donor-fit extraction from CFP (if provided).
3. **Program logic**: RBM chain, ToC, logframe, SMART indicators, assumptions, baselines/targets.
4. **MEAL + GESI + SDG**: accountability loop, inclusion analysis, SDG mapping.
5. **Safeguarding/Do No Harm**: PSEA, conflict sensitivity, privacy, consent, environmental screening.
6. **Budget logic**: personnel/travel/equipment/training/ops/contingency/co-financing + red-flag checks.
7. **Draft/adapt**: donor-aligned framing, structure, language.
8. **Readiness check**: risk matrix, scenarios, compliance score, confidence report, verification plan.

## Default Delivery Package

00. Elevator Pitch  
01. Executive Summary  
02. Concept Note (if requested)  
03. Strategic Context  
04. Stakeholder Mapping  
05. GESI Analysis  
06. Safeguarding / Do No Harm Checklist  
07. RBM Chain  
08. Theory of Change  
09. Logframe Matrix  
10. MEAL Plan  
11. SDG Alignment  
12. Budget Table  
13. Co-financing Summary  
14. Sustainability / Exit Strategy  
15. Partnership Structure  
16. Donor Adaptation Notes  
17. Risk Matrix and Scenarios  
18. Human Impact Narrative  
19. Compliance Score  
20. Confidence Report  
21. Sources / Traceability (or `Evidence Needed` in source-limited mode)  
22. JSON Export Block

## Compliance Score Format

```text
Compliance Score: XX/100
✅ GESI indicators present
✅ SDG alignment mapped
⚠️ Sustainability needs strengthening
❌ Partner MoU missing
```

## JSON Output Skeleton

```json
{
  "project": {},
  "executive_summary": "",
  "concept_note": "",
  "strategic_context": {},
  "stakeholders": [],
  "rbm_chain": {},
  "theory_of_change": {},
  "logframe": [],
  "meal_plan": [],
  "gesi_analysis": {},
  "safeguarding": {},
  "budget": {},
  "co_financing": {},
  "sustainability": {},
  "partnerships": {},
  "donor_adaptation": {},
  "risks": [],
  "scenarios": [],
  "sdg_alignment": [],
  "narrative": "",
  "compliance_score": {},
  "confidence_report": {},
  "sources": []
}
```

## Limits

Do not:
- guarantee donor approval,
- replace legal/financial review,
- fabricate data, baselines, citations, or partner commitments.

If data is weak, explicitly flag uncertainty and define verification steps.

## Author

Vassiliy Lakhonin
