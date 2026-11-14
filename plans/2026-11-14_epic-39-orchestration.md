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
| #43 | Start page | merged (PR #54, 02d63b2); LinkedIn/website URLs from the user still pending |
| #32 | Applicant calculator, incl. derived coupled features | worker running |
| #33 | Single-score explanation | open |
| #34 | Model quality | open |
| #35 | Cut-off and expected loss | open |
| #36 | Model card | open |
| #37 | Random forest vs. scorecard | open |
| #38 | Deployment | needs the user's Streamlit Community Cloud account |

## Decisions

- The four coupled features (`funded_amnt`, `funded_amnt_inv`,
  `installment`, `fico_range_high`) are derived from the inputs in the
  scoring layer as part of #32 (own commit), as suggested in the review of
  #49.
- Issues run strictly in sequence: all pages touch `app/ui.py` and both
  locale files.
