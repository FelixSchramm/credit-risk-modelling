# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-09-01 06:35 UTC (fallback session: reviewer for PR #17, then worker for issue #5)
**Chain status:** issue #4 done and merged; issue #5 implemented, PR #18 open —
next up: reviewer session for PR #18

## Done

- **Issue #2 — Data Leakage beheben:** PR #16 reviewed and merged into
  `claude/github-issues-review-3scsqi` (merge commit `485b167`), issue #2
  closed manually with a comment linking the PR.
  Review result: no structural findings. One minor finding was fixed by the
  reviewer directly (commit `0c28fb5`): the closing "Comments on Findings"
  cell described the corrected metrics as if they had been measured, although
  the outputs were cleared and the model was never retrained. It now names the
  outstanding local run and phrases 0.65-0.75 as the expectation.
- **Issue #4 — Notebook-Logik nach `src/` auslagern:** PR #17 reviewed and
  merged (merge commit `c4d72ac`), issue #4 closed manually.
  `03_src/` is gone; the logic now lives in `src/data_processing.py`,
  `src/features.py`, `src/train.py` and `src/evaluate.py`, and the notebook
  imports them via `sys.path.insert(0, "..")`.
  Review result: the refactor was verified cell by cell against the old
  notebook and is faithful; `black` and `ruff` pass on `src/`; the full chain
  was smoke-tested end to end against a synthetic LendingClub-shaped frame.
  Two minor findings fixed by the reviewer (commit `c012f13`): `joblib` was
  imported by `src/train.py` but missing from `requirements.txt` (it only
  resolved transitively via scikit-learn), and the README folder structure
  still named `random_forest_v1.joblib` while the notebook writes
  `random_forest.joblib`.

## In progress

- **Issue #5 — Notebook-Reproduzierbarkeit / Kurs-Artefakte:** implemented on
  branch `issue-05-notebook-reproducibility`, **PR #18 open, state: review
  pending**. Only `01_notebooks/prediction.ipynb` is touched.
  Course markers (`# (b)`, `# (q)`, `# (s)`, ...) replaced by comments that say
  WHY; `df.info` fixed to `df.info()`; the EDA cells got their own section and
  the sections are renumbered 1-5; each section markdown cell now states the
  decision behind the code; the title cell documents how to run the notebook.
  Two cleanups the goal required: the duplicated matplotlib/seaborn imports in
  two adjacent EDA cells moved into the first cell, and the
  `try/except FileNotFoundError` around the CSV load removed (it turned one
  clear error into a `NameError` cascade).
  **All code cells are committed unexecuted.** See the decision below.

## Next step

- Reviewer session for **PR #18** (issue #5). After the merge the plan order
  is #8 → #9 → #3 → #7 → #6 → #10 → #11 → #12 → #13.

## Open questions / decisions taken

- **Raw dataset not available in cloud sessions.** `02_data/raw/` contains only
  `.gitkeep`; the ~1.6 GB Kaggle CSV is not in the repo and cannot be
  downloaded without credentials.
  - **Open task for a local run (carried over from #2 and #4):** execute
    `01_notebooks/prediction.ipynb` top to bottom on the full dataset, record
    the new ROC AUC / precision / recall / confusion matrix. Only then may the
    README metrics be updated (that is issue #3).
  - Issue #2's acceptance criteria 2 ("Restart & Run All") and 4 ("README
    consistent") are therefore **not verified**. The drop logic was verified
    against a synthetic DataFrame with the LendingClub column names instead.
  - Issue #4 was verified the same way (synthetic CSV + `nbclient` run by the
    worker, synthetic end-to-end call chain by the reviewer). The real
    "Restart & Run All" on the full dataset is still outstanding.
  - Every following issue that needs real data must degrade the same way:
    implement and document the code path, record the unverified step here.
- **Decision taken in issue #5: the notebook is committed with empty outputs.**
  Acceptance criterion 1 asks for strictly monotonic `execution_count` values,
  which only a real execution produces — and the only data available in a cloud
  session is synthetic. Committing the outputs of a synthetic run would put
  meaningless plots and fabricated metrics into a portfolio repo, so the
  conservative option was chosen: every code cell reset to unexecuted. The
  structure was verified instead, by executing a *copy* of the notebook with
  `nbclient` against a synthetic LendingClub-shaped CSV (3000 rows, all columns
  the notebook and `src/` touch) — all 18 code cells run without error and
  produce counts 1-18; the copy was not committed.
  **Open task, local:** run
  `jupyter nbconvert --to notebook --execute --inplace 01_notebooks/prediction.ipynb`
  on the real CSV. That single run closes the last open point of #5 and
  produces the metrics that issues #2 and #3 are waiting for.
- **Open finding from the PR #17 review, deliberately NOT implemented there
  (structural, belongs to #9/#10):** `split_and_scale` in `src/train.py`
  returns `StandardScaler.fit_transform` output, i.e. numpy arrays, so the
  feature names are lost the moment the data leaves the function. The notebook
  also never uses the returned `scaler`. Harmless today, but issue #9 (SHAP)
  and issue #10 (WOE/IV scorecard) both need feature names for readable
  output. Fix it there with `sklearn.set_config(transform_output="pandas")` or
  by wrapping split + scale in a `Pipeline`/`ColumnTransformer`.
- Observation from issue #2, not acted on: `issue_year` stays in the feature
  set. It is known at origination, so it is not leakage, but as a time index it
  can make the model learn the vintage rather than the risk — worth a look in
  #5 or #10.
- Notebook outputs are currently inconsistent: the cells from the drop cell
  onwards have cleared outputs, the earlier EDA cells still carry stored
  outputs and execution counts from the leaky run. Cleaning all of this up is
  issue #5.

- **Successor sessions still cannot be spawned automatically.** All four
  fallback sessions so far (2026-08-30, 2026-08-31 06:00, 2026-08-31 18:00,
  2026-09-01 06:00) had only the `github` MCP server available; the
  `claude-code-remote` tools (`create_session` / `create_trigger`) that
  CLAUDE.md step 6 requires are not connected in this environment.
  `CronCreate` is no substitute — it is session-only and dies with the
  session. Consequence: the relay advances at most one step per fallback
  firing (06:00/18:00 UTC). To run at full speed, the relay environment needs
  the claude-code-remote MCP server attached.
  - Consequence for the next session: nothing is running. Whoever starts
    next takes the role that HANDOVER.md records here, not the one the
    previous session was supposed to spawn.
  - Because of this, the 2026-09-01 06:00 fallback session did the reviewer
    job for PR #17 **and then continued as the worker for issue #5 in the
    same session** rather than ending with an unspawnable successor. The
    90% budget rule still applies and was not close to being hit.

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
  The merged branches `issue-02-fix-leakage` and `issue-04-src-modules` are
  therefore still on the remote and have to be deleted by hand in the GitHub
  UI. Do not spend time retrying.
