# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-08-28 (setup session — no issue work started yet)
**Chain status:** not started

## Done

- (nothing yet — protocol and fallback routine set up on 2026-08-28)

## In progress

- (nothing)

## Next step

- Start with issue **#2 — Data Leakage im Kreditausfall-Modell beheben**.
  Read the issue in full first; the drop-list of post-outcome columns is
  specified there.

## Open questions / decisions taken

- Raw dataset (`accepted_2007_to_2018Q4.csv`, ~1.6 GB from Kaggle) is not in
  the repo. If it cannot be downloaded in a cloud session, implement and
  document the code changes anyway and record here which steps still need a
  local run for verification.

## Known pitfalls

- Never force-push `claude/github-issues-review-3scsqi`.
- Issue PRs target the integration branch, not `main` — GitHub's `Closes #N`
  auto-close does not fire there; close issues manually after the merge.
- Every issue PR needs the reviewer-agent pass (see CLAUDE.md, "Per-issue
  code review") before merging; record mid-review state here if handing over.
- README metrics (AUC 0.9999) are known-wrong until #2 is done — update README
  only in #3, after the leakage fix.
