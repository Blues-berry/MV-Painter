# Final GO / NO-GO: View-wise Counterfactual Geometry Control

## Decision

**STOP. Do not develop a formal R2.1 controller from this mechanism.** Keep the earlier BAVGC STOP and its files unchanged. This new experiment answers a different causal question, but it does not establish that legal reference-view error is a useful control signal for unseen-view baked quality. Do not expand to the remaining four objects or search new scales, schedules, groups, signals, or candidate rules. Return to the final 1014 empirical paper revision.

This is a six-object, one-seed, purposively selected exploratory counterfactual test, not an independent validation. The intervention was real, paired, and passed identity gates; the method gate failed.

## A–D answers

### A. Can view-wise geometry-budget changes stably change final baked quality?

The perturbations change generated pixels and produce a small B+ versus B− baked-LPIPS difference: B+ is lower on 5/6 objects, with object-bootstrap mean ΔLPIPS (B+−B−) of −0.000153 and 95% interval [−0.000311, −0.000018]. This is evidence of a local response under the frozen setting, not a practically established improvement. Against B0, fixed B+ improves the mean by only 0.000093 and its interval includes zero; fixed B− is slightly worse on average. Thus a scale transfer can alter the bake, but a reliable, useful quality gain over the baseline has not been shown.

### B. Can observable reference appearance error guide that change?

**No.** The lower-error action matches the lower unseen-bake-LPIPS action for only 3/6 objects with RGB MAE and 4/6 with CIEDE2000. Their exact intervals are broad. For one object the two source metrics select opposite actions; other objects show lower reference error paired with worse nonreference-view LPIPS or worse baked LPIPS. MAE-selected and CIEDE-selected two-call policies each beat B0 on 4/6 objects, but both mean effects are small and both object-bootstrap intervals cross zero.

### C. Does the mechanism go beyond simple scheduling or two-candidate selection?

**No.** The paired B+/B− probe is a useful causal test of this GeoTex adapter, but choosing between two complete outputs by the lower reference error is ordinary test-time candidate selection. It requires two full generation trajectories. A fixed one-call B+ policy has a slightly better mean LPIPS than either reference-selected policy on this cohort. The prior-art review also finds online feedback scale selection, scheduled ControlNet scales, geometry/reference conflict handling, and UV-space multiview guidance. The present rule has no established algorithmic distinction or compute-adjusted advantage.

### D. Is it worth continuing toward R2.1?

**No. STOP the method search.** The action direction is not reliably identified by the legal feedback, selected policies do not outperform simple fixed control, their additional compute is not repaid, and novelty is weak. Resume the 1014 empirical revision without adding this mechanism as a method claim.

## Frozen test and evidence

- Six previously exposed GeoTex objects; conditions B0, B+, B−; 18 successful generations total; one shared seed/input realization per object.
- δ = 0.20, steps 34–49, deep/middle only. Applied-scale sums remained 9.90 over all six views per affected step/group after native caps. Shallow remained uniformly capped at 0.8.
- The six B0 generation panels, all six B0 UV textures, and all 66 B0 native-EGL renders match the historical Fixed Mean outputs pixel-for-pixel. Same object inputs and initial latent hashes are recorded across the three conditions.
- Twenty-four UV bakes were completed (GT plus three conditions per object). The evaluator scored 11 unseen cameras per object from the unchanged GLB and UV map. B0, B+ and B− mean foreground LPIPS are 0.141271, 0.141178 and 0.141331.
- All six objects and outputs are retained. Generation time was 154.91 s over 18 calls, excluding model load and metric evaluation. The 24 bake metadata timestamps span about 470 s; the 264-image native-EGL render took 11.1 s. A B+/B− choice costs two trajectories, compared with one for fixed B+.
- Renderer assessment is unlit base-color-only. This study does not claim full PBR or human-fidelity results. The cohort is small and purposive; object bootstrap intervals are descriptive.

## Provenance and retained records

- [Frozen protocol](COUNTERFACTUAL_PROTOCOL.md)
- [Intervention identity audit](INTERVENTION_IDENTITY_AUDIT.md)
- [Per-object condition metrics and response summary](ACTION_RESPONSE_RESULTS.csv) · [JSON summary](ACTION_RESPONSE_SUMMARY.json)
- [Reference-to-bake direction analysis](SOURCE_TO_BAKE_DIRECTION_ANALYSIS.md)
- [Counterexamples and visual evidence](FAILURE_CASES.md)
- [Prior-art and novelty review](PRIOR_ART_COMPARISON.md)
- [Source and artifact hash manifest](SOURCE_HASH_MANIFEST.json)
- [All-object unseen-view comparison](visuals/ALL_OBJECTS_ALL_CONDITIONS_11VIEWS.png)

The implementation is isolated in worktree `/4T/tmp/MV-Painter-counterfactual`, branch `codex/counterfactual-view-control-20261014`, based on `384f97e2a6e23b17555fa88f1a7f5fcb48d6e3bb`. It is not merged. The original BAVGC archive, 1014 paper and supplement, checkpoint, historical data and main tracked files were not changed by this study.
