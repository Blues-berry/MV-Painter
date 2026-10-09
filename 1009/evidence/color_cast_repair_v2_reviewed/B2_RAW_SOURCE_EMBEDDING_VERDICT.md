# B2 selected raw-source embedding intervention

## Decision

The frozen intervention **did not support the cached-embedding mismatch as a sufficient or reliably corrective cause of the color failures**. The candidate failed both locked CIEDE2000 advancement criteria: only 1/4 objects improved on the mean of five unseen views, and the object-paired mean change was **+0.173 ΔE00** (higher is worse), versus the required at least 3/4 wins and mean ≤ −1.0. The two Fig. 4 cases showed no clear visual correction. The stop rule applies; no Fresh B outcome was opened and no further cache replacement, scale, or Gate search is authorized by this result.

## Locked experiment and identities

- Protocol: `protocol/B2_RAW_SOURCE_EMBEDDING_LOCK.json`, SHA-256 `3fdfe82d3f5d082752aca950055dabd4a24426ca4652fb8baa8180e54e307a6c`.
- Runner amendments: Amendment 01 SHA-256 `4fcf3cccac33744e68b995cf36d64f0a8e91b731add75ffe35011f0eccb25eeb`; Amendment 02 SHA-256 `2026cd7b9161dcd0684745e3c1a7cec7007ad8db6f424363d65953351c04f188`. The chain pins the initial runner, both pre-generation fixes, and the final runner.
- Sampling runner: `run_raw_source_embedding_intervention.py`, SHA-256 `676612448998670096d52f2a42e3363be01d580764406657faadcbb9d6e16df7`.
- Checkpoint SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`; inference config SHA-256 `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Metric code: `run_chroma_anchor_evaluation.py`, SHA-256 `ae1ab26a67338d46f1d53dce292c13037387896bbb4aa1479c1544ab75353831`.
- Objects: original Fig. 4 rows 1 and 2 (`eac4b392b7b448a2b6ec77e8936abe1b`, `ea7601dbeb2c46188571cb86e8fdb5bf`), one normal-color development case (`c76ac44df995482185077da81939b306`), and one GT-only high-texture development case (`8bd93fcae54940bd903a94a9094da4ee`). All four are the Phase B development objects; none are Fresh B validation outcomes.
- Treatment: replace only cached `global_embeds` with the concatenated frozen vision-encoder embedding of the officially selected raw source RGB (view 014 for reverse objects; view 000 otherwise), using the unchanged vision processor. No GT or other target view contributes to that embedding.
- Run identity: attempt 04, PID 524277, 2026-10-09 06:04:21.998–06:05:39.345 UTC, 8/8 generation calls, reported generation wall time 77.326 s. Physical GPU 1, NVIDIA RTX 5090, device UUID `2abab5d9-0ecf-cfff-c0f1-95921fe8c165`, `CUDA_VISIBLE_DEVICES=1`.
- Runtime: Python 3.13.5; PyTorch 2.7.1+cu128; Diffusers 0.37.0; Transformers 4.57.6; NumPy 2.2.6; UNet/VAE FP16; both vision encoders FP32; 50-step `EulerDiscreteScheduler` (pipeline default `EulerAncestralDiscreteScheduler`); xFormers unavailable; deterministic algorithms disabled; TF32 matmul disabled; cuDNN TF32 enabled; cuDNN benchmark disabled. Exact processor, scheduler and attention-backend settings are in the run `runtime.json` (SHA-256 `bfad12c0cfb5ed4fe02866ea97c7827c4365fc5f0d40716dc4c70dd6a8200236`).
- Raw detailed rows: `runs/phase_b2_raw_source_embedding_attempt_04/B2_RAW_SOURCE_EMBEDDING_RESULTS.csv`, SHA-256 `bed55eb8c2a2c87877597c4162e645c2ca8cd7e7967abf2de89d41f4d2b9bbf6`. It records each output PNG SHA, source PNG SHA, selected/cached embedding tensor SHA, condition, alpha, geometry, initial latent and VAE posterior/RNG identities.
- Run-state SHA-256 and individual PNG identities are included in the campaign checksum inventories; generated PNGs remain local-only. The casebook embeds the original B2 outputs and reconstructed metric targets.

## Paired-factor and metric provenance

Across all paired conditions, the manifest verifies equal hashes for the transformed condition tensor, source alpha, GeoTex features, initial latent, VAE-processor pixels, posterior mean/std/sample/noise and pre/post posterior RNG. The global embedding and its derived prompt contribution are the intended treatment and therefore change. All 48 prediction-file hashes were checked against the saved PNGs.

