# EVIDENCE_INTEGRATION_STATUS_20261001

Round-2 evidence integration: merge of the two formal experiment branches into a single
integration branch. Evidence only — the manuscript, supplementary material, and response
letter are NOT modified in this round.

## 1. Git provenance

| role | SHA | branch | remote |
|---|---|---|---|
| merge base | `edfb8d02ba050b79897955a32d0cafc1bb80f9b5` | — (final technical acceptance HEAD) | — |
| cross-backbone input | `4f312566ed42a7b56fae9f11d91d4591d71fd1f2` | `codex/next-review-response-20260930` | `mvpainter` |
| robustness-1 input | `99d6c88f28050a3fb74a04d74f555ba30f27ff3e` | `codex/main-backbone-robustness1-20260930` | `origin` |
| **integration merge** | **`9f571928380873f69e0d4607f49180a0b68232fb`** | `codex/round2-evidence-integrated-20261001` | pushed to `mvpainter` |

- Remote SHA verification passed: cross-backbone = `4f31256`, robustness-1 = `99d6c88`.
  Note: the robustness-1 branch lives on the `origin` remote (MV-Painter repo), not on
  `mvpainter`; the SHA matches the required `99d6c88` exactly.
- Merge base `edfb8d0`; changed-file overlap between the two sides relative to base:
  **0 files** (cross-backbone 71 files, robustness-1 61 files). Merge executed with
  `--no-ff`, recursive strategy, **zero conflicts**; robustness-1 side contributed
  61 files / +120,374 lines, all new files (evidence artifacts + runner scripts).
- Paper-file integrity: `git diff edfb8d0..HEAD` over
  `final_round2.tex` / `supplementary_round2.tex` / `response_letter_round2.md` is
  **empty**; blob SHAs identical to `edfb8d0` (`06b93afc9105` / `d8be7f8516ac` /
  `194d32d35d1e`). Neither input branch touched the three paper files.

## 2. Main-backbone final evidence (robustness-1)

Source: `final/round2/coordination/main_backbone_robustness1_20260930/`
(`MAIN_BACKBONE_ROBUSTNESS1_REPORT.md`, `PROTOCOL_LOCK.md`, shared-input audit, raw CSV/JSON).

- Scope: strict-276 Core-5 (GFL / GC3 / LFM / L-LHL / L-LLH) re-run under an independent,
  pre-frozen reference-preprocessing realization (R1: `object_seed = 10042 + idx` vs
  R0: `42 + idx`). Protocol locked before any R1 metric existed.
- **Primary gate: `ROBUSTNESS_SUPPORTED`.**
- Preprocessing robustness headline (LLH − GFL, FG-PSNR dB, 10k percentile bootstrap,
  seed 20260930): R0 `+3.244 [+2.936, +3.542]` (242/276) → R1 `+3.233 [+2.928, +3.527]`
  (241/276) — essentially unchanged.
- Stability: 4 core comparisons × 7 metrics = 28 cells → **27 STABLE_STRONG,
  1 STABLE_DIRECTIONAL** (LLH−GC3 full_ssim), **0 UNSTABLE**; Core-5 ranking identical
  in R0 and R1 on all 7 metrics.
- Completeness: R1 Core-5 **1380/1380** rows, 0 integrity aborts; shared-input preflight
  PASS (0 mismatches across processes/methods; deterministic components match R0 500/500,
  reference-derived components differ 150/150 — genuine independence); R0 anchor re-run
  10/10 bit-exact (max |delta| = 0.0); R0 GC3 completion 276/276.

## 3. MV-Adapter final evidence (cross-backbone)

Source: `CROSS_BACKBONE_VALIDATION_MVADAPTER.md` + `final/round2/mv_adapter/`
(protocol, hash manifest, paired bootstrap JSON, standard panel CSV, exact-76 run dirs).

- Layer-wise effect: **SUPPORTED** — PSNR, ΔE00 and GT-relative texture error CIs
  exclude 0 in favor of layer-wise; FG-/Edge-SSIM small reverse; LPIPS ns
  (10k object bootstrap, seed 20260928).
- Temporal-position effect: **NOT_SUPPORTED** — within the frozen scales, LLH vs LHL
  ordering does not transfer as a stable temporal-position advantage.
