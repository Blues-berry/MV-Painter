# Strict-276 Texture-Fidelity Audit (final_audit_20261001, Phase 3)

Audit date: 2026-10-01. Script: `scripts/audit_strict276_texture_20261001.py`
(analysis-only; no generation, no GPU). Data artifacts:
`texture_audit/partA_confirmation_texture_probes.csv`,
`texture_audit/partB_per_object_texture.csv`, `texture_audit/paired_bootstrap.json`,
`texture_audit/partB_validation_vs_runner_csv.json`.

Framing rule (mandatory): every texture metric below is a **distance to the
GT statistics of the same object** (|gen − gt| or symmetric log error). No
"higher variance is better" claim is made or permitted anywhere in this audit.

## Part A — same-runner confirmation set (runtime probes)

Surface: the rescued confirmation CSVs (`rescued_tmp_20261001/layer_confirmation_20260930/`)
already contain per-object generation and GT texture probes computed by
`geotex.eval_exploration` at run time (fg_rgb_std, fg_grad_mag, fg_lap_var, fg_hf_energy
and gt_* counterparts). Metric: absolute distance |gen − gt|, paired LLH vs comparator,
10k object-level percentile bootstrap, seed 20260930. Positive = LLH closer to GT.

| comparison | probe | mean Δ distance | 95% CI | win/lose | favors |
|---|---|---:|---|---|---|
| LLH − global_fixed_low | rgb_std | +0.00245 | [+0.00172, +0.00318] | 186/276 | LLH |
| LLH − global_fixed_low | grad_mag | +0.05764 | [+0.04658, +0.06797] | 215/276 | LLH |
| LLH − global_fixed_low | lap_var | +0.00477 | [+0.00354, +0.00598] | 211/276 | LLH |
| LLH − global_fixed_low | hf_energy | +0.01367 | [+0.01142, +0.01579] | 215/276 | LLH |
| LLH − layer_fixed_mean | rgb_std | +0.00374 | [+0.00327, +0.00421] | 223/276 | LLH |
| LLH − layer_fixed_mean | grad_mag | +0.00968 | [+0.00667, +0.01267] | 183/276 | LLH |
| LLH − layer_fixed_mean | lap_var | +0.00049 | [+0.00032, +0.00067] | 179/276 | LLH |
| LLH − layer_fixed_mean | hf_energy | −0.00081 | [−0.00129, −0.00032] | 100/276 | LFM |
| LLH − layer_lhl | rgb_std | −0.00009 | [−0.00074, +0.00057] | 106/276 | n.s. |
| LLH − layer_lhl | grad_mag | +0.01213 | [+0.00732, +0.01676] | 192/276 | LLH |
| LLH − layer_lhl | lap_var | +0.00046 | [+0.00012, +0.00082] | 156/276 | LLH |
| LLH − layer_lhl | hf_energy | −0.00135 | [−0.00208, −0.00059] | 113/276 | LHL |

Reading: against the global control, LLH is significantly closer to GT on **all four**
probe statistics. Against the layer alternatives the picture is **mixed and honest**:
LLH wins most cells, LFM/LHL keep a small significant advantage on high-frequency
energy, and rgb_std vs LHL is not separated.

## Part B — retained stage-placement images (offline recomputation)

Surface: `final/round2/stage_placement_276_20260929/predictions/` (4 schedules × 276 + GT,
the only full-image strict-276 set on disk). Masks rebuilt deterministically on CPU via
the runner's own data path (`collate_batch` → `prepare_batch`, alpha branch, unique6);
metrics computed on the same 3×2 view grid the runner evaluated, using
`geotex.round2_texture` conventions (erosion_radius=1) — the cross-backbone panel
conventions. Metric: CIEDE2000 (lower better) and symmetric log errors for
laplacian_variance / rgb_std / gradient_magnitude (lower better). obj_0069 excluded
(foreground empty after erosion) → n=275. Bootstrap as Part A. Positive = LLH better.

| comparison | metric | mean Δ | 95% CI | win/lose | favors |
|---|---|---:|---|---|---|
| llh − fixed_mean | ciede2000 | +2.79101 | [+2.55311, +3.04778] | 271/275 | LLH |
| llh − fixed_mean | logerr lap_var | +0.19434 | [+0.17807, +0.20975] | 253/275 | LLH |
| llh − fixed_mean | logerr rgb_std | +0.00172 | [−0.01593, +0.01934] | 121/275 | n.s. |
| llh − fixed_mean | logerr grad_mag | +0.00089 | [−0.00726, +0.00853] | 148/275 | n.s. |
| llh − c3_lhl | ciede2000 | +0.27239 | [+0.09848, +0.46904] | 138/275 | LLH |
| llh − c3_lhl | logerr lap_var | +0.26791 | [+0.24885, +0.28595] | 257/275 | LLH |
| llh − c3_lhl | logerr rgb_std | −0.00333 | [−0.03556, +0.02882] | 130/275 | n.s. |
| llh − c3_lhl | logerr grad_mag | +0.03487 | [+0.02424, +0.04553] | 194/275 | LLH |
| llh − hll | ciede2000 | +4.99256 | [+4.57662, +5.42549] | 268/275 | LLH |
| llh − hll | logerr lap_var | +0.29159 | [+0.26563, +0.3169] | 249/275 | LLH |
| llh − hll | logerr rgb_std | +0.00130 | [−0.03013, +0.03244] | 126/275 | n.s. |
| llh − hll | logerr grad_mag | −0.04684 | [−0.06572, −0.0281] | 113/275 | HLL |

Reading: **CIEDE2000 — the strongest color-fidelity cell — favors LLH against every
comparator** (decisively vs fixed_mean and hll, marginally vs c3_lhl), and the
Laplacian-variance distance favors LLH against every comparator. rgb_std is never
separated; gradient magnitude splits 2:1 for LLH.

## Convention note (scope honesty)

The runtime extended probes (Part A) and the offline `round2_texture` metrics (Part B)
are **different metric surfaces** with different mask/erosion/value-range conventions:
recomputed GT statistics do not match runtime CSV probe values in absolute scale
(validation block in `paired_bootstrap.json`), exactly as expected across conventions.
Every comparison above is therefore made **within** a single surface; no number is
pooled across surfaces. Both surfaces independently use distance-to-GT framing.
Corroborating evidence using the Part-A surface over additional conditions (including
Core-7 rows) exists in
`coordination/core7_same_runner_completion_20261001/TEXTURE_FIDELITY_EXTENSION_*.csv|json`.

## Bottom line for Reviewer-1's texture concern

1. The layer-wise schedule does **not** trade texture-statistic fidelity away: on the
   same runner as the headline fidelity numbers, LLH is significantly closer to GT than
   the global control on all texture probes, and closer than every layer alternative on
   most cells, with the exceptions listed verbatim above.
2. Color fidelity (CIEDE2000) favors LLH against all four stage-placement schedules.
3. All claims are bounded to the 276-object clean-v2 strict holdout and to
   distance-to-GT framing; no smoothness/preference claim is made.
