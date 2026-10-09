# P0 trace-lock summary

This Markdown summary preserves the reproducibility facts needed for handover without uploading the local JSON lock or its machine-specific paths. The original JSON is retained outside the repository and checksummed in `../../LOCAL_ONLY_ASSETS_LEDGER.md`.

- Purpose: locate the first material divergence between archived Fresh C outputs and controlled reruns; diagnostic only.
- Condition: `native_gfl`; target-view mode: `unique6`; target views: `0, 15, 12, 16, 13, 14`.
- Frozen checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`.
- Frozen base runner SHA-256: `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`.
- Protocol: 50 EulerDiscreteScheduler steps, 256-pixel resolution, one GPU shard; object seed is `42 + object index`, latent seed is `42`.
- Trace points: initial latent and final RGB for every selected run; scheduler pre/post latent and U-Net input/noise prediction at steps `0, 1, 10, 25, 49`; VAE decode input/output for every selected run.
- Runs: `python313_trace_repeat1`, `python313_trace_repeat2`, `python310_trace`.
- Selection was locked before new forensic outputs: panel 1 (highest focal C3-GFL FG-PSNR), panel 3 (lowest focal FG-PSNR), and panel 20 (highest focal FG-LPIPS). No reselection after outputs.

| Sample | Object index | Object seed | Object UID | Frozen selection stratum |
|---|---:|---:|---|---|
| `freshc_panel_01` | 232 | 274 | `c76ac44df995482185077da81939b306` | highest focal FG-PSNR |
| `freshc_panel_03` | 236 | 278 | `ca887928bb664bcba121219f0af41293` | lowest focal FG-PSNR |
| `freshc_panel_20` | 10 | 52 | `06fa4974f8cd4d4ea792e98fa1521457` | highest focal FG-LPIPS |

Historical trace environment recorded: Python 3.13.5, torch 2.7.1+cu128, torchvision 0.22.1+cu128, diffusers 0.37.0, transformers 4.57.6, RTX 5090. This environment note is not a claim that the three runs shared one software stack.

Compare each run only against its matching immutable archived PNG and run ledger. Compare cross-environment tensors only after input and scheduler identity checks. Do not combine residual logs from different run roots. This diagnostic lock is not a new population-level estimate and does not establish a validated color fix.
