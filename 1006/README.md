# 1006 — evidence package and bounded manuscript candidate

Updated: 2026-10-07.

**Current gate:** scientific evidence freeze is **YES for bounded claims**;
reviewer closure is **PARTIAL** and direct system upload is **HOLD**. The
submitted 01549 3AFC is retained as complementary C3/TCAS preference evidence.
The later 40-slot study is analyzed as a prespecified confirmatory endpoint
family with documented execution deviations; no endpoint supports an adjusted
LLH preference advantage. See
`gates/SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md`,
`gates/FINAL_READINESS_VERDICT_20261007.md`, and
`evidence/human_study/HUMAN_STUDY_CONFIRMATORY_REASSESSMENT_20261007_ZH.md`.

E6 completed its 24-object calibration, technical checks, and all 288 locked
development generations, then **stopped at the method-difference/value gate**:
full-LPIPS worsened in all 24 object-averaged comparisons and substantive
novelty was not established. No E6 Fresh D is launched. See
`evidence/audits/E6_POST_DEVELOPMENT_METHOD_REVIEW_20261006_ZH.md`.

Fresh C is now complete. Its original four-condition run passed integrity on
300 objects and supports the locked C3−GFL foreground PSNR endpoint: +0.522 dB
(95% object-bootstrap CI [+0.404, +0.641]). The separately frozen LLH/linear
revision-era addendum also passed on the same 300 objects. An independent
direction/Holm audit recomputed 28 checks with zero discrepancies. The results
show endpoint and object-level tradeoffs; no strategy is declared an overall
winner. The final 20-group, six-strategy comparison gallery and cohort forest
plot are built. Details and allowed wording are in
`evidence/audits/FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md`.

Use `evidence/audits/FRESH_C_EVIDENCE_PACKET_INDEX_20261006.md` as the direct
index to the frozen cohort, protocols, both integrity gates, analyses, 28-check
direction audit, complete six-method object index, and final 20-group atlas.
The claim-level ledger at
`evidence/audits/next_stage_20261006/CLAIM_EVIDENCE_AUTHORITY_LEDGER.json` and
its audit are historical, pre-freeze evidence maps. Current release and freeze
decisions are recorded in the dated gate files below. Human-study authority is
tracked separately by `evidence/human_study/HUMAN_STUDY_CLASSIFICATION_OVERRIDE_20261007.json`,
`gates/HUMAN_STUDY_GATE_VERDICT_20261007.md`, and the source-pinned
reassessment; the override changes only the human classification, not the
recorded deviations or any other evidence entry.
The sign correction and its scope are recorded in
`evidence/audits/DIRECTION_AND_SIGN_AUDIT_20261006.md`.

The Fresh C addendum watcher initially blocked on a GPU-lock handoff held by
the completed primary driver. This happened before addendum inference; the
incident and state hashes are preserved in
`data/fresh_c/FRESH_C_ADDENDUM_GPU_LOCK_HANDOFF_INCIDENT_20261006.json`. The
primary lock was released, and the unchanged addendum completed with PASS
integrity and analysis. No cohort, condition, input, seed, or cap was changed.

The old LLH handoff package was confirmed **not distributed** and remains
superseded. The researcher confirmed that the later 40-slot response export is
the confirmatory human study. Its frozen eight-endpoint family was reanalyzed
with 37 field-valid participants; no endpoint survives Holm correction. The
assignment and stimulus provenance deviations are disclosed in the linked
reassessment, so this is a confirmatory endpoint analysis with documented
execution deviations, not a claim of fully protocol-adherent execution. The
submitted 01549 3AFC remains evidence only for its original C3/TCAS comparison.
The 1006 main-text candidate and Supplement S8 report both studies within those
scopes. Neither study establishes an adjusted LLH preference advantage or
absolute reference fidelity.

An input-only list of 24 UV-complete, CC BY Fresh C assets is frozen for a
possible GLB panel. It uses the first eligible assets in frozen cohort order;
it is not the previously proposed texture/coverage/geometry-stratified sample,
and it is not an independent held-out 3D sample. The new bake/camera/sampler
pipeline has not passed technical validation: the current production baker
rebuilds UVs with xatlas, while 9/24 selected assets have out-of-range native
UVs. See the feasibility audit before any bake work. The existing N=20 GLB-native
results remain a bounded unlit base-color supplement, not a human or full-PBR
fidelity result.

