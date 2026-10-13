# ANONYMOUS_RELEASE_AUDIT (final acceptance, 2026-09-30)

## ANONYMOUS_RELEASE = PASS (identity leakage: none found after scrub; completeness gaps documented below — non-blocking for a PDF-only initial submission)

## 1. Identity-leakage scan

Scanned `release/` (the public lightweight hand-off) for
`/4T/CXY`, `CXY`, `车学远`, `chexueyuan`, `Blues-berry`, `github.com`,
`wandb`, `hostname`, `东南大学`, `Southeast University`, usernames:

- FIXED: `release/round2_repro/cross_backbone_preflight.json` contained 20
  machine-specific absolute paths (`/4T/CXY/MV-Painter`, `/4T/tmp/...`,
  `/4T/CXY/Wonder3D`). All replaced with neutral placeholders
  (`<repo-root>`, `<external-run-dir>`, `<external-root>`). Re-scan of
  `release/` is now clean. (The preflight is regenerable locally via
  `python scripts/cross_backbone_preflight.py ...`; the committed version is
  the shippable record.)
- `github.com/huanngzh/MV-Adapter` and `github.com/Tangshitao/MVDiffusion`
  references are THIRD-PARTY official upstream repositories (citations),
  not author identity — retained.

## 2. Build-cache exclusion rule (required when packaging code)

`MVPainter/mvpainter/custom_rasterizer/build/` contains compiler artifacts
(`build.ninja`, `.ninja_log`) embedding absolute machine paths. Any release
ZIP MUST exclude `**/build/`, `__pycache__/`, `.git/`, logs, and temp dirs.
These are not source files and are not part of `release/`.

## 3. Completeness of the anonymous release package

Present in `release/round2_repro/`: PROTOCOL.json, README.md,
round2_eval_config_overlay.yaml, result_schema.json,
cross_backbone_preflight.json.

Gaps relative to a full method package (LTAG/GSG/FSC module code, full
configs, training/inference/evaluation entry points, object lists, FAC
negative-result reproduction instructions):

- The method components exist in the working tree
  (`MVPainter/mvpainter/model_unet_geotex.py`, `adaptive_correction.py`,
  `MVPainter/configs/mvpainter-geotex-{gsg-fsc-only,fac-train}.yaml`,
  `geotex/` evaluation scripts, object lists under
  `final/round2/clean_dataset_v2/`) but are NOT yet copied into the release
  directory.
- The README's own "Release checklist" already records that the anonymous
  URL assembly (commit hash, ZIP SHA-256, checkpoint hashes, download
  scripts) happens "before making an anonymous URL public".

## 4. Why non-blocking

The venue accepts PDF-only initial submission (LaTeX/code required only at
revision), and the submission does not include the code package in this
round. The identity scan — the acceptance criterion — is PASS after the
scrub above. The completeness gaps are recorded as the pre-publication TODO
and do not affect any manuscript claim.
