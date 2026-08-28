# CLAUDE.md

Compact project context for Claude Code. Keep this short and current.

Coding standards and behavioral guidelines live in
@CLAUDE_CODING_RULES.md — they apply to every session and every role.

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
starting it.

Note: the raw dataset (`accepted_2007_to_2018Q4.csv`) is NOT in the repo and
may not be available in a fresh cloud session. Issues that need the real data
(model retraining) should degrade gracefully: implement + document the code
path, and record in HANDOVER.md if a step could not be executed against the
full dataset so it can be verified locally.

## Autonomous session protocol (relay of single-purpose sessions)

This repo is worked on autonomously by a relay of Claude Code web sessions,
each with exactly one job:

- **Worker session:** implements exactly one issue and opens its PR, then
  spawns the reviewer.
- **Reviewer session:** reviews that PR, fixes clear findings itself, merges,
  then spawns the next worker.

A fallback routine (2x daily, 06:00/18:00 UTC) restarts the relay if it
stalls (>12h without a commit while issues remain open).

### Rules for every session

1. **Branches:** `claude/github-issues-review-3scsqi` is the integration
   branch (never force-push it). Each issue lives on its own feature branch
   `issue-NN-<short-slug>` off the integration branch. When all issues are
   done, the final session proposes a PR from the integration branch to
   `main` for the user to review.
2. **Session start:** fetch + check out the integration branch, read this
   file, `CLAUDE_CODING_RULES.md` and `HANDOVER.md`, then do the one job
   your role defines.
3. **Commit early, push often:** commit and push after every completed unit
   of work. Git history + `HANDOVER.md` are the only handover channel —
   nothing outside pushed commits survives a session.
4. **Keep `HANDOVER.md` current:** update it before ending your session
   (done / in progress / next step / open PR + its state / pitfalls) and
   push it.
5. **90% budget rule:** note the `total_tokens` value at session start. When
   the remaining budget falls below **10% of that starting value**: do not
   start anything new, commit and push the current state, finalize
   `HANDOVER.md`, write an archive snapshot (see "Handover archive"), and
   schedule the successor **as a +5h one-shot trigger instead of an
   immediate spawn** (see step 6), then end the turn.
6. **Spawning the successor:** use the claude-code-remote MCP tools.
   - Normal case (budget fine): `create_session` in the same environment —
     the successor starts immediately.
   - 90% rule hit: `create_trigger` with `run_once_at` = now + 5 hours,
     `create_new_session_on_fire: true`, `initiation: "human_schedule"`.
   - Either way the prompt must be fully standalone — use the templates
     below and fill in issue/PR numbers. Never end your session without
     having spawned or scheduled the successor (unless the relay is
     complete, see step 7).
7. **Completion:** when all issues #2-#13 are done, do NOT spawn a
   successor. Update `HANDOVER.md` to state the relay is finished, write a
   final archive snapshot (reason: "all issues done"), and ask the user in
   the session summary whether to open the PR to `main` and disable the
   fallback routine.

### Worker session (one issue)

1. Identify the next open issue N from `HANDOVER.md`; read issue N in full.
2. Create `issue-NN-<short-slug>` off the integration branch.
3. Implement the issue following `CLAUDE_CODING_RULES.md`; commit/push per
   unit of work.
4. Open a PR targeting `claude/github-issues-review-3scsqi`.
   Note: `Closes #N` does NOT auto-close issues for PRs into a non-default
   branch — the reviewer closes the issue manually after the merge.
5. Update `HANDOVER.md` (PR number, state: "review pending"), push it to the
   integration branch.
6. Spawn the reviewer session (worker → reviewer template) and end the turn.

### Reviewer session (one PR)

1. Review the full PR diff with fresh eyes. Three questions, in priority
   order:
   1. **Is the code as simple and as short as possible?** Flag
      overcomplication, speculative abstraction, unnecessary
      configurability, dead code, anything where 50 lines would do the job
      of 200.
   2. **Does hand-written code reimplement something an established package
      already provides** (pandas, numpy, scikit-learn, scipy, shap,
      optbinning, ...)? Prefer the package; flag the reinvention.
   3. **Are the rules in `CLAUDE_CODING_RULES.md` followed?** Especially
      "Simplicity First" and "Surgical Changes".
2. Post the findings as a PR review with inline comments (github MCP tools),
   most severe first. If there is nothing to flag, say so explicitly in a
   short review — do not invent findings.
3. **Fix only clear-cut findings yourself** (simplifications, package
   replacements, style/docstring fixes) — commit and push them to the
   feature branch. **Structural or debatable findings are NOT implemented**:
   leave them as PR comments and record them in `HANDOVER.md` so the user or
   a later issue can pick them up.
4. Merge the PR into the integration branch (regular merge, no force-push),
   close issue #N manually with a comment linking the PR, delete the
   feature branch.
5. Update `HANDOVER.md` (issue N done, next issue), write an archive
   snapshot (reason: "issue #N merged").
6. Spawn the next worker session (reviewer → worker template) and end the
   turn — or, if all issues are done, follow "Completion" above.

### Handover archive

Snapshots of `HANDOVER.md` go to `docs/handovers/YYYY-MM-DD_HHMM.md`
(current UTC date/time), prefixed with one line
`# Handover <timestamp> — <reason>`. Write a snapshot:

- after every merge (reviewer, reason: "issue #N merged"),
- whenever the 90% rule triggers (reason: "90% budget reached"),
- at relay completion (reason: "all issues done").

Snapshots are append-only history — never edit or delete old ones. The
current working state always lives in `/HANDOVER.md` at the repo root.

### Fallback sessions

If you were started by the fallback routine: read `HANDOVER.md` and adopt
the role that matches the recorded state — an open PR with review pending
makes you the reviewer; otherwise you are the worker for the next open
issue. Then follow that role's protocol above, including spawning the
successor.

### Prompt templates

Worker → reviewer:

> Continue the autonomous relay on FelixSchramm/credit-risk-modelling as the
> REVIEWER session. Fetch and check out branch
> `claude/github-issues-review-3scsqi`, read CLAUDE.md (section "Autonomous
> session protocol"), CLAUDE_CODING_RULES.md and HANDOVER.md. Review PR #<PR>
> for issue #<N> following the "Reviewer session" protocol: post a PR review
> (simplicity first, package reuse, coding-rules compliance), fix only
> clear-cut findings yourself, merge, close issue #<N>, archive the handover,
> then spawn the next worker session. Apply the 90% budget rule.

Reviewer → worker:

> Continue the autonomous relay on FelixSchramm/credit-risk-modelling as the
> WORKER session. Fetch and check out branch
> `claude/github-issues-review-3scsqi`, read CLAUDE.md (section "Autonomous
> session protocol"), CLAUDE_CODING_RULES.md and HANDOVER.md. Implement issue
> #<N> on a feature branch following the "Worker session" protocol, open the
> PR, update HANDOVER.md, then spawn the reviewer session. Apply the 90%
> budget rule.
