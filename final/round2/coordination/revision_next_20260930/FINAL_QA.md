# Final QA — next-round revision package (2026-09-30)

Deliverables: `final/round2/final_round2.tex` (+PDF), `supplementary_round2.tex`
(+PDF), `response_letter_round2.md`, coordination docs, evidence directories.

## A. Numeric traceability (paper value -> evidence file)

| Paper value | Evidence |
|---|---|
| Shared-input ablation table (Table 1, tab:layerablation) | `coordination/layer_lhl_v1/ablation_summary.json` (hash-verified) |
| Paired deltas layer-LHL vs fixed-low (+3.083 dB FG-PSNR etc.) | same summary; bootstrap seed 20260929 |
| Complete factorial table (tab:factorial) + paired comparisons | `coordination/layer_factorial_v1_20260930/factorial_summary.json`, rows_seed42/43_44.json, SHA-256 index |
| Strict-276 confirmation table (tab:confirmation) | `coordination/layer_confirmation_20260930/confirmation_analysis.json` + per-schedule rows/CSV/manifests |
| LLH vs fixed-mean (all 7 metrics) | confirmation_analysis.json `layer_llh_minus_layer_fixed_mean` |
| LLH vs layer-LHL replica (all 7) | confirmation_analysis.json `layer_llh_minus_layer_lhl` |
| Fixed-mean vs replica mixed | confirmation_analysis.json `layer_fixed_mean_minus_layer_lhl` |
| Cross-runner replica check (r=0.66; 14.78 vs 12.97) | confirmation_analysis.json `cross_runner_lhl_check` |
| Strict-276 clean-v2 panel / stage follow-up / serialized SSIM | unchanged from prior freeze (`E0A_EVIDENCE_FREEZE_20260929.json`, `stage_placement_276_20260929/`) |
| Global bake table (tab:bake12) | `main_adapter_baking/cpu_bake_12/UNSEEN_OBJECT_METRICS.csv` (recomputed, matches) |
| Layer bake extension rows (S4b, 4-way same-draw) | `coordination/bake_layerwise_20260930/UNSEEN_OBJECT_METRICS.csv` (means: fixed-low 10.763 / C3 12.565 / layer-LHL 15.005 / layer-LLH 16.679 dB; CIEDE2000 26.287/21.643/16.922/14.186; FG-LPIPS 0.1705/0.1562/0.1420/0.1215; LLH 12/12 wins vs LHL and vs C3 on all three metrics) |
| MV-Adapter table | `mv_adapter/MV_ADAPTER_UNIFIED_RESULTS.csv` (unchanged) |
| GT-relative texture errors (RGB-std/Lap/HF/grad) | `scheme_new_schedule/layer_official_v2_merged/texture_error_comparisons.json` (archived in handoff doc) |
| Checkpoint / object-list hashes | recomputed 2026-09-30, match freeze manifests |
| layer_lhl_v1 artifact hashes | `sha256sum -c` 5/5 OK |

## B. Reviewer coverage

- R1.1: complete-object panels + full contact sheet + global bake case study +
  layer-wise same-draw bake extension + seam/video honesty. PASS (bounded).
- R1.2: +0.96 dB retired; strict-276 panels protocol-separated; pre-registered
  confirmation of LLH/fixed-mean + LHL replica. PASS.
- R1.3: four-dimension taxonomy; variation never implies fidelity. PASS.
- R1.4: paired CIs everywhere; zero-crossing never equivalence; historical
  Edge-SSIM retired with acknowledgment. PASS.
- R1.5: FAC implementation details; honest data-availability statement; no
  video claims. PASS (request-based access stated).
- R2.1: contribution = training-free layer-wise control; (i)-(iv) ablation
  decomposition; complete 8-pattern factorial; counterexamples retained. PASS.
- R2.2: CAI demoted to empirical diagnostic in method + Remark + response. PASS.
- R2.3: second-backbone audit labeled global stage-position replication;
  interface audit documented; no layer-wise cross-backbone claim. PASS
  (layer-wise cross-backbone = BLOCKED, documented).
- R3: thanked; improvements noted. PASS.

## C. Experiments: run vs not run (this round)

RUN (all pre-registered where applicable):
1. Determinism smoke (same-GPU duplicate, obj_0024): PASS after seeding.
2. Full 8-pattern binary factorial: 24 obj x 3 seeds x 8 patterns = 576 rows.
3. strict-276 confirmation: layer-LLH 276/276; layer-fixed-mean 276/276;
   layer-LHL replica 276/276 (seeded, same runner).
4. Layer-wise bake: 12 objects x {layer_llh, layer_lhl} = 24 GLB exports +
   unseen-view evaluation.
5. Same-draw global controls bake: 12 objects x {global_fixed_low, global_c3}.
6. Cohort panel generation (layer + global) with per-object seeding.

NOT RUN (with reasons):
- Equal-budget global pilot completion: runner has no resume (restart = 3.5 h);
  prior partial attempt (211/276) lacks checkpoint provenance -> internal record only.
- Layer-wise cross-backbone (MV-Adapter) run: per-block interface exists but
  requires depth allocation + recalibration + 76-object rerun (GPU-hours +
  design decisions beyond this round's pre-registered scope). BLOCKED, documented.
- LLH/LHH/fixed-mean were NOT added to the holdout beyond the pre-registered
  candidates (protocol lock forbids post-hoc additions).
- No FAC/TRB controller search (task boundary).

## D. Claims: keep / remove / downgrade

KEEP (directly supported): layer-wise vs global fixed-low paired gains
(development); complete-factorial robust directions (late-high helps,
early-high hurts); LLH > LHL and LLH > fixed-mean on strict-276 same-runner
set; LLH > LHL in the bake (12/12); stage-placement sensitivity incl.
budget-matched global HLL-vs-LLH pair; CAI as empirical diagnostic only;
non-dominance of C3 vs fixed-low; bake case-study feasibility.

REMOVED from deliverable source: +0.96 dB pooled gain; old CLIP-IQA; blinded
preference study; historical 300-object pooled tables (deleted, archived
outside the tex).

DOWNGRADED: layer-LHL from "motivated optimum" to "representative transfer
record + replica"; C3/LHL from "main method" to "shared-layer baseline";
second-backbone audit from "cross-backbone validation" to "global
stage-position replication"; old bake from "TCAS case study" to "global
conditions case study" + same-draw layer extension.

## E. Author-review readiness

- LaTeX compiles clean (main 13 pp / 0 errors / 0 unresolved refs; supplementary 7 pp / 0 errors). Reference list 1:1 with citations (43 bibitems after removing the two uncited CLIP-IQA entries; counter updated to {43}).
- Every number in the deliverable traces to a hashed artifact (Section A).
- No forbidden wording detected by audit: "uniquely optimal", "universally
  superior", "non-inferior", "equivalence", "CAI-selected", "+0.96 dB",
  CLIP-IQA, preference study, supplementary video (see grep log below).
- Remaining science gaps are stated in the manuscript (Limitations) and in
  the response letter; no BLOCKED item is presented as complete.

STATUS: ready for author final review; not submitted anywhere.

## F. Prohibited-wording grep audit

See `final_qa_grep.txt` in this directory (run 2026-09-30 on the deliverable
tex/md files). All 12 hits are negative/honest statements (e.g. "no
supplementary video is part of this revision", "the historical +0.96 dB is
retired"); no active claim uses the prohibited wording. Reference list
verified 1:1 with `\cite` usage.
