# MV-Adapter Round 2 — Exact Calibration Final Handoff

Date: 2026-09-29  
Scope: Codex B, Exact Mesh calibration and direct LHL transfer diagnostic

## Executive result

The ten previously missing GLBs are restored as 10/10 `Exact` assets. The
canonical proof is in `GLB_RECOVERY_MANIFEST.json` and
`GLB_RECOVERY_AUDIT.md`; all ten official Objaverse-XL SHA-256 values match.

The scale audit found a real protocol mismatch:

- `calibration_exact_24` used `low=0.75, high=1.50` for its eight binary
  schedules. It is therefore an **initial-grid stage ablation**, not a
  selected-Pareto-pair CAI calibration.
- The frozen fixed-scale rule selected a Pareto pair of `fixed_low=0.75` and
  `fixed_1.0=1.00` on the 24-object Exact calibration.
- A new independent 24-object run at `low=0.75, high=1.00` reports all eight
  stage combinations, but the frozen rule supplies no unique stage winner or
  tie-break. Its result is consequently set-valued/undefined.
- A new 76-object `LHL=(0.75,1.00,0.75)` run is reported as **Direct LHL
  shape-transfer diagnostic**. It is not called CAI-calibrated.

No existing calibration or holdout result was overwritten. `final_round2.tex`
and `response_letter_round2.md` were not modified.

## 1. Exact GLB recovery

All ten requested UIDs were matched by recomputing Objaverse-XL UUID v5 from
official Smithsonian `fileIdentifier` metadata. The official downloader then
returned the original file and every downloaded SHA-256 matched the metadata.

| UID count | Exact | Modified | Proxy | Missing |
|---:|---:|---:|---:|---:|
| 10 | 10 | 0 | 0 | 0 |

The recovered files are in:

`final/round2/mv_adapter/recovered_exact_meshes/`

The per-UID source, fileIdentifier, source, fileType, expected SHA-256 and
download URL are recorded in:

`final/round2/mv_adapter/GLB_RECOVERY_MANIFEST.json`

The original-source audit is:

`final/round2/mv_adapter/GLB_RECOVERY_AUDIT.md`

The historical render replay and its caveat for `obj_0070` remain recorded;
they do not downgrade the recovered GLB classification, but the repaired
legacy render is not claimed as untouched source-render provenance.

## 2. CAI scale-protocol audit

The inspected files were:

- `results/calibration_exact_24/run_config.json`
- `results/calibration_exact_24/calibration_analysis.json`
- `calibration_rule.json`
- `run_experiment.py`
- `CALIBRATION_RESULT_FREEZE.json`

`run_config.json` contains `low=0.75`, `high=1.5`; `run_experiment.py`
passes those two values directly to `stage_schedule(low, high, label)`, where
`L` maps to low and `H` maps to high. Thus all eight original stages really
used 0.75/1.50.

The original Exact run remains valid as a 24×12 Exact record (288 rows), but
its eight stage rows are labelled **initial-grid stage ablation**. They are not
silently relabelled or substituted.

The fixed-scale part of the same Exact run gave a clear two-scale Pareto
tradeoff under the frozen rule: conservative `fixed_low=0.75`, aggressive
`fixed_1.0=1.00`. This selection is unchanged.

`CALIBRATION_RESULT_FREEZE.json` is a historical mixed-geometry freeze. It
records `geometry_source=mixed`, 264 Exact rows plus 24 proxy rows, and the
old `NO_CLEAR_TRADEOFF` result. It was inspected but deliberately not edited;
it must not be mixed with the later Exact-only calibration analysis.

## 3. Selected-pair eight-stage calibration

Independent output directory:

`results/calibration_exact_selected_pair_24/`

Protocol record: `PROTOCOL.json`  
Metrics: `per_object_metrics.csv`  
Analysis: `calibration_analysis.json`

The run used the same 24 objects, reference images, Exact GLBs, seed
`20260928`, 50 inference steps, geometry-conditioning implementation and
metrics as the original Exact run, with only `low=0.75, high=1.00` and the
eight requested schedules changed. It contains 192 rows, exactly 24 rows per
stage, all `exact_mesh`, all finite.

| Stage | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | ΔE00 | GT-relative texture error |
|---|---:|---:|---:|---:|---:|---:|
| LLL | 13.180365 | 0.539721 | 0.246733 | 0.214056 | 21.101089 | 2.014652 |
| HLL | 13.164069 | 0.539913 | 0.246683 | 0.212602 | 21.137087 | 2.025720 |
| LHL | 13.188347 | 0.541985 | 0.247391 | 0.212607 | 21.098781 | 2.166349 |
| LLH | 13.188645 | 0.540701 | 0.247071 | 0.214165 | 21.088926 | 2.014778 |
| HHL | 13.185924 | 0.541766 | 0.247157 | 0.211509 | 21.099462 | 2.291930 |
| HLH | 13.176108 | 0.540844 | 0.247009 | 0.212887 | 21.112331 | 2.044953 |
| LHH | 13.195733 | 0.542454 | 0.247575 | 0.212857 | 21.088518 | 2.216884 |
| HHH | 13.189399 | 0.542170 | 0.247329 | 0.211876 | 21.090342 | 2.288052 |

