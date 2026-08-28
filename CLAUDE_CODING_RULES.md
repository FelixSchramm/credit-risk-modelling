# Claude Coding Rules

Coding standards and behavioral guidelines for all work in this repo.
Referenced from CLAUDE.md; applies to every session and every role.

## General Coding Standards
- Write code in English, as easy as possible and do not use emojis.
- Follow PEP 8 coding style for Python
- Variable and function names: use snake_case
- Use reStructuredText (reST) format for all Python docstrings.
- Format: Use `:param name: description` and `:return: description`.
- Python code needs to be formatted with `black`; linting with `ruff`
  (see issue #13).

## Commit & Branching Conventions
- Use conventional commits (https://www.conventionalcommits.org/)
- Feature branches per issue: `issue-NN-<short-slug>`, branched off the
  integration branch `claude/github-issues-review-3scsqi`.
- Reference the issue number in each commit
  (e.g. `fix: drop post-outcome leakage columns (#2)`).
- Commit messages explain the WHY in the body when it is not obvious.
- Keep commits small and focused: one commit = one logical change.

## Documentation Requirements
- Every code module needs a Markdown file or a module-level docstring.
- Every function needs a docstring.
- Inline comments: Focus on WHY, not WHAT

## Plans
- Implementierungs-/Ausführpläne werden **immer** im Ordner `plans/` abgelegt.
- `plans/` ist **nicht** in `.gitignore` und wird ins Repo committet (nicht nur lokal).
- Dateiname-Format: `YYYY-MM-DD_name.md` (aktuelles Datum + kurzer Slug),
  z. B. `2026-06-25_api-anbindung.md`.

# Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- In autonomous chain sessions nobody can answer: record the open question and
  your chosen assumption in `HANDOVER.md` instead, pick the conservative
  option, and continue.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
