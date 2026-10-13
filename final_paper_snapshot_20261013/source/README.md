# Final empirical manuscript and reproduction source

This final package consolidates existing experiments; it contains no new training or inference.

Build clean, Supplement and authenticated-baseline marked PDFs with `python3 build_final.py` (pdflatex and latexdiff required).

Install `requirements-statistics.txt`. Recompute inherited evidence with `python3 scripts/build_evidence.py`, `python3 scripts/analyze_stability015.py` and `python3 scripts/analyze_cross_view015.py`. These scripts write derived figures/tables; run in a copied directory when preserving release bytes.

Run `python3 verify_added_evidence.py` to reproduce the original Middle-minus-average(Early,Late) primary exactly and verify all added requested-slot means. Run `python3 data/original276_retrain/recompute_statistics.py --output /tmp/request276.json --verify-against data/original276_retrain/EXTERNAL_AUDIT.json`. Repeat with `--exclude-known-replacement --verify-against data/original276_retrain/FAILED_INPUT_EXCLUSION275.json` and a distinct output file for the failed-slot sensitivity. These are descriptive requested-slot analyses; one known random replacement prevents exact 276 actual-UID confirmation.

FAC components run on CPU with PyTorch using `python3 scripts/audit_fac_source015.py --snapshot-only`; this is not historical full-model training replay. See `fac_code_snapshot/README.md`.

The data/attempt_registry directory preserves 105 experiment/iteration/archive entries and selected additional negative-development reports. Copies, seeds and views are not new independent cohorts. Licensed raw meshes/images, bulk checkpoints and participant-level human responses are not redistributed. Current-at-audit helper snapshots are not authenticated historical runtime bytes. Complete inference additionally requires the recorded upstream runtime, weights and licensed assets.

Author identity/funding declarations are inherited from the prior author materials and remain separate from the anonymous main manuscript. The packet is prepared for author review and has not been submitted to a journal.
