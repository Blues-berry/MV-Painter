# TCAS final submission candidate — author review

This is the pre-submission revision of the published e943 candidate. Original01549,1014finalv1 and the earlier frozen candidate are preserved outside this directory. No formal journal submission or author approval is claimed.

## Read these first

- [Chinese author review](FINAL_AUTHOR_REVIEW_ZH.md)
- [Clean manuscript,14 pages](1014finalv1.pdf) and [source](1014finalv1.tex)
- [Supplement,71 pages](Supplementary_1014finalv1.pdf) and [source](Supplementary_1014finalv1.tex)
- [Response,5 pages](review/Response_to_Reviewers.pdf) and [editable text](review/Response_to_Reviewers.md)
- [Marked manuscript versus authenticated01549,22 pages](marked/Marked_up_Manuscript_01549.pdf)
- [Final editable Figure1](figure1/fig1_tcas_editable.svg), [vectorPDF](figure1/fig1_tcas.pdf), [preview](figure1/fig1_tcas_preview.png)
- [Before/after figure comparison](figure1/FINAL_FIGURE_COMPARISON.png)
- [Claim/evidence map](CLAIM_EVIDENCE_MAP.csv), [verification report](VERIFICATION_REPORT.md), [SHA manifest](MANIFEST.sha256)

## Status

Scientific accuracy and editorial/technical checks pass within the documented inspection scope. R1 andR2 closure remain PARTIAL; R2.1 remains PARTIALLY ADDRESSED. AUTHOR_APPROVAL=PENDING. Diagram clarity and successful builds do not establish algorithmic novelty or material fidelity.

## Evidence and sources

`data/` retains all144 frozen source files byte-identically, including the original timing primary and its separate twelve-test family. Historical negatives and incomplete provenance remain explicit. `fac_code_snapshot/` preserves recovered components, not verified full historical training. The current Figure1 is the author-selected illustrative interface. The original author SVG, editable export and generator are in `figure1/`; former experimental figure records are preserved in `figure1/baseline_e943/`. `vendor/source_01549/final_0903.tex` is the authenticated baseline, SHA203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01.

## Rebuild and verify

Run `python build_1014finalv1.py` from this directory to rebuild main/supplement using the frozen vector figure; run `bash review/build_response.sh` for the response and `python marked/build_marked.py` after the main build for the marked PDF. The reviewer-location template and final label map are in `audit/`; if manuscript pagination changes, resolve those locations against the newaux before rebuilding the response. `python scripts/build_evidence.py` recomputes existing object statistics into an audit report without replacing frozen data or figures. It does not run models.

`python figure1/fig1_generator.py` rebuilds the final editable figure from the preserved original author SVG; itsPDF may differ in creation metadata. To use a regeneratedPDF, copy it to `figures/fig1_tcas_control.pdf` before rebuilding the main. Required local tooling: pdflatex/latexdiff/pandoc and Python NumPy,SciPy,Matplotlib,Pillow,CairoSVG. Fonts are DejaVu Sans from the recorded Linux font location. Compiled figures contain embedded fonts. No checkpoint download or GPU is required to rebuild documents or verify the delivered statistics.

Git delivery is on codex/tcas-final-submission-20261013. The commit identifier is returned in the delivery message; it is not embedded in its own hashed files. The manifest excludes transient build outputs and itself.

Pre-submission repairs have been independently checked in the actual PDFs. Public reviewer-material permissions, original human-study ethics documentation, journal-system requirements and final coauthor approval remain separate author decisions; full private audit reports are not included here. Restored standalone GT context: `python scripts/analyze_gt_context.py`. Both GeoTex22s and GSO5.5s videos are supplied separately.
