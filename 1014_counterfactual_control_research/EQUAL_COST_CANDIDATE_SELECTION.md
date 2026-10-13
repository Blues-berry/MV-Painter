# Equal-Generation-Cost Candidate Selection Check

## Why this add-on was run

The six-object B0/B+/B− study used two complete trajectories for a feedback-selected B+/B− action, while a fixed B+ profile needs one. Phase C explicitly requires a same-generation-count simple candidate baseline. This add-on keeps the same six objects, does not change the view-budget perturbation or expand the cohort, and adds one second Fixed Mean candidate per object. Total new generations are 24/30.

## Frozen comparison

- Candidate A is the original Fixed Mean B0 run with latent seed 42.
- Candidate B is another Fixed Mean B0 run with latent seed 43. Object ordering, source views, target views, conditioning, geometry features, checkpoint, config, 50-step schedule and B0 scales are unchanged.
- Across all six objects, input hashes are identical between candidates except for the initial latent. B0 requested/applied scales remain the Fixed Mean values, including the native shallow cap. The fresh B0(seed42) UV textures are pixel-identical to the prior Fixed Mean textures for all six objects.
- For each object, choose the lower reference RGB MAE candidate; separately repeat with lower reference CIEDE2000. These two calls are the equal-cost, no-view-budget-control best-of-two baseline.
- Compare against the original two-call policy that generates B+ and B− with the same latent seed and chooses the lower reference error. Ground-truth and unseen-camera scores are used only after the candidate decisions are fixed.

## Results

Both reference metrics selected the same Fixed Mean candidate on all six objects in this realization.

| Two-call policy | Mean object LPIPS | Object-bootstrap 95% interval | Better than Fixed Mean best-of-two |
|---|---:|---:|---:|
| Fixed Mean best-of-two, selected by reference MAE | 0.139807 | [0.094898, 0.185240] | reference |
| B+/B− action choice, selected by reference MAE | 0.141199 | [0.096696, 0.187384] | action lower on 3/6 |
| B+/B− action choice, selected by reference CIEDE2000 | 0.141187 | [0.096647, 0.187384] | action lower on 3/6 |

For the paired MAE comparison, action minus Fixed Mean best-of-two is +0.001392 LPIPS with object-bootstrap interval [−0.004838, +0.007499]. For CIEDE2000 selection it is +0.001380 [−0.004838, +0.007499]. The point estimates favor simple Fixed Mean candidate selection; the six-object intervals are wide. Neither feedback rule demonstrates an equal-cost advantage.

| Object | Fixed Mean candidate chosen by MAE / CIEDE | Fixed Mean best-of-two LPIPS | B+/B− selected action by MAE | Action LPIPS | Action minus fixed best-of-two |
|---|---|---:|---|---:|---:|
| `1dc2c857` | seed43 / seed43 | 0.143714 | B+ | 0.152782 | +0.009068 |
| `21678bd6` | seed42 / seed42 | 0.171982 | B− | 0.171900 | −0.000082 |
| `238ff3e4` | seed42 / seed42 | 0.058953 | B− | 0.059094 | +0.000140 |
| `2dd9bc81` | seed42 / seed42 | 0.237632 | B+ | 0.237469 | −0.000163 |
| `2f6c9448` | seed43 / seed43 | 0.081205 | B− | 0.093236 | +0.012031 |
| `e261c0fe` | seed43 / seed43 | 0.145356 | B− | 0.132713 | −0.012643 |

This comparator confirms that a two-call error-based choice can benefit from candidate sampling without changing view budgets. The view-action selection did not beat that simple equal-cost control on average or across most objects. It remains ordinary test-time selection rather than evidence for a distinct controller.

## Cost and limits

The six additional generations took 46.45 seconds of measured inference. The original 18 calls took 154.91 seconds, for 201.36 seconds across all 24 calls; model loading and offline scoring are excluded. Both compared policies require two generation calls per object. The add-on uses one extra latent realization on the same six purposive development objects, so it is an exploratory compute-matched comparison rather than independent confirmation.

All six seed-43 panels, residual-dose logs, source metrics, baked textures, GLBs and 66 unseen-camera renders are retained in `EQUAL_COST_BASELINE/`. The 198-render native-EGL manifest also includes GT and the seed42 B0 replay as identity checks. `EQUAL_COST_BASELINE/ARCHIVE_MAP.md` maps the isolated execution records to their archived copies.
