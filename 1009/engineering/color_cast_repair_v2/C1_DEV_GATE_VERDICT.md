# C1 development gate verdict

**Decision: FAIL; stop before independent validation.** The method, four-object cohort, thresholds, metrics, and visual stop rule were frozen in `protocol/C1_DEV_METHOD_LOCK.json` before the C1 outcome was reviewed. The final decision and evidence hashes are pinned in `C_REPAIR_METHOD_LOCK.json`.

Numeric criteria passed: mean unseen-view ΔFG-CIEDE2000 −1.5602 (95% paired object-bootstrap CI [−2.2621, −0.6299], 4/4 wins); mean ΔFG-PSNR +0.1805 dB; mean ΔFG-LPIPS −0.00186; mean foreground L* SSIM-to-GT Δ −0.00015. Bootstrap used 10,000 draws with seed 20261009 and objects as the resampling unit.

The mandatory visual criterion failed. On Fig. 4 row 1, the candidate is nearly indistinguishable from GFL and does not visibly correct the cast. On Fig. 4 row 2, the bounded shift cools the output but leaves a substantial mismatch and introduces faint cyan/blue silhouette rims. The normal-color and high-texture objects showed no obvious detail/structure damage or new cast. The review uses the four development objects only and is recorded in `runs/phase_c/dev/C1_DEV_MANUAL_REVIEW.json`; its casebook is `C_REPAIR_BEFORE_AFTER.pdf`.

Because one gate failed, the candidate was not frozen for holdout, Fresh B was not opened, no validation amendment was created, and no Fresh B repair run was authorized. Do not describe this candidate as a validated or successful repair.
