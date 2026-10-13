# Layer-wise revision evidence index

## Version boundary

This index belongs to the author-review layer-wise revision compiled from
`final/round2/final_round2.tex` and `supplementary_round2.tex`. The previous
manuscript, PDFs, response letter, historical records, and old experimental
branches remain archived under
`final/round2/archive/revision_before_layer_lhl_20260929/` and are not
overwritten.

## Claim-to-evidence map

| Claim | Direct evidence | Scope / restriction |
|---|---|---|
| Layer-wise residual control improves foreground quality over global fixed-low | `layer_lhl_v1/ablation_summary.json`, three raw per-seed CSVs, Table 1 in the manuscript | 24 objects × 3 seeds; development ablation; paired shared inputs |
| Layer-LHL is not a universal optimum | Same summary; layer-fixed-mean and layer-LLH rows; paired bootstrap intervals | In the development protocol, layer-fixed-mean is better on FG-LPIPS and layer-LLH is better on all seven reported metrics; no selector claim |
| Layer-LHL gain transfers beyond the development objects | `LAYER_LHL_HANDOFF_20260929.md` and `handoff_verification.json` | Independent strict-276 transfer record; not a paired replacement for the new development ablation |
| Generic schedule comparison | Existing original-protocol warm-up/cosine audit in Supplementary S5 and frozen E0/E1 records | Separate strong-residual protocol; not mixed with clean-v2 layer-wise numbers |
| Real 3D path is operational | Existing 12-object bake audit and contact sheet in Supplementary S4 | Descriptive case study; does not establish a layer-LHL or population-level 3D advantage |
| Cross-backbone boundary | Existing Exact-GLB 76-object MV-Adapter audit | Compatibility/stage-position diagnostic only; no layer-LHL cross-backbone causal claim |

## New layer-wise artifact paths

- `layer_lhl_v1/ablation_summary.json`: frozen means and paired bootstrap intervals.
- `layer_lhl_v1/shared_input_hashes.json`: target, geometric input, geometric feature, and initial-latent hashes for 24 objects and 3 seeds.
- `layer_lhl_v1/raw_csv/seed42_per_object_metrics.csv` (and seed43/seed44): raw paired rows.
- `layer_lhl_v1/seed42_evaluation_manifest.json` (and seed43/seed44): object, view, checkpoint, and output provenance.
- `layer_lhl_v1/ARTIFACT_SHA256SUMS.txt`: copied artifact checksums.
- `layer_lhl_v1/obj_0000_ablation_comparison.png`: representative visual only; not a substitute for the paired statistics.
- `layer_lhl_v1/layerwise_visual_success_panel.png`:正文用 GT/fixed-low/C3/layer-LHL 并排图。
- `layer_lhl_v1/layerwise_visual_tradeoff_panel.png`:正文用 layer-fixed/layer-LHL/layer-LLH 反例图。

## Interpretation rule

The revision may claim a concrete, training-free layer-wise control and a
conditional foreground-quality benefit under the frozen protocol. It may not
claim that layer-LHL, LHL, C3, or any CAI-derived schedule is globally or
universally optimal. A metric or protocol not listed above cannot be used as
direct support for the main contribution.
