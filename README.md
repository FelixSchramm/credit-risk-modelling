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

**2. Set up the environment.** Python 3.11 is what this was developed against;
3.10+ should work. `src/train.py` uses `StandardScaler.set_output`, which needs
scikit-learn 1.2 or newer.

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

## Repository layout

```
credit-risk-modelling/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── 01_notebooks/
│   └── prediction.ipynb          # the analysis: EDA, cleaning, model, evaluation
│
├── src/                          # importable pipeline used by the notebook
│   ├── __init__.py
│   ├── data_processing.py        # loading, target, leakage and NaN handling
│   ├── features.py               # term/emp_length conversion, one-hot encoding
│   ├── train.py                  # split, scaling, random forest, persistence
│   └── evaluate.py               # ROC AUC, Gini, KS, classification report
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
