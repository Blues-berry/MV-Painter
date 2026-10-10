# E5 residual-dose feasibility report

**Run status:** completed; numerical implementation gate PASS.

**Scientific status:** no quality-effect or dose-independent mechanism evidence.

**Chronology:** protocol and code frozen at 2026-10-06 07:04 UTC, after the
earlier V3/B outcomes were known and before E5 outputs.

**Scope:** six reused development-probe objects; not a new cohort.

## Fixed design and provenance

The pilot ran 174 generations on two RTX 5090 GPUs: one native low-profile
baseline, one alpha-zero hook no-op, and 27 fixed group × window × relative-dose
conditions per object. It preserved the original probe indices and
`object_seed = 42 + index`; no quality metric was computed, and generated image
tensors were stored only as hashes. The write/read behavior of the
reference-only UNet was handled explicitly: every reference-write wrapper call
was logged unchanged, and additive residual perturbations were applied only on
the target-read pass.

The pre-run lock is `data/e5_residual_dose/E5_LOCK.json`; launch identity,
shard outputs, runtime versions, and per-wrapper traces are in the ignored
local `data/e5_residual_dose/runs/` directory. Their hashes are recorded in
`E5_TECHNICAL_GATE.json` and `E5_CAP_CONTEXT_SUMMARY.json`. The compact gate and
cap summary are suitable for the public evidence package; raw traces and model
assets are not required to reproduce this development-only summary when the
hash-indexed local ledger is available.

## Result

The exact alpha-zero output hash matched the baseline for all six objects.
Across 4,860 active target-read wrapper-step interventions, all values were
finite and every group × alpha stratum had 100% of steps within the predeclared
5% relative-dose error bound. The largest observed error was 0.00470 (0.47%);
there were no zero-norm or infeasible numeric steps. All 4,860 reference-write
calls were logged as unchanged. The GPU runtime was PyTorch 2.7.1+cu128,
Diffusers 0.37.0, and two NVIDIA RTX 5090 devices. Full counts and intervals
are in `data/e5_residual_dose/E5_TECHNICAL_GATE.json`.

The separately prelogged cap context shows why this technical result cannot
be promoted to a cap-respecting, three-group dose match. The equivalent total
scale is an L2 norm ratio after dtype rounding, not an exact scalar multiplier.
Deep and middle had no cap-exceeding steps at any tested alpha. Shallow exceeded
its native cap of 0.8 in 164/540 steps (30.4%) at the smallest tested alpha
0.005, 211/540 (39.1%) at 0.01, and 360/540 (66.7%) at 0.02. The complete
stratified values are in `data/e5_residual_dose/E5_CAP_CONTEXT_SUMMARY.json`.

## Reviewer and paper consequence

E5 establishes only that this additive diagnostic can be realized numerically
on a small, previously used development set. It does not show that the quality
response is stable under equalized dose, that layer × window interaction is
causal beyond the tested native scale profiles, or that a method improves
texture quality. At the frozen magnitudes, the shallow-layer cap prevents a
three-group cap-respecting match; lowering alpha, changing the shallow dose,
or changing the grouping after seeing this result would be an unregistered
redesign and was not done.

For the current revision, treat all Layer × Window results as conditional on
the named requested/effective scale and native cap profile. Withdraw any
dose-independent mechanism interpretation. A future cap-aware mechanism study
would need a new intervention definition, a new disjoint object cohort, and a
separate pre-output protocol; it is not justified as an add-on to this revision
because it would change the method question and reopen R2.1. This finding does
not resolve R1's human/3D fidelity concerns or R2's contribution-sufficiency
judgment.
