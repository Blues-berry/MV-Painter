# TCAS final submission candidate — author review

This is the single new candidate from the final scientific/editorial integration. Original01549,1014finalv1 and the earlier frozen candidate are preserved outside this directory. No formal journal submission or author approval is claimed.

## Read these first

- [Chinese author review](FINAL_AUTHOR_REVIEW_ZH.md)
- [Clean manuscript,15 pages](1014finalv1.pdf) and [source](1014finalv1.tex)
- [Supplement,71 pages](Supplementary_1014finalv1.pdf) and [source](Supplementary_1014finalv1.tex)
- [Response,5 pages](review/Response_to_Reviewers.pdf) and [editable text](review/Response_to_Reviewers.md)
- [Marked manuscript versus authenticated01549,22 pages](marked/Marked_up_Manuscript_01549.pdf)
- [Final editable Figure1](figure1/fig1_tcas_editable.svg), [vectorPDF](figure1/fig1_tcas.pdf), [preview](figure1/fig1_tcas_preview.png)
- [Before/after figure comparison](figure1/FINAL_FIGURE_COMPARISON.png)
- [Claim/evidence map](CLAIM_EVIDENCE_MAP.csv), [verification report](VERIFICATION_REPORT.md), [SHA manifest](MANIFEST.sha256)

## Status

Scientific accuracy and editorial/technical checks pass within the documented inspection scope. R1 andR2 closure remain PARTIAL; R2.1 remains PARTIALLY ADDRESSED. AUTHOR_APPROVAL=PENDING. Diagram clarity and successful builds do not establish algorithmic novelty or material fidelity.

## Evidence and sources

`data/` retains all144 frozen source files byte-identically, including the original timing primary and its separate twelve-test family. Historical negatives and incomplete provenance remain explicit. `fac_code_snapshot/` preserves recovered components, not verified full historical training. Figure1's portable raw sources, trace, identity ledger and editable generator are in `figure1/`; all RGB changes are forbidden. `vendor/source_01549/final_0903.tex` is the authenticated baseline, SHA203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01.

## Rebuild and verify

Run `python build_1014finalv1.py` from this directory to rebuild main/supplement using the frozen vector figure; run `bash review/build_response.sh` for the response and `python marked/build_marked.py` after the main build for the marked PDF. The reviewer-location template and final label map are in `audit/`; if manuscript pagination changes, resolve those locations against the newaux before rebuilding the response. `python scripts/build_evidence.py` recomputes existing object statistics into an audit report without replacing frozen data or figures. It does not run models.

`python figure1/fig1_generator.py` rebuilds the final editable figure from packaged source images andtrace; itsPDF may differ in creation metadata. To use a regeneratedPDF, copy it to `figures/fig1_tcas_control.pdf` before rebuilding the main. Required local tooling: pdflatex/latexdiff/pandoc and Python NumPy,SciPy,Matplotlib,Pillow,CairoSVG. Fonts are DejaVu Sans from the recorded Linux font location. Compiled figures contain embedded fonts. No checkpoint download or GPU is required to rebuild documents or verify the delivered statistics.

Git delivery is on codex/tcas-final-submission-20261013. The commit identifier is returned in the delivery message; it is not embedded in its own hashed files. The manifest excludes transient build outputs and itself.
