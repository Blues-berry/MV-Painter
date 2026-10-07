# E6 development protocol — freeze before calibration or new outputs

## Identity and separation

Use all 24 UIDs, in the original order, from
`final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt`. This is a reused
development cohort. Fresh B/C/D outputs cannot select parameters. Preserve the
frozen runner, wrapper, checkpoint, config, metric and generation hashes from
E5; import them without changing the core sources. New E6 hooks are separately
hashed. Do not mutate E5 locks, sources, results or the submitted manuscript.

Three sequential stages:

1. **Calibration:** 24 native-GFL generations at latent seed 42, no image metrics.
   Collect unscaled r/h and applied-scale traces. Derive q using the fixed
   two-level median rule in the method spec. Hash and freeze the references.
2. **Technical:** original probe indices 0,4,9,13,16,21; per object native C3,
   C3 observer no-op, and the three candidate multipliers. Exactly 30 generations;
   no image quality metrics or visual inspection.
3. **Development quality:** only after the technical gate passes, all 24 objects
   at latent seeds 42,43,44, four conditions C3 and the three multipliers. Exactly
   288 generations. Metrics and generated mosaics are stored locally. Development
   outputs are not confirmation and no significance criterion selects k.

Calibration + technical + development = 342 generations, with no post-output
expansion. Input sampling remains `object_seed=42+original_index` for every
condition and latent seed, so generation-seed sensitivity cannot change views.
Initial latent and diffusion random seeds use the stated latent seed. Seeds are
nested within object; metrics average over seeds before computing object effects.

## Technical gate

- Baseline and observer-no-op output SHA-256 agree on all six objects; input
  hashes agree across all five conditions for each object.
- All wrapper steps record the reference-write skip unchanged; every group
  supplies target-read traces for every step. Expected nine wrappers are checked
  from the actual model; write/read counts must match within each wrapper/step.
- Every active scale is finite, nonnegative and no larger than its original cap.
- For each group x multiplier, at least 99% of nonzero, non-saturated steps have
  realized correction-norm error <=5% relative to the *bounded applied target*.
  Saturated steps stay in the report and are not scored as achieving the original
  requested target. Report the saturation and zero-norm fractions separately.
- The math tests cover zero/invalid values, exact caps, discrete C3 windows, and
  execution tests cover reference preservation, no-op identity and one scalar
  across the mosaic. GPU nonfinite/zero input cases stop the gate; no data removal.

Any gate failure terminates this candidate; no magnitude/cohort/cap retuning.
An infrastructure error may resume only with the same lock; all attempts and
partial rows remain recorded. Integrity includes unique expected rows, all
seven finite metrics, saved output hashes and shared input identity before
reading quality results.

## Fixed selection and stop rule

For each k, average its paired FG-PSNR and FG-LPIPS deltas versus C3 within object
over all three seeds, then average over the 24 objects. Qualify only if PSNR>0
and LPIPS<0. Rank qualifying k by lower mean LPIPS delta, higher mean PSNR delta,
then smaller distance to 1, then lower k. If none qualify, stop E6 and record
`STOP_DEVELOPMENT_NO_JOINT_GAIN`; do not begin Fresh D.

Store all candidates, object deltas, seed means, cap gaps and runtime costs.
Any intervals are descriptive development intervals, not independent efficacy.
If a candidate qualifies, derive its object-independent fixed-scale ablation
from development-only average applied traces at each group/step, freeze the
selected multiplier and require the separate contribution-difference review.

## Confirmation handoff — not permission to run early

Fresh D is untouched and disjoint from all historical/training/development and
the entire Fresh C candidate queue. Default N=300; estimate paired-delta SD from
development and plan 90% marginal power at conservative two-sided alpha .025
for 0.5 dB and .01 LPIPS. Use the larger required N, with floor 300 and ceiling
600, frozen before D outputs. This approximation does not guarantee joint power;
report it as planning only. If required N exceeds 600, keep 600 with the expected
precision limitation recorded before output, never sequential significance-based
expansion. No non-inferiority margin is implied.

Nine conditions are those in the user-approved plan. Fixed-scale traces are
development-derived; pooled-reference q is the median of the three q_l values;
static-target ablation sets a(t)=1. Primary family: two endpoints for new−C3.
Baseline family: eight tests (PSNR/LPIPS x GFL/GFH/no-adapter/generic-linear).
Ablation family: six tests (PSNR/LPIPS x three ablations). Holm within each
family, two-sided paired object tests, 10,000 object bootstrap draws; report
nominal intervals explicitly. Joint improvement requires both corrected primary
tests and both expected directions; do not turn other endpoints into primaries.
Five other Core7 metrics remain secondary descriptive endpoints. Fresh D and
human/GLB final locks must exist before their respective output/response exposure.
