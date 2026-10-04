# FORMAL_VISUAL_EVIDENCE_AUDIT — Experiment D

Objects: the 24-object set frozen in visualization_24.txt BEFORE any method
metric was computed (GT-only stratification: texture tercile x coverage
tercile, geometry-tercile spread within cells, seed 20261002; see
stratification_summary.json). No "representative" imagery is used anywhere.

Artifacts: formal_qualitative_archive/ —
  * panel_<i>_<uid>.png: per object, GT (unique6 views 0,15,12,16,13,14) +
    no_adapter + native GFL/GFH/GC3 + LFM-EXACT + LHL + LLH
  * contact_sheet_24.png: full 24-object contact sheet
  * archive_manifest.json (selection rule, condition list, missing count = 0)

Provenance: all prediction panels are byte-frozen outputs of the formal
campaigns (predictions/<condition>/<uid>.png, shared latents per object,
latent seed 42) — identical reference draw across conditions.

Post-metric figure sets (strongest win / median / strongest loss) were NOT
generated: any such selection would require a rank rule and disclosure; the
pre-frozen stratified set was preferred to keep the archive strictly
selection-free. If needed later, the rank rule must be pre-registered and
disclosed in captions.