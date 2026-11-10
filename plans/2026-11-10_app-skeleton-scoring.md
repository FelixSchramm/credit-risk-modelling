# Plan: issue #31, app skeleton and scoring layer

Goal: a runnable multipage Streamlit skeleton plus a tested scoring module.

1. `src/scoring.py` (no Streamlit import):
   - `build_feature_vector`: start from `feature_defaults`, overwrite with the
     user input. `term` and `emp_length` arrive as text and are converted with
     the functions of `src.features`; a categorical input sets its dummy
     column and clears the other dummies of the same group (reference category
     has no column). Unknown field or category raises `ValueError`.
   - `build_scorecard_row`: same on `scorecard_defaults`, unencoded.
   - `score`: calibrated PD of both models (forest input is scaled).
   - `percentile_of`, `band_of`: rank in the test portfolio and risk band.
2. `streamlit_app.py` in the repo root (sidebar, `st.navigation`), pages in
   `app/views/` (`home.py` placeholder), `app/ui.py` with `get_bundle()`
   (`st.cache_resource`, `BUNDLE_PATH`, clear message and `st.stop()` if the
   file is missing) and `PAGES`.
3. Tests: `tests/conftest.py` builds a small synthetic bundle with
   `build_bundle`; `tests/test_scoring.py`; `tests/test_app_smoke.py`
   (`AppTest`: every page renders, missing bundle gives a message).
4. `streamlit==1.66.1` in `requirements.txt`, `black --check` in CI covers
   `app` and `streamlit_app.py`, README and HANDOVER updated.
