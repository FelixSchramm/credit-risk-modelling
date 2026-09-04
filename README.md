# Credit Risk Modelling

A probability-of-default (PD) model on the historical LendingClub dataset
(2007-2018Q4). The task is to estimate, at the moment of application, how likely
a loan is to end as "Charged Off" — the question a credit risk function answers
before the money leaves the bank.

## Dataset

LendingClub accepted loan data, ~2.2 million records with 151 columns covering
borrower attributes, loan characteristics and repayment outcomes.

- **Source:** [LendingClub accepted loans (2007-2018Q4) on Kaggle](https://www.kaggle.com/datasets/wordsforthewise/lending-club)
- **Target:** `loan_status`, reduced to a binary outcome — `0` = Fully Paid,
  `1` = Charged Off. Loans that are still running are excluded: their outcome is
  not yet known, and labelling them as non-defaults would be wrong.
- **Window:** the analysis is restricted to loans issued 2015-2018. LendingClub's
  volume grew by orders of magnitude over the full history and its lending
  standards changed with it, so a recent, homogeneous window is closer to the
  population a scorecard would actually be applied to.

The raw CSV is ~1.6 GB and is **not** part of this repository (see
`.gitignore`); it has to be downloaded separately, see "How to run".

## How to run

**1. Get the data.** Download the dataset from the Kaggle link above and place
`accepted_2007_to_2018Q4.csv` in `02_data/raw/`. Nothing else needs to be put
there — the notebook does all cleaning in memory.

**2. Set up the environment.** Python 3.11 or newer is required — the pinned
`pandas`, `numpy`, `scikit-learn`, `scipy`, `matplotlib` and `shap` releases all
declare `requires-python >= 3.11`. `requirements.txt` pins exact versions that
were resolved and run together, so the install reproduces a known-good
environment rather than whatever is current on PyPI. If you deviate from the
pins: `src/train.py` uses `StandardScaler.set_output`, which needs scikit-learn
1.2 or newer.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Run the notebook**, top to bottom ("Restart & Run All"):

```bash
jupyter notebook 01_notebooks/prediction.ipynb
```

Non-interactively, writing the outputs back into the notebook:

```bash
jupyter nbconvert --to notebook --execute --inplace 01_notebooks/prediction.ipynb
```

A full run takes a few minutes and a fair amount of memory, mostly for loading
the raw CSV. For a quick pass, the loading cell documents how to read only a
sample via `nrows`. The run writes one artefact, the fitted model, to
`04_models/random_forest.joblib` (untracked).

The notebook imports the pipeline from `src/`, so it has to be run from within
the repository — the import cell puts the project root on `sys.path` relative to
`01_notebooks/`.

**4. Run the tests** (optional, and independent of the dataset — they work on
small synthetic frames):

```bash
pytest
```

`pytest.ini` points at `tests/` and puts the repository root on the import
path, so the command works from the root without further arguments.

## Repository layout

```
credit-risk-modelling/
│
├── README.md
├── LICENSE
├── requirements.txt
├── pytest.ini
├── .gitignore
│
├── 01_notebooks/
│   └── prediction.ipynb          # the analysis: EDA, cleaning, model, evaluation
│
├── src/                          # importable pipeline used by the notebook
│   ├── __init__.py
│   ├── data_processing.py        # loading, target, leakage and NaN handling
│   ├── features.py               # term/emp_length conversion, one-hot encoding
│   ├── train.py                  # split, scaling, forest, scorecard, persistence
│   └── evaluate.py               # ROC AUC, Gini, KS, classification report
│
├── tests/                        # pytest suite for the src/ modules
│   ├── test_data_processing.py
│   ├── test_features.py
│   ├── test_evaluate.py
│   └── test_train.py
│
├── 02_data/
│   ├── raw/                      # place accepted_2007_to_2018Q4.csv here (untracked)
│   └── processed/                # unused; the pipeline keeps intermediates in memory
│
└── 04_models/                    # random_forest.joblib is written here (untracked)
```

`docs/`, `HANDOVER.md` and the `CLAUDE*.md` files at the repository root are
working material for the ongoing rework of this repository, not part of the
analysis.

## Workflow

The notebook follows the pipeline in `src/` section by section.

**1. Load data** — read the raw CSV.

**2. Exploratory analysis** — loan amount distribution, issuance volume per year
(which motivates the 2015-2018 window), correlation structure of the numeric
features.

**3. Cleaning and preprocessing** — keep only completed loans, drop columns with
more than 40% missing values, remove identifiers, free text and date columns,
then drop the rows that still carry NaNs.

This step also removes every **post-outcome column** — `total_pymnt`,
`recoveries`, `last_fico_range_*` and the rest of the fields that are only
filled once the loan has been repaid or has defaulted. They are the reason the
first version of this project reported an ROC AUC of 0.9999: they leak the
target into the features. The concrete lists live in `src/data_processing.py`.

**4. Feature engineering** — `term` and `emp_length` converted to numbers, the
remaining categorical columns one-hot encoded.

**5. Training and evaluation** — stratified 70/30 split, features standardized
with a scaler fitted on the training set only, `RandomForestClassifier` with
`class_weight="balanced"`. Evaluation reports ROC AUC, Gini and the KS statistic
for discrimination, plus a reliability diagram for calibration.

**6. Interpretability** — impurity-based feature importances, a SHAP summary
plot showing the direction and size of each feature's effect, and a waterfall
plot explaining one single high-risk loan in the form an adverse-action notice
would need.

**7. Scorecard benchmark** — the classical counterpart to the forest: features
binned by `optbinning`, replaced by their Weight of Evidence, selected on
Information Value and fed to a logistic regression. Both models are scored on
the same test rows, and the section closes with the trade-off a bank actually
faces between the two.

## Results

**The corrected model has not yet been run on the full dataset, so no metrics
are quoted here.**

Earlier versions of this README reported an ROC AUC of **0.9999**. That number
was an artefact of the data leakage described in step 3, not evidence of
predictive power — the model was reading columns that only exist because the
outcome was already known. It has been removed rather than restated.

What the corrected model should produce, once the notebook has been run against
the full dataset, is an ROC AUC in the region of **0.65-0.75** — a Gini of
roughly 0.30-0.50 in the form a scorecard validation would report it. That is
what a realistic PD model on LendingClub data achieves and what can be defended
in a credit risk context. This section will be filled in with the measured
values from that run.

Two things are worth stating up front about how those numbers should be read:

- **Recall on the "Charged Off" class** is the business-relevant quantity — it
  says how many of the loans that actually defaulted the model flags. Precision
  and recall trade off against each other, so the decision threshold follows
  from the cost of a missed default versus the cost of turning away a good
  customer; the model does not choose it.
- **Discrimination is not calibration.** With `class_weight="balanced"` the
  predicted probabilities are deliberately shifted and cannot be used as PDs in
  an expected-loss calculation without recalibration. That is acceptable for a
  ranking model, but it has to be said rather than assumed.

## Regulatory context

A PD model is not a free-standing object: in a bank it is an input to two
different regulatory calculations. Being precise about which part of them this
project touches is more useful than claiming to cover them.

### Basel: PD is one of three inputs, and only one is built here

Under the internal ratings-based (IRB) approach, the capital requirement for a
credit exposure comes out of a supervisory risk-weight function fed by three
estimates:

| Input | Question it answers | Here |
| --- | --- | --- |
| **PD** — probability of default | How likely is this borrower to default? | modelled |
| **LGD** — loss given default | If they default, what share of the exposure is lost? | not modelled |
| **EAD** — exposure at default | How much is outstanding at that moment? | not modelled |

Expected loss is `PD x LGD x EAD`, so a PD model on its own answers one third of
the question. For a fully drawn, amortising consumer loan EAD holds few
surprises — it is close to the outstanding balance. LGD is a genuine second
modelling problem: recovery on unsecured consumer debt is driven by collections
behaviour rather than by collateral, and this project does not attempt it.

Two further details decide how the numbers here may be read:

- **The default definition is not the regulatory one.** Basel defines default as
  90 days past due or unlikeliness to pay. The target here is LendingClub's
  `Charged Off` status, which is a write-off — a later and stricter event that a
  loan reaches long after it would already have counted as defaulted under the
  regulatory definition. The two are not interchangeable, and a model trained on
  one does not estimate the other.
- **The horizon is not the regulatory one.** An IRB PD is a one-year
  probability. This model is fitted at origination against the outcome over the
  loan's entire 36- or 60-month term, which makes it closer to a lifetime PD.

### IFRS 9: PD drives the loss allowance and the staging

IFRS 9 requires expected credit losses (ECL) to be recognised up front rather
than waiting for a loss event, and PD is the first factor of the same
`ECL = PD x LGD x EAD`, discounted. Which PD is required depends on the stage
the exposure sits in:

| Stage | Condition | Allowance |
| --- | --- | --- |
| 1 | no significant increase in credit risk since initial recognition | 12-month ECL |
| 2 | significant increase in credit risk, not credit-impaired | lifetime ECL |
| 3 | credit-impaired | lifetime ECL, interest on the net carrying amount |

The staging is where the two frameworks pull apart. IFRS 9 PDs are
point-in-time and forward-looking — conditioned on where the cycle currently is
and on macroeconomic scenarios. Basel IRB PDs are deliberately the opposite:
long-run averages, insensitive to the cycle by design. One estimate cannot be
both, which is why banks maintain separate PD models for the two purposes
instead of reusing one.

### Switzerland

FINMA implements the Basel framework through the Capital Adequacy Ordinance and
its circulars. In practice the standardised approach dominates: risk weights
come from a supervisory table and no internal PD enters the capital calculation
at all. Internal PD models under IRB require explicit FINMA approval and are
used by only a small number of institutions. Provisioning splits along a similar
line — banks reporting under IFRS apply IFRS 9, while banks reporting under the
Swiss accounting rules follow FINMA's own expected-loss provisioning
requirements, which are graduated by the category of the institution. The
vocabulary above therefore travels to a Swiss bank; which of the two regimes
that bank actually applies does not follow from it.

### What this project is not

A learning and portfolio project on a public historical dataset from a US
peer-to-peer lending platform. It is **not** a supervisory-approved model and
makes no claim to satisfy any regulatory requirement. Beyond the default
definition and the horizon above, it lacks essentially everything that turns a
classifier into a rating system:

- **No calibration.** `class_weight="balanced"` shifts the predicted
  probabilities away from the observed default rate on purpose (see "Results"),
  so the output ranks borrowers rather than estimating a PD level — and there is
  neither a through-the-cycle nor a point-in-time calibration on top, so it fits
  neither definition even after recalibration.
- **No rating system.** No grades, no masterscale, no margin of conservatism.
- **No validation in the supervisory sense.** No out-of-time testing, no
  independent validation function, no annual review, no ongoing monitoring, no
  override policy, no model documentation of the kind a validation unit means.
- **No representativeness argument.** One platform, one country, one time
  window. Nothing has been established about how that relates to any bank's own
  portfolio.

None of this makes the exercise idle. The steps are the ones a real PD project
runs: the leakage correction, the origination-only feature set, the scorecard
benchmark, the discrimination and calibration metrics. It does mean the result
is a demonstration of method, not a PD.

## License

MIT — see [LICENSE](LICENSE).
