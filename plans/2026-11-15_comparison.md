# Plan: forest vs. scorecard page (issue #37)

1. `src/comparison.py` (small, tested): `iv_overview(iv_table)` sorts by IV and
   returns the columns the page shows; `dropped_features(iv_table)` lists the
   features with `selected == False`; `default_min_iv()` reads the threshold from
   the `train_scorecard` signature because the bundle does not store it;
   `winner(metrics)` returns `"scorecard"` or `"rf"` from the two AUCs, so the
   conclusion text follows the numbers.
2. Texts first, EN then DE: `[comparison]`, `nav.comparison`,
   `nav_desc.comparison`. EN follows notebook section 7 ("Reading the gap",
   "When the scorecard wins ...", "When the forest wins", the closing summary),
   DE translates it. The IV rules of thumb are not repeated: they are shown from
   the glossary entry `iv` (`how_to_read`, via tooltip and an expander).
3. `app/views/comparison.py`, registered in `PAGES` after `performance`:
   same-test-rows note, metric table plus grouped bar chart (both models, model
   colours and labels), conclusion chosen by `winner`, mechanics (WOE, binning,
   additive, traceable), IV table (`st.dataframe`, translated headers, selected
   flag, dropped features named with the threshold), the practice question.
   Links to the performance page (ROC, calibration) instead of repeating it.
4. Tests: `tests/test_comparison.py` for the functions; smoke tests of the page
   in both languages (metrics equal the bundle, IV table sorted, tooltips,
   conclusion for both AUC orderings).
5. Real bundle: IV table, dropped features, metrics; headless start; AppTest;
   screenshots. Check the guide and the menu order.
6. HANDOVER.md.
