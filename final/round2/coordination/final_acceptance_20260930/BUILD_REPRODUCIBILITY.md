# BUILD_REPRODUCIBILITY (final acceptance, 2026-09-30)

Source commit at build time: `66044ca07d723c2dfeb66d4f28623a3d8d76e530`
(branch `codex/next-review-response-20260930`)

## Self-contained build from `final/round2`

Both documents now compile **inside** `final/round2` with no dependency on the
parent `final/` directory:

- `fig1_layerwise_20260930.pdf` copied to `final/round2/fig1_layerwise_20260930.pdf`
  (SHA-256 `83085718f0dd38329509ff6e651ca99b588d12fcf65110f739c91327f032ce9f`,
  byte-identical to `final/fig1_layerwise_20260930.pdf`).
- `elsevier-logo.pdf` and `cag-logo.pdf` copied into `final/round2/`
  (previously resolved only from the parent directory; without them
  `pdflatex` exited 1 with two `File not found` errors).
- `elsarticle.cls` and `cag.sty` provided as symlinks to `../output/`
  (the frozen build-dependency store; existing `final/` symlinks untouched).
- `\includegraphics` paths rewritten from `round2/...` to be relative to
  `final/round2` in `final_round2.tex` and `supplementary_round2.tex`
  (build-infrastructure change only; rendered content identical).

## Compile commands

```bash
cd final/round2
pdflatex -interaction=nonstopmode final_round2.tex         # 2 passes
pdflatex -interaction=nonstopmode supplementary_round2.tex # 2 passes
```

Working directory: `/4T/CXY/MV-Painter/final/round2`

## Results

| Document | Exit code | Errors | Pages | Undefined refs | Undefined citations | Warnings |
|---|---|---:|---:|---|---|---|
| final_round2 | 0 | 0 | 13 | 0 | 0 | 2 (font shape substitution, benign) |
| supplementary_round2 | 0 | 0 | 7 | 0 | 0 | 1 (`h` float specifier changed to `ht`, benign) |

## SHA-256

| File | SHA-256 |
|---|---|
| final_round2.tex | `cc8e29659340d344733581f0f8cda3e545230fd41301bc19d332097b1b360d92` |
| supplementary_round2.tex | `046d10b710ac42213b8a83fb1cc18bc366186d805383727df8a9bccb1d6b1340` |
| final_round2.pdf | `f4f6dcd6acb8c0863202b55ca3cc66741ffa70bd70b8187bc5c537592c7e040a` |
| supplementary_round2.pdf | `ad97f1cee9d3b72996fd6766803d8ea90aa457b9b060531331cd07664b221695` |
| fig1_layerwise_20260930.pdf | `83085718f0dd38329509ff6e651ca99b588d12fcf65110f739c91327f032ce9f` |

## Phase 12 final-build hashes (supersedes the baseline above)

Source commit: `2b788e6` (paper sync). Working tree clean at build time;
TeX identical to the committed version.

| File | SHA-256 |
|---|---|
| final_round2.tex | `7164cac3e6b8d97de4aaee4c746192e2459a92303b171f868a847f6ff45382a1` |
| final_round2.pdf | `30150d0efadd1ebf8621112c16aade00573a67b8c8a17d9581b006a371b55aee` |
| supplementary_round2.tex | `be0fb55892771d28e00b609a3ec822e76140aade941e1e2aff745d4c66294a58` |
| supplementary_round2.pdf | `28a623a85d4d98616fb353df7590a2025e1d059697271869dca4f252cfe381cb` |
| response_letter_round2.md | `de5ec77a55a87945ca39a9ccc81b2614a219f4be86756106724e73a85489c287` |

Final build: 0 errors, 0 undefined references/citations, main 13pp,
supplementary 7pp; PDF metadata contains no author identity (Creator=TeX,
Producer=pdfTeX-1.40.20). Bibliography: 43 entries (1:1 with the frozen
reference list).
