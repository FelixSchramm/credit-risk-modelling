# CLAUDE.md

Compact project context for Claude Code. Keep this short and current.

## What this is

Credit risk portfolio project: a probability-of-default (PD) model on the
LendingClub dataset (2007-2018Q4). Part of an application portfolio for data
science roles in the Swiss banking sector. The single notebook lives in
`01_notebooks/prediction.ipynb`; `docs/REPO_REVIEW.md` contains the full repo
review that produced the work plan.

## Work plan

GitHub issues #2-#13 are the work plan (issue #14 defines the git workflow).
Work them in this order:

**#2 (leakage fix) → #4 (modularize src/) → #5 (notebook reproducibility) →
#8 (KS/Gini/calibration) → #9 (SHAP) → #3 (README) → #7 (pinning/LICENSE) →
#6 (tests) → #10 (WOE/IV scorecard) → #11 (Basel/IFRS9/FINMA context) →
#12 (repo hygiene) → #13 (CI)**

Each issue is written to be self-contained. Read the issue in full before
starting it. Close issues via `Closes #N` in the merge/PR description or by
referencing them in the commit message.

Note: the raw dataset (`accepted_2007_to_2018Q4.csv`) is NOT in the repo and
may not be available in a fresh cloud session. Issues that need the real data
(model retraining) should degrade gracefully: implement + document the code
path, and record in HANDOVER.md if a step could not be executed against the
full dataset so it can be verified locally.

## Autonomous session protocol (session chain)

This repo is worked on by a chain of Claude Code web sessions that hand over
to each other because of the 5-hour usage windows. Every session MUST follow
this protocol:

1. **Branches & PRs:** `claude/github-issues-review-3scsqi` is the
   integration branch (fetch + check it out first; never force-push it).
   Each issue is worked on its own feature branch `issue-NN-<short-slug>`
   branched off the integration branch and merged back via a PR after a
   mandatory code review (see "Per-issue code review" below). When everything
   is done, the final session proposes a PR from the integration branch to
   `main` for the user to review.
2. **Start of session:** read this file and `HANDOVER.md`, then continue with
   the next open step recorded there.
3. **Commit early, push often:** commit and push after every completed unit of
   work (at the latest after every finished issue; for larger issues, after
   each coherent sub-step). Git history + `HANDOVER.md` are the only handover
   channel — nothing outside pushed commits survives a session.
4. **Keep `HANDOVER.md` current:** update it after every completed unit
   (done / in progress / next step / known pitfalls), commit it together with
   the work.
5. **90% budget rule:** note the `total_tokens` value at session start. When
   the remaining budget falls below **10% of that starting value**:
   - do not start anything new,
   - commit and push the current state,
   - finalize `HANDOVER.md`,
   - archive the handover (step 5a),
   - schedule the successor session (step 6),
   - end the turn with a short status summary.

   **5a. Handover archive:** copy the finalized `HANDOVER.md` to
   `docs/handovers/YYYY-MM-DD_HHMM.md` (current UTC date and time), add a
   first line `# Handover <timestamp> — session ended: <reason>` (reason:
   "90% budget reached", "all issues done", or "fallback restart"), and
   commit + push it together with the updated `HANDOVER.md`. One snapshot
   per session, written only at handover time — never edit old snapshots.
6. **Scheduling the successor:** create a one-shot trigger via the
   claude-code-remote MCP tool `create_trigger` with:
   - `run_once_at` = now + 5 hours,
   - `create_new_session_on_fire: true`,
   - `initiation: "human_schedule"`,
   - a fully standalone prompt, e.g.:
     > "Continue the autonomous work chain on FelixSchramm/credit-risk-modelling.
     > Fetch and check out branch `claude/github-issues-review-3scsqi`, read
     > CLAUDE.md (section 'Autonomous session protocol') and HANDOVER.md, and
     > continue with the next open step. Follow the protocol including the 90%
     > handover rule."
7. **Completion:** when all issues #2-#13 are done, do NOT schedule another
   session. Update `HANDOVER.md` to state the chain is finished, archive it
   per step 5a (reason: "all issues done"), and ask the user (in the session
   summary) whether to open the PR to `main` and disable the daily fallback
   routine.

A daily fallback routine (Claude Code web "Routine") independently checks the
branch and restarts the chain if it stalled (>12h without a commit while
issues remain open). If you are that fallback session, follow the same
protocol above.

### Per-issue code review (mandatory before every merge)

1. When an issue's implementation is complete on its feature branch: push it
   and open a PR targeting `claude/github-issues-review-3scsqi`.
   Note: `Closes #N` does NOT auto-close issues for PRs into a non-default
   branch — after the merge, close issue #N manually with a comment linking
   the PR.
2. Spawn a **fresh reviewer agent** (Agent tool, clean context — it must not
   inherit the author's reasoning) with this mandate:
   - Review the full PR diff. Three questions, in priority order:
     1. **Is the code as simple and as short as possible?** Flag
        overcomplication, speculative abstraction, unnecessary
        configurability, dead code, anything where 50 lines would do the
        job of 200.
     2. **Does hand-written code reimplement something an established
        package already provides** (pandas, numpy, scikit-learn, scipy,
        shap, optbinning, ...)? Prefer the package; flag the reinvention.
     3. **Are the CLAUDE.md rules followed?** Coding standards (PEP 8,
        snake_case, reST docstrings, black), commit conventions, and the
        Behavioral Guidelines — especially "Simplicity First" and
        "Surgical Changes".
   - Post the findings as a PR review with inline comments (github MCP
     tools), most severe first. If there is nothing to flag, say so
     explicitly in a short review — do not invent findings.
3. The working session addresses **every** finding: fix and push, or reply
   on the thread with a short justification why not. Re-request a review
   pass only after substantial rework, not for trivial fixes.
4. Merge the PR into the integration branch (regular merge, no force-push),
   close issue #N manually, delete the feature branch, update `HANDOVER.md`.
5. If the 90% rule triggers mid-review-cycle: record the PR number and its
   exact state (review pending / findings open / ready to merge) in
   `HANDOVER.md` so the successor session resumes exactly there.

# AI Coding Instructions

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
- Chain work lives on `claude/github-issues-review-3scsqi`; reference the
  issue number in each commit (e.g. `fix: drop post-outcome leakage columns (#2)`).
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
