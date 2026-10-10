# 1008 scientific and response consistency audit

> **Historical candidate audit:** this report records an earlier 13-page main, 11-page Supplement, and 19-page marked-up PDF. Its artifact hashes and page locators are superseded by [`1008_RESPONSE_LOCATOR_AUDIT.md`](1008_RESPONSE_LOCATOR_AUDIT.md) and [`../submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md`](../submission_1008_author_review/SOURCE_PACKAGE_BUILD_CHECK.md). Use those files for the current 16/16/16-page build.

**Review basis:** authenticated 01549 post-first-round manuscript, final 1008 active TeX/PDFs, Supplementary Material, response Markdown/PDF, figure/table disposition, and reviewer locator matrix. This report replaces older consistency reports whose page counts and manuscript hashes belong to superseded candidates.

## Source and compiled artifact identity

| Artifact | SHA-256 | Pages / size |
|---|---|---|
| Active Manuscript TeX | `6767189865c00b6cb90867c4428ff921a2d2c2fa6eb03fc9fc705604ef1e2525` | 59,741 bytes |
| Manuscript PDF | `93aefbf6cb5ef68382db18342acbb791b833f1e87f45494558452ae8b4114e4d` | 13 pages; 3,952,160 bytes |
| Supplementary TeX | `2a92459d9a43e6d4222a5f41d0809670c6822feec9db325e99478f086a69549f` | 36,128 bytes |
| Supplementary PDF | `5a2a41ffd151785469665f53241807ea283fa2894a6eec0fd77f9f969b63989f` | 11 pages; 4,036,225 bytes |
| Response Markdown | `47d74ac5ed14b9c3b45d41e064c1da36219d49b7e872e7e4ba6bf340e2a243d5` | 13,066 bytes |
| Response PDF | `ff80bbaf94ee1b0b1d6b596e640eab0035f7a7700d3ffa37efdd0671f4a1b203` | 5 pages; 34,844 bytes |
| Marked-up Manuscript PDF | `6951be9831fbf7d472ea30e0bee4472d1d25b93fd9508bd3380000563834f424` | 19 pages; 4,042,537 bytes |
| Fresh C layout comparison PDF | `79c2db05799f5729f128a6c76a2476098f16c75378c9a75fb413a0734ecd4a85` | 2 pages; 9,891,159 bytes |

The active main TeX matches the author-review copy byte-for-byte. The supplement TeX matches the packaged source byte-for-byte. The main and marked-up PDFs are byte-identical to their recorded build outputs. Local TeX Live and clean-source-ZIP builds succeeded. The app-side compiler did not complete on the isolated worktree path; the saved project build scripts and clean-source ZIP both completed.

## Reviewer locator audit

The response letter uses section, figure, table, and supplement-section names rather than fixed PDF page numbers. The accompanying `REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv` provides page and TeX-line anchors; the current 13-page main PDF and 11-page supplement were inspected by page text extraction. Verified anchors are:

| Point | Main manuscript locator | Supplement locator |
|---|---|---|
| R1.1 | Figures 4–5, pp. 11–12; limitations, pp. 8–9 | Figure S1, p. 9; S6–S8, pp. 8–9 |
| R1.2 | protocol, pp. 4–5; Tables 3–4, p. 8 | S2, p. 2; Core-7 S5, pp. 6–7; S8, p. 9; historical S9, pp. 9–10 |
| R1.3 | metric scope, pp. 3–4; Fig. 4, p. 11; preference Table 5, p. 8; limitations, p. 8 | S2, p. 2; S7, pp. 8–9 |
| R1.4 | Table 4 and endpoint discussion, p. 8 | S2, p. 2 |
| R1.5 | FAC subsection, p. 7; limitations, p. 8 | S11, pp. 10–11; dose-response Table S13, p. 11 |
| R2.1 | Introduction/Related Work, pp. 1–3; Method, pp. 3–5; Fresh C results, p. 8 | S3–S5, pp. 3–7; S9, pp. 9–10 |
| R2.2 | TCAS Method, p. 4; historical Table 2, p. 6; development Fig. 6, p. 13 | S10, pp. 9–10 |
| R2.3 | stage/applicability analysis, p. 7; limitations, p. 8 | S5, pp. 5–7 |
| R3 | No technical edit claimed | No new experiment claimed |

The retrospective Core-7 table reports opposing C3−GFH results (+0.725229 dB Full-view PSNR, nominal 95% CI [+0.647134,+0.806467]; −1.214235 dB FG-PSNR, [−1.313952,−1.114705]). These saved-row intervals are descriptive and post hoc; Core-7 does not establish a single runner or complete input identity across its seven conditions. It is not pooled with Fresh C and is not a reproduction of the submitted +0.96 dB result. A former reviewer-matrix row that labeled it same-runner/confirmatory was corrected in both active copies.

The reviewer claim/evidence matrix was reconciled with the final manuscript: FAC and the original 01549 three-condition preference result are marked as retained historical evidence with limits; the separate V3 status remains “no new responses.”

## Scientific claim cross-check

- Fresh C is described as the author-specified paired N=300 comparison under one frozen checkpoint, common runner, seed policy, cohort, inputs, views, and metrics, using recorded cap semantics. The primary C3−GFL FG-PSNR value is `+0.522352 dB`, with 95% object-bootstrap CI `[+0.404160,+0.640669]`. No historical Table 4 checkpoint-hash gate is imposed.
- GFH and Generic Linear remain counter-results with more favorable means than C3 on all four displayed endpoints. The C3−GFH Edge-SSIM contrast remains `−0.01881` with interval `[−0.02084,−0.01683]`; no equivalence or non-inferiority claim is made.
- The historical v1/v2 distinction is preserved: the 01549 main-table and Section 4.7/FAC runs are not silently unified; Fresh C is not claimed to reproduce the old `+0.96 dB` estimate.
- Variation metrics are labeled as diagnostics, not texture fidelity. The retained preference study is kept separate from Fresh C and from fidelity claims.
- FAC is retained as previously reported first-round evidence with the 1,200-versus-1,706 list discrepancy and missing run-bound seed/output manifest disclosed. The response does not claim public code release.
- CAI's selector/proposition/proof/optimality claim is withdrawn; TCAS, its equation, C3 profile, and development history remain.
- R2.3 is explicitly not fully answered: no matched same-intervention evaluation on a genuinely different geometry-conditioned multi-view backbone is claimed. R3 receives no invented technical task.

## Remaining limits

R1.1 remains partial because Fresh C did not pass the bake-input gate and does not establish a new seam/PBR result. R1.5 retains first-round outcomes with incomplete run provenance. R2.1 remains subject to editorial novelty judgment. R2.3 remains open. The figure provenance note records creator attribution present in the Supplement and limits this package to private review; public redistribution rights were not re-audited here.