The 24 per-view paired records are in `B2_RAW_SOURCE_EMBEDDING_PAIRED_RESULTS.csv`; four object summaries are in `B2_RAW_SOURCE_EMBEDDING_OBJECT_RESULTS.csv`; metric-level means, wins and 95% intervals are in `B2_RAW_SOURCE_EMBEDDING_SUMMARY.csv`. The unit of inference is the object: five non-source views are equally averaged within each object, then a 10,000-draw percentile bootstrap (seed 20261009) resamples the four paired object means. No pixels are pooled across objects.

The metric-target source PNG paths and file SHA-256 values, unique6 order, recreated RGB-tile/mask hashes and code/config identities are in `B2_METRIC_INPUT_RECONSTRUCTION.json`. The original sampling CSV did **not** store the target-grid or mask-grid tensor hashes at generation time. The supplemental manifest therefore records a same-seed, same-dataset-code reconstruction on the same CUDA resize path and explicitly marks that missing in-process hash comparison; it does not claim a hash that was never captured.

## Results

| Development object | Five-view ΔFG-CIEDE2000 | ΔFG-PSNR (dB) | ΔFG-LPIPS | Δforeground L* SSIM-to-GT |
|---|---:|---:|---:|---:|
| Fig. 4 row 1 | +0.0773 | −0.1697 | +0.00154 | +0.00554 |
| Fig. 4 row 2 | +0.0068 | +0.0145 | +0.00052 | −0.00832 |
| Normal color | +0.9058 | −0.2092 | +0.00236 | +0.01084 |
| High texture | −0.2982 | +0.0812 | −0.00055 | +0.00589 |
| **Object-paired mean** | **+0.1729** | **−0.0708** | **+0.000965** | **+0.00349** |
| **95% object-bootstrap CI** | **[−0.2044, +0.6810]** | **[−0.1894, +0.0478]** | **[−0.000031, +0.001949]** | **[−0.00477, +0.00952]** |

The CIEDE2000 gate fails decisively: only the high-texture object improved, by a small amount; the normal object regressed most. PSNR, LPIPS and foreground lightness-structure values remained within their numeric no-major-regression limits, but these results do not compensate for failed color improvement. Mean treatment-to-cached foreground L* SSIM across unseen views was 0.9253. The mean exact-pixel background-changed fraction was 0.7818; this metric counts any changed background pixel without measuring change magnitude and is descriptive, not a visual-quality score.

The source-view mean changes were ΔFG-CIEDE2000 +0.0650, ΔFG-PSNR −0.0613 dB, ΔFG-LPIPS +0.00158, and Δforeground L* SSIM-to-GT +0.00223. Source results are reported separately and do not replace the five-view gate.

As an additional reproducibility check, each B2 cached-baseline PNG was byte-identical to the earlier Phase B GFL baseline for the same four development objects (4/4 SHA-256 matches); the pairwise paths and hashes are in `B2_BASELINE_REPRODUCIBILITY.csv`. This confirms a narrow same-object baseline repeat. It does not close the separate 120-object Fresh C discrepancy reported in the earlier campaign.

## Visual review and scope

`B2_RAW_SOURCE_EMBEDDING_CASEBOOK.pdf` has one page per object, with each of the six locked views shown as GT target, cached baseline and selected-raw-source treatment. Review of the two Fig. 4 pages found no clear visible reduction in the existing color mismatch. The normal and high-texture pages show no obvious large detail or structure loss, but also no useful color correction. This was an unblinded development review; there was no independent human validation review because the candidate failed the development gate and Fresh B stayed sealed.

This experiment shows that refreshing the cache from the official raw selected source image is not a sufficient repair for these failures. It does not eliminate the previously measured cache/source inconsistency, establish that this inconsistency causes the purple cast, or identify the complete color-generation root cause. Combined with the earlier opposite-direction Fig. 4 responses to the transformed-condition refresh, the evidence supports an object-dependent appearance-control path but not a stable correction. No Fresh B repair prediction or metric was accessed.

## Stop decision and next route

`advance_gate = FAIL`; stop this candidate. Do not run Fresh B for this treatment, tune a scale, search gates, or add schedule combinations. The most justified next step is a read-only audit of the historical `global_embeds.npy` creation path and its selected-view/processor provenance (zero GPU calls). Only if that audit yields a single reproducible implementation correction should it be frozen for a new small development comparison; an 8-call development check is about 77 seconds of sampler time at the measured B2 rate. A hypothetical 300-call independent paired validation would take about 48.3 minutes at that same rate, plus model startup and preprocessing. The current evidence does not authorize those validation calls.
