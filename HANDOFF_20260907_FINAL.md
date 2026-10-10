# 01549 manuscript handoff and recovery

The authoritative submitted baseline is CAG-S-26-01549. The 48-page Editorial Manager PDF at the repository root has SHA-256 `5de31993ec9f40a0e7a43d5c8d2ac0816a6d057e715348d23f2e157dc0aca6ba`. The byte-identical 15-page standalone manuscript copies have SHA-256 `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da`.

## Preserve these 01549 source and recovery files

- Submitted package and original TeX archive: `final/submission_new_0907/` and `final/submission_new_0907/latex.zip`.
- Submitted TeX archive SHA-256: `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`.
- Main TeX sources: `final/final_0903.tex`, `final/final_0903_marked.tex`, and `final/final_0903_marked_addonly.tex`.
- Supplementary TeX source: `final/supplementary_0903.tex`.
- Current reviewer-revision sources derived from 01549: `final/round2/final_round2.tex` and `final/round2/supplementary_round2.tex`.

The CAG-D-26-00962 reviewer materials are retained as the review set for this 01549 revision, per the author's confirmation. The submitted 01549 PDF remains the immutable baseline; later TeX sources are revision work products.

## Rebuild the submitted manuscript

From `final/`, run:

```sh
latexmk -pdf -interaction=nonstopmode final_0903.tex
latexmk -pdf -interaction=nonstopmode final_0903_marked.tex
python3 strip_difdel.py
latexmk -pdf -interaction=nonstopmode final_0903_marked_addonly.tex
```
