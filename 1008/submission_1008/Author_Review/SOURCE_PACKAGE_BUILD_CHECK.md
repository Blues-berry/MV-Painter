# 1008 final build and clean-source check

**Captured:** 2026-10-10 · **State:** `AUTHOR_REVIEW_READY / DRAFT` · **Submission approval:** `NO`

## Source identity

- Active manuscript TeX SHA-256: `c2d53295f32cfce1730f4b56f4a3820ddcc422caabca56ccd3f95486846684dc`.
- Active Supplement TeX SHA-256: `226aa3c7e9d597a9b71ad9efddd5427b7d13d375bb4c45795d4d8ea7417383e5`.
- Both TeX files in the author-review folder match the active sources byte-for-byte.
- `LaTeX_Source_1008.zip`: 45 members, 32,191,366 bytes, SHA-256 `06858818d3a011630b808cd50bc993d331f923fc2a795858543521dcb6dd3c60`; ZIP CRC passes.
- The archive excludes `.json`, `.npz`, `.pt`, `.pth`, `.ckpt`, `.glb`, `.pyc`, build outputs, and caches. It includes the active main and Supplement sources, their build scripts, required figures, and the historical 01549 source materials.
- Authenticated 01549 TeX SHA-256 remains `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.

## Final author-review artifacts

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 16 | 4,162,592 | `93ec302d912ad1964575581e13b9d27dfbca3db729e0058274a57946208fe84b` |
| `Marked-up_Manuscript_1008.pdf` | 17 | 4,186,867 | `b4f92a7829b564e54680c9a84fed2a7e355cb2f6ee5fc8585c10ba42a14d2130` |
| `Supplementary_1008.pdf` | 13 | 4,047,325 | `d5b660a65f0e8a58208a8a2b5dab567ad39bdfd5de3cfc400334641701707590` |
| `Response_to_Reviewers_1008.pdf` | 6 | 43,337 | `49f4d8f046b033364c063655b03cb44ca6b16e37346a2a865deca38b3d77d069` |
| `Response_to_Reviewers_1008.docx` | — | 16,981 | `c1f3a96c432c90ce04c6e3e3a1d9f0427a8d6b915b6bbb0bbf5df018998ece26` |
| `UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.pdf` | 1 | 24,797 | `480ebbc3b910b3c763caebd1a5341bf80b9961fbd9b93402a9656ce25a38c3f2` |

The concise 01549→1008 change note and the risk/experiment decision table accompany these files. Response headings are explicitly marked for author verification against the editor's exact second-round decision.

## Build and evidence checks

- The repository scripts `build_revision_1008.sh`, `build_supplement_1008.sh`, and `build_marked_up_1008.sh` all exited successfully from the working tree.
- The clean ZIP was extracted into an empty temporary directory; all three scripts rebuilt the main, Supplement, and marked-up PDFs at 16, 13, and 17 pages. Whitespace-normalized extracted PDF text matched each corresponding author-review PDF. The logs contain no unresolved citations or references.
- Page review covered the Fresh C summary Tables 3–4 (main p. 8), temporal/layer/color Tables 5–7 (p. 9), interface and preference Tables 8–9 (p. 10), Limitations (p. 11), and Figures 4–7 (pp. 13–16). The tables and captions fit; figure context/ROI pairs and the archival color example render without clipping. The one-page risk PDF was also checked.
- Main numerical anchors were checked against the preserved canonical evidence: Fresh C N=300, C3−GFL FG-PSNR `+0.522352` dB `[+0.404160,+0.640669]`; GFH and Generic Linear outperform C3 on all four shown cohort means; C3/GFL applied deep/middle sums are `82.5/62.5`; the separate strict-276 temporal L–L–H result favors that profile on six endpoints but does not match realized residual dose. The 26-object color sample remains failure-enriched, and the Fresh C bake gate remains failed.
- The LaTeX template reports minor logo-cell overfull boxes below 1.1 pt and ordinary underfull boxes; no text, table, or figure clipping was observed. `latexdiff` prints Unicode “Wide character in print” warnings, but the marked-up PDF builds and its extracted text matches the delivered copy.

## Remaining author actions and scientific limits

- Compare the paraphrased response headings with the exact second-round decision; the retained review PDF in the workspace says “Initial submission.”
- Confirm publication/redistribution rights for the archival Figure 6 panel, or remove/replace it. Its PDF is byte-identical to the 01549 source figure, but its panel-level object/run map and underlying model-asset rights are not available.
- The main remaining scientific risks are the task-specific novelty judgment (R2.1), unresolved native-default/color/3D validation (R1.1), and absent matched cross-backbone intervention (R2.3). No GPU experiment was launched. E1 remains the preferred conditional experiment only after its unchanged-input CPU preflight passes.
- No journal submission was made; `SUBMISSION_APPROVED=NO`.
