# Fresh C GLB panel object selection record — 2026-10-06

The 24-object list is selected only from the frozen Fresh C UID order and
input-side eligibility. Eligibility requires a valid, hash-matching source
GLB, a license in the candidate-queue allowlist (`CC0`, `CC BY`, or
`CC BY-SA`), and finite vertex UV coordinates on every nonempty mesh. The
selection script does not open prediction images, per-object metrics, or
analysis files. It stops at the first 24 eligible UIDs; the frozen list is
never replaced after output review.

The machine-readable selection and per-mesh UV audit are in
[`FRESH_C_GLB_PANEL_SELECTION_20261006.json`](/4T/CXY/MV-Painter/1006/data/fresh_c/FRESH_C_GLB_PANEL_SELECTION_20261006.json),
reproducible with
`python 1006/scripts/freeze_fresh_c_glb_panel_selection.py`. All 24 selected
assets currently carry the `CC BY` tag and require creator/source attribution
before any external distribution.

Chronology is a limitation: the primary Fresh C method run and its aggregate
analysis had completed when the list was frozen, while the independent
LLH/linear addendum was still running. Selection remained input-only, but this
is a same-cohort, outcome-blind subset rather than an independent held-out 3D
cohort. Do not describe it as a preregistered 3D confirmation.

This record freezes object identity only. The bake implementation, camera/view
mapping, glTF sampler validation, unseen-view renderer, and their integrity
checks must pass before reporting any new 3D endpoint. The scope is limited to
the exported unlit base-color representation. It cannot establish human
fidelity, full-PBR appearance, lighting robustness, or seam improvement.
