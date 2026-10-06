# 1006 — evidence package and bounded manuscript candidate

Updated: 2026-10-06.

This directory gathers the audit record, experiment outputs, analysis scripts,
protocols, reviewer mapping, attribution register, and a separate revised
manuscript candidate. The previously submitted 01549 manuscript and round-two
source remain outside this directory and were not edited. File hashes are
recorded in `MANUSCRIPT_PRESERVATION_AUDIT.md`.

## Current disposition

The candidate is a bounded empirical paper about inference-time geometry-
adapter scaling in the tested MVPainter-style residual path. It reports
requested scale, implementation caps, measured residual norms, object-level
heterogeneity, the four distinct FRESH_CONFIRM_B temporal contrasts, limited
GLB-native unseen-view results, and interface-specific boundary evidence.
It does not claim a universal schedule winner, a dose-independent Layer ×
Window law, human-validated LLH fidelity, seam improvement, or cross-backbone
transfer.

The candidate compiles, but the final readiness verdict is **HOLD**. This is
not a claim that a reviewer or editor accepted the claim reduction. Human
responses are still absent; the C3/GFL analysis on FRESH_CONFIRM_B is
retrospective; the strict-276 provenance chain is incomplete; two panel asset
licenses still need source-level checks; and contribution adequacy
remains a substantive venue risk after comparison with Scheduled Style
Injection. A new, disjoint Fresh C3-versus-GFL follow-up is now in progress:
its cohort protocol and 1,000-ID technical queue were frozen before any method
output. All 600 screen assets downloaded without failure; 594 pass the basic
geometry screen and are now in the frozen 17-view render/duplicate audit. No
method outputs exist. The follow-up is explicitly revision-era and does not
replace the original preregistration. See
`evidence/audits/FRESH_C_INPUT_SCREEN_20261006.md`,
`evidence/audits/FRESH_C_REMEDIATION_ACTION_LOG_20261006.md`,
`gates/FINAL_READINESS_VERDICT.md`, and `gates/REVIEWER_CLOSURE_FINAL.md` for
the controlling decisions and residual gates; `gates/BLOCKER_REMEDIATION_PLAN_20261006.md`
maps each open reviewer item to a feasible action and an honest fallback. A separate E5 technical pilot
completed on six already-used development objects: its alpha-zero and numeric
precision gates passed, but the shallow cap was exceeded in 30.4% of steps even
at the smallest predeclared perturbation. It therefore supplies no
cap-respecting three-group dose match and no quality or mechanism evidence;
see `evidence/audits/E5_RESIDUAL_DOSE_FEASIBILITY_REPORT_20261006.md`.
The GitHub task branch is public and currently contains the contact sheet and
compiled supplement with the two license-uncertain derivatives. It is a review
snapshot with an open rights gate, not a license-cleared release; resolve those
assets or remove/rebuild the affected artifacts before final publication.

## Evidence authority and supersession

Use the following order when a local artifact and an older report disagree:

1. `gates/FINAL_READINESS_VERDICT.md` is the current release and submission
   gate.
2. `gates/REVIEWER_CLOSURE_FINAL.md` maps each supplied reviewer issue to the
   revised candidate and states what remains open.
3. `manuscript/main_1006.tex` and `manuscript/supplementary_1006.tex` are the
   current candidate text; their PDFs are the compiled copies.
4. `evidence/audits/` contains source audits, including older pre-rewrite
   matrices and readiness snapshots. Those historical files are preserved
   for traceability and are not the final gate.
5. `data/derived/` contains reproducible endpoint tables. The accompanying
   reports identify retrospective and exploratory results explicitly.

Do not promote old Fresh300, strict-276, or pre-GLB-renderer language back
into the paper without rechecking its source and status. In particular,
strict-276 is a retrospective same-cohort comparison, and the additional
FRESH_CONFIRM_B C3−GFL comparison was selected after B outcome exposure.

## Contents

- `evidence/audits/`: cohort, statistical, renderer, interaction, narrative,
  cross-interface, integrity, provenance, and comparative paper-revision
  strategy reports.
- `evidence/protocols/` and `logs/fresh_b/`: frozen analysis protocols,
  human-study rules, B locks, integrity records, and execution logs. No human
  responses are present. Fresh C protocol and candidate-queue locks are in
  `evidence/protocols/` and `data/fresh_c/`.
- `data/`: copied per-object/per-condition metrics and manifests, derived
  paired summaries, GLB-native endpoints, strict-276 row data, and interface
  evidence. Raw rendered prediction images, residual traces, source meshes,
  and some large source payloads are not redistributed; hashes and original
  locations are identified in the archived manifests and audit reports. Fresh
  C source meshes, input renders, predictions, and residual logs are locally
  staged under `data/fresh_c/` and excluded from the public commit; the frozen
  UID, source, render, and output hash records are packaged when each gate
  passes.
- `scripts/`: analysis, figure, and attribution-table builders for the
  candidate package.
- `figures/`: paper figures regenerated from packaged tables.
- `licenses/`: per-object attribution metadata and release limitations.
- `guides/`: frozen human-response format and validation instructions for
  future data supplied by the user.
- `manuscript/`: candidate LaTeX, figures, bibliography, build style files,
  compiled PDFs, and copies of the 01549 formatting reference. The source
  format copies are reference inputs, not modified originals.
- `review/`: supplied reviewer comments, the original working response draft,
  and a page/line-mapped response candidate. Neither is an editor decision or
  proof that the unresolved novelty/fidelity concerns were accepted.
- `gates/`: current release, reviewer-closure, and next-action decisions.
- `evidence/audits/REVISION_STRATEGY_COMPARATIVE_EVIDENCE_20261006_ZH.md`:
  literature-based comparison of revision routes and a reviewer-mapped
  evidence plan. It recommends an 01549-continuity revision using 1006 as the
  evidence authority; it does not change the manuscript or readiness verdict.
- `source_inventory.json` and `SHA256SUMS.txt`: package-relative provenance
  and integrity records.

The final same-workspace script/build verification is recorded at
`evidence/audits/PACKAGE_BUILD_VERIFICATION_20261006.md`.

## Rebuild and reproduce

Run from the repository root. Python analysis requires the packages listed
in `code/reproducibility_release/environment/requirements-tested.txt` plus
Matplotlib for figures. The GLB renderer itself is not rerun by these compact
analysis commands; its exact render hashes and output metrics are preserved
in the audit package.

```bash
python 1006/scripts/analyze_strict276_c3_retrospective.py
python 1006/scripts/analyze_fresh_b_c3_gfl_posthoc.py
python 1006/scripts/generate_figures.py
python 1006/scripts/build_objaverse_attribution_tex.py
```

Compile the paper from the manuscript directory with the supplied Elsevier
class/style files and a LaTeX installation:

```bash
cd 1006/manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error main_1006.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary_1006.tex
```

These commands rebuild the included figures/tables and PDFs; they do not
recreate omitted image-generation payloads or train/infer any model. A
paper-wide clean-clone reconstruction of every historical result is not
claimed complete.

## Publication and release boundary

The asset table attributes all 24 models. Current Sketchfab API metadata
corroborates 22/24 license records. Two entries rely on the archived
Objaverse `by` metadata only; one of those has a stored personal-project-use
description and the other model endpoint returns 404. Do not treat those two
records as cleared for redistribution until the source terms are confirmed.
Panel 06 is CC BY-SA 4.0 and is separately attributed. See
`licenses/README.md`.

The paper remains a double-anonymous candidate with no author metadata or
final page/line response references. No journal system upload or editor
decision is represented by this package.
