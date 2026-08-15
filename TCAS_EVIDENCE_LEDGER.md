# TCAS evidence ledger

This file is the compact provenance map for the current paper revision. Results
from different checkpoints or scale semantics must not be combined.

## Frozen primary protocol

| Field | Value |
|---|---|
| Formal paper source | `final/final_submit.tex` |
| Primary checkpoint | `mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt` |
| Scheduler / steps | `EulerDiscreteScheduler.from_config(...)`, `set_timesteps(50)` |
| Seed | 42; schedules within each run share initial latents |
| Main adapter semantics | capped forward; effective scale is `min(requested_scale, layer cap)`; caps deep/middle/shallow = 3.0/3.5/0.8 |
| Probe / validation | 24-object probe (`obj_0000`--`obj_0023`); frozen schedule on disjoint 276-object holdout (`obj_0024`--`obj_0299`); 300-object full pool is descriptive |
| Primary metrics | PSNR, FG-SSIM, foreground MAE; LapVar is a diagnostic only |

## Evidence-to-claim map

| Claim | Evidence | Allowed wording |
|---|---|---|
| Early high intervention is damaging in v2 | `stage_ablation_v2_24obj_rerun/stage_utility_analysis.json`; PSNR delta -0.788 dB, CI [-1.420,-0.156] | Conditional on this adapter/checkpoint/cap regime |
| Middle intervention gives the main fidelity gain | Same file; PSNR delta +0.574 dB, CI [0.391,0.756] | Supports middle-stage concentration |
| Late intervention is structurally neutral | Same file; FG-SSIM delta +0.001, CI [-0.002,0.003] | Do not claim late high is intrinsically harmful |
| C3 is a robust compromise | `mvpoutput/revision_c3_sensitivity/`, `mvpoutput/revision_top2_300/` | Robust conditional schedule, not universal optimum |
| C3 transfers without re-searching | A2 300-object CSV and summary | Frozen transfer evidence |
| Residual normalization is not an independent method | `norm_schedule_v2_strength_match_6obj/`; norm_flat equals fixed_low_weak objectwise | Mechanism diagnosis only |

## Prohibited evidence mixing

- Do not mix `refattn_v1`, v2, and v3 numerical tables.
- Do not interpret LapVar without PSNR/FG-SSIM and artifact or perceptual evidence.
- Do not use the old `stage_ablation_v2_24obj` summary in place of the rerun.
- Do not describe C3 as adapter-independent or globally optimal.
- Do not describe residual normalization as an adapter-agnostic upgrade.

## Reproducibility entry points

- Stage utility: `geotex/explore_stage_ablation.py` and `geotex/analyze_stage_utility.py`.
- Normalization audit: `geotex/explore_norm_schedule.py`.
- Latest stage output: `mvpoutput/explore_contradiction/stage_ablation_v2_24obj_rerun/`.
- Latest normalization audit: `mvpoutput/explore_contradiction/norm_schedule_v2_strength_match_6obj/`.
- Disjoint holdout recomputation: `mvpoutput/revision_holdout_split/holdout_summary.json` via `geotex/analyze_holdout_split.py`.
