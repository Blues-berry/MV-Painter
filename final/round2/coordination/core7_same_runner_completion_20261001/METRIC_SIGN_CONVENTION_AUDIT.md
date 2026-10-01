# AUDIT — Paired-delta sign convention across all analysis chains (2026-10-01)

Scope: every analysis script that reports paired deltas / bootstrap CIs for
paper-facing comparisons. Trigger: external review noted that
"LLH − GFL FG-LPIPS = +0.0308" cannot be the literal difference
LPIPS(LLH) − LPIPS(GFL) (which would be negative if LLH is better), so the
wording "first minus second" must be checked against the code.

## Finding (one line)

**All chains use the same benefit-oriented transform in code; the code is
internally consistent. One experiment report and one protocol lock describe
the transform ambiguously ("first minus second") without stating the
lower-is-better reversal. No numeric result is affected.**

## Per-chain code evidence

| Chain | Script | Transform | Effective convention |
|---|---|---|---|
| Main backbone (strict-276 confirmation) | scripts/analyze_layer_confirmation_20260930.py L37-38 | `sign = BETTER[metric]; diffs = sign * (a - b)` | positive = first condition better |
| Robustness-1 (R0/R1) | scripts/analyze_robustness1_20260930.py L57-58 | same `BETTER` map, `sign * (a - b)` | positive = first condition better |
| MV-Adapter panel | final/round2/mv_adapter/analyze_layerwise_panel_20260930.py L22,L85 | `delta = (a - b) if metric not in LOWER_BETTER else (b - a)` | positive favors LEFT condition |
| MVDiffusion panel | scripts/analyze_mvdiffusion_panel_20260930.py L25-26,L90 | same LOWER_BETTER form | positive favors LEFT condition |

`BETTER` map (main backbone): fg/full_psnr +1, fg/full/edge_ssim +1,
fg/full_lpips −1. `LOWER_BETTER` set (cross-backbone): fg_lpips, ciede2000,
gt_relative_texture_error. The two encodings are equivalent.

## Wording audit

| Document | Wording | Verdict |
|---|---|---|
| CROSS_BACKBONE_VALIDATION_MVADAPTER.md L66 | "Positive favors the left condition (LPIPS/dE00/GT-texture lower-better)" | correct |
| CROSS_BACKBONE_VALIDATION_MVDIFFUSION.md L88 | same | correct |
| MAIN_BACKBONE_ROBUSTNESS1_REPORT.md L77 | "Mean paired deltas (first minus second)" | **ambiguous** — omits the benefit transform; a literal reader computes LPIPS(LLH) − LPIPS(GFL) < 0 and sees a contradiction with the reported +0.0308 |
| main_backbone_robustness1_20260930/PROTOCOL_LOCK.md statistics plan | "'minus' = first minus second" | same omission |
| EXPERIMENT_PROTOCOL_LOCK (revision_next_20260930) | no explicit sign statement | neutral |

Recommended canonical sentence for future documents (and for the paper's
statistics section when the next paper-edit window opens):

> "For lower-is-better metrics (LPIPS, CIEDE2000, GT-relative texture
> errors), paired differences are sign-reversed so that positive values
> uniformly denote improvement of the first-named condition. Deltas are
> never pooled across metrics with different directions."

## Action taken

- Erratum-style clarification appended to the Robustness-1 report directory
  as a separate file (original report left untouched):
  `METRIC_SIGN_CONVENTION_ERRATUM.md` (same directory).
- This audit + the Core-7 protocol lock adopt the raw-delta convention with
  explicit per-metric direction labels (no reversal), which is unambiguous
  by construction.
- Cross-backbone reports need no change.

## Win-rate check

Win rates in all chains count `delta > 0` as a win under the SAME
benefit-oriented transform (analyze_layer_confirmation L44 `d > 0`;
robustness1 same; panel scripts `win_rate` on the transformed delta), so
win rates are consistent with the reported deltas. No mixed convention
found between delta and win-rate within any chain.
