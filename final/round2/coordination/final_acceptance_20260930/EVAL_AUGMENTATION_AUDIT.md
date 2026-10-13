# EVAL_AUGMENTATION_AUDIT (final acceptance, 2026-09-30)

## FINAL_PROTOCOL_CLASSIFICATION = LEGAL_INFERENCE_PREPROCESSING

## Question

`MVPainterData.__getitem__` (via `load_im_cond`) applies
`random_stretch_or_compress` (0.5-1.5x per axis, center-preserving on the
foreground mask) plus `random_resize` (uniform 0.8-1.0 zoom-out) to the
reference conditioning image at every dataset load. Is this transform a legal
component of the evaluation protocol, or a training-only augmentation that
leaks into evaluation?

## Evidence

### 1. The official codebase has exactly ONE quantitative data path

- Official configs
  (`final/EM_questionnaire_notes/share_kit/MVPainter/MVPainter/configs/`):
  ALL five official configs (`mvpainter-geotex-full-train.yaml` L27-28,
  `mvpainter-geotex-fac-train.yaml` L45-46, `mvpainter-geotex-v2-train.yaml`
  L43-44, `mvpainter-geotex-gsg-fsc-only.yaml` L38-39,
  `mvpainter-train-controlnet.yaml` L19-20) instantiate
  `validation: -> src.data.mvpainter_dataset.MVPainterData` — the same class
  whose loader applies the stretch. The official framework's validation
  protocol therefore includes the transform.
- There is NO train/eval flag, NO augmentation flag, and NO alternative
  dataset class in the official codebase; the transform cannot be "turned
  off" without modifying official code.
- The standalone demo pipeline (`mvpainter/mvpainter_pipeline.py`, uses
  `recenter_img` only, no stretch) is a product-inference path, not the
  framework's evaluation protocol; it is also inconsistent with the
  training loader (a known official train/demo gap, not a protocol we
  can adopt for the controlled comparisons).

### 2. Design logic keeps evaluation conditioning in-distribution

The frozen checkpoint (`geotex_step_0002000.pt`, SHA-256 `0618d6b2...`,
controlled retrain of the official training protocol) was trained
exclusively on stretched reference conditionings. Evaluating with the
stretched reference keeps the conditioning distribution identical to
training; disabling the stretch would evaluate the checkpoint under a
conditioning distribution it never saw, with no official-code support.

### 3. Scope of the transform (verified in the imported copy
`MVPainter/src/data/mvpainter_dataset.py`)

- `load_im_cond` L218-219: stretch + resize applied — ONLY the reference
  branch is randomized.
- `load_im` (targets) L269, `load_im_normal` L325, `load_img_depth` L354:
  `random_resize` is commented out — targets, normals, depth, masks, and
  view order are fully deterministic. This matches the manuscript's
  disclosure (Supplementary S9: "targets, masks, depths, and view order
  are deterministic").

### 4. The historical failure was the UNSEEDED realization, not the transform

The archived layer-LHL strict-276 record did not seed the Python RNG, so its
reference draws were irreproducible across runner restarts (archived FG-PSNR
14.78 vs 12.97 seeded rerun, cross-restart r=0.66). This is fixed in every
current runner by per-object seeding `object_seed = 42 + obj_idx` before
`collate_batch`:
- `scripts/run_layer_confirmation_276_20260930.py` L179-183 (strict-276
  confirmations);
- `geotex/round2_main_eval.py` L73-75, L130-135 (clean-v2 300-object
  evaluation);
- `final/round2/coordination/layer_factorial_v1_20260930/run_full_factorial_probe.py`
  L164-166 (8-pattern factorial);
- `scripts/generate_layer_bake_panels_20260930.py` L119-122 and
  `scripts/generate_global_bake_controls_20260930.py` (bake prediction).
The archived unseeded record is excluded from all paired claims and is
labeled an independent protocol surface in the manuscript.

### 5. Pre-registration

`EXPERIMENT_PROTOCOL_LOCK.md` recorded the transform and its consequences
(shared-draw pairing validity; absolute values not comparable across runner
invocations) BEFORE the confirmation runs were executed.

## Conclusion-A conditions — status

| Condition | Status |
|---|---|
| Transform is part of the official evaluation protocol | PASS (official validation configs instantiate the same loader) |
| Per-object realization frozen | PASS (object_seed = 42 + idx, all three RNGs) |
| All methods share one condition realization per object | Within-run: PASS by construction (single collate per object); cross-runner same-draw: verified in Phase 3 |
| Manuscript describes the frozen realization accurately | PASS (S9/S10 + Limitations + same-draw bake wording); minor explicitness improvement optional |

## Paper-facing experiments using this protocol (all consistent)

1. Clean-v2 300-object four-condition table (`geotex/round2_main_eval.py`,
   seeded).
2. Strict-276 confirmations: layer-fixed-mean, layer-LHL replica,
   layer-LLH (`scripts/run_layer_confirmation_276_20260930.py`, seeded).
3. 8-pattern factorial probe, 24 objects x 3 seeds (seeded).
4. Shared-input 6-method probe (seeded).
5. 12-object bake predictions, layer + same-draw global controls (seeded,
   same-draw verified in Phase 4).
6. FAC instance-level analysis (`geotex/eval_fac_v2.py` imports
   MVPainterData; same protocol surface).

## Ruling

The transform is a component of the official evaluation data path, applied
identically to every method, with frozen per-object realizations and full
manuscript disclosure. It does not invalidate any paired conclusion.
Closing it would (a) deviate from the official validation path, (b) create a
train/eval conditioning mismatch for the frozen checkpoint, and (c) fork the
entire frozen evidence base — with no protocol-validity gain, because all
paper claims are within-run paired comparisons under a shared realization.

No rerun is required on the grounds of this classification. The remaining
verification obligation is Phase 3 (shared-input determinism) — if sharing
FAILS, this ruling is void and the affected experiments must be rerun.
