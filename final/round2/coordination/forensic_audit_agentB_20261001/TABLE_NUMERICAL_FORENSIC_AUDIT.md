# TABLE_NUMERICAL_FORENSIC_AUDIT.md (Phase 3 + Phase 9 integration — agent B)

Covers: Trigger A (identical values), Trigger B (protocol shift), Trigger C
(CI/wording), and the Full-SSIM provenance table. Companion artifacts:
`FULL_SSIM_GLOBAL_PROVENANCE_TABLE.csv`, `phase1a_stats.json`,
`phase1b15_effective_budget_stats.json`, `phase7_r0r1_sensitivity.json`.

## Trigger A — implausibly identical values

Scanned same-runner per-object CSVs (276 rows × 4 schedules) and pairwise
deltas: **no zero-delta duplicates, no cross-method identical rows**. LLH−LHL
Full-PSNR wins 276/0 (all deltas nonzero, mean +1.193) — the opposite failure
mode of duplicated artifacts. The only exact-zero metrics found anywhere are
the bake UV-seam values, handled separately in Phase 10 (`BAKE_METRIC_IMPLEMENTATION_AUDIT.md`).

## Trigger B — UNEXPLAINED_PROTOCOL_SHIFT (historical LHL 14.78)

- Archived layer-LHL strict-276 record: FG-PSNR 14.776; seeded same-runner
  replica: 12.974 (gap ≈ 1.8 dB); R0→R1 realization drift: ≈0.03 dB.
- Status: **QUARANTINED** by the Case-B exclusion (parallel session's
  `ARCHIVED_LHL_PROVENANCE_AUDIT.md` + `historical_result_exclusion_reason.md`;
  agent B reviewed both and concurs: head/tail merge, +3.23/+0.38 dB split,
  3.3×/2.1× texture-variance reduction, GT bitwise identical, realization
  mean-neutral → randomness refuted, root cause unreconstructible).

**P0 content flag (paper, not audit-blocking but revision-mandatory):**
`final_round2.tex` L470–481 still (a) quotes the archived means (Full-PSNR
22.052, FG-PSNR 14.776, …) and (b) attributes the record to "did not seed the
Python RNG governing the reference-image preprocessing draw" — the exact
"reference preprocessing randomness" explanation the task doc forbids and the
audits refuted (realization lottery mean-neutral ≈0.03 dB cannot produce
+1.8 dB). Required revision per release rule: keep one Case-B exclusion
sentence, delete the quoted means and the RNG-causality sentence. The
accompanying claim "all holdout conclusions rest on the seeded, same-runner
confirmation set" is correct and stays.

## Trigger C — CI vs wording

Grep of `final_round2.tex` / `supplementary_round2.tex`:

- L254: "A confidence interval crossing zero is described as **no detected
  difference**, not as evidence of equivalence or non-inferiority." ✓
- L209: "they do not establish equivalence or non-inferiority" ✓
- L537–538: serialized Full-SSIM C3 loss CI "a detected loss … not evidence
  that the schedules are equivalent" ✓
- L691: warm-start control CI crossing zero → "does not prove equivalence" ✓
- No instance of "equivalent"/"non-inferior" claimed from a zero-crossing CI
  was found. **PASS.**
- ± conventions: L254 declares ± = SD across objects (matches the
  engineering convention).

## Phase 9 — Full-SSIM provenance

Full enumeration in `FULL_SSIM_GLOBAL_PROVENANCE_TABLE.csv`. Summary:

- Every Full-SSIM-bearing table is single-provenance: pre-save tables
  (`tab:strict276`, `tab:confirmation`, S9, factorial, confirmation-means
  supplement) vs the dedicated PNG-reload table (`tab:serialized276`).
- **No table mixes provenance** — the paper's design of excluding SSIM from
  `tab:stage276` and giving the saved-artifact branch its own table satisfies
  the Phase-9 gate.
- The pre-save vs saved-artifact divergence is quantified in-paper
  (mean |ΔSSIM| 0.00395 across runners; fp16→fp32 +0.03198 decomposition) and
  used only to justify non-pooling, not to retrofit numbers.
- One prose location (L478 archived quote) carries historical pre-save numbers
  — flagged above under Trigger B; it is a prose quotation, not a mixed table.

## Cross-check bonus (Phase 4 support)

Agent B's independent recomputation of the same-runner matrix reproduced the
paper/letter digits exactly: LLH−GFL FG-PSNR +3.244 (242/276), LLH−LFM
Full-PSNR +1.311 (275/276), LLH−LHL Full-PSNR +1.193 (276/276), FG-SSIM
+0.00701, FG-LPIPS −0.00889 — matching supplementary L436–443 line-for-line.

## Verdict

Tables: `VALIDATED`. Provenance discipline: `VALIDATED`. One mandatory
revision item (archived LHL prose quote + RNG causality, L470–481) carried to
the final report as a P0 content flag — to be executed only in the sanctioned
paper-revision window.
