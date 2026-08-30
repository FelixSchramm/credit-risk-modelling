# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-08-30 (fallback session, acted as worker for issue #2)
**Chain status:** issue #2 implemented, PR #16 open — review pending

## Done

- (nothing merged yet)

## In progress

- **Issue #2 — Data Leakage beheben:** implemented on branch
  `issue-02-fix-leakage`, **PR #16** targeting the integration branch.
  State: **review pending**.
  What the PR does: adds an explicit `post_outcome_cols` deny-list plus a
  prefix rule for `hardship_*`/`settlement_*` to the drop cell of
  `01_notebooks/prediction.ipynb`, adds a markdown section documenting the
  leakage finding, rewrites the closing "Comments on Findings" cell, and
  clears the stored outputs of the affected cells (they came from the leaky
  run).

## Next step

- Reviewer session for **PR #16** (review, fix clear-cut findings, merge,
  close issue #2 manually, archive handover), then worker session for the
  next issue in the plan: **#4 — Notebook-Logik nach `src/` auslagern**.

## Open questions / decisions taken

- **Raw dataset not available in the cloud session.** `02_data/raw/` contains
  only `.gitkeep`, the ~1.6 GB Kaggle CSV is not in the repo and cannot be
  downloaded without Kaggle credentials. Consequences for issue #2:
  - The corrected model could **not** be retrained, so the new realistic AUC
    is **not yet measured**. Issue #2 expects roughly 0.65-0.75.
  - **Open task for a local run:** execute the notebook top to bottom on the
    full dataset, record the new AUC / precision / recall / confusion matrix,
    and only then update the README metrics (that is issue #3).
  - Instead of a real run, the drop logic was verified against a synthetic
    DataFrame with the LendingClub column names: no post-outcome column
    survives, no legitimate origination column (`fico_range_low/high`, `dti`,
    `int_rate`, `term`, ...) is removed by mistake.
- Decision: stored outputs of the cells from the drop cell onwards were
  cleared rather than left in place — they showed the AUC 0.9999 of the leaky
  run and would have contradicted the corrected code. Clearing all remaining
  notebook artifacts is issue #5.
- Observation, not acted on (out of scope for #2): `issue_year` stays in the
  feature set. It is known at origination, so it is not leakage, but as a
  time index it can make the model learn the vintage rather than the risk —
  worth a look in #5 or #10.

- **Successor session could NOT be spawned.** This session ran as the
  scheduled fallback routine and had only the `github` MCP server available —
  the `claude-code-remote` tools (`create_session` / `create_trigger`) that
  CLAUDE.md step 6 requires were not connected, so the reviewer session for
  PR #16 could not be started. Safety net: the fallback routine runs twice a
  day (06:00/18:00 UTC) and, per "Fallback sessions", the next firing will
  read this file, see "PR #16 review pending" and adopt the reviewer role. If
  the relay is meant to run at full speed, the environment of the relay
  sessions needs the claude-code-remote MCP server attached.

## Known pitfalls

- Never force-push `claude/github-issues-review-3scsqi`.
- Issue PRs target the integration branch, not `main` — GitHub's `Closes #N`
  auto-close does not fire there; the reviewer closes issues manually after
  the merge.
- Every issue PR is merged only by a reviewer session (see CLAUDE.md,
  "Reviewer session"); always record the open PR number and its state
  (review pending / findings open / merged) here.
- README metrics (AUC 0.9999) are known-wrong. They stay wrong until the
  notebook has actually been re-run on the full dataset locally — do not put
  a guessed number into the README in #3.
