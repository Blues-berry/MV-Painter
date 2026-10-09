# Final color root-cause report

## Scope and verdict

This report covers the locked four-object Phase B intervention and C1 development trial. It does not claim that the full color-generation root cause has been found. **Root cause is partial:** global appearance embeddings causally control generated chroma, and the stored global-embedding cache is inconsistent with the current reference input; replacing that cache changes the two Fig. 4 failure outputs in opposite directions. Those facts identify a control path and a plausible contributor, but they do not explain the complete color error or provide a stable correction. The source-conditioned chroma anchor failed its pre-registered visual gate, so no independent validation was run.

## Frozen identities and scope

- Branch: `codex/r1-color-cast-repair-v2-20261009`; frozen parent: `46e741180a2fd539a43234c51f4f3019e346424e`.
- Model checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Inference config SHA-256: `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
- Phase B runner SHA-256: `a4ed336f1ae72fc8ee52cbe4a738a117bdd5ac40120f17356b74dceb1765fd78`; generated helper SHA-256: `14bf84690552c973bac9304d3ba80fe184ff68232329bacfc7c1d734a96fd99b`.
- Phase B runtime JSON SHA-256: `619ca45e907af714b49a1d3b998d7a8a19ab4831ab08b4254bed99762c1103ca`; paired intervention CSV SHA-256: `2544445cf181f425f1bd4d049404b185790182d8289915a4a430cddb68fc26c5`.
- Development objects: Fig. 4 row 1 `eac4b392b7b448a2b6ec77e8936abe1b`; Fig. 4 row 2 `ea7601dbeb2c46188571cb86e8fdb5bf`; normal `c76ac44df995482185077da81939b306`; high texture `8bd93fcae54940bd903a94a9094da4ee`.
- Readout lock: `protocol/A_COLOR_READOUT_LOCK.json`; intervention lock and amendments: `protocol/B_PROTOCOL_LOCK.json`, `B_PROTOCOL_AMENDMENT_01.json` through `03.json`. Input-only Fresh B audit locks and source files are listed in `A_SOURCE_VIEW_COLOR_AUDIT.md`.

## Findings

### Source view and reference condition

Dataset code confirms the source reference is unique6 tile 0: view 014 for `reverse=True` and view 000 otherwise. In these four development objects the source target tile is byte-identical to the selected raw source RGB. The condition-only random stretch/compress and canvas transform changes its geometry; source condition-to-target mask IoU ranges from 0.3215 to 0.8053. Pixelwise condition-to-target color matching is therefore invalid. The locked readout instead uses robust Lab foreground distributions (alpha ≥ 0.75, three-pixel erosion, at least 64 pixels) and the geometry target mask for GT-relative metrics.

Across the four objects, GFL source-view median CIEDE2000 to GT is 18.20–21.56 and the mean of the five unseen views is 19.05–24.08. The locked magenta-direction residual fraction (Δa* ≥ +5 and Δb* ≤ −5) averages 1.24% on source views and 1.34% across unseen views; it is descriptive and does not capture every perceptual material mismatch. Full per-view, source-statistic, and per-object rows are in `runs/phase_b/A_PER_VIEW_COLOR_READOUT.csv`, `A_SOURCE_COLOR_STATISTICS.csv`, and `A_PER_OBJECT_COLOR_SUMMARY.csv`.

### Causal appearance-channel evidence

All 64 Phase B generation calls used the same checkpoint, initial latent, geometry features, scheduler, and pre-posterior RNG per object. Runtime used Python 3.13.5, PyTorch 2.7.1+cu128, Diffusers 0.37.0, Transformers 4.57.6, FP16 UNet/VAE, RTX 5090 physical GPU 1, 50-step `EulerDiscreteScheduler` (pipeline default class was `EulerAncestralDiscreteScheduler`), and the logged CLIP processors/backend flags. Sampling took 485.1 seconds. The failed pre-generation serialization attempt and model-load preflight each made zero diffusion calls.

VAE-only ±6 Lab source-color perturbations failed the locked directional response rule (0/4 objects for both source and unseen-view response). Global-embedding-only a* perturbations passed for both signs on 4/4 source and 4/4 unseen-view objects; b*+ passed 4/4 and b*− passed 2/4. The joint arm passed all except b*− at 3/4. This establishes a causal color-control route through global embeddings, not that the route moves outputs toward GT.

The Fresh B input-only audit found cached embeddings numerically unequal to both the exact transformed conditions and unaugmented selected sources for 150/150 objects. For the 98 selected-view-014 objects, the cache was closer to raw view 000 than raw view 014 on max-absolute distance for 84/98 and cosine similarity for 94/98; neither raw view was an exact match. This is a cache/source provenance discrepancy, not proof of a color cause. In the four Phase B objects, refreshing the embedding from current transformed conditions shifted the two Fig. 4 failures in opposite GT-relative directions (unseen ΔCIEDE2000 −0.370 and +0.284); the normal and high-texture outputs were pixel-identical to GFL.

### Adapter and layer comparisons

No Adapter had mean unseen ΔCIEDE2000 +20.067 versus GFL and lost on all four objects, but also caused large geometry/lightness changes (mean L* SSIM versus GFL 0.193; full-grid RGB MAE 51.328). This cannot isolate a pure adapter-induced hue cast. LLH had mixed object-level color effects (mean unseen ΔCIEDE2000 +2.564, two wins and two losses) and mean L* SSIM versus GFL 0.576. These comparisons do not establish a fine-detail advantage for LLH.

### Repair prototype

The one frozen C1 candidate passed its numeric development criteria but failed the locked visual gate: Fig. 4 row 1 had no clear visible gain; row 2 retained substantial color mismatch and acquired faint cyan/blue silhouette rims. The normal and high-texture cases had no obvious detail/structure damage. Since the four-object visual criterion failed, the method lock closes the Fresh B gate. No Fresh B candidate image or repair metric was opened, and no C2 generation-time correction was attempted.

### Raw selected-source cache intervention (B2)

Because the input-only audit found that cached embeddings match neither the transformed condition nor the official raw selected source, a locked eight-call development intervention replaced only `global_embeds` with the frozen vision-encoder output from that raw selected source. It used the same four objects, six-view protocol, checkpoint and config listed above. The pre-generation amendment chain, sampling runner hash, attempt state, runtime backend configuration and per-image hashes are in `protocol/B2_RAW_SOURCE_EMBEDDING_LOCK.json`, amendments 01–02 and `runs/phase_b2_raw_source_embedding_attempt_04/`.

The paired object-level mean across five unseen views was ΔFG-CIEDE2000 **+0.1729** (95% object-bootstrap CI [−0.2044, +0.6810], 1/4 wins); mean ΔFG-PSNR was −0.0708 dB, ΔFG-LPIPS +0.000965, and foreground L* SSIM-to-GT Δ +0.00349. Both CIEDE2000 advancement criteria failed (the lock required at least 3/4 wins and mean ≤−1.0). Visual review showed no clear correction for either Fig. 4 case. The normal and high-texture cases showed no obvious large detail loss, but the intervention also provided no useful color gain. The method was stopped; Fresh B outcomes remained unopened. The per-view/object tables and casebook are `B2_RAW_SOURCE_EMBEDDING_PAIRED_RESULTS.csv`, `B2_RAW_SOURCE_EMBEDDING_OBJECT_RESULTS.csv`, `B2_RAW_SOURCE_EMBEDDING_SUMMARY.csv` and `B2_RAW_SOURCE_EMBEDDING_CASEBOOK.pdf`.

The B2 detailed run table includes the checkpoint, config, source RGB, cached and selected embedding, condition, geometry, initial latent, VAE posterior/RNG, runner and generated-PNG SHA-256 identities. `B2_METRIC_INPUT_RECONSTRUCTION.json` adds raw GT source-file SHA-256 values and same-seed target/mask tensor reconstructions on the same CUDA resize path. The original sampling process did not log target-grid or mask-grid tensor hashes, so the supplemental hashes cannot be compared with an in-process hash that was never captured; this traceability gap is explicit. The casebook's development visual review was not blinded to treatment labels and is not represented as independent validation.

The four B2 cached-baseline PNGs are byte-identical to the existing Phase B GFL baseline PNGs for the same development objects (4/4 SHA matches; `B2_BASELINE_REPRODUCIBILITY.csv`). This closes the repeat check for those four objects only. It does not resolve the separate 120-object Fresh C output discrepancy.

### Read-only Fresh C cache-builder audit

The historical builder `1006/scripts/precompute_fresh_c_global_embeds.py` (SHA-256 `6bc2d0cef02cff8c853e64a3bc24bd247040ea4b53424c423f62bffe2b10f7ee`) and frozen inference runner `scripts/run_validation_v3_experiment.py` (SHA-256 `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`) use the same ordered object-index seed policy: `42 + index` for Python, NumPy, and Torch before loading the dataset item. The builder calls the same `MVPainterData[index]` path; the inference helper `collate_batch` calls that same dataset index. Their dataset and helper source hashes match (`b4220fe8e73e2193709bd09d682623ccace44a780d82afecf417edea49aa3d8a` and `e078f9e2cb3d85447f036fa4c0158929fa4e5f3c7f17571ed6bf0c6f7e7f94f3`).

The builder computes both vision-encoder outputs from the transformed `cond_imgs` tensor through the configured image processor; it does not embed the raw selected RGB directly. This static audit found no code-level seed-policy discrepancy that explains a cache/input difference. It did not rerun the builder, mutate any cache, or isolate a single runtime-library cause for the separate output mismatch. It therefore does not change the B2 verdict or establish a validated color fix.

## Evidence chain and limitations

The root `COLOR_INTERVENTION_RESULTS.csv` retains Phase B output/condition/geometry/seed identities and per-view measurements; its locked checkpoint, runner, and runtime identities are in `runs/phase_b/runtime.json` and `run_manifest.json`. The root `C_REPAIR_PAIRED_RESULTS.csv` contains 24 object/view rows with checkpoint, baseline runner and generation manifest, condition/input/target/mask/baseline/candidate image hashes, C1 code/runner/lock hashes, and per-view metrics. The root `COLOR_REPAIR_VALIDATION.csv` is the four-row object-level C1 development aggregate, explicitly marked `cohort=dev`, and records its input/output, candidate, method-lock, and generation-manifest identities. `runs/phase_b/A_CONDITION_ENCODING_TRACE.csv` and `condition_encoding_trace.json` record the encoded input path. The source pathway and C1 casebooks use SHA-verified images; image SHA values are retained in their manifests/CSVs. `SHA256SUMS.txt` supplies the final file identity inventory.

The cohort is a four-object development set, not an independent validation set. Numeric gains cannot establish generalization. The true full color-generation root cause remains unresolved; this result should be reported as a bounded causal investigation with a failed repair prototype, not as a solved color defect.

The B2 runner completed 8/8 diffusion calls in 77.326 seconds on physical RTX 5090 GPU 1 (device UUID `2abab5d9-0ecf-cfff-c0f1-95921fe8c165`) with FP16 UNet/VAE and a 50-step EulerDiscrete sampler. B2 attempts 01–03 made zero generations and are preserved. The current and prior failed intervention results do not support opening Fresh B or claiming a validated repair.
