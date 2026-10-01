# FIGURE_SELECTION_PROVENANCE.md (Phase 11 — agent B)

All display figures in `final_round2.tex` + `supplementary_round2.tex`,
with object IDs, source cohort, selection criterion (as recoverable from
captions/manifests), and the metric-rank cross-check against the paper-facing
same-runner matrix. Per-object ranks from
`phase1a_llh_gfl_per_object_deltas.csv` (LLH − GFL, 276 objects).

## Figure inventory

| figure | object(s) | cohort / source | stated criterion | verified rank (LLH−GFL FG-PSNR) | verdict |
|---|---|---|---|---|---|
| fig:method (fig1_layerwise_20260930.pdf) | n/a | schematic | — | — | no selection issue |
| fig:complete0066 (L267) | obj_0066 | 12-object stratified bake cohort → `main_adapter_clean_v2/comparisons/` | caption: "representative object … not selected as a best-case metric example" | **rank 2/276, +7.16 dB** | **P0 FLAG** — see below |
| fig:completefailures (L279/282) | obj_0048, obj_0078 | same pool | "failure-boundary examples … baking/exporter boundary case … very low raw texture coverage" | rank 95 (+4.86) and 75 (+5.22) — both wins | acceptable with wording caveat |
| fig (L350) success panel | dev object(s) | `layer_lhl_v1` dev-24 ablation | "representative development object" | dev cohort, not holdout | OK — labeled as development |
| fig (L362) counterexample panel | dev object(s) | dev-24 ablation | "Visible counterexample for the temporal schedule claim" | dev cohort | OK — honest counterexample, labeled |
| S? contact sheet (supp L183) | all 12 | exact bake cohort | complete cohort shown | — | OK — no selection |
| bake tables (L634) | 12 objects | stratified quartile cohort (manifest CSV) | documented stratification | — | OK — case-study framed |
| MV-Adapter panel (L720) | means over 76 | full cohort | — | — | OK |

## P0 flag: obj_0066 "representative"

The caption states the panel "is qualitative evidence and is not selected as
a best-case metric example." Against the paper's current headline comparison
(LLH vs GFL same-runner matrix), obj_0066 is the **2nd-largest win of 276**
(+7.16 dB). The figure was evidently produced under the older clean-v2
four-condition protocol (its caption narrates C3 vs fixed-high
over-control), and the archived aggregates for that protocol are
condition-level only — the per-object rank under the historical C3−FH pairing
could not be verified from archived artifacts. Either way the caption's
blanket disclaimer is unverifiable and, under the current headline
comparison, false.

Required revision-window action (choose one):
1. Re-pick the representative object by a **pre-stated fixed rule** — the
   median-band set from this audit (obj_0130/0261/0205/0150/0277/0140, deltas
   +3.33…+3.43) is ready to use; or
2. Keep obj_0066 and rewrite the caption to disclose the rank ("one of the
   largest per-object improvements, shown to illustrate the effect's visual
   magnitude"), plus the protocol it was selected under.

## Wording caveat: "Failure-boundary examples"

obj_0048/obj_0078 are mid-rank wins on the schedule metric; the "failure"
refers to baking/export and coverage limitations, not schedule losses. The
caption should say so explicitly ("both objects improve under the schedule on
image metrics; they illustrate bake-pipeline limitations") to preempt a
reviewer cross-check. obj_0048 is also the vertex-reindexed object disclosed
at L655.

## Selection-date provenance

The comparison PNGs are git-ignored (binary) — no commit history proves the
selection date. Recoverable context: the 12-object cohort manifest is frozen
(`exact_baking_cohort_manifest.csv`, stratified by development delta
quartiles, selection documented as geometry/performance-based before the
strict-276 confirmation existed). The paper-figure subset selection (0066 /
0048+0078) is not documented anywhere in the repo — this audit's finding is
that it must be either re-ruled or re-labeled.

## Verdict

`VALIDATED_WITH_LIMITATIONS` — all quantitative figures/tables are
cohort-complete (no per-object cherry-picking in any table); the single
qualitative "representative" figure (obj_0066) fails the caption's own
standard under the current headline comparison and requires the fix above.
No figure claims to be a random or median draw, so no stronger provenance is
currently claimable.
