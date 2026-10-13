# MV-Adapter Unified Exact Results

## Scope

This report is a numerical aggregation only. No new MV-Adapter inference was
started in this pass, and none of the existing result directories was
overwritten. Every row below contains the same 76-object Exact Mesh cohort
(`obj_0024`--`obj_0099`, `geometry_source=exact_mesh`). The machine-readable
table is `MV_ADAPTER_UNIFIED_RESULTS.csv`; the complete paired-bootstrap
record is `MV_ADAPTER_PAIRED_COMPARISONS.json`.

The historical holdout was run with `low=0.75, high=1.50`. Its linear and
cosine rows are therefore labelled `h1.50`. The independent matched-range
follow-up was run with `low=0.75, high=1.00` and is labelled `h1.00`. These
two dynamic-scale families are reported separately and are not pooled.

`PSNR`, `FG-SSIM`, and `Edge-SSIM` are higher-is-better. `FG-LPIPS`,
`CIEDE2000 (Delta E00)`, and `GT-relative texture error` are lower-is-better.
Values are object-level arithmetic means over the 76 objects.

## Unified 76-object table

| Method | Protocol family | Scale schedule/range | PSNR | FG-SSIM | Edge-SSIM | FG-LPIPS | CIEDE2000 | GT-relative texture error |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| No geometry | historical Exact holdout | 0.00 | 13.114180 | 0.498481 | 0.233429 | 0.183496 | 20.719805 | 1.700798 |
| Fixed-low | historical Exact holdout | 0.75 | 13.357177 | 0.527539 | 0.239997 | 0.187693 | 20.149543 | 2.224047 |
| Fixed-1.0 | historical Exact holdout | 1.00 | 13.317624 | 0.527349 | 0.239653 | 0.188759 | 20.264210 | 2.197877 |
| Linear warm-up (h1.50) | historical Exact holdout | 0.75 -> 1.50 | 13.310451 | 0.527796 | 0.239868 | 0.190332 | 20.229784 | 2.338546 |
| Cosine bump (h1.50) | historical Exact holdout | 0.75 -> 1.50 -> 0.75 | 13.300914 | 0.527090 | 0.239671 | 0.190178 | 20.284921 | 2.219668 |
| Linear warm-up (h1.00) | matched-range follow-up | 0.75 -> 1.00 | 13.332426 | 0.528047 | 0.240094 | 0.188445 | 20.194007 | 2.182502 |
| Cosine bump (h1.00) | matched-range follow-up | 0.75 -> 1.00 -> 0.75 | 13.327002 | 0.527812 | 0.239955 | 0.188232 | 20.211197 | 2.215665 |
| LHL | direct LHL shape-transfer diagnostic | 0.75, 1.00, 0.75 | 13.344064 | 0.528325 | 0.240235 | 0.188051 | 20.182146 | 2.269096 |
| Fixed mean | equal-budget follow-up | 5/6, 5/6, 5/6 | 13.337215 | 0.527776 | 0.240051 | 0.188163 | 20.196643 | 2.202812 |
| HLL | equal-budget follow-up | 1.00, 0.75, 0.75 | 13.320944 | 0.526805 | 0.239621 | 0.188194 | 20.243426 | 2.232062 |
| LLH | equal-budget follow-up | 0.75, 0.75, 1.00 | 13.353306 | 0.527814 | 0.239974 | 0.188346 | 20.157122 | 2.198930 |

The source CSV and exact unrounded values for each row are preserved in
`MV_ADAPTER_UNIFIED_RESULTS.csv`. The historical h1.50 dynamic rows remain
valid historical results, but they are not same-range controls for LHL or the
h1.00 matched-range rows.

## LHL paired comparisons

The following table reports `LHL - comparator` as the raw paired mean
difference. The bracketed interval is the percentile 95% object-level paired
bootstrap CI from 10,000 resamples (`seed=20260928`). For the three error
metrics, a positive raw difference is worse for LHL; the final `win%` column is
direction-aware and always means the percentage of objects where LHL is
better. A CI containing zero is not interpreted as a clear improvement.

