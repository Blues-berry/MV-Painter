# 1008 numerical and citation consistency report

This current report supersedes old numerical reports tied to the frozen 9-page candidate. It is based on the authenticated 01549 source, the active 1008 main and supplement, their delivered PDFs, the response source/PDF, and the reviewer traceability table.

- Active main source hash and the main/supplement/response/marked-up PDF hashes and page counts are listed in `1008_FINAL_SCIENTIFIC_CONSISTENCY_REPORT.md`.
- The main and supplement local TeX builds completed successfully per `1008_FINAL_BUILD_REPORT.md`; the final main and supplement report no unresolved citations or cross-references. The app-side compiler could not initialize platform directories for the isolated worktree source.
- The response uses full precision for the registered Fresh C primary value (`+0.522352 dB`, CI `[+0.404160,+0.640669]`) and preserves the rounded main-table rendering. It also reports the C3−GFH Edge-SSIM trade-off (`−0.01881`, CI `[−0.02084,−0.01683]`).
- GFH and Generic Linear counter-results, the historical v1/v2 distinction, the lack of a non-inferiority margin, the retained first-round preference/FAC work and their scope limits, the CAI withdrawal, and the open R2.3 generalization question are consistent across the manuscript, supplement, and response.
- Page/section/figure/table locators were checked against extracted text from the current 13-page main and 11-page supplement. Fresh C Figures 4–5 occupy pages 11–12; the historical development Figure 6 is on page 13. Exact reviewer-to-manuscript and TeX-line mapping is in `review/REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv`.

No claim of texture fidelity, valid Fresh C baking, seam quality, PBR quality, human preference for Fresh C, unique CAI-derived optimum, or cross-backbone generalization is made.
