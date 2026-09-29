# MV-Adapter Final Interpretation

## Bottom line

The 76-object Exact Mesh aggregation is complete and contains no new
inference. LHL `(0.75,1.00,0.75)` is a direct shape-transfer diagnostic, not a
CAI-calibrated schedule. The frozen CAI rule did not produce a legal unique
winner: its status remains `undefined_set_valued` for both the original
initial-grid stage and the independent selected-pair stage.

The data support measurable temporal-placement differences within this
MV-Adapter backbone, but not a uniformly dominant stage placement. LHL has no
clear practical advantage over conservative fixed-low or the equal-budget
fixed-mean control. The new evidence is therefore diagnostic and exploratory,
not a positive confirmation of a uniquely selected adaptive schedule.

## Evidence inventory

### A. Initial-grid calibration

The original 24-object Exact eight-stage rows used `low=0.75` and
`high=1.50`. They are retained as an initial-grid stage ablation. They must
not be described as the eight-stage calibration of the later selected Pareto
pair `(0.75,1.00)`.

### B. Selected-pair stage calibration

The independent 24-object supplement used the same Exact calibration objects,
seed, reference image, geometry-conditioning implementation, inference steps
and evaluation metrics, with `low=0.75` and `high=1.00`. Its frozen rule still
returns `undefined_set_valued`; no tie-breaking rule was added after seeing
the results. Thus there is no CAI stage winner to transfer to the holdout.

### C. Direct LHL shape-transfer

LHL was run on the same 76-object Exact holdout and compared with no geometry,
fixed-low, fixed-1.0, and the h1.50 historical dynamic baselines. It is
labelled **Direct LHL shape-transfer diagnostic**. It is not renamed after the
fact as CAI-calibrated.

### D. Equal-budget follow-up ablation

Fixed mean, HLL, LHL and LLH were compared with nominal mean scale
`5/6 = 0.8333333333333334`. This is a targeted follow-up on an already-used
holdout. It matches nominal scale mean only; it does not establish equality of
the accumulated geometry residual norm, residual direction, or effective
conditioning strength.

## Mechanism-level answers

### Is there an observable stage-position effect on the second backbone?

Yes, within the MV-Adapter results there are measurable paired differences
among equal-budget placements. For example, LHL is higher than HLL in mean
Edge-SSIM by `0.000613` with a paired 95% CI `[0.000135, 0.001217]`, and
higher than LLH by `0.000261` with CI `[0.000032, 0.000522]`. Other metrics
do not move uniformly: LLH has the highest mean PSNR among the four
equal-budget conditions, while LHL has the highest mean FG-SSIM and
Edge-SSIM, and its GT-relative texture error is higher than fixed mean and
LLH. These patterns are evidence of stage-position sensitivity, not evidence
that one position dominates every target.

The comparison is within the MV-Adapter backbone. A formally matched
equal-budget result for the other backbone is not available in the current
evidence set, so no cross-backbone same-direction claim is made here.

### Does LHL provide a practical gain over conservative fixed-low?

No uniform practical gain is established. LHL has a paired PSNR difference of
`-0.013114` (CI `[-0.062438, 0.020680]`) relative to fixed-low. The small
FG-SSIM difference is positive, while the LPIPS, Delta E00 and texture-error
differences are mixed and their CIs include zero. This does not justify
selecting LHL as a practical replacement for fixed-low.

### Does LHL differ from equal-budget fixed mean?

No clear difference is established. The LHL-minus-fixed-mean CIs cross zero
for all six reported metrics. The mean values are close, and the modest
directional variations should be treated as exploratory rather than as a
confirmed shape or texture improvement.

### Did CAI produce a unique choice?

No. The frozen CAI algorithm is set-valued/undefined. That statement means
only that the pre-specified rule failed to define a legal unique selection; it
does not mean that all schedules are statistically identical. The complete
paired table and bootstrap JSON preserve the observed stage effects without
turning any favorable holdout row into a CAI winner.

### Which conclusions are exploratory?

The matched-range h1.00 linear/cosine reruns, direct LHL holdout, and
equal-budget fixed-mean/HLL/LLH comparison are all follow-up or diagnostic
analyses on the existing Exact holdout. They are useful for mechanism
description and scale fairness, but they are not the original frozen
confirmatory selection protocol. Any architecture-level explanation based on
geometry residual injection position, amplitude, or backbone design remains a
hypothesis: the present results do not identify a causal mechanism.

## Evidence boundaries

- **Exact Mesh provenance:** satisfied for the reported cohort; the GLB
  recovery manifest and source hashes are retained in the recovery directory.
- **Calibration/holdout separation:** satisfied for the 24-object calibration
  versus 76-object holdout split used by these analyses.
- **Pretraining disjointness:** not established. Exact GLB recovery does not
  prove that the 76 object IDs are disjoint from the official MV-Adapter
  pretraining UID list; that list was not available for a definitive overlap
  audit.
- **Scale fairness:** h1.50 historical linear/cosine rows are not mixed with
  the h1.00 matched-range rows. Fixed-low, fixed-1.0 and no-geometry were
  reused only after source-code verification that their outputs do not depend
  on the unused `high` argument.
- **Cross-backbone comparison:** no absolute PSNR comparison is made between
  MVPainter and MV-Adapter. A same-protocol second-backbone equal-budget
  comparison is not complete in the current evidence, so no shared-direction
  or causal mechanism claim is made.
- **Model provenance:** the actual Manojb SD2.1 mirror and its recorded commit
  and component hashes are in `BASE_MODEL_VERIFICATION.json`; no replacement
  source is silently substituted.

The shared implementation provenance is `run_experiment.py` SHA-256
`ac29e58c7c8efa1d95799cb2d02b59f34941252a151ff7ce16524d7791a1f6a3`,
`geometry_scale.py` SHA-256
`a89f15042696b06a1e8fb5196fc7da2cd816cbf1cc94f49c880edf6188edcde4`, and
`data_manifest.json` SHA-256
`d256c9327d35c26dbcab4dc0cb30d1cffb7802e27827d9950763529df0211db5`.
All compared runs use seed `20260928` and 50 inference steps. The base-model
record resolves to Manojb commit
`0094d483a120f3f33dafbd187ea4aa60d10de75c`; the component SHA-256 values are
preserved in `BASE_MODEL_VERIFICATION.json`.

## Reproducibility files

- Unified means: `MV_ADAPTER_UNIFIED_RESULTS.csv`
- Complete LHL paired statistics: `MV_ADAPTER_PAIRED_COMPARISONS.json`
- Scale audit: `MV_ADAPTER_EXACT_SCALE_AUDIT.md`
- Matched-range follow-up: `MV_ADAPTER_MATCHED_RANGE_RESULTS.md`
- Equal-budget follow-up: `MV_ADAPTER_EQUAL_BUDGET_RESULTS.md`
- Original/selected-pair protocols: `results/calibration_exact_24/` and
  `results/calibration_exact_selected_pair_24/`
- Holdout protocols: `results/holdout_exact_*_76/PROTOCOL.json`

The aggregation command was:

```bash
PYTHONPATH=. python final/round2/mv_adapter/generate_unified_results.py
```

No `final_round2.tex` or `response_letter_round2.md` file was modified.
