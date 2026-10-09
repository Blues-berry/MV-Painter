# Reviewed color-cast investigation archive

This is a file-level archive of the reviewed r1color evidence, not an adopted repair or a paper-facing experiment. The source worktree remains at `/4T/CXY/MV-Painter-r1color`, branch `codex/r1-color-cast-repair-v2-20261009`, commit `32bb9106fa0ea6199e6a16f9279343c0b21581a6`. Every copied file is byte-checked against that source and listed in `1009/main_consolidation/MAIN_INTEGRATION_COPY_MANIFEST.csv`.

## What the evidence supports

- In the four-object Phase B development probe, changing the global appearance embedding changed chroma in both registered directions on all four objects; the VAE-only arm did not. This identifies a controllable color pathway in those cases, not the complete cause of the original color drift.
- The Fresh B input-only audit found the stored cache matched neither the exact current transformed condition nor the selected raw-source reconstruction within 0.03 for any of 150 inputs. On 98 selected-view-014 inputs, the cache was closer to raw view 000 in 84. This is a cache/source mismatch observation, not a color-causality test.
- C1 met its four-object numeric gate (mean unseen-view ΔFG-CIEDE2000 = −1.5602; 95% CI [−2.2621, −0.6299]; 4/4), but failed the locked visual gate: one case showed no clear gain, and the other retained mismatch with a faint cyan/blue silhouette rim. Fresh B was not opened for validation.
- B2 attempt 04 completed eight GPU generations on four development objects, with 24 matched object/view pairs; its four cached-baseline outputs reproduce the prior Phase B GFL images. Replacing the cached embedding with the selected raw-source embedding did not pass the frozen correction gate (mean paired ΔFG-CIEDE2000 = +0.172906; 95% CI [−0.204353, +0.681015]; 1/4 objects improved), and the casebook shows no clear correction. It does not validate a repair.
- B2's target-grid and mask-grid hashes were reconstructed after generation from the same code/seed/CUDA path because the sampler did not capture them in-process. Treat that reconstruction as supplemental provenance, not an independent live hash record. No independent Fresh B repair validation was performed.

The root-cause verdict therefore remains partial: global appearance conditioning controls chroma, and cache/source alignment is a plausible object-dependent contributor. Neither C1 nor B2 is a validated color repair. No color-repair code was added to the default inference path.

## Archive boundary

The included PDFs, protocol locks, verdicts, and small result tables were selected because they explain or directly support the reviewed findings. The branch-specific runners and summarizers remain on the source branch: they depend on that checkout's local dataset/checkpoint paths and are not standalone main-repository tools. Raw predictions, caches, embeddings, and other generated outputs remain in the source worktree. The valid local-only checksum list covers 84 files. The branch's `SHA256SUMS.txt` is stale: 12 of 107 listed hashes differ, while the affected files match their committed Git blobs; that list is not used as evidence.

The C1 visual review PDF is retained once; the two other casebook PDFs in the source branch are exact duplicates. The Fresh B files here are input audits only. `D_VALIDATION_LOCK.json` is a protocol record; its proposed validation was not run.
