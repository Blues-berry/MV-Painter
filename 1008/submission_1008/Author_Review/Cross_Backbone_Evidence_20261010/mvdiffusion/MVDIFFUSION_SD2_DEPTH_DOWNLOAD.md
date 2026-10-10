# MVDiffusion SD2-Depth Native Mirror Download Record

Date: 2026-09-30. Branch: `codex/next-review-response-20260930`.

## Connectivity test (passed once, then proxy refused)

`model_info("sd2-community/stable-diffusion-2-depth")` succeeded once:

```
repo: sd2-community/stable-diffusion-2-depth
commit: 6cb92dd9430a7f6da8d9e99d7b60acdebcc348b7
private: False
gated: False
```

Saved log: `results/phase_c_logs/sd2_depth_connectivity_test.txt`.
The repo is public and not gated; 32 files listed via `list_repo_files`
(`results/phase_c_logs/sd2_depth_download_plan.txt`).

## Download attempts (all failed; per task section 25, stop after three paths)

1. `hf download ... --local-dir ...` — the installed `hf` CLI has no `--dry-run`;
   a file-listing preview was used instead, and the download path is the Python
   `snapshot_download` below (same backend).
2. `snapshot_download` with default Xet — stalled at ~8.3 MB of the first
   shard, no progress for minutes.
3. `snapshot_download` with `HF_HUB_DISABLE_XET=1` and a 30-attempt/30 s
   backoff loop — every attempt failed with proxy `502 Bad Gateway`
   (`CONNECT tunnel failed` to `huggingface.co:443`). Independent `curl`
   probes confirm the egress proxy refuses both API and CDN endpoints
   (`results/phase_c_logs/sd2_depth_download_retry.log`).

```
SD2_DEPTH_DOWNLOAD = BLOCKED   (first campaign, 2026-09-30 morning:
                                proxy 502; 30+30 attempts exhausted)
SD2_DEPTH_DOWNLOAD = COMPLETED (recovery campaign, 2026-09-30, after the
                                egress proxy recovered; resumable
                                snapshot_download with priority order
                                vae -> unet/text fp bins -> ema ckpt)
```

## Consequences (updated after download completion)

- Section 26 PASSED on the completed mirror: `StableDiffusionDepth2ImgPipeline`
  loads locally and `UNet in_channels = 5`
  (`results/phase_c_logs/sd2_depth_native_load_check.txt`).
- Sections 27-29 executed: post-load state equivalence YES (1552/1552 tensors
  bitwise), single-object output equivalence YES (12/12 PNG SHA-256 bitwise),
  `NATIVE_MIRROR_EQUIVALENT = YES`, no 75-object rerun required. See
  `results/phase_c_logs/MVDIFFUSION_POSTLOAD_OUTPUT_EQUIVALENCE.md`.
- The deployed base remains `models/sd21_depth_compat` with
  `depth_gen_new.pth` strict-load, exactly as in the archived 75-object run.
- Bitwise reproducibility of that deployment was re-verified on 2026-09-30:
  a fresh official runner rerun of obj_0024-obj_0026 (seed 42, 50 steps)
  produced PNG SHA-256 identical to the archived `holdout_exact_75_50steps`
  grids, 36/36.
- All scheduled Phase D conditions therefore run on the same compat base with
  the same seeds as the existing 75-object deployment, so every paired
  comparison in the Phase D panel is internal to one base. No absolute
  cross-backbone score pooling is implied or performed.