Frozen-rule conclusion: `stage_selection.status=undefined_set_valued`, with
the complete eight-stage candidate set retained. No post-hoc winner or
LHL-favouring tie-break was added. This is a protocol amendment/ablation
report, not a confirmatory CAI winner selection.

## 4. Exact holdout results

The pre-existing Exact holdout remains in:

`results/holdout_exact_76/`

It contains 76 objects × 5 defined schedules = 380 rows, all Exact Mesh and
finite. The five schedules are `no_geometry`, `fixed_low`, `fixed_1.0`,
`linear_warmup` and `cosine_bump`.

| Schedule | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | ΔE00 | GT-relative texture error |
|---|---:|---:|---:|---:|---:|---:|
| no_geometry | 13.114180 | 0.498481 | 0.233429 | 0.183496 | 20.719805 | 1.700798 |
| fixed_low | 13.357177 | 0.527539 | 0.239997 | 0.187693 | 20.149543 | 2.224047 |
| fixed_1.0 | 13.317624 | 0.527349 | 0.239653 | 0.188759 | 20.264210 | 2.197877 |
| linear_warmup | 13.310451 | 0.527796 | 0.239868 | 0.190332 | 20.229784 | 2.338546 |
| cosine_bump | 13.300914 | 0.527090 | 0.239671 | 0.190178 | 20.284921 | 2.219668 |

The existing 10,000-resample object-level bootstrap is
`results/holdout_exact_76/paired_bootstrap_exact.json`. It retains all five
predefined comparisons. It is not retroactively augmented with a CAI schedule.

## 5. Direct LHL shape-transfer diagnostic

Independent output directory:

`results/holdout_exact_lhl_shape_transfer_76/`

Protocol: `PROTOCOL.json`  
Metrics: `per_object_metrics.csv`  
Bootstrap: `lhl_bootstrap_diagnostic.json`

The schedule was recorded before inference as three equal stages with
boundaries `[1/3, 2/3]`:

`early=0.75, middle=1.00, late=0.75`

The run used the same 76-object Exact holdout, seed `20260928`, 50 steps and
the same reference/geometry conditioning. It contains 76 rows, all
`exact_mesh`. Each row is paired with the corresponding object row from the
five-schedule Exact holdout.

The table below reports direction-aware LHL-minus-baseline deltas. For
LPIPS, ΔE00 and texture error, a positive direction means lower error for
LHL; each interval is a 95% object bootstrap CI from 10,000 resamples.

| Comparator | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | ΔE00 | GT-texture error |
|---|---|---|---|---|---|---|
| fixed_low | −0.013114 [-0.062438, 0.020680] | 0.000785 [0.000110, 0.001568] | 0.000238 [-0.000026, 0.000532] | −0.000358 [-0.001396, 0.000476] | −0.032603 [-0.122552, 0.028960] | −0.045049 [-0.191690, 0.059778] |
| fixed_1.0 | 0.026440 [-0.014223, 0.077067] | 0.000975 [-0.000346, 0.002543] | 0.000582 [0.000111, 0.001200] | 0.000708 [0.000002, 0.001408] | 0.082063 [-0.007949, 0.201253] | −0.071219 [-0.160830, 0.010398] |
| linear_warmup | 0.033612 [-0.004319, 0.074121] | 0.000529 [-0.000421, 0.001499] | 0.000367 [-0.000042, 0.000852] | 0.002281 [0.000673, 0.004234] | 0.047638 [-0.020299, 0.122842] | 0.069450 [-0.021419, 0.169094] |
| cosine_bump | 0.043150 [-0.026741, 0.112732] | 0.001235 [-0.001088, 0.003535] | 0.000564 [0.000040, 0.001206] | 0.002128 [0.000384, 0.004171] | 0.102775 [-0.006629, 0.219278] | −0.049429 [-0.120473, 0.020830] |
| no_geometry | 0.229883 [-0.253787, 0.672832] | 0.029844 [0.021050, 0.038859] | 0.006806 [0.002219, 0.011906] | −0.004555 [-0.016345, 0.007762] | 0.537659 [-0.481625, 1.519203] | −0.568298 [-1.083832, −0.079041] |

The diagnostic shows no uniformly positive LHL result across all six metrics.
It is therefore retained as a complete negative/mixed diagnostic, not used to
manufacture a CAI-calibrated claim.

