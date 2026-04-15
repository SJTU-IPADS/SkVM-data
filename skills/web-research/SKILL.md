---
name: web-research
description: Web search, data extraction, and structured report generation from online sources.
---

# Web Research

## Research Workflow

1. **Define scope** — Identify what information is needed and from what sources
2. **Search & fetch** — Use web_fetch to gather data from relevant URLs
3. **Extract & validate** — Pull specific data points, cross-reference sources
4. **Synthesize** — Combine findings into a structured report
5. **Save** — Write results to a well-formatted file

## Web Fetching Strategies

### API-first approach
Many sites offer structured JSON at predictable URLs:
- `https://wttr.in/City?format=j1` — weather data
- `https://api.example.com/v1/data` — REST APIs
- Add `?format=json` or accept headers for JSON

### Fallback: HTML parsing
When no API exists, fetch the HTML and extract data using patterns in the response text.

## Structured Reports

When creating research reports, use this structure:

```markdown
# [Topic] Research Report

## Executive Summary
[2-3 sentence overview of key findings]

## Findings
### [Category 1]
- Key point with supporting detail
- Data point with source

### [Category 2]
...

## Comparison Table
| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Feature 1 | ... | ... | ... |

## Market Trends / Analysis
[Broader context and patterns]

## Conclusion
[Actionable takeaways]
```

## Data Accuracy

- Prefer primary sources over aggregators
- Note when information may be outdated
- Use multiple sources for critical facts
- Clearly attribute sources when available
- If web access is unavailable, use knowledge but note the limitation
