# Round015: application repeatability, incoming-view diagnostics and recoverable FAC code

Parent: frozen round014 commit `249f86d`. The title and TCAS/C3 identity are preserved. Core metrics, paired primary/secondary tests and all adverse outcomes remain unchanged. New seed/dominance/UV-overlap summaries are post-inspection descriptive additions, not fresh confirmatory experiments. No new algorithm, model training, parameter search or generated model outputs were introduced.

The ten-object original UV-projection diagnostic was replayed from its recorded source bytes: all 80 values match exactly. Known camera-color controls pass, while identical black controls give zero variance despite their unfaithful appearance. This distinguishes incoming-view agreement from fidelity and does not validate quantitative seams, PBR or arbitrary UV/camera calibration.

GSO100/GSO20 fixed-seed summaries retain all three seeds and use objects as the resampling unit. Small cohort-average PSNR effects do not provide universal per-object repeatability. Four-endpoint Fresh C dominance is a descriptive comparison of recorded composite point estimates, not significant per-object quality dominance.

`fac_code_snapshot` contains two recovered entry trees and the source/component audit. Their controller source is identical; three distinct CPU fixtures verify component forward/gradient paths and state-save/load identity. Full historical FAC training/checkpoint replay remains incomplete. See the source README before using archival configuration or comments.

Build the main text/Supplement with `python build_round_015.py`. `scripts/build_marked.py` compares the marked manuscript to the authenticated original submission. Install `requirements-statistics.txt` and run `scripts/build_evidence.py`, `scripts/analyze_stability015.py` and `scripts/analyze_cross_view015.py` to recompute statistics. The projection replay additionally requires the recorded licensed images/meshes and Trimesh; its snapshot and hash/path protocol are in `data/gap_closure015`. The standalone FAC component rerun requires PyTorch and `python scripts/audit_fac_source015.py --snapshot-only`, without base diffusion weights.

The complete submission ZIP contains the updated main/marked/Supplement/response, other administrative attachments, flat LaTeX source, statistics, recovered FAC source, licensed mesh examples and videos. Unzip it and upload the corresponding items separately according to the file map. This is private author-review delivery, not a journal submission or a complete replication badge application.

Round-specific comparison and remaining reviewer risks: `02_RESULTS_RISKS_AND_COMPARISON.md`. Three-round review: `03_ROUNDS_013_015_SYNTHESIS_ZH.md`. Validation and checksums are recorded in the final manifests. No calibrated acceptance probability or 90% acceptance guarantee is asserted.

VISUAL_MODEL_REVIEW.json is a release snapshot of the actual reviewed PDFs/plots/rendered pages. Rebuilding can change PDF metadata and file bytes; renewed byte checks and presentation review are needed before calling a changed build the same reviewed snapshot. The isolated source rebuild is verified for extracted text/layout, not identical PDF creation-time bytes.