The previously submitted 01549 manuscript and round-two source remain
untouched. The separate 1006 candidate has been updated after the bounded
scientific evidence freeze; reviewer, rights, and final delivery gates remain
open. This directory gathers the audits, data, protocols, figure sources,
reviewer mapping, attribution register, and candidate manuscript.
Original-manuscript hashes are recorded in `MANUSCRIPT_PRESERVATION_AUDIT.md`.

## Current disposition

The working narrative remains a bounded empirical characterization of
inference-time geometry-adapter scaling in the tested residual path: requested
profiles, native cap execution, object heterogeneity, and endpoint-specific
image/GLB boundaries. Fresh C supports C3 over GFL on its locked primary
endpoint, while comparisons against LLH and generic linear prevent a unique
winner claim. A2/A3/A3b remain native-dose, stress-regime, and bounded-map
evidence; they do not establish a dose-independent Layer × Window law.

The scientific evidence freeze is **YES for the bounded scope**; final
readiness remains **HOLD**. The proposed new 24-object GLB bake and seam claim
are retired; historical N=20 GLB-native results remain unlit base-color
unseen-view evidence with mixed endpoints. strict-276 remains retrospective
with incomplete legacy provenance. Source rights, participant-data handling,
the final manuscript/response rewrite, clean delivery rebuild, and R2.1
contribution adequacy remain open. E5 provides no cap-respecting three-group
dose match; E6 supplies a stopped method candidate and no Fresh D. See the
2026-10-07 freeze/readiness/reviewer verdicts and Fresh C comparison report.

The current reviewer mapping is `gates/REVIEWER_CLOSURE_20261007.md`; dated
2026-10-06 matrices remain historical snapshots. Current freeze and delivery
decisions are in `gates/SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md` and
`gates/FINAL_READINESS_VERDICT_20261007.md`.

The GitHub task branch is a review snapshot and still contains two visual
derivatives with unresolved source-license terms. This evidence update does
not clear those assets for redistribution or make the branch a journal-system
submission package.

The historical 300-object LLH/linear comparison data are indexed under
`data/campaign_B1B2_prior/` and `data/campaign_C_prior/`. Matching six-input
hashes cover all 300 pairs, while the older run manifests omit config hashes.
The old generic-schedule report remains unchanged under
`evidence/audits/superseded/`; its positive LLH−linear FG-LPIPS direction is
corrected in `evidence/audits/LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md`:
positive A−B LPIPS favors linear because lower is better.

The broader archived strategy audit reproduces 19 historical pairwise files
(18 formal, one exploratory) and five Holm families/28 tests. B3 has 750 exact
duplicate rows in its later shard layout and conflicting `num_shards` metadata;
duplicates do not increase N. See
`evidence/audits/FORMAL_PAIRWISE_DIRECTION_AUDIT_20261006.md` and
`FORMAL_HOLM_FAMILY_AUDIT_20261006.md`.

The pre-outcome layout prototype remains in
`figures/strategy_comparison_gallery/prototype/` as historical layout QA. The
final Fresh C gallery is in
`figures/strategy_comparison_gallery/fresh_c_final/`: 20 unique groups balanced
across C3−GFL, LLH−C3, LLH−linear, and C3−linear; each group shows the same UID
and six views for the reference and all six strategies. Cohort rankings are
separate by endpoint and registered multiplicity family, with effect sizes,
intervals, and object-favorable fractions. Individual-object significance and
cross-metric winner scores are never computed. The outcome-ranked examples are
not used to choose the human-study sample. The confirmatory human endpoint
analysis, execution deviations, aggregate table, forest plot, and provenance
are in `evidence/human_study/`; raw participant-level files are not copied into
`1006` again. Their prior public source-branch location and separate governance
review are recorded in the manuscript and human-study reassessment.

Five source-checked strategy-alignment figures remain in
`figures/evidence_alignment/`: Fresh B object-level endpoint tradeoffs, the
retrospective Campaign C LLH–linear pairing, GT texture-complexity
heterogeneity, and separate MV-Adapter and MVDiffusion interface-boundary
plots. Direction conventions and allowed interpretations are in
`evidence/audits/next_stage_20261006/STRATEGY_FIGURE_ALIGNMENT_20261006_ZH.md`.
These historical figures do not replace Fresh C, pool backbones, or designate
a cross-metric winner. Rebuild them with
`python 1006/scripts/generate_evidence_alignment_figures.py`.

