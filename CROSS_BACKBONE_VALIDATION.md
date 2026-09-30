# Cross-backbone validation audit

This audit separates a genuine transfer experiment from a model that merely
generates multiple views. The machine-readable preflight is
`release/round2_repro/cross_backbone_preflight.json`; rerun it with:

```bash
python scripts/cross_backbone_preflight.py \
  --output release/round2_repro/cross_backbone_preflight.json
```

## What is already usable

| Candidate | Why it fits | Local status | Paper-safe role |
|---|---|---|---|
| MVPainter + GeoTex-Adapter | The anchor method: five-channel geometry residuals injected into a joint six-view UNet | Main 276-object clean-v2 artifacts are present | Main absolute table |
| Official MV-Adapter SD2.1 | Independent SD2.1 multi-view adapter with an explicit image+geometry branch; its residual scale can be exposed per denoising step | Official source, base, adapter weights, manifests and Exact holdout are present | Primary second-backbone diagnostic |
| Official MVDiffusion depth branch | Independent correspondence-aware depth-conditioned multi-view diffusion model | Official source pinned; 75-object ScanNet-compatible interop run completed at 50 steps with finite metrics; current SD2.1 depth base is explicitly marked compatibility-only | Interop deployment diagnostic; no pooled absolute score |
| Wonder3D v1.0 | Local six-view model, Objaverse inputs and nearly complete six-view output inventory | 299 inputs and 1,794 RGB outputs are present | Boundary/generation baseline only |

## Deployment and validation records

### MVPainter / GeoTex-Adapter

The main MVPainter deployment is the controlled GeoTex-Adapter checkpoint at
training step 2000. It is not presented as a recovered historical checkpoint.

| Item | Frozen record |
|---|---|
| Checkpoint | `mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt` |
| Checkpoint SHA-256 | `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` |
| Source commit | `f2f0019a008277213af0127fa7cb628cb5fa1eef` |
| Conditioning | 3-channel normal + 1-channel depth + 1-channel foreground mask |
| Output protocol | joint six-view UNet, 256×256 per view, `unique6` order `[0,15,12,16,13,14]` |
| Sampler / steps / seed | Euler, 50 steps, seed 42; shared initial latent per object and condition |
| Evaluation cohort | 300 clean-v2 objects: 24 probe objects and 276 strict holdout objects |
| Conditions | no adapter, fixed-low `1.25`, fixed-high `2.50`, C3 `(1.25,2.50,1.25)` |

Deployment and inference validation passed: the checkpoint loads, the complete
300-object × 4-condition artifact is present, per-object rows are finite, and
the clean-v2 object list is disjoint from the historical 1,118-object training
list. The strict 276-object means are:

| Condition | Full PSNR | FG-PSNR | Full SSIM | FG-SSIM | FG-LPIPS | Edge-SSIM |
|---|---:|---:|---:|---:|---:|---:|
| No adapter | 10.514 | 8.776 | 0.726 | 0.478 | 0.207 | 0.479 |
| Fixed low | 15.086 | 7.030 | 0.850 | 0.355 | 0.202 | 0.500 |
| Fixed high | 13.365 | 5.410 | 0.823 | 0.229 | 0.210 | 0.494 |
| C3 | 14.875 | 6.763 | 0.855 | 0.348 | 0.201 | 0.500 |

These results validate the main deployment and the conditional C3 trade-off,
not a uniformly dominant method: C3 improves full-image and edge-related
measurements while its foreground PSNR/FG-SSIM remain below fixed-low. The
raw-PNG audit independently checks RGB reconstruction, masks, depth-derived
Edge-SSIM and view ordering; its values are kept separate from the original
float-evaluation table because PNG quantization changes some SSIM values.

The current MVPainter evidence includes a completed 12-object stratified
baking and unseen-view case study, including same-draw comparisons between
global and layer-wise controls (frozen records:
`final/round2/coordination/bake_layerwise_20260930/`). This establishes an
operational and comparative case-study result, but not population-level 3D
superiority; no generated GT bake or DISTS evaluation is available. The
six-view target panel also contains the selected reference view; only the
other target views are unseen relative to that reference.

Detailed source: `final/round2/main_adapter_clean_v2/MAIN_ADAPTER_CLEAN_V2_FINAL_AUDIT.md`.

### MVDiffusion depth branch

MVDiffusion was deployed as an isolated official depth-branch interop test. It
is not pooled with MVPainter or MV-Adapter absolute scores because its input
and camera assumptions differ.

| Item | Frozen record |
|---|---|
| Upstream commit | `4cd4e513e259be07a6c5e6a813258f77374afa59` |
| Checkpoint | official `depth_gen_new.pth`, SHA-256 `a90b6f900896e57e5688e1e1543e4992d87c4824cc00dc53cff46bea15f02765` |
| Input conversion | 12 source views `[0,1,2,4,5,7,9,12,13,14,15,16]`, ScanNet-style depth/camera export |
| Evaluation targets | six RGB-withheld targets `[0,12,13,14,15,16]`; target depth remains provided |
| Geometry / steps | orthographic source converted to equivalent pinhole; 50 steps |
| Cohort | 75 objects; `obj_0070` excluded because its repaired render has no valid depth |
| Compatibility base | local `sd21_depth_compat`, `native_official_depth_base=false`; extra depth channel zero-initialized |

