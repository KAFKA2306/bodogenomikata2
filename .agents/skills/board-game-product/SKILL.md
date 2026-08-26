---
name: board-game-product
description: Build trustworthy board-game product features with source-backed rules, fail-loud anti-fabrication constraints, minimal duplication, and end-to-end verification.
---

# Board Game Product

## Goal

Produce useful player-facing board-game features while reducing duplicated agent instructions, dependencies, manual work, and hidden failure paths.

## Source authority

- Prefer current publisher/designer rules, FAQ, and errata for externally verifiable facts.
- Preserve edition, language, revision, expansion, sequel, and regional boundaries.
- Keep verified rules separate from summaries, translations, interpretations, and generated text.
- Never reconstruct missing rules from model memory or plausible completion.
- Missing or ambiguous authority must become an explicit blocked/failure state.

## Mandatory anti-fabrication constraints

- Keep one established networking path. Do not add parallel `httpx`, `requests`, `aiohttp`, `curl_cffi`, or equivalent clients.
- Do not add broad `try-except`, silent fallback, default substitution, or defensive branches that convert missing/invalid evidence into apparent success.
- Do not invent defaults for missing facts, parse failures, identity mismatches, or source ambiguity.
- Avoid manual shadow mappings when schema/runtime validation can remain authoritative.
- Error handling may add context, typed failure states, or cleanup, but must preserve failure visibility.

The purpose is not stylistic minimalism. Unsupported claims must be unable to survive the pipeline as accepted facts.

## Implementation

Use existing repository commands, data structures, and shared validation before creating helpers, workflows, schemas, dependencies, or tool-specific skills.

AI providers and external content tools are replaceable implementation details. Do not make Gemini, NotebookLM, Playwright browser automation, or another provider a source of factual authority.

Prefer shared structured validation over game-specific scripts. Remove superseded instructions instead of keeping multiple overlapping skills.

## Verification

Validate the smallest affected path first, then broader repository checks. For public changes, verify the actual player-facing output after deployment rather than treating a successful build as completion.
