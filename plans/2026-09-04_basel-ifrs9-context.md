# Basel / IFRS 9 / FINMA context (issue #11)

## Goal

Place the project in the regulatory context PD models are actually used in,
without claiming it meets any regulatory requirement.

## What already exists

Three pieces of the issue are already in the notebook and must not be
duplicated:

- Section 5 puts the AUC/Gini/KS in relation to the usual retail range
  (Gini 0.30-0.50, KS 0.20-0.35) — that is step 2 of the issue, delivered by #8.
- The calibration cell already states `ECL = PD x LGD x EAD` and why
  `class_weight="balanced"` makes the output unusable as a PD (#8).
- Section 7 already contrasts an IRB rating system with an IFRS 9 PD as the two
  cases where interpretability outweighs discrimination (#10).

What is missing is the framing itself: which of the three Basel inputs this
project builds, how the target and the horizon differ from the regulatory
definitions, how IFRS 9 staging uses a PD, the Swiss implementation, and an
explicit list of what makes this not a rating system.

## Steps

1. `README.md`: new section "Regulatory context" between "Results" and
   "License" — Basel PD/LGD/EAD split, the two mismatches (default definition,
   horizon), IFRS 9 ECL and stages 1/2/3, PIT vs TTC, FINMA implementation,
   then "What this project is not".
   -> verify: no sentence claims compliance; every regulatory statement is
   either definitional or hedged.
2. `01_notebooks/prediction.ipynb`: one scope paragraph in the intro cell,
   pointing at the README section rather than repeating it.
   -> verify: a copy of the notebook still executes top to bottom.
3. Carried over from #10: `tests/test_train.py` is missing from the README
   layout block. One line, disclosed in the PR as out of scope.

## Decisions

- No new "section 8" in the notebook. The regulatory material belongs in the
  README; the notebook gets the scope statement only, so the two do not drift
  apart.
- `plans/` is created here because `CLAUDE_CODING_RULES.md` requires it.
  Issues #2-#10 did not do this — recorded in `HANDOVER.md` for the user.
