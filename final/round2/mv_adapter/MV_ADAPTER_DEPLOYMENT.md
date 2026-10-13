# MV-Adapter SD2.1 deployment record

Status: Official adapter/base deployment and the mixed-geometry calibration are
complete. GPU0 was used for this work. GPU1 was reserved by Codex A's existing
evaluation and was not used here; the final audit found it idle.

## Official source

- Repository: <https://github.com/huanngzh/MV-Adapter>
- Branch: `main`
- Commit: `4277e0018232bac82bb2c103caf0893cedb711be`
- Snapshot: `upstream/` (official source snapshot, then the documented local
  geometry-scale patch)
- Pipeline: `mvadapter/pipelines/pipeline_mvadapter_i2mv_sd.py`
- Entry point: `scripts/inference_ig2mv_sd.py`

The unmodified source hashes were recorded before the local patch. The
modified hashes are also recorded in `OFFICIAL_DEFAULTS.json`.

## Models

- Requested base model: `stabilityai/stable-diffusion-2-1-base`
- Resolved public copy: `Manojb/stable-diffusion-2-1-base`
- Resolved commit: `0094d483a120f3f33dafbd187ea4aa60d10de75c`
- Adapter repository: `huanngzh/mv-adapter`
- Adapter file: `mvadapter_ig2mv_sd21.safetensors`
- Base-model component SHA-256: see `BASE_MODEL_VERIFICATION.json`
- Adapter SHA-256: `a26fcabcce6e53bd31677074e067030fc93af33381a5559365581e793cc78ae2`
- Adapter integrity: safetensors opened successfully; 198 tensors found

The text encoder and UNet were already present on the server and match the
resolved repository bit-for-bit. The VAE was re-downloaded from the resolved
repository because the older local VAE had the same size but a different hash.
The patched MV-Adapter pipeline loaded successfully from the assembled local
base directory on CPU and passed an actual GPU0 constant-scale equivalence
smoke test. Ten fixed-manifest meshes remain unavailable; their explicitly
marked depth-convex-hull proxies are listed in `proxy_manifest.json` and are
used only by the mixed-geometry recovery run.

The model hashes must be filled only after the actual files are downloaded;
no placeholder numerical result is permitted.

## Environment audit

The official requirements are retained at `upstream/requirements.txt`. The
currently visible environment versions are listed in `OFFICIAL_DEFAULTS.json`.
The upstream requirements include `nvdiffrast`, Open3D, PyMeshLab and
CV-CUDA; this repository does not modify the main MV-Painter environment or
install those packages.

## Reproducibility

The source-level checks can be run without a GPU:

```bash
pytest -q final/round2/mv_adapter/tests/test_geometry_scale.py
python -m py_compile \
  final/round2/mv_adapter/upstream/mvadapter/geometry_scale.py \
  final/round2/mv_adapter/upstream/mvadapter/pipelines/pipeline_mvadapter_i2mv_sd.py \
  final/round2/mv_adapter/upstream/scripts/inference_ig2mv_sd.py
```

The calibration rule and data manifest are frozen. Exact-geometry runs remain
available if the missing original meshes are recovered; current mixed-proxy
results must not be interpreted as exact-geometry results.
