# Orchestration of epic #39 (remaining issues)

Recovery point for the orchestrator session. The canonical state is
`HANDOVER.md` on `main`; this file only records the orchestration itself.

## Procedure per issue

1. Sonnet worker implements the issue on `issue-NN-<slug>` off `main`,
   opens a PR against `main`, updates `HANDOVER.md` in the PR.
2. Sonnet reviewer reviews the PR (CLAUDE.md, "Reviewer session"), fixes
   clear-cut findings, records the review in `HANDOVER.md`.
3. Orchestrator checks the report and CI, merges, closes the issue,
   deletes the feature branch, starts the next worker.

Every agent commits and pushes after each completed unit of work, so nothing
is lost when a session ends unexpectedly.

## Order and state

| Issue | Content | State |
|---|---|---|
| #42 | Glossary | merged (PR #53, d6cc1a0), issue closed |
| #43 | Start page | merged (PR #54, 02d63b2); LinkedIn/website links are added in the #34 branch (own commit) |
| #32 | Applicant calculator, incl. derived coupled features | merged (PR #55, b9aa721) |
| #33 | Single-score explanation | merged (PR #56, 7478562) |
| #34 | Model quality (+ start page links, commit 44c70a2) | merged (PR #57, 5b942b0) |
| #35 | Cut-off and expected loss | merged (PR #58, 8126a7a) |
| #36 | Model card | merged (PR #59, 21f228a) |
| #37 | Random forest vs. scorecard | merged (PR #60, a60091b) |
| #38 | Deployment | prep merged (PR #61, 86b7e75). App created at credit-risk-modeling-fs.streamlit.app but "Error installing requirements": reproduced with uv, ortools<9.12 (optbinning 0.21.0) has no cp313 wheel; resolves on 3.11 and 3.12. User must redeploy with Python 3.11. Then a final worker adds the link and closes #38 |

## Decisions

- The four coupled features (`funded_amnt`, `funded_amnt_inv`,
  `installment`, `fico_range_high`) are derived from the inputs in the
  scoring layer as part of #32 (own commit), as suggested in the review of
  #49.
- Issues run strictly in sequence: all pages touch `app/ui.py` and both
  locale files.
