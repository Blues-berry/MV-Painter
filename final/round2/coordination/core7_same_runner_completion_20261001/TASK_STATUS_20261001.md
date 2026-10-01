# TASK STATUS — Core-7 completion + round-2 priority experiments & forensic audits (2026-10-01)

Branch: codex/round2-evidence-integrated-20261001 (base d30ed4f).
Task boundary honored: experiments + audits ONLY; no paper/supplementary/
response-letter text touched.

## Deliverables (all complete)

### 1. Core-7 same-runner completion (the headline task)
- no_adapter + global_fixed_high added to the frozen strict-276 R0
  protocol (verbatim per-object code path; pre-registered in
  PROTOCOL_LOCK_CORE7_COMPLETION.md).
- Preflight PASS (GFL anchor bit-exact vs frozen R0; cross-method and
  cross-process input hashes identical). Formal 552/552 rows, in-run
  integrity 0 aborts, post-hoc cross-process audit 0/276 mismatches.
- Result: strict-276 Core-7 matrix (7 conditions x 276, same cohort +
  runner + realization + shared input) — LLH best on FG-PSNR / FG-LPIPS /
  Full-PSNR / Full-SSIM and all four GT-relative texture errors; beats
  no_adapter by +5.15 dB FG-PSNR and fixed_high by +0.82 dB FG-PSNR /
  +2.59 dB Full-PSNR (all CIs exclude 0). Honest reversals reported:
  FG-SSIM ranks no_adapter first (blur), fixed_high leads Full-LPIPS by
  0.002 and Edge-SSIM by 0.006. See CORE7_SAME_RUNNER_REPORT.md.

### 2. P2 texture-fidelity extension (offline, no GPU)
GT-relative gradient/Laplacian/RGB-std/HF errors now computed for all
seven conditions from the frozen per-object columns
(TEXTURE_FIDELITY_EXTENSION_*). LLH - GFL: all four diagnostics
significantly favor LLH. Mechanism note: fixed-low OVERSHOOTS GT gradient
energy (1.54x), no_adapter undershoots (0.89x), LLH closest (1.13x).

### 3. P1 MV-Adapter mapping sensitivity (pre-registered, 228 runs)
The only distinct alternative contiguous 4→3 mapping (M3) leaves the
layer-vs-global direction intact: 16/18 MAPPING_STABLE; primary metrics
STABLE and slightly STRONGER under M3 (PSNR +0.10→+0.15, CIEDE2000
+0.34→+0.48, GT-texture +0.31→+0.41); the single "SENSITIVE" label is a
|delta|<=0.001 LPIPS flip (already ns in the frozen M1 report). The
mapping-arbitrariness objection is defused. MAPPING_SENSITIVITY_REPORT.md.

### 4. P3 seam / cross-view consistency audit (CPU-only, 96 GLBs)
Direct texture-space UV-seam CIEDE2000 measurement on the existing 12-object
bakes. In the matched bake generation LLH has the LOWEST seam
discontinuity (mean 4.89 / p90 14.56 / frac>10 18.6% vs G-FL 8.86 / 26.17 /
28.6%). ../BAKE_SEAM_AUDIT_20261001/SEAM_CROSSVIEW_AUDIT.md.

### 5. Forensic audits
- METRIC_SIGN_CONVENTION_AUDIT.md: all four analysis chains use the same
  benefit-oriented transform; one experiment report + one protocol lock
  word it ambiguously; erratum appended (original files untouched).
- PROTOCOL_LOCK_SAMPLE_INDICES_ERRATUM.md: the inline "[3,23,45,...]" in
  two older MDs is a transcription error; both executed JSONs used the
  correct canonical draw [11,25,113,...]; no validity impact; Core-7
  preflight ran on the canonical sample.
- ARCHIVED_LHL_PROVENANCE_AUDIT.md: archived 14.78 dB record forensically
  decomposed using its surviving 276 predictions. GT/mask/metric/data all
  verified IDENTICAL to current protocol; drift is generator-side and
  source-group-structured (hex-UID +4.94 dB); stage-2 GPU experiment
  REFUTES the cond-augmentation hypothesis (aug-OFF still -6.9 dB from
  archived; seeded regen bit-exact). Root cause bounded to an
  unrecoverable uncommitted runner-time code state. Quarantine upgraded:
  excluded from ALL quantitative claims, with mechanism wording recorded
  for the next paper-edit window.
- GENERATION_SEED_AUDIT.md: the dev-24 3-seed runs vary the FULL
  stochastic stack (initial latent + VAE cond latent + preprocessing;
  layer_lhl_ablation_shared.py L125-140), so generation-noise robustness
  is already covered at n=24; the priority-5 latent-seed experiment is
  not required.
- MAPPING_CHRONOLOGY_AUDIT.md: mapping fixed in pre-registration before
  any layer-wise row existed; profile values come from the main backbone.

## Not done (out of scope / explicitly not required)
- No paper, supplementary, or letter edits (per task boundary).
- No third preprocessing realization, no 276 x latent-seed runs (P5
  resolved by audit), no new bake generation (P3 measured existing bakes).
- The equal-budget pilot and other legacy records remain outside paper
  evidence, unchanged.

## GPU accounting (RTX 5090 x2)
- Core-7 formal: 552 runs (~2.4 h wall)
- MV-Adapter M3: 228 runs (~25 min wall)
- LHL stage-2: 24 regens (~10 min)
- Preflights: 2 x 30 rows