The requested-versus-applied native-cap diagram and its CSV show scale clipping
only and do not claim equal residual dose. The Fresh C gallery includes the
cohort forest plot rebuilt from the two PASS-gated analyses.

## Evidence authority and supersession

Use the following order when a local artifact and an older report disagree:

1. `gates/FINAL_READINESS_VERDICT_20261007.md` is the current release and
   submission gate; the 2026-10-06 readiness file is a historical snapshot.
2. `gates/REVIEWER_CLOSURE_20261007.md` maps reviewer issues to evidence and
   remaining manuscript actions.
3. `gates/SCIENTIFIC_EVIDENCE_FREEZE_VERDICT_20261007.md` defines the current
   bounded scientific freeze. The candidate manuscript reflects that evidence;
   remaining reviewer, rights, and delivery gates are tracked separately and
   it is not the journal-system submission package.
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
  human-study rules, B locks, integrity records, and execution logs. The
  40-slot confirmatory endpoint analysis and execution-deviation record are in
  `evidence/human_study/`.
  Fresh C protocol and candidate-queue locks are in
  `evidence/protocols/` and `data/fresh_c/`. LLH and endpoint-matched linear
  are frozen as a separate revision-era Fresh C addendum, with independent
  launch and integrity/analysis scripts and an automatic gate watcher.
- `data/`: copied per-object/per-condition metrics and manifests, derived
  paired summaries, the compact historic Experiment C snapshot plus a
  file-level index for its full outputs, GLB-native endpoints, strict-276 row data, and interface
  evidence. Raw rendered prediction images, residual traces, source meshes,
  and some large source payloads are not redistributed; hashes and original
  locations are identified in the archived manifests and audit reports. Fresh
  C source meshes, input renders, predictions, and residual logs are locally
  staged under `data/fresh_c/` and excluded from the public commit; the frozen
  UID, source, render, and output hash records are packaged when each gate
  passes.
- `scripts/`: analysis, figure, and attribution-table builders for the
  candidate package.
- `figures/`: paper figures regenerated from packaged tables plus the
  retrospective strategy-comparison layout prototype.
- `licenses/`: per-object attribution metadata and release limitations.
- `guides/`: response-format guidance retained for provenance. The old LLH
  handoff package was not distributed; the later 40-slot confirmatory endpoint
  analysis and its deviations are documented under `evidence/human_study/`.
- `manuscript/`: candidate LaTeX, figures, bibliography, build style files,
  compiled PDFs, and copies of the 01549 formatting reference. The source
  format copies are reference inputs, not modified originals.
- `review/`: supplied reviewer comments, the original working response draft,
  and a page/line-mapped response candidate. Neither is an editor decision or
  proof that the unresolved novelty/fidelity concerns were accepted.
- `gates/`: current release, reviewer-closure, next-action, and human-study
  authority verdicts; the human gate's reproducible checks are recorded in
  `evidence/human_study/HUMAN_STUDY_GATE_VALIDATION_20261007.json`.
- `evidence/audits/ASSET_SOURCE_LICENSE_RECHECK_20261006.md` and
  `licenses/ASSET_SOURCE_LICENSE_RECHECK_20261006.json`: direct source-level
  API check for the two visual-panel assets whose redistribution terms remain
  unresolved.
- `evidence/audits/REVISION_STRATEGY_COMPARATIVE_EVIDENCE_20261006_ZH.md`:
  literature-based comparison of revision routes and a reviewer-mapped
  evidence plan. It recommends an 01549-continuity revision using 1006 as the
  evidence authority; it does not change the manuscript or readiness verdict.
- `source_inventory.json` and `SHA256SUMS.txt`: package-relative provenance
  and integrity records.

The initial same-workspace script/build verification is recorded at
`evidence/audits/PACKAGE_BUILD_VERIFICATION_20261006.md`; the later published-
commit fresh-checkout rebuild and its scope limits are recorded at
`evidence/audits/CLEAN_CHECKOUT_REBUILD_20261006.md`.

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
python 1006/scripts/generate_evidence_alignment_figures.py
python 1006/scripts/test_strategy_gallery_selection.py
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
recreate omitted image-generation payloads or train/infer any model. A fresh
checkout of published commit `00c4891` passed its 401 recorded checksums and
reproduced the compact analysis, figures/tables, and LaTeX. The updated
package index includes this follow-up's audit files. A paper-wide
end-to-end reconstruction of every historical GPU result is not claimed
complete because some prediction, residual, and render payloads are not
included.

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