| Comparator | PSNR delta [95% CI]; win% | FG-SSIM delta [95% CI]; win% | Edge-SSIM delta [95% CI]; win% | FG-LPIPS delta [95% CI]; win% | Delta E00 delta [95% CI]; win% | GT-texture delta [95% CI]; win% |
|---|---|---|---|---|---|---|
| No geometry | +0.229883 [-0.253787, +0.672832]; 64.5% | +0.029844 [+0.021050, +0.038859]; 80.3% | +0.006806 [+0.002219, +0.011906]; 67.1% | +0.004555 [-0.007762, +0.016345]; 46.1% | -0.537659 [-1.519203, +0.481625]; 67.1% | +0.568298 [+0.079041, +1.083832]; 59.2% |
| Fixed-low | -0.013114 [-0.062438, +0.020680]; 48.7% | +0.000785 [+0.000110, +0.001568]; 47.4% | +0.000238 [-0.000026, +0.000532]; 51.3% | +0.000358 [-0.000476, +0.001396]; 56.6% | +0.032603 [-0.028960, +0.122552]; 48.7% | +0.045049 [-0.059778, +0.191690]; 63.2% |
| Fixed-1.0 | +0.026440 [-0.014223, +0.077067]; 59.2% | +0.000975 [-0.000346, +0.002543]; 57.9% | +0.000582 [+0.000111, +0.001200]; 56.6% | -0.000708 [-0.001408, -0.000002]; 55.3% | -0.082063 [-0.201253, +0.007949]; 59.2% | +0.071219 [-0.010398, +0.160830]; 31.6% |
| Fixed mean | +0.006849 [-0.024497, +0.034504]; 56.6% | +0.000549 [-0.000103, +0.001385]; 39.5% | +0.000184 [-0.000024, +0.000436]; 47.4% | -0.000113 [-0.000774, +0.000709]; 50.0% | -0.014497 [-0.069869, +0.043365]; 57.9% | +0.066284 [-0.028245, +0.187375]; 55.3% |
| HLL | +0.023119 [-0.019055, +0.080996]; 51.3% | +0.001520 [-0.000006, +0.003580]; 55.3% | +0.000613 [+0.000135, +0.001217]; 57.9% | -0.000143 [-0.001009, +0.000757]; 55.3% | -0.061280 [-0.193290, +0.041587]; 56.6% | +0.037034 [-0.066952, +0.177634]; 59.2% |
| LLH | -0.009242 [-0.055429, +0.022729]; 46.1% | +0.000511 [-0.000102, +0.001207]; 39.5% | +0.000261 [+0.000032, +0.000522]; 46.1% | -0.000296 [-0.001198, +0.000712]; 63.2% | +0.025024 [-0.032059, +0.108336]; 57.9% | +0.070166 [-0.050221, +0.216403]; 56.6% |
| Matched linear (h1.00) | +0.011638 [+0.000971, +0.023440]; 53.9% | +0.000278 [-0.000189, +0.000769]; 44.7% | +0.000141 [-0.000060, +0.000377]; 53.9% | -0.000394 [-0.000891, +0.000146]; 57.9% | -0.011860 [-0.036995, +0.010723]; 48.7% | +0.086595 [-0.001115, +0.196638]; 43.4% |
| Matched cosine (h1.00) | +0.017061 [-0.012204, +0.050986]; 60.5% | +0.000512 [-0.000182, +0.001273]; 59.2% | +0.000280 [+0.000027, +0.000601]; 60.5% | -0.000181 [-0.000646, +0.000398]; 57.9% | -0.029051 [-0.080996, +0.017236]; 55.3% | +0.053431 [+0.003667, +0.116490]; 30.3% |

These are paired comparisons on the same object IDs, not independent-group
comparisons. Win rate is descriptive; no multiplicity correction or post-hoc
winner rule was introduced.

## Protocol labels and interpretation boundary

The results retain four distinct labels:

1. **Initial-grid calibration:** the original 24-object eight-stage run with
   `low=0.75, high=1.50`.
2. **Selected-pair stage calibration:** the independent 24-object `0.75/1.00`
   eight-stage supplement. The frozen rule remains
   `undefined_set_valued`.
3. **Direct LHL shape-transfer:** the 76-object LHL run with
   `(0.75,1.00,0.75)`. It is not a CAI-calibrated winner.
4. **Equal-budget follow-up ablation:** fixed mean, HLL, LHL and LLH, where
   the nominal mean scale is `5/6`. This was a targeted follow-up on an
   already-used holdout, not the original confirmatory freeze.

Consequently, no schedule in this table is called the CAI-calibrated winner.
The equal-budget comparison matches nominal scale mean only; it does not match
the accumulated geometry residual norm or any other effective conditioning
budget.

## Reproducibility and commands

The aggregation was performed with the repository helper:

```bash
PYTHONPATH=. python final/round2/mv_adapter/generate_unified_results.py
```

The script validates 76 unique object IDs, `exact_mesh` provenance, finite
metrics, and 10,000-resample paired bootstrap settings. The source-run audits
for scale formulas are in `MV_ADAPTER_EXACT_SCALE_AUDIT.md` and the source
protocols are under `results/holdout_exact_*_76/PROTOCOL.json`.

All compared runs use seed `20260928`, 50 inference steps, the frozen
reference image and geometry-conditioning implementation, and the manifest
`data_manifest.json`. The recorded implementation hashes are:

