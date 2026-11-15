"""Scoring layer of the dashboard: turn one application into a calibrated PD.

Pure functions on the bundle from :mod:`src.bundle`; no Streamlit import, so
everything here is covered by the tests. Also the explanations of one score
(SHAP for the forest, WOE contributions for the scorecard).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import shap

from src.features import convert_emp_length


def _check_input(user_input: dict[str, object], bundle: dict[str, object]) -> None:
    """Reject unknown fields and categories instead of ignoring them silently.

    :param user_input: Field name to entered value.
    :param bundle: Bundle with ``input_spec``.
    :return: None.
    :raises ValueError: If a field or a category is not part of ``input_spec``.
    """
    spec = bundle["input_spec"]
    unknown = sorted(set(user_input) - set(spec))
    if unknown:
        raise ValueError(f"Unknown input fields: {unknown}; allowed: {sorted(spec)}")
    for field, value in user_input.items():
        categories = spec[field].get("categories")
        if categories is not None and value not in categories:
            raise ValueError(f"Unknown category {value!r} for {field!r}")


def _coupled_columns(values: dict[str, object], term_months: int) -> dict[str, float]:
    """Derive the model columns that are tied to the inputs.

    Decision: ``funded_amnt``, ``funded_amnt_inv``, ``fico_range_high`` and
    ``installment`` are model features, but the user cannot enter them. Left at
    the portfolio median they would describe an impossible loan (e.g. a funded
    amount unequal to the loan amount), so they follow the effective values
    (input, else default): both amounts equal ``loan_amnt``, ``fico_range_high``
    is ``fico_range_low`` + 4, ``installment`` is the annuity of ``loan_amnt``
    at ``int_rate`` (percent per year) over ``term_months``.

    :param values: Effective values of one application, including the defaults.
    :param term_months: Term in months (36 or 60).
    :return: Derived value per column, only for columns that are in ``values``.
    """
    amount = values["loan_amnt"]
    monthly_rate = values["int_rate"] / 1200
    derived = {
        "funded_amnt": amount,
        "funded_amnt_inv": amount,
        "fico_range_high": values["fico_range_low"] + 4,
        "installment": amount * monthly_rate / (1 - (1 + monthly_rate) ** -term_months),
    }
    return {name: value for name, value in derived.items() if name in values}


def build_feature_vector(
    user_input: dict[str, object], bundle: dict[str, object]
) -> pd.DataFrame:
    """Build the one-row, unscaled feature vector of the forest.

    Everything the user does not enter stays at the portfolio default
    (``feature_defaults``). A categorical input sets its dummy column and
    clears the other dummies of the same group; the reference category (the
    one dropped by ``drop_first``) has no column, so all of its dummies are 0.

    :param user_input: Field name to entered value; ``term`` and ``emp_length``
        as text like in the raw data, e.g. ``" 36 months"``.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: One row with exactly ``bundle["feature_names"]`` as columns.
    :raises ValueError: For an unknown field or category.
    """
    _check_input(user_input, bundle)
    names = bundle["feature_names"]
    values = dict(bundle["feature_defaults"])
    raw_columns = set(bundle["scorecard_columns"])
    for field, value in user_input.items():
        if field == "term":
            values[field] = int(value.split()[0])
        elif field == "emp_length":
            values[field] = convert_emp_length(value)
        elif field in values:
            values[field] = value
        else:
            # Dummy columns look like "<field>_<category>" and are not raw columns.
            for name in names:
                if name.startswith(f"{field}_") and name not in raw_columns:
                    values[name] = name == f"{field}_{value}"
    values.update(_coupled_columns(values, values["term"]))
    return pd.DataFrame([values])[names]


def build_scorecard_row(
    user_input: dict[str, object], bundle: dict[str, object]
) -> pd.DataFrame:
    """Build the one-row, unencoded input of the scorecard.

    :param user_input: Field name to entered value, as for
        :func:`build_feature_vector`.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: One row with exactly ``bundle["scorecard_columns"]`` as columns.
    :raises ValueError: For an unknown field or category.
    """
    _check_input(user_input, bundle)
    values = {**bundle["scorecard_defaults"], **user_input}
    term_months = int(values["term"].split()[0])
    values.update(_coupled_columns(values, term_months))
    return pd.DataFrame([values])[bundle["scorecard_columns"]]


def score(user_input: dict[str, object], bundle: dict[str, object]) -> dict[str, float]:
    """Score one application with both models.

    :param user_input: Field name to entered value.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: Calibrated default probability per model (``"rf"``,
        ``"scorecard"``).
    """
    x_rf = bundle["scaler"].transform(build_feature_vector(user_input, bundle))
    x_scorecard = build_scorecard_row(user_input, bundle)
    return {
        "rf": float(bundle["rf"].predict_proba(x_rf)[0, 1]),
        "scorecard": float(bundle["scorecard"].predict_proba(x_scorecard)[0, 1]),
    }


def percentile_of(proba: float, reference: np.ndarray) -> float:
    """Rank of a score in the test portfolio.

    :param proba: Default probability of the application.
    :param reference: Test-set scores of the same model (``proba_rf`` or
        ``proba_scorecard``).
    :return: Percentage of test loans with a score at or below ``proba``.
    """
    return float((np.asarray(reference) <= proba).mean() * 100)


def band_of(proba: float, bands: pd.DataFrame) -> int:
    """Find the risk band of a score.

    A score between two bands goes to the higher one, a score above the last
    band to the last band.

    :param proba: Default probability of the application.
    :param bands: ``bands_rf`` or ``bands_scorecard`` from the bundle.
    :return: Number of the band (1 is the lowest risk).
    """
    position = np.searchsorted(bands["score_max"].to_numpy(), proba)
    return int(bands["band"].iloc[min(position, len(bands) - 1)])


def _uncalibrated(model: object) -> object:
    """Return the fitted model inside the calibration wrapper.

    :param model: ``bundle["rf"]`` or ``bundle["scorecard"]``.
    :return: The forest, or the WOE plus logistic regression pipeline.
    """
    return model.calibrated_classifiers_[0].estimator.estimator


def forest_explainer(bundle: dict[str, object]) -> shap.TreeExplainer:
    """Build the TreeSHAP explainer of the forest.

    TreeSHAP needs the inner forest, so it explains the uncalibrated forest
    score (``class_weight="balanced"``, around 0.5 on average), not the
    calibrated PD that the page shows.

    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: The explainer; build it once, it is slow compared to one row.
    """
    return shap.TreeExplainer(_uncalibrated(bundle["rf"]))


def explain_forest(
    user_input: dict[str, object],
    bundle: dict[str, object],
    explainer: shap.TreeExplainer,
) -> tuple[pd.DataFrame, float]:
    """Split the uncalibrated forest score of one application into SHAP values.

    :param user_input: Field name to entered value.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :param explainer: Result of :func:`forest_explainer`.
    :return: Table with ``feature``, ``value`` (unscaled, as the user sees it)
        and ``contribution`` (SHAP value for the default class), and the base
        value. Base value plus all contributions is the uncalibrated forest
        probability of default.
    """
    row = build_feature_vector(user_input, bundle)
    explanation = explainer(bundle["scaler"].transform(row))
    table = pd.DataFrame(
        {
            "feature": bundle["feature_names"],
            "value": row.iloc[0].astype(float).to_numpy(),
            "contribution": explanation.values[0, :, 1],
        }
    )
    return table, float(explanation.base_values[0, 1])


def explain_scorecard(
    user_input: dict[str, object], bundle: dict[str, object]
) -> tuple[pd.DataFrame, float]:
    """Split the scorecard log-odds of one application into feature contributions.

    The contribution is the logistic coefficient times the WOE of the bin the
    application falls into (``BinningProcess`` assigns the bin). It stays in
    log-odds of default instead of scorecard points, because the bundle has no
    points scaling and log-odds are what the regression adds up. A positive
    value raises the risk (the WOE is the log of good over bad, the
    coefficients are negative).

    :param user_input: Field name to entered value.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: Table with ``feature``, ``value`` (raw), ``woe`` and
        ``contribution`` for the features the scorecard kept, and the
        intercept. Intercept plus all contributions is the uncalibrated
        log-odds of default.
    """
    row = build_scorecard_row(user_input, bundle)
    pipeline = _uncalibrated(bundle["scorecard"])
    woe = pipeline.named_steps["woe"].transform(row, metric="woe")
    logit = pipeline.named_steps["logit"]
    table = pd.DataFrame(
        {
            "feature": woe.columns,
            "value": row[woe.columns].iloc[0].to_numpy(),
            "woe": woe.iloc[0].to_numpy(),
            "contribution": logit.coef_[0] * woe.iloc[0].to_numpy(),
        }
    )
    return table, float(logit.intercept_[0])


def top_contributions(table: pd.DataFrame, n: int, rest_label: str) -> pd.DataFrame:
    """Keep the n largest contributions and sum up the rest.

    :param table: Table with a ``contribution`` column, e.g. from
        :func:`explain_forest`.
    :param n: Number of features to keep.
    :param rest_label: ``feature`` text of the summed row.
    :return: The n rows with the largest absolute contribution, largest first,
        plus one row ``rest_label`` with the sum of all others (left out if
        there is nothing left). The total of ``contribution`` is unchanged.
    """
    ordered = table.reindex(
        table["contribution"].abs().sort_values(ascending=False).index
    )
    top, rest = ordered.iloc[:n], ordered.iloc[n:]
    if rest.empty:
        return top
    summary = pd.DataFrame(
        {"feature": [rest_label], "contribution": [rest["contribution"].sum()]}
    )
    return pd.concat([top, summary], ignore_index=True)


def cutoff_table(
    y_true: np.ndarray,
    proba: np.ndarray,
    thresholds: np.ndarray,
    loss_share: float,
    margin_share: float,
    loan_amount: float,
) -> pd.DataFrame:
    """Portfolio figures and a net result for every cut-off.

    A loan is rejected if its score is strictly above the threshold (a tie goes
    to the accepted part, like ``predict``). The scores are sorted once and the
    figures of all thresholds come from cumulative sums.

    The net result is an illustration of the cut-off logic, not a portfolio
    calculation: every accepted good loan earns ``margin_share * loan_amount``,
    every accepted default loses ``loss_share * loan_amount`` (an LGD
    placeholder, LGD and EAD are not modelled), rejected loans earn and lose
    nothing. One ``loan_amount`` stands for all loans because the bundle has no
    per-loan amounts.

    :param y_true: True labels (1 = Charged Off).
    :param proba: Predicted default probabilities.
    :param thresholds: Cut-offs to evaluate.
    :param loss_share: Loss per accepted default as a share of the loan amount.
    :param margin_share: Income per accepted good loan as a share of the loan amount.
    :param loan_amount: Loan amount in USD.
    :return: One row per threshold with ``threshold``, ``accepted``,
        ``rejected``, ``caught`` (rejected defaults), ``missed`` (accepted
        defaults), ``rejected_good``, ``approval_rate``, ``default_rate_accepted``
        (NaN if nothing is accepted), ``precision`` and ``recall`` (of the
        default class, precision 0 if nothing is rejected) and ``net_result``.
    """
    order = np.argsort(proba)
    defaults_up_to = np.concatenate([[0], np.cumsum(np.asarray(y_true)[order])])
    n_loans = len(order)
    n_defaults = defaults_up_to[-1]
    # Loans with a score at or below the threshold are accepted.
    accepted = np.searchsorted(np.asarray(proba)[order], thresholds, side="right")
    missed = defaults_up_to[accepted]
    rejected = n_loans - accepted
    caught = n_defaults - missed
    rejected_good = rejected - caught
    accepted_good = accepted - missed
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(rejected > 0, caught / rejected, 0.0)
        default_rate_accepted = missed / accepted
    return pd.DataFrame(
        {
            "threshold": thresholds,
            "accepted": accepted,
            "rejected": rejected,
            "caught": caught,
            "missed": missed,
            "rejected_good": rejected_good,
            "approval_rate": accepted / n_loans,
            "default_rate_accepted": default_rate_accepted,
            "precision": precision,
            "recall": caught / n_defaults,
            "net_result": loan_amount
            * (margin_share * accepted_good - loss_share * missed),
        }
    )
