# E5 residual-dose feasibility protocol

**Status:** Freeze before the E5 run. Development-only; no quality metrics or
visual judgments will be collected or inspected.

## Question and boundary

Can a small additive perturbation, aligned with each adapter correction and
normalized to the current hidden-state norm, be applied at a fixed layer group
and denoising window with controlled numerical error? This pilot only tests
implementation feasibility. It does not test whether equalized dose explains
the response surface, improves texture quality, or establishes a layer-by-time
mechanism.

## Fixed inputs and run size

- Use the existing 24-object development probe in its original UID order and
  preserve `object_seed = 42 + original object index`.
- Select indices `0, 4, 9, 13, 16, 21` before this pilot; record their UIDs and
  the probe list hash in `E5_LOCK.json`.
- Generate one unmodified baseline and one alpha-zero hook no-op per object,
  then the fixed Cartesian product of 3 groups (`deep`, `middle`, `shallow`),
  3 windows (W1 steps 0–9, W3 steps 20–29, W5 steps 40–49), and 3 magnitudes
  (`alpha = 0.005, 0.01, 0.02`). Total: 174 generations, 87 per GPU shard.
- Keep the frozen checkpoint, config, shared six-view input path, 50-step
  EulerDiscreteScheduler, seed 42, and capped low-profile baseline. Do not
  compute or inspect image metrics; persist output tensor hashes only.
- Lock hashes for the runner, adapter wrapper, reference-only pipeline,
  generation/data/metric utilities, checkpoint, config, pilot, and auditor.

## Intervention and measurements

For each targeted wrapper during the selected group/window, let `h` be the
pre-adapter hidden state and `r` the unscaled adapter correction. The baseline
wrapper first applies its existing native scale and cap. Then add

`delta = alpha * ||h||_2 * r / ||r||_2`.

Cast `delta` to the activation dtype, add it to the baseline wrapper output,
and measure the actually realized output increment after dtype rounding.
Record hidden norm, raw correction norm, capped baseline scale, cap, requested
delta, realized delta, relative target error, dtype, and any zero/nonfinite or
reference-pass skip. This additive diagnostic can take the total correction
beyond the native cap; it is not a candidate deployed profile and must not be
described as a cap-respecting method result.

The reference-only UNet executes a write pass and a target-read pass for each
denoising step. The pilot must log both calls, leave every write-pass call
unchanged, and apply the diagnostic only on the read pass. It also logs the
realized delta-to-raw-correction norm ratio as an equivalent extra scale, with
an explicit flag when the combined equivalent scale is above the native cap.

## Technical gates

1. For every object, baseline and alpha-zero no-op generated tensors must have
   identical SHA-256 values.
2. The unmodified reference-write path must receive no intervention.
3. For each requested magnitude and each layer group, at least 99% of active
   wrapper-step interventions must have finite values and an actually realized
   relative-dose error at or below 5%.
4. All zero-hidden, zero-correction, nonfinite, and cap-context cases remain in
   the ledger; none may be removed from denominators after launch.
5. Any failed technical gate ends E5. Do not change magnitudes, groups,
   windows, objects, caps, or implementation to obtain a pass.

No positive/negative image-quality result can be produced by this protocol.
Passing E5 permits only the statement that the diagnostic is numerically
implementable on this development subset. A confirmatory dose-matched campaign
would require a new, disjoint object cohort, a separate frozen protocol, and a
review of whether the paper still needs that mechanism claim.
