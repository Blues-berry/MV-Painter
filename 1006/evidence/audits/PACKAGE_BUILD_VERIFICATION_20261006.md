# Package analysis and manuscript-build verification — 2026-10-06

This is a same-workspace package rebuild, not an isolated clean-clone audit.
It confirms that the included compact analysis scripts and candidate LaTeX
sources execute with the files and tools available in this workspace. It does
not claim that every historical generation result can be regenerated from a
clean clone.

## Analysis and figure commands

All four commands completed successfully from the repository root:

```text
python 1006/scripts/analyze_strict276_c3_retrospective.py
python 1006/scripts/analyze_fresh_b_c3_gfl_posthoc.py
python 1006/scripts/build_objaverse_attribution_tex.py
python 1006/scripts/generate_figures.py
```

The strict-276 script regenerated 14 endpoint-pair summary rows and 552
object-contrast rows. Key results include GC3−GFL FG-PSNR +1.207771 dB
[1.116967, 1.294989] and Edge-SSIM +0.007760 [0.006773, 0.008746], and
GC3−GFH FG-PSNR −1.214235 dB [−1.313952, −1.114705] and Edge-SSIM −0.026012
[−0.028044, −0.023991]. Intervals are retrospective and nominal.

The FRESH_CONFIRM_B post-hoc script regenerated seven endpoint summary rows
and 150 object-level paired deltas. FG-PSNR GC3−GFL is +0.501881 dB
[0.341873, 0.662862] (100/150 favorable); Edge-SSIM is +0.005034
[0.003348, 0.006753] (105/150). Exploratory Holm p-values are 0.0007 across
the seven endpoints. The pair was not registered and B had already been
unblinded; these results do not become a prospective confirmation.

The attribution-table builder wrote 24 panel records from the stored
metadata snapshot. The figure script regenerated the paper figures from the
included result tables.

## LaTeX outputs

Using the supplied class/style files, both commands completed with exit code
0:

```text
cd 1006/manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error main_1006.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary_1006.tex
```

- `main_1006.pdf`: 7 pages, 270,923 bytes.
- `supplementary_1006.pdf`: 11 pages, 27,171,181 bytes.
- `pdftotext` confirmed the key results tables, retrospective labels,
  limitations, and asset-attribution section are present.
- Visual inspection covered main pages 4–7 and supplementary pages 9–11;
  no clipped tables, missing figures, or blank evidence pages were observed.

LaTeX emitted non-fatal layout warnings (underfull boxes, one small table
overrun, and template geometry warnings). There were no undefined citations,
missing graphics, or build errors. The warnings do not change the scientific
readiness verdict.

The build outputs, package scripts, and generated data are enumerated in
`source_inventory.json` and checked by `SHA256SUMS.txt`. Run
`python 1006/scripts/build_source_inventory.py` after intentional package
changes to refresh both records.

## Confirmatory human-study revision rebuild — 2026-10-07

After the human-study classification update, both manuscript sources were
rebuilt from the current candidate with the same commands above. The main
manuscript compiled to 8 pages (275,601 bytes); the supplement compiled to 12
pages (27,175,980 bytes). Text extraction confirms that main Section 4.5
reports the prespecified human endpoints with execution deviations and that
Supplement S8 contains the complete eight-endpoint table, deviation account,
and data-governance limitation. The forest plot was separately checked: the
vertical 0.5 reference, pointwise intervals, and endpoint labels are visible.

The confirmatory reanalysis reproduced 37 valid participants and all eight
endpoint estimates from the public source commit; its table is numerically
identical to the earlier sensitivity calculation. None of the eight Holm-
adjusted tests is below 0.05. The package inventory was refreshed to 477 files
and `SHA256SUMS.txt` was regenerated after the manuscript, analysis, and gate
updates. LaTeX returned success; the non-fatal layout warnings from the
template remain.
