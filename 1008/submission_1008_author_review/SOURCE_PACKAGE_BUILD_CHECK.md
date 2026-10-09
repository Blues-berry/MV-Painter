# 1008 clean-source package and build check

**Captured:** `2026-10-09T15:11:43Z` UTC  
**State:** `AUTHOR_REVIEW_READY / DRAFT`; no journal submission; `SUBMISSION_APPROVED=NO`.

## Source identity

- Active main TeX SHA-256: `1a6e7e5365634445ad73e02c146fd1c62b28c5372cfede028ca85028dbdb8409`.
- Active Supplement TeX SHA-256: `eb524d957fb2be30ea2ef5615ba1a031f104a5d5cc002f0df54ead4d5ac7d2c1`.
- Main and Supplement TeX in the author-review folder match the active sources byte-for-byte.
- Source ZIP: 44 members, 32,012,972 bytes, SHA-256 `56314a762b75f9cbec6473ddcebc3284762f0ff3865b360b6c535359a23a5c72`, CRC `OK`.
- ZIP manuscript/Supplement members match the active TeX byte-for-byte. Excluded generated/data extensions: 0 (`.json`, `.npz`, `.pt`, `.pth`, `.ckpt`, `.glb`).
- Authenticated 01549 baseline TeX SHA-256: `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`.

## Delivered build artifacts

| File | Pages | Bytes | SHA-256 |
|---|---:|---:|---|
| `Manuscript_1008.pdf` | 13 | 3,955,936 | `3b6f4f42e6982da25bd8096321184ef6f0ff9c309690f057462ec1f22519e8a2` |
| `Marked-up_Manuscript_1008.pdf` | 13 | 3,969,882 | `784ce3e443aa3700e130ec27fc76282ac9806d486833a08d854068ce3ba02984` |
| `Supplementary_1008.pdf` | 13 | 4,047,319 | `e43d87e48254d744fe7433d1d28a573e0f9fc4a1785b175ff8735ed9e81925ad` |
| `Response_to_Reviewers_1008.pdf` | 6 | 39,469 | `a0375867f2b7365c61a0aae9ca09a5677c4b8d7479500bcb970c8ef0d8cafdb2` |

The editable response DOCX SHA-256 is `65e2b82a2e511e609d348eec971b5a7f6512bb7bba1cec5311058f6821e8d30e`; its source Markdown SHA-256 is `041c978d4d83767921f68af2100ec0c67c275b007cb62b805da02cdb26f7ee78`.

## Clean source extraction

A fresh temporary directory was populated only from `LaTeX_Source_1008.zip`. All three included scripts exited successfully; each executes pdfLaTeX twice. Main manuscript, Supplement, and marked-up output rebuilt at 13, 13, and 13 pages. Whitespace-normalized text extracted from each clean-build PDF matches its delivered counterpart. The ZIP passes CRC and excludes the listed generated/checkpoint/GLB extensions.

Rendered-page review covered main manuscript pp. 8–9 and 11–12 and Supplement p. 13. The matched full-object figures, tables, and final color-diagnostic paragraph fit without clipping; the Supplement ends on its final text page rather than carrying a stray line to a blank page.

## Reviewer-source provenance and limits

The retained round-two review PDF is labeled “initial-submission reviews”; exact second-round comment text has not been authenticated. The response follows the current task and preserved issue/evidence matrix and remains subject to author verification against the editor's original decision letter.

Fresh C is not a numerical reproduction of the 01549 +0.96 dB estimate. Color diagnostics are failure-enriched and validate no repair. No valid Fresh C bake/seam/PBR or matched second-backbone TCAS comparison is available. Cover letter, highlights, graphical abstract, and title page remain author-review drafts.

The Codex built-in LaTeX compiler was invoked on the saved active manuscript, but the request remained pending without diagnostics and was stopped after repeated waits. This does not count as an editor-native compile pass. The repository's two-pass build scripts succeeded from the working tree and clean ZIP extraction; those are the certified build checks for this package.
