# GPU Handoff Status

Date: 2026-09-29  
Scope: read-only resource check; no experiment was started.

## Current status

GPU0 is idle. The read-only process search found no active
`run_experiment.py`, `round2_main_eval`, `inference_ig2mv_sd`, or MV-Adapter
training/inference process in this session. `nvidia-smi` reported no compute
applications:

| GPU | Device | Driver | Memory used / total | Utilization |
|---:|---|---|---:|---:|
| 0 | NVIDIA RTX 5090 | 570.172.08 | 41 MiB / 32607 MiB | 0% |
| 1 | NVIDIA RTX 5090 | 570.172.08 | 15 MiB / 32607 MiB | 0% |

The small nonzero memory values are driver/runtime overhead, not an active
experiment. The current inference and follow-up result directories are
complete; no MV-Adapter job is left running by this session.

## Runtime

- Shell Python: `/home/ubuntu/anaconda3/bin/python`
- Conda environment: `base` (`/home/ubuntu/anaconda3`)
- PyTorch: `2.7.1+cu128`
- CUDA reported by PyTorch: `12.8`
- Unrestricted/CUDA-enabled runtime check: `torch.cuda.is_available() == True`,
  two NVIDIA RTX 5090 devices visible.

The restricted diagnostic shell can report CUDA unavailable even on the same
host because it does not expose the device context. Codex A/D should verify
CUDA from the actual execution context before launching work; the
unrestricted execution context used for the completed GPU check is CUDA
enabled.

## Accessible paths

- SD2.1 base model:
  `/4T/CXY/MV-Painter/final/round2/mv_adapter/models/sd21_base`
- MV-Adapter weights/code:
  `/4T/CXY/MV-Painter/final/round2/mv_adapter/models/mv-adapter`
- Exact object manifest:
  `/4T/CXY/MV-Painter/final/round2/mv_adapter/data_manifest.json`
- Recovered Exact meshes:
  `/4T/CXY/MV-Painter/final/round2/mv_adapter/recovered_exact_meshes`
- Model provenance and hashes:
  `/4T/CXY/MV-Painter/final/round2/mv_adapter/BASE_MODEL_VERIFICATION.json`

Both GPU0 and GPU1 are available for a later, separately coordinated task.
This handoff does not start Codex A or Codex D work.
