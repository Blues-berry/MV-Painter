# MVDiffusion depth interop

This directory contains an isolated deployment of the official MVDiffusion
depth branch.  The upstream snapshot is pinned at commit
`4cd4e513e259be07a6c5e6a813258f77374afa59`.

The input exporter keeps the frozen MVPainter renders unchanged and writes a
ScanNet-compatible copy.  It uses 12 source views
`[0,1,2,4,5,7,9,12,13,14,15,16]`; the six target views are
`[0,12,13,14,15,16]`.  The source depth PNG stores normalized values with
`65535` as invalid.  The exporter converts valid pixels with the recorded
`near=2, far=4` range to millimetres, and inverts the stored world-to-camera
matrix to obtain the camera-to-world pose expected by MVDiffusion.

`obj_0070` is excluded from the runnable 75-object holdout because its repaired
RGB render has no valid depth pixels.  No replacement depth is synthesized.

The frozen source views are orthographic, whereas the official MVDiffusion
depth model was trained for perspective ScanNet scenes.  The exporter records
an orthographic-equivalent pinhole intrinsic and all resulting metrics are
named `interop_*`; they must not be pooled with the native MVPainter or
MV-Adapter absolute-score tables.

The six evaluation targets are RGB-withheld only: their depth maps are still
provided as part of the 12-view condition.  Thus this is not a strict
geometry-held-out novel-view experiment; it is an interface/deployment
diagnostic under known target geometry.

## Reproduce

```bash
python scripts/gpu_preflight.py --device cuda:0

python scripts/prepare_mvdiffusion_scannet.py \
  --manifest final/round2/mv_adapter/data_manifest.json \
  --split holdout --exclude-object obj_0070 \
  --output-root final/round2/mvdiffusion/data/scannet/holdout_exact_75 \
  --output-manifest final/round2/mvdiffusion/data_manifest_holdout_exact_75.json

python scripts/build_mvdiffusion_sd21_depth_compat.py \
  --base-model final/round2/mv_adapter/models/sd21_base \
  --output-model final/round2/mvdiffusion/models/sd21_depth_compat

python scripts/run_mvdiffusion_depth.py \
  --data-root final/round2/mvdiffusion/data/scannet/holdout_exact_75 \
  --data-manifest final/round2/mvdiffusion/data_manifest_holdout_exact_75.json \
  --model-id final/round2/mvdiffusion/models/sd21_depth_compat \
  --checkpoint final/round2/mvdiffusion/upstream/weights/depth_gen_new.pth \
  --output-dir final/round2/mvdiffusion/results/holdout_exact_75_50steps \
  --steps 50 --device cuda:0

python scripts/evaluate_mvdiffusion_depth.py \
  --data-manifest final/round2/mvdiffusion/data_manifest_holdout_exact_75.json \
  --output-dir final/round2/mvdiffusion/results/holdout_exact_75_50steps \
  --csv final/round2/mvdiffusion/results/holdout_exact_75_50steps/per_object_metrics.csv
```

## Deployment result

The official depth checkpoint is present at
`upstream/weights/depth_gen_new.pth` (6,525,955,586 bytes;
SHA-256 `a90b6f900896e57e5688e1e1543e4992d87c4824cc00dc53cff46bea15f02765`).
Strict loading succeeds after an explicit legacy-diffusers key migration (16
VAE attention keys renamed and one non-persistent position-id buffer dropped).
The 5-step smoke and the full 75-object, 50-step run both completed on CUDA;
each object has all 12 predicted views.

The current interop summary is:

| Objects | Steps | Interop PSNR | Interop foreground SSIM | Interop edge SSIM |
|---:|---:|---:|---:|---:|
| 75 | 50 | 10.1036 | 0.3154 | 0.2189 |

These values are diagnostics only.  The run uses the local
`sd21_depth_compat` base (`native_official_depth_base=false`), whose extra
depth input channel is zero-initialized, and it also inherits the
orthographic-to-pinhole conversion above.  A paper-quality absolute comparison
requires rerunning with the native official SD2-depth base and keeping that
provenance in the run configuration; the present numbers must not be pooled
with MVPainter or MV-Adapter scores.

The local `sd21_depth_compat` base is a bootstrap for environments where the
Hugging Face SD2-depth repository is not accessible: it zero-initializes the
extra UNet depth channel.  It is suitable for deployment and interface
verification, but not for a paper-quality absolute claim.  A native-base rerun
is the remaining step if this branch is promoted from an interop diagnostic to
a reported baseline.
