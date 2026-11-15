# Plan: prepare deployment on Streamlit Community Cloud (#38)

The deployment itself needs the user's Streamlit Community Cloud account and is
not part of this PR. This PR prepares everything that works without it.

1. Readiness checks -> verify: bundle size, start without raw dataset,
   `.python-version` and CI agree on 3.11, no missing system packages.
2. Visual check with Playwright against the real bundle: seven pages x
   {en, de} x {light, dark} at 1280x800 and seven pages at 390 px ->
   verify: no exception, `scrollWidth <= innerWidth` at 390 px, nothing
   clipped, no uncalibrated score labelled as probability.
3. Minimal layout fixes for clear-cut problems, one commit each.
4. README: calculator screenshots DE and EN near the top, commented
   placeholder for the app URL under the title (no fake link).
5. HANDOVER: click-by-click checklist for the user and what the next session
   does with the URL; #38 state "prepared, waiting for the app URL".

Step 5 of the issue (CI import smoke test) is dropped by the epic addendum.