## 6. Evidence scope and provenance

The three evidence labels are deliberately separated:

1. **Exact Mesh:** satisfied. All 100 MV-Adapter objects used in the Exact
   calibration/holdout partitions have verifiable original GLBs; the ten
   recovered files are independently SHA-verified.
2. **Calibration-disjoint:** satisfied for the 76-object holdout. Objects
   `obj_0000`–`obj_0023` were used for calibration and `obj_0024`–`obj_0099`
   were used for holdout; the sets are disjoint.
3. **Pretraining-disjoint:** not verified. The official checkout documents an
   `objaverse_list_6w.json` training-ID file, but the file is absent from the
   source snapshot and no authoritative local copy was found. No claim of
   disjointness from official MV-Adapter pretraining is made.

The SD2.1 base actually used is the public Manojb mirror, not an owned
Stability AI Hub repository:

- repository: `Manojb/stable-diffusion-2-1-base`
- resolved commit: `0094d483a120f3f33dafbd187ea4aa60d10de75c`
- local path: `models/sd21_base`
- text encoder SHA-256:
  `681c555376658c81dc273f2d737a2aeb23ddb6d1d8e5b3a7064636d359a22668`
- UNet SHA-256:
  `28ec9cf3b239c0751c201b1f6fb46b551df5862731b30a37aa1360101cb3fbab`
- VAE SHA-256:
  `3e4c08995484ee61270175e9e7a072b66a6e4eeb5f0c266667fe1f45b90daf9a`

Full provenance is in `BASE_MODEL_VERIFICATION.json`. The original requested
Stability AI API repository returned 404; the mirror and exact component
hashes are the reproducible source record.

## 7. Reproduction commands executed in this supplement

The two GPU commands were run with `CUDA_VISIBLE_DEVICES=0` and offline model
loading; neither command downloads models or GLBs:

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 PYTHONPATH=. \
python final/round2/mv_adapter/run_experiment.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --output-dir final/round2/mv_adapter/results/calibration_exact_selected_pair_24 \
  --split calibration --geometry-source exact --device cuda:0 \
  --seed 20260928 --steps 50 --low 0.75 --high 1.0 \
  --schedule LLL --schedule HLL --schedule LHL --schedule LLH \
  --schedule HHL --schedule HLH --schedule LHH --schedule HHH
```

```bash
CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1 PYTHONPATH=. \
python final/round2/mv_adapter/run_experiment.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --adapter-path final/round2/mv_adapter/models/mv-adapter \
  --output-dir final/round2/mv_adapter/results/holdout_exact_lhl_shape_transfer_76 \
  --split holdout --geometry-source exact --device cuda:0 \
  --seed 20260928 --steps 50 --low 0.75 --high 1.0 --schedule LHL
```

The CPU analysis commands were:

```bash
python final/round2/mv_adapter/analyze_selected_pair.py \
  --csv final/round2/mv_adapter/results/calibration_exact_selected_pair_24/per_object_metrics.csv \
  --output final/round2/mv_adapter/results/calibration_exact_selected_pair_24/calibration_analysis.json \
  --low 0.75 --high 1.0

PYTHONPATH=. python final/round2/mv_adapter/analyze_lhl_transfer.py \
  --lhl-csv final/round2/mv_adapter/results/holdout_exact_lhl_shape_transfer_76/per_object_metrics.csv \
  --baseline-csv final/round2/mv_adapter/results/holdout_exact_76/per_object_metrics.csv \
  --output final/round2/mv_adapter/results/holdout_exact_lhl_shape_transfer_76/lhl_bootstrap_diagnostic.json
