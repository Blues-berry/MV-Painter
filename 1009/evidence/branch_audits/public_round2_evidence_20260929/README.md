# Archived public Round-2 evidence branch audit

## Decision

- Source branch: `codex/public-round2-evidence`
- Archived source HEAD: `78c871ffb4a9906b86b3a0c801d8286607799e3d`
- Parent: `d9379fe93e51a5dbf28cc1bfce9bd72b80bdbc48`
- Merge base with audited main: `34c77a4417eb3e037756ad483c70ef9e3f0c2bdb`
- Source status: `SOURCE_READY` at the archived commit; no worktree was checked out or changed for this audit.
- Integration: `SELECTIVE_CONTENT_MERGE`; full-history merge rejected; `NO_CONFLICT` because no merge or cherry-pick was attempted.
- Paper impact: `INDIRECT`. This compact result package restores the source rows behind the current paper's stage-placement values. No manuscript, Supplement, response, figure, or submission file was edited.

The source branch has 80 commits, 548 trees, 1,282 unique blobs (650,449,134 uncompressed bytes), including 14 blobs at least 5 MiB and a largest blob of 76,043,516 bytes. Its tree differs from the audited main in 2,395 paths. It adds legacy `final/` content and deletes 253 active `1008/` paths and 484 `1009/` paths. Its ignore rules also reopen broad legacy output trees. The history is not safe to merge wholesale.

The source changes `GeoTexResnetWrapper._skip_correction` from an instance field to a class field and toggles it around the reference-write pass without `try/finally` or restoration of prior state. That can leak state across concurrent calls and leave correction disabled after an exception. Main's instance-local state and exception-safe restoration are retained. No runtime code from this branch was selected; `MVPainter/src/data/mvpainter_dataset.py` is unchanged.

## Selected evidence

The package retains the unified formal per-object table, its protocol and terminal manifests, the accepted paired analysis, the saved-PNG-reload Full-SSIM table and analysis, and the contemporaneous baseline audit note. `SOURCE_IMPORT_MANIFEST.csv` records all 294 tracked files in the source stage-placement directory plus the selected coordination report (295 source paths total).

The four formal per-schedule CSVs were omitted as duplicate partitions of `per_object_metrics.csv`. The four saved-SSIM partitions contain the same object, UID, and metric values as `serialized_full_ssim_per_object.csv`; the unified table also preserves prediction metadata. The 276 generated per-object JSON runner records were inspected and validated but are not copied into this curated package. Their metric rows agree with the CSVs and their 55,200 residual samples are finite. The original records remain recoverable from the archived source commit. Three transient status/coordination markers are omitted; `final_manifest.json` records the terminal result.

## Validation and paper traceability

The run manifest records checkpoint SHA-256 `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`, the 276-object list SHA-256 `a6aa8ab6e475763e1b5e67dc8c712ec8f1940e3952d65897c820887554bbd044`, 50 steps, seed 42, and four schedules (`fixed_mean`, `hll`, `llh`, `c3_lhl`). The terminal manifest reports 276 records and zero errors. The acceptance manifest reports 1,104 finite formal rows and 50 logged residual steps per object/schedule.

Validation found that all 1,104 rows in the unified CSV exactly match the four per-schedule CSVs and the metric rows in all 276 JSON records. The saved object-level bootstrap comparisons reaggregate exactly from the per-object rows with `geotex/round2_stats.py` (10,000 resamples, seed 20260928). The current Supplement's Table S7 matches all 12 displayed formal means and confidence intervals when the raw `C3 − comparator` convention is recomputed. The source acceptance JSON uses a benefit-oriented sign for LPIPS, whereas Table S7 displays raw differences; the LPIPS signs were therefore checked against the raw per-object rows. The saved-PNG-reload Full-SSIM mean and interval also reaggregate exactly.

This is the source of the current manuscript's post-inspection `MAIN-STAGE-276` claim: `C3 − temporal L–L–H` FG-PSNR is `−0.177084` dB (95% object-bootstrap CI `[−0.230539, −0.130784]`), with L–L–H favorable on all six formal endpoints. `C3 − fixed-mean` FG-PSNR is `+0.502875` dB (95% CI `[+0.462018, +0.542244]`). The saved-artifact Full-SSIM result is kept separate from the formal pre-save metrics.

The manuscript already labels this as a post-inspection analysis on the clean-v2 276-object cohort, not an independent replication or a dose-matched causal test. The separate retrospective Core-7 rows are not interchangeable with these stage-placement rows; the source audit does not pool or substitute them. No schedule-optimality claim follows from these comparisons.

The active manuscript and Supplement SHA-256 values remain `dd7cb925ea098f31a12753d8b368e621c458bdef2d8b7f4a57935aaadce73ff4` and `59f0809bf0cb3c03b645380afb1bc5f3849008588902b5ca8422c65cf5c2e7ed`. The response source remains `1fadfc5714ed3864f702d0238aa348c8782500c5c42369d9d7763390ba974cdb`; the canonical submission package checksum list still passes 48/48. No TeX or submission file changed, so no rebuild was needed. `SUBMISSION_APPROVED=NO`.

`SHA256SUMS.txt` covers this curated package. No predictions, checkpoints, GLBs, generated images, or full worktree were copied.