The strict checkpoint load, five-step smoke test and full 75-object CUDA run
completed successfully; all objects have the expected 12 predicted views and
all interop metrics are finite:

| Objects | Steps | Interop PSNR | Interop foreground SSIM | Interop Edge-SSIM |
|---:|---:|---:|---:|---:|
| 75 | 50 | 10.1036 | 0.3154 | 0.2189 |

This is an interface/deployment diagnostic under known target geometry, not a
strict geometry-held-out novel-view test. The orthographic-to-pinhole
conversion, compatibility base and zero-initialized depth channel prevent a
paper-quality absolute comparison. A native official SD2-depth-base rerun
would be required before MVDiffusion could be reported as a matched baseline.

Detailed source and reproduction commands:
`final/round2/mvdiffusion/MVDIFFUSION_INTEROP.md`.

The MV-Adapter Exact holdout currently contains 76 objects and five defined
conditions (380 rows), all tagged `exact_mesh` and finite. Its exact unified
holdout means are approximately:

| Condition | PSNR | FG-SSIM |
|---|---:|---:|
| no geometry | 13.1142 | 0.4985 |
| fixed-low (0.75) | 13.3572 | 0.5275 |
| fixed-1.0 | 13.3176 | 0.5273 |
| LHL (0.75, 1.0, 0.75) | 13.3441 | 0.5283 |
| equal-budget fixed mean | 13.3372 | 0.5278 |

These numbers support a restrained statement: placement changes are measurable
within MV-Adapter, but the frozen CAI rule did not select a unique stage
schedule and LHL does not establish a uniform practical gain. The current
results should therefore strengthen the paper's *scope and boundary* claim,
not be rewritten as a positive replication of the main C3 optimum.

## Candidate ranking for further work

1. **Keep MV-Adapter SD2.1 as the main cross-backbone evidence.** The official
   geometry-guided branch, exact meshes, fixed calibration/holdout split and
   per-step residual-scale patch are already deployed. Report paired deltas
   within this backbone; never pool its absolute PSNR with MVPainter.

2. **Best additional deployment: MVDiffusion depth-conditioned generation.** Its
   official implementation is a separate correspondence-aware multi-view
   diffusion model that takes depth sequences and is explicitly used for mesh
   texturing. This is the closest additional architecture for a geometry
   control study, and the existing 17-view depth/camera exports can be
   converted to its scene-style inputs. The 75-object deployment is complete,
   but its text/scene conditioning differs from the reference-image protocol,
   and the current run uses an explicitly marked SD2.1 compatibility base;
   therefore it remains a follow-up interop diagnostic rather than a drop-in
   replacement or paper-quality absolute baseline. The deployment keeps the
   orthographic-to-pinhole conversion and the excluded all-invalid-depth
   object explicit in its manifest.

3. **NVS-Adapter SD2.1 + depth ControlNet is a lower-cost adapter diagnostic.**
   The official project provides an SD2.1 NVS-Adapter and an optional depth
   ControlNet path, but it uses a four-query/view setup and the depth path is
   SD1.5-specific. It needs a four-view subset and an explicit version-matched
   protocol; it should not be presented as the same six-view geometry-texture
   task without that adaptation.

4. **Do not prioritize Era3D or Wonder3D for TCAS transfer.** They are useful
   multi-view generation references, but their released inference paths do not
   expose the external geometry residual adapter whose strength TCAS controls.
   A condition-input scale sweep would answer a different question.

5. **Defer MVEdit/3D-Adapter for this revision.** The official repository
   describes a 24-GB-class UI and notes that the GRM-based adapter weights are
   not released. It is not a clean, reproducible candidate for the current
   controlled schedule table.

## Tests and deployment boundary

- `pytest -q geotex/tests final/round2/mv_adapter/tests/test_geometry_scale.py`:
  **57 passed**.
- The MV-Adapter protocol generator and all relevant Python entry points pass
  syntax compilation.
- The local Wonder3D source and existing output inventory pass the preflight;
  no new Wonder3D TCAS result is claimed because it has no matching geometry
  residual interface.
- The restricted sandbox has no `/dev/nvidia*`, but the approved external
  execution path sees two RTX 5090 devices. MVDiffusion strict checkpoint load,
  single-object smoke, and the 75-object/50-step run all passed on that path;
  the output inventory is complete and all interop metrics are finite. The
  current base is `native_official_depth_base=false`, so these results are
  deployment evidence only and are not pooled with absolute backbone scores.

## Recommended manuscript wording

> On an independent SD2.1 geometry-conditioned multi-view adapter (MV-Adapter),
> stage placement produced measurable but non-uniform changes across structure
> and texture metrics. The prespecified rule did not identify a unique optimal
> placement, so we treat this experiment as evidence that temporal placement is
> backbone- and adapter-dependent, while the conservative--high--conservative
> pattern remains a validated result for the main MVPainter/GeoTex regime.

This wording is deliberately narrower than claiming that TCAS universally
transfers or that the second backbone reproduces C3.