- Exact-76 evidence: 3 new layer conditions (`holdout_exact_layer_{fixed,lhl,llh}_76`)
  × 76 objects = **228 new rows**, all `exact_mesh`, all metrics finite (verified:
  3 × 77-line CSVs = 228 data rows); existing global rows (R0/G-FL/G-LHL/G-LLH) reused
  without rerun.
- Identity gate: **IDENTITY_AUDIT PASS** — wrapper multipliers=1.0 vs global runner:
  PNG SHA-256 / pixels / max-abs-diff 0 / metrics equal, and 9/9 PNG SHA equal to the
  archived 76-object grids.
- Pre-registered mechanical mapping (resolves the previously BLOCKED 4→3 grouping gate):
  shallow = 320@64, middle = 640@32, deep = {1280@16, 1280@8}; normalized count weights
  2/1/1 → deep = middle = 1.193490054249548, shallow = 0.4195298372513563.

## 4. MVDiffusion final evidence (cross-backbone)

Source: `CROSS_BACKBONE_VALIDATION_MVDIFFUSION.md` + `final/round2/mvdiffusion/`
(interop/residual-control audits, results panels, phase C/D dirs, paired bootstrap).

- Interface classification: **PARTIAL** — the deployed depth path goes through latent
  concat (scaling forbidden) and the literal additive branch never activates; the only
  adjustable surface is 9 CPBlock replacement semantics with convex-combination α, where
  α ≡ 1 is strictly identical to the official path.
- Native mirror: **NATIVE_MIRROR_EQUIVALENT = YES** — `UNet in_channels = 5`
  (native depth-concat base), post-load **1552/1552** bitwise-identical tensors,
  **12/12** views PNG SHA-256 bitwise equal (max abs pixel diff 0); no 75-object rerun
  needed for deployment.
- Phase-D identity: **PASS** (`phase_d_identity_{official,alpha1}`, α identically 1 at
  every scheduled point, strict path).
- Scale: **450 new** 12-view generations (6 new conditions × 75 objects,
  `holdout_exact_75`, official deployment base `sd21_depth_compat` unchanged);
  standard panel CSV verified at 525 data rows = 7 conditions × 75 objects.
- Layer-wise effect: **NOT_REPLICATED** (negative/mixed, preserved as found) — PSNR /
  SSIM / ΔE00 significantly worse under layer-wise α; GT-relative texture slightly
  improved. Mapping: deep = {mid, up0}, middle = {up1}, shallow = {up2, up3};
  multipliers deep = middle = 1.3502458265122749, shallow = 0.4746317504091673.

## 5. Reviewer-facing evidence boundary

The three backbones carry different evidential weight and must not be conflated:

| backbone | verdict | reviewer-facing framing |
|---|---|---|
| Main MVPainter | strong positive | LLH advantage on the strict-276 holdout is robust to a fully independent reference-preprocessing realization (`ROBUSTNESS_SUPPORTED`, 27/28 STABLE_STRONG). |
| MV-Adapter | partial positive | Layer redistribution **transfers** (layer-wise effect SUPPORTED with the pre-registered mechanical mapping, identity gate PASS); temporal positioning does **not** form a stable unified advantage (NOT_SUPPORTED). Claim only the layer/scale dimension. |
| MVDiffusion | negative / boundary | Under a different (PARTIAL) control interface the layer-wise advantage is **NOT replicated**; results are negative/mixed and must be reported as boundary evidence, **never packaged as positive replication**. |

Any reviewer-facing text must keep this asymmetry explicit: one strong positive backbone,
one partial transfer (scale dimension only), one honest non-replication.

## 6. Remaining experiments

**NO MANDATORY EXPERIMENT REMAINS FOR CURRENT REVIEWER RESPONSE.**

The integration audit found no data or protocol hard errors in either input branch; no
new experiments were opened in this round.

## Workspace notes (non-evidence)

- Pre-merge working-tree state of the robustness-1 session (3 modified D19-era docs:
  `CODEX_B_STATUS.md`, `DECISION_LOG.md`, `LAYER_LHL_HANDOFF_20260929.md`) was stashed —
  `stash@{0}` "robustness1 session D19 WIP (3 docs) saved before round2-evidence-integration
  20261001" — and is NOT part of this integration. Untracked `.codex/` and
  `scripts/verify_sd2_depth_mirror.py` remain uncommitted.