```

## 8. LaTeX tables

The following compact tables are directly insertable after adding the desired
caption and label. Values are object-level means; lower is better for LPIPS,
ΔE00 and GT-relative texture error.

```latex
\begin{table*}[t]
\centering
\caption{Exact MV-Adapter calibration at the selected fixed-scale pair $(0.75,1.00)$. All eight schedules are reported; the frozen rule defines no unique stage winner.}
\begin{tabular}{lrrrrrr}
\toprule
Schedule & PSNR$\uparrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ & FG-LPIPS$\downarrow$ & $\Delta E_{00}\downarrow$ & GT-texture$\downarrow$\\
\midrule
LLL & 13.180365 & 0.539721 & 0.246733 & 0.214056 & 21.101089 & 2.014652\\
HLL & 13.164069 & 0.539913 & 0.246683 & 0.212602 & 21.137087 & 2.025720\\
LHL & 13.188347 & 0.541985 & 0.247391 & 0.212607 & 21.098781 & 2.166349\\
LLH & 13.188645 & 0.540701 & 0.247071 & 0.214165 & 21.088926 & 2.014778\\
HHL & 13.185924 & 0.541766 & 0.247157 & 0.211509 & 21.099462 & 2.291930\\
HLH & 13.176108 & 0.540844 & 0.247009 & 0.212887 & 21.112331 & 2.044953\\
LHH & 13.195733 & 0.542454 & 0.247575 & 0.212857 & 21.088518 & 2.216884\\
HHH & 13.189399 & 0.542170 & 0.247329 & 0.211876 & 21.090342 & 2.288052\\
\bottomrule
\end{tabular}
\end{table*}
```

```latex
\begin{table*}[t]
\centering
\caption{Exact 76-object holdout means for the five predefined schedules.}
\begin{tabular}{lrrrrrr}
\toprule
Schedule & PSNR$\uparrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ & FG-LPIPS$\downarrow$ & $\Delta E_{00}\downarrow$ & GT-texture$\downarrow$\\
\midrule
No geometry & 13.114180 & 0.498481 & 0.233429 & 0.183496 & 20.719805 & 1.700798\\
Fixed low & 13.357177 & 0.527539 & 0.239997 & 0.187693 & 20.149543 & 2.224047\\
Fixed 1.0 & 13.317624 & 0.527349 & 0.239653 & 0.188759 & 20.264210 & 2.197877\\
Linear warmup & 13.310451 & 0.527796 & 0.239868 & 0.190332 & 20.229784 & 2.338546\\
Cosine bump & 13.300914 & 0.527090 & 0.239671 & 0.190178 & 20.284921 & 2.219668\\
\bottomrule
\end{tabular}
\end{table*}
```

```latex
\begin{table*}[t]
\centering
\caption{Direct LHL shape-transfer diagnostic on the Exact 76-object holdout. Entries are LHL-minus-comparator paired means with 95\% object-bootstrap CIs; 10,000 resamples.}
\begin{tabular}{lrrrrrr}
\toprule
Comparator & $\Delta$PSNR & $\Delta$FG-SSIM & $\Delta$Edge-SSIM & $\Delta$FG-LPIPS$^\dagger$ & $\Delta\Delta E_{00}^\dagger$ & $\Delta$GT-texture$^\dagger$\\
\midrule
Fixed low & -0.013114 & 0.000785 & 0.000238 & -0.000358 & -0.032603 & -0.045049\\
Fixed 1.0 & 0.026440 & 0.000975 & 0.000582 & 0.000708 & 0.082063 & -0.071219\\
Linear warmup & 0.033612 & 0.000529 & 0.000367 & 0.002281 & 0.047638 & 0.069450\\
Cosine bump & 0.043150 & 0.001235 & 0.000564 & 0.002128 & 0.102775 & -0.049429\\
No geometry & 0.229883 & 0.029844 & 0.006806 & -0.004555 & 0.537659 & -0.568298\\
\bottomrule
\end{tabular}
\\[-2pt]
\footnotesize $^\dagger$ Error metrics are direction-adjusted so positive favors LHL. Full CIs are in the machine-readable bootstrap JSON.
\end{table*}
```

## Final protocol decision

The Exact Mesh and calibration-disjoint conditions are met for the defined
experiments. The fixed-scale calibration has a reproducible conservative /
aggressive pair, but the stage rule has no unique winner. Therefore the
strict frozen six-way CAI holdout claim remains **not defined**, while the
five-group Exact holdout and the complete LHL transfer diagnostic are valid
reported results. Pretraining-disjointness remains unknown and is not claimed.

## 9. Scale fairness supplement and equal-budget mechanism follow-up

The additional scale audit is in `MV_ADAPTER_EXACT_SCALE_AUDIT.md`. It confirms
that historical `linear_warmup` and `cosine_bump` used the old 0.75–1.50 range,
while `fixed_low`, `fixed_1.0` and `no_geometry` are independent of the unused
high parameter. The matched-range follow-up at 0.75–1.00 is documented in
`MV_ADAPTER_MATCHED_RANGE_RESULTS.md` and contains 152 new Exact rows plus
10,000-resample paired bootstrap results.

The equal-mean mechanism follow-up is documented in
`MV_ADAPTER_EQUAL_BUDGET_RESULTS.md`. It compares fixed mean, HLL, LHL and LLH
at mean scale 5/6. It contains 228 new rows, a 304-row combined four-condition
CSV, and complete 10,000-resample pairwise bootstrap results. The result shows
stage-position differences without a uniformly dominant schedule; this is
evidence of measured effects, not a causal mechanism proof.

The requested two-backbone mechanism conclusion is not yet claimed. The
main-adapter equal-mean/HLL/LLH formal experiment remains pending in
`final/round2/STAGE_PLACEMENT_RESULTS.md`, and its existing C3 comparisons use
a different scale protocol. No absolute MVPainter-vs-MV-Adapter PSNR comparison
or cross-backbone direction claim is therefore made.
