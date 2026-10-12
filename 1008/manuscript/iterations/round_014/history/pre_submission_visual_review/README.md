# Round 014 — controlled empirical revision

This independent revision retains TCAS/C3 and uses the completed evidence to evaluate geometry-control strength, temporal allocation and actual baked appearance. No new algorithm, training run or GPU experiment was introduced in this round.

Read:

- [Clean manuscript](deliverables/Manuscript_round_014.pdf)
- [Marked manuscript versus authenticated submission](deliverables/Manuscript_round_014_marked.pdf)
- [Supplementary material](deliverables/Supplementary_round_014.pdf)
- [Response to reviewers](deliverables/Response_to_Reviewers_round_014.pdf)
- [Actual exported-mesh video](deliverables/Real_Baked_Comparison_round_014.mp4)
- [Results and remaining risks](02_RESULTS_RISKS_AND_COMPARISON.md)
- [Evidence/asset disposition](01_EVIDENCE_AND_ASSET_DISPOSITION.md)

The main findings retain the ten-object local bake gain beside the separate twenty-object non-detection. Native-interface primaries do not establish a middle-window advantage. Different cohorts, operators and sampling protocols are not pooled. Historical adapter/FAC replay gaps remain explicit.

## Rebuild and recompute

Python requirements for the current evidence computation are recorded in requirements-statistics.txt. The build additionally needs pdfLaTeX/TeX Live, latexdiff and pandoc. Journal class/style files are vendored from the authenticated source.

Run from this directory:

    python scripts/build_evidence.py
    python build_round_014.py
    python scripts/build_marked.py
    pandoc Response_to_Reviewers_round_014.md --standalone --pdf-engine=pdflatex -V geometry:margin=0.8in -V fontsize=11pt -o build/Response_to_Reviewers_round_014.pdf
    python scripts/validate_and_package.py

The authoring transformations reproduce this round from the preserved parent:

    python scripts/revise_manuscript.py
    python scripts/revise_supplement.py

Existing model inference requires the recorded upstream project, weights, licensed source inputs and environment. The available exercised inference/calibration runners are preserved under data/completed_supplement013/scripts. Their original protocol identifiers and source paths are archival; the portable object-level recomputation above requires neither GPU nor model weights. This is not a complete historical FAC training replay.

## Evidence and version identity

The current data index is data/FACTS_round_014.json. It independently reconstructs completed study means and pairwise contrasts from object/view records and checks original Holm adjustments. Source hashes, prior independent validation, corrected calibration and unchanged original375 records remain available. The seven-schedule rank sensitivity is post hoc and descriptive.

Supplementary sections S1-S9 are grouped by question. Old section IDs are mapped in SUPPLEMENT_SECTION_CROSSWALK.json. Original field names, failed-attempt statuses and source-protocol identifiers are preserved as historical evidence, rather than relabeled as current status.

The marked PDF uses CFONT text additions/deletions against the authenticated submitted final_0903.tex, SHA256 203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01. Tables are treated atomically and deleted display equations are suppressed for safe rendering. Removed-only references/citations display identifiers. The complete expanded-source change record is CHANGES_FROM_AUTHENTICATED_SUBMISSION.diff; details are in MARKED_DIFF_SCOPE.json. A later-round source is not substituted for the submission baseline.

Images are recorded research outputs with retained credits. The conceptual interface figure keeps its existing AI-artwork disclosure; new numerical figures are produced directly from recorded data. No image-generation tool retouched experimental outputs.

## Delivery scope

The review package includes source, rebuild files, object/view metrics, protocols, analysis code, attributed displays and the actual exported-mesh video. Four first-input-object exports (GT, Native, Fixed Mean and Late-high) support the named application comparison; every method remains in the numerical data and video. Trained weights, the complete generated-image archive and participant-level responses are not included. Source assets must be obtained under their recorded licenses. Raw diagnostic arrays and the full mesh archive remain in the preserved server evidence archive.

The GitHub copy is in the existing private author-review repository. It is not a journal submission or a declaration that all reviewer concerns have been resolved.
