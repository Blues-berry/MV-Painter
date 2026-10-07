# C&G revision evidence package — proposed layout

**Release status: NOT CLEARED.** This is a submission-facing structure and README draft, not a redistributable package. Candidate figure rights are `CLOSED_WITH_EXCLUSIONS`, but clean-checkout rebuild and final package review remain open. The public remote tree contains participant-level records; do not copy those records here. Do not copy source GLBs. Figure D may be included only with the 20 row-level credits in `FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`.

## Main claim

This revision evaluates how requested adapter scales are transformed by the existing MVPainter wrapper's layer rules and native caps, then measures the resulting image-space endpoint and object-level variation on Fresh C. It does not propose a new multi-view generator or establish a universally optimal schedule.

## Fresh C cohort and conditions

Fresh C uses N=300 objects. The original four conditions completed 1200/1200 rows; the LLH/generic-linear addendum completed 600/600 rows on the same frozen cohort. The six strategies reported together are no-adapter, GFL, GFH, C3, LLH, and generic linear. The inferential unit is the object. FG-PSNR and FG-LPIPS remain separate endpoints; no overall winner is defined.

## Proposed package layout

- `code/`: compact analysis and figure-generation code.
- `configs/`: frozen method and environment configuration.
- `analysis/`: documented analysis entry points and validators.
- `protocols/`: frozen cohort, endpoint, and multiplicity-family rules.
- `frozen_tables/`: approved aggregate numerical authority and derived tables.
- `figures/`: only regenerated, rights-cleared final figures.
- `supplementary/`: approved supplement and aggregate evidence.
- `archive/`: forensic/debug history not required by reviewers.

## Regeneration commands

From the repository root, the current local figure candidate command is:

```bash
python 1006/scripts/build_final_fresh_c_figures.py
```

The current closure table/reconciliation builder is:

```bash
python 1006/scripts/build_final_revision_closure_artifacts.py
```

These commands currently read files from the working evidence tree; they are not yet a self-contained clean-package build. A submission candidate must copy only approved inputs into the proposed structure, update paths, record dependency versions, and rerun from a clean checkout before publication.

## Known limitations

- Human perceptual fidelity remains an independent unresolved claim; participant-level files are prohibited from release.
- New Fresh C 24-object 3D and seam claims are retired after the native-UV/alpha gate failure.
- The preserved full asset ledger still has UNKNOWN rows. The current Figure D sources are verified CC BY with attribution; unknown source assets, source GLBs, and UID-linked per-object tables are excluded. The 300-row cohort inventory is an audit record, not a release manifest.
- strict-276 is retrospective support with incomplete runner/input-tensor provenance.
- CAI is descriptive only; Layer×Window findings are secondary, dose-limited characterization.
- R2.1 remains open as a venue-risk judgment.
- Current clean-checkout submission reproducibility is FAIL; generation and historical reconstruction have narrower limits.
