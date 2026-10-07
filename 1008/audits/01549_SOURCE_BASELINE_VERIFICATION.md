# 01549 source-baseline verification

Audit date: 2026-10-07 UTC  
Working branch: `codex/cg-round2-1008-revision-20261008`  
Evidence reference: `d59c4606ad54239bf4df4f20067bcc54989404f7`

## Selected submission source

The 01549 baseline is the source package submitted as
`final/submission_new_0907/latex.zip`, specifically its `final_0903.tex`
member. The package and submitted manuscript agree on the title, abstract,
section order, figure captions, and nine numbered tables. The submission PDF
is `final/submission_new_0907/Manuscript 0907.pdf`.

| Artifact | SHA-256 | Finding |
|---|---|---|
| Submitted LaTeX package | `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a` | Source archive used as the baseline |
| `final_0903.tex` inside the package | `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01` | Matching 01549 source |
| Submitted manuscript PDF | `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da` | 15 pages; matches the archived `final/final_0903.pdf` byte-for-byte |
| Current root `final/final_0903.tex` | `fc61ce367b4297e001a409084201e9f67f208fc05da82ff70af67f094ff31746` | Not the source that generated the submitted PDF; its title and contents differ |

The submitted title is **“Timestep-Conditioned Adapter Scaling for Multi-view
Diffusion Texture Generation.”** The source sequence is Introduction, Related
Work, Method, Experiments, Limitations, Conclusion, Data availability, and
Declaration. The package contains Figures 1–7 and Tables 1–9.

## Build verification

The package source was extracted and rebuilt with:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error final_0903.tex
```

The rebuild used pdfTeX / TeX Live 2019 and latexmk 4.67. It produced 15 pages
with the submitted PDF's page dimensions. The rebuilt binary differed because
of PDF metadata/timestamps, while all 15 pages rasterized identically at
100 dpi and the extracted text/layout matched. The PDF match, rather than the
current root TeX filename, is the deciding provenance check.

## 1008 preservation copy

The verified package source, its original ZIP, submitted PDF, figures, and
required style/class files have been copied without replacing the submitted
source into:

`1008/manuscript/source_01549/`

The extraction contains `final_0903.tex`, `fig1.pdf`–`fig7.pdf`,
`cag.sty`, `elsarticle.cls`, and the original package/PDF copies. This
directory is the read-only revision source. New manuscript files will be
created separately in `1008/manuscript/`.

## Excluded manuscript candidate

At the d59 checkout, `final/round2/final_round2.tex` has SHA-256
`d40b992663c943d27aa637386503456b6d5d8afa316269dad8a8662136c789f1`.
It is a later, substantially restructured candidate, not the 01549 source.
The exact claimed eight-page d59 PDF was not present at that commit, and the
source did not clean-build there because its class/style and figure inputs
were absent. Therefore the eight-page count is not authenticated by the
available d59 checkout. This does not affect the identity of the submitted
01549 baseline.
