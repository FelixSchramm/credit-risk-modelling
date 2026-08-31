# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-08-31 18:00 UTC (fallback session, acted as worker for issue #4)
**Chain status:** issue #4 implemented, PR #17 open — next up: reviewer session
for PR #17

## Done

- **Issue #2 — Data Leakage beheben:** PR #16 reviewed and merged into
  `claude/github-issues-review-3scsqi` (merge commit `485b167`), issue #2
  closed manually with a comment linking the PR.
  Review result: no structural findings. One minor finding was fixed by the
  reviewer directly (commit `0c28fb5`): the closing "Comments on Findings"
  cell described the corrected metrics as if they had been measured, although
  the outputs were cleared and the model was never retrained. It now names the
  outstanding local run and phrases 0.65-0.75 as the expectation.

## In progress

- **Issue #4 — Notebook-Logik nach `src/` auslagern:** implemented on branch
  `issue-04-src-modules`, **PR #17 open, state: review pending**.
  `03_src/` renamed to `src/` (a package name must not start with a digit);
  the notebook logic now lives in `src/data_processing.py`, `src/features.py`,
  `src/train.py` and `src/evaluate.py`; the notebook imports them via
  `sys.path.insert(0, "..")`. EDA, plots and the narrative stay in the
  notebook. README folder structure updated to the real module names.

## Next step

- Reviewer session for **PR #17** (issue #4). After the merge the plan order
  is #5 → #8 → #9 → #3 → #7 → #6 → #10 → #11 → #12 → #13.

## Open questions / decisions taken

- **Raw dataset not available in cloud sessions.** `02_data/raw/` contains only
  `.gitkeep`; the ~1.6 GB Kaggle CSV is not in the repo and cannot be
  downloaded without credentials.
  - **Open task for a local run (carried over from #2):** execute
    `01_notebooks/prediction.ipynb` top to bottom on the full dataset, record
    the new ROC AUC / precision / recall / confusion matrix. Only then may the
    README metrics be updated (that is issue #3).
  - Issue #2's acceptance criteria 2 ("Restart & Run All") and 4 ("README
    consistent") are therefore **not verified**. The drop logic was verified
    against a synthetic DataFrame with the LendingClub column names instead.
  - Every following issue that needs real data must degrade the same way:
    implement and document the code path, record the unverified step here.
  - Issue #4 was verified the same way: a synthetic CSV with the LendingClub
    column names was written to `02_data/raw/` and the notebook was executed
    top to bottom with `nbclient` — it runs through, but the metrics of that
    run are meaningless and were not stored in the notebook. The real
    "Restart & Run All" on the full dataset is still outstanding.
- Observation from issue #2, not acted on: `issue_year` stays in the feature
  set. It is known at origination, so it is not leakage, but as a time index it
  can make the model learn the vintage rather than the risk — worth a look in
  #5 or #10.
- Notebook outputs are currently inconsistent: the cells from the drop cell
  onwards have cleared outputs, the earlier EDA cells still carry stored
  outputs and execution counts from the leaky run. Cleaning all of this up is
  issue #5.

- **Successor sessions still cannot be spawned automatically.** All three
  fallback sessions so far (2026-08-30, 2026-08-31 06:00, 2026-08-31 18:00)
  had only the `github` MCP server
  available; the `claude-code-remote` tools (`create_session` /
  `create_trigger`) that CLAUDE.md step 6 requires are not connected in this
  environment. `CronCreate` is no substitute — it is session-only and dies
  with the session. Consequence: the relay advances at most one step per
  fallback firing (06:00/18:00 UTC). To run at full speed, the relay
  environment needs the claude-code-remote MCP server attached.
  - Consequence for the next session: nothing is running. Whoever starts
    next takes the role that HANDOVER.md records here, not the one the
    previous session was supposed to spawn.

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
- **Deleting a remote branch fails in these sessions** (`git push --delete`
  and the `:refs/heads/...` form both abort with "the remote end hung up").
  The merged branch `issue-02-fix-leakage` is therefore still on the remote
  and has to be deleted by hand in the GitHub UI. Do not spend time retrying.
