# Residual-budget controller pilot (2026-09-29)

This is an independent pilot in `/4T/tmp/mvpainter-adaptive-control`. It does
not modify the main worktree or the skeleton-validation agent's files.

## What was implemented

`TRB-TCAS` is a runtime, input-only controller:

1. Run an input-conditioned C3 pass to measure residual energy by depth group
   (`deep`, `middle`, `shallow`) and denoising stage.
2. Use those measurements as a per-depth/per-stage residual-energy budget.
3. During the actual pass, shrink the intervention when the current residual
   exceeds its calibrated budget.
4. Apply a trust region: the scale never falls below fixed-low (1.25, or the
   existing shallow-layer cap) and never exceeds the C3 mid-stage ceiling (2.50).

The unrestricted residual-budget variant (`RB-TCAS`) was retained as a
diagnostic. It improves some scalar metrics but visibly washes out texture, so
it is not a candidate method claim.

## 12-object, 50-step pilot means

All conditions use the same checkpoint, object order, and initial latent seed.

| condition | FG-SSIM | PSNR | FG LapVar | LapCorr | FG MAE | excess-HF |
|---|---:|---:|---:|---:|---:|---:|
| fixed-low | 0.3082 | 21.179 | 0.02203 | 0.1632 | 0.5958 | 0.00679 |
| C3-TCAS | 0.3068 | 20.797 | 0.01677 | 0.1490 | 0.6449 | 0.00564 |
| RB-TCAS (diagnostic only) | 0.3425 | 20.937 | 0.00845 | 0.1685 | 0.6565 | 0.00336 |
| TRB-TCAS | 0.3115 | 21.123 | 0.01930 | 0.1607 | 0.6108 | 0.00616 |

Paired TRB versus C3 over 12 objects:

- FG-SSIM: `+0.00470`, 95% t CI `[-0.00227, +0.01166]`, 8/12 wins.
- PSNR: `+0.3265`, 95% t CI `[+0.0255, +0.6275]`, 9/12 wins.
- LapCorr: `+0.01170`, 95% t CI `[+0.00504, +0.01835]`, 10/12 wins.
- FG MAE: `-0.0341`, 95% t CI `[-0.0695, +0.0013]`, 9/12 wins.

The controller therefore has a plausible signal, but the SSIM advantage is not
yet statistically decisive and the method does not dominate fixed-low on every
texture metric. The visual grid must be included with any later claim:
`outputs/trb_4obj_50step/visual_grid_gt_low_c3_trb.png`.

## Important negative result

Unrestricted RB-TCAS is not acceptable as the main method. Its scalar SSIM and
excess-HF numbers improve, but its LapVar falls to `0.00845` and the visual
outputs are visibly over-smoothed. This is evidence that a residual-energy
controller can game structural metrics by suppressing detail; it is not a
paper-ready improvement.

## Expert-review gate before claiming novelty

TRB-TCAS is more than a renamed schedule because it uses an input-conditioned
residual budget and changes only when the measured residual violates that
budget. However, the current pilot is still insufficient for a paper claim:

1. repeat on a locked 24-object probe and the strict-276 holdout;
2. report calibration overhead and an ablation for no calibration, global
   calibration, and per-depth/per-stage calibration;
3. report exact integrated residual-energy budgets and scale traces;
4. include complete-object and unseen-view visual comparisons, including
   failures, not only selected examples;
5. run at least one additional seed and verify the fixed-GT SSIM decomposition;
6. run the real baking/coverage evaluation before making a 3D-output claim.

Until these gates pass, the correct status is **promising method prototype,
not submission-ready evidence**. The previous round2 evidence-cleaned branch
remains unchanged.

## Equal-budget follow-up

The follow-up used the same 12 objects, seed, checkpoint, and 50-step protocol.
HLL and LLH were adjusted to 17 high-scale steps so their scale sum is exactly
`742.5`, matching C3's nominal schedule sum. Results:

| condition | FG-SSIM | PSNR | LapCorr | FG MAE |
|---|---:|---:|---:|---:|
| C3 (LHL) | 0.3062 | 20.769 | 0.1485 | 0.6476 |
| HLL-eq | 0.3175 | 21.104 | 0.1637 | 0.6136 |
| LLH-eq | 0.3128 | 21.637 | 0.1559 | 0.5802 |
| TRB | 0.3122 | 21.075 | 0.1612 | 0.6135 |

TRB's actual applied scale sum was approximately `568.0` per object because
the trust region shrinks many C3 mid-stage scales and the shallow cap is active;
it is therefore not an equal-budget comparison to C3. The paired result also
shows that TRB does not beat the equal-budget schedule alternatives: HLL-eq
has higher mean SSIM and LLH-eq has higher mean PSNR and lower MAE. This is a
blocking result for a strong claim that the residual controller has discovered
a uniquely preferable stage placement.

The independent expert review therefore rates the current method as
`borderline → weak reject` for a method-focused venue. The next valid move is
to either (a) redesign the controller with an explicitly equalized residual
budget and validate it on a locked holdout, or (b) honestly reposition the
paper as an auditable inference-control/measurement study. Do not run a
strict-276 claim-expansion experiment until one of these two directions is
selected and the budget definition is fixed.
