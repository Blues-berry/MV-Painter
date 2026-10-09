# Fresh C execution semantics and intervention accounting

**Status: bounded implementation-aware analysis; not a new algorithm or schedule.**

## Logged chain

`requested scale → native cap/layer rule → actually applied scale → applied residual correction → image-space endpoint`

The accounting table reconstructs the first four stages from existing Fresh C logs for GFL, GFH, C3, LLH, and generic linear. It covers 50 recorded timesteps × 3 layer groups × 5 strategies (750 strategy/group/step records). `FRESH_C_EXECUTION_SEMANTICS_REPRESENTATIVE.csv` gives exact rows for steps 0, 12, 24, 37, and 49; the complete 750-row table is `FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv`.

The per-row fields include requested and applied scale, cap-activation fraction, median and interquartile range of the applied correction L2 norm, correction mean-absolute magnitude, and record/object counts. These are logged summaries; no values were interpolated. The correction norm is after the effective scale and is not a common-dose intervention measure across methods.

## Interpretation

The nominal global scale does not describe a scalar intervention by itself. The wrapper applies layer-specific profiles and native caps; shallow scales requested above the cap are clipped. The frozen caps are deep 3.0, middle 3.5, and shallow 0.8. GFL and GFH request 1.25 and 2.50 at all groups respectively; both exceed the shallow cap, so their shallow applied scale is 0.8. Other schedules have time- and layer-specific requested profiles, which are preserved in the row-level table and figure.

Applied correction magnitudes also depend on the residual being scaled. LLH and generic linear may have different measured correction norms even when labels or requested scales alone look similar. The accounting therefore explains why a nominal scale label is not equivalent to equal realized residual dose. It does **not** estimate quality under equal realized dose and does not establish that one residual profile caused an endpoint difference independently of the full implementation.

## Figure and reproducibility inputs

- Figure A candidate: `1006/figures/FRESH_C_EXECUTION_SEMANTICS.pdf` and `.png`.
- Source table: `1006/evidence/audits/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv`.
- Builder: `1006/scripts/summarize_fresh_c_execution_semantics.py`.
- Representative exact rows: `1006/evidence/audits/FRESH_C_EXECUTION_SEMANTICS_REPRESENTATIVE.csv`.

Allowed terms: **execution semantics**, **intervention accounting**, or **implementation-aware analysis**. Do not call this a new schedule algorithm, equal-dose causal test, or optimality result.