| Item | SHA-256 |
|---|---|
| `run_experiment.py` | `ac29e58c7c8efa1d95799cb2d02b59f34941252a151ff7ce16524d7791a1f6a3` |
| `upstream/mvadapter/geometry_scale.py` | `a89f15042696b06a1e8fb5196fc7da2cd816cbf1cc94f49c880edf6188edcde4` |
| `data_manifest.json` | `d256c9327d35c26dbcab4dc0cb30d1cffb7802e27827d9950763529df0211db5` |

The base model provenance is recorded in `BASE_MODEL_VERIFICATION.json`:
the resolved Manojb mirror commit is
`0094d483a120f3f33dafbd187ea4aa60d10de75c`; component hashes are text
encoder `681c555376658c81dc273f2d737a2aeb23ddb6d1d8e5b3a7064636d359a22668`,
UNet `28ec9cf3b239c0751c201b1f6fb46b551df5862731b30a37aa1360101cb3fbab`,
and VAE `3e4c08995484ee61270175e9e7a072b66a6e4eeb5f0c266667fe1f45b90daf9a`.
This is the actual public mirror used for the runs, not an unverified claim
that it is owned by Stability AI.

## LaTeX tables

The following table is directly insertable after adding the usual `booktabs`
package. It intentionally includes the scale-family label so h1.50 and h1.00
dynamic rows cannot be silently conflated.

```latex
\begin{table}[t]
\centering
\caption{Unified Exact 76-object MV-Adapter results. Dynamic schedules are separated by their tested high scale.}
\begin{tabular}{lrrrrrr}
\toprule
Method & PSNR$\uparrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ & FG-LPIPS$\downarrow$ & $\Delta E_{00}\downarrow$ & GT-texture$\downarrow$\\
\midrule
No geometry & 13.114180 & 0.498481 & 0.233429 & 0.183496 & 20.719805 & 1.700798\\
Fixed-low (0.75) & 13.357177 & 0.527539 & 0.239997 & 0.187693 & 20.149543 & 2.224047\\
Fixed-1.0 & 13.317624 & 0.527349 & 0.239653 & 0.188759 & 20.264210 & 2.197877\\
Linear h1.50 & 13.310451 & 0.527796 & 0.239868 & 0.190332 & 20.229784 & 2.338546\\
Cosine h1.50 & 13.300914 & 0.527090 & 0.239671 & 0.190178 & 20.284921 & 2.219668\\
Linear h1.00 & 13.332426 & 0.528047 & 0.240094 & 0.188445 & 20.194007 & 2.182502\\
Cosine h1.00 & 13.327002 & 0.527812 & 0.239955 & 0.188232 & 20.211197 & 2.215665\\
LHL & 13.344064 & 0.528325 & 0.240235 & 0.188051 & 20.182146 & 2.269096\\
Fixed mean & 13.337215 & 0.527776 & 0.240051 & 0.188163 & 20.196643 & 2.202812\\
HLL & 13.320944 & 0.526805 & 0.239621 & 0.188194 & 20.243426 & 2.232062\\
LLH & 13.353306 & 0.527814 & 0.239974 & 0.188346 & 20.157122 & 2.198930\\
\bottomrule
\end{tabular}
\end{table}
```

```latex
\begin{table}[t]
\centering
\caption{LHL paired bootstrap summary on the Exact 76-object cohort. Entries are raw LHL-minus-comparator mean differences with 95\% CIs; win rates are direction-aware.}
\begin{tabular}{lrrrrrr}
\toprule
Comparator & PSNR & FG-SSIM & Edge-SSIM & FG-LPIPS & $\Delta E_{00}$ & GT-texture\\
\midrule
No geometry & +0.229883 & +0.029844 & +0.006806 & +0.004555 & -0.537659 & +0.568298\\
Fixed-low & -0.013114 & +0.000785 & +0.000238 & +0.000358 & +0.032603 & +0.045049\\
Fixed-1.0 & +0.026440 & +0.000975 & +0.000582 & -0.000708 & -0.082063 & +0.071219\\
Fixed mean & +0.006849 & +0.000549 & +0.000184 & -0.000113 & -0.014497 & +0.066284\\
HLL & +0.023119 & +0.001520 & +0.000613 & -0.000143 & -0.061280 & +0.037034\\
LLH & -0.009242 & +0.000511 & +0.000261 & -0.000296 & +0.025024 & +0.070166\\
Matched linear h1.00 & +0.011638 & +0.000278 & +0.000141 & -0.000394 & -0.011860 & +0.086595\\
Matched cosine h1.00 & +0.017061 & +0.000512 & +0.000280 & -0.000181 & -0.029051 & +0.053431\\
\bottomrule
\end{tabular}
\end{table}
```
