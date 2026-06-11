---
name: Development Workflow v2
description: Cleanup-first, incremental commit strategy for bodoge-no-mikata v2
type: feedback
---

## Development Discipline

**Cleanup-First Approach:**
- Proactively remove unused files, stale code, temporary files, and legacy artifacts
- Do NOT accumulate technical debt — delete as you discover obsolete code
- Keep codebase lean and focused

**Why:** Minimize noise, reduce cognitive load, maintain code clarity. "Small" project size is a feature, not a constraint.

**How to apply:**
- Before adding new code, identify and delete dead code, old experiments, unused imports
- When refactoring, remove replaced patterns immediately
- Search for TODOs, FIXMEs, experiments dirs — clean them up
- Delete any file not actively used in v2 pipeline

## Incremental Commit Strategy

**Commit Frequency:**
- Smallest logical unit per commit (one feature, one fix, one cleanup)
- Aim for 5-10 commits per development session
- Commit after each passing test (TDD cycle)
- Commit after each successful deletion/cleanup

**Why:** Enables safe rollback, clear audit trail, context preservation. Small commits = easy bisect if something breaks.

**How to apply:**
- `git add <specific-file>` (avoid `git add .`)
- Commit message: verb + noun (e.g., "delete: remove unused experiments dir", "feat: add BGG fetcher", "test: verify slug generation")
- Push frequently (every 3-5 commits) to avoid losing work
- Use conventional commits format

## State Preservation

**Keep State Small:**
- After each commit, project should be in a "working" state (tests pass, no broken imports)
- If a task spans multiple logical pieces, split across multiple commits
- Never commit "partial work" or "works on my machine"

**Why:** Enables pairing, easy interruption/resume, safe team handoff.

**How to apply:**
- Run tests before each commit
- Verify imports/dependencies resolved
- Document commit message with task context if complex
