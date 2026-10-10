#!/usr/bin/env python3
"""Assemble a timestamped 1008 submission draft from the authoritative package."""
from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVISION = ROOT / "1008/manuscript/revision_01549_restored"
REVIEW = ROOT / "1008/submission_1008_author_review"
OUT = ROOT / "1008/submission_1008"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy(src: Path, relative: str) -> Path:
    if not src.is_file():
        raise FileNotFoundError(src)
    dest = OUT / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def run(args: list[str], cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    run(["python3", str(ROOT / "1008/scripts/build_latex_source_1008.py")])
    run(["pandoc", str(REVIEW / "UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.md"),
         "--pdf-engine=xelatex", "-V", "geometry:landscape",
         "-V", "geometry:margin=0.22in", "-V", "fontsize=6pt",
         "-o", str(REVIEW / "UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.pdf")])
    run(["pandoc", str(REVIEW / "Response_to_Reviewers_1008.md"),
         "-o", str(REVIEW / "Response_to_Reviewers_1008.docx")])

    active_tex = REVISION / "manuscript_1008.tex"
    review_tex = REVIEW / "Manuscript_1008.tex"
    if digest(active_tex) != digest(review_tex):
        raise SystemExit("Active manuscript TeX differs from the reviewed package copy.")

    core = {
        "Manuscript_1008.tex": active_tex,
        "Manuscript_1008.pdf": REVIEW / "Manuscript_1008.pdf",
        "Marked-up_Manuscript_1008.pdf": REVIEW / "Marked-up_Manuscript_1008.pdf",
        "Supplementary_1008.tex": REVISION / "Supplementary_1008.tex",
        "Supplementary_1008.pdf": REVIEW / "Supplementary_1008.pdf",
        "Response_to_Reviewers_1008.md": REVIEW / "Response_to_Reviewers_1008.md",
        "Response_to_Reviewers_1008.pdf": REVIEW / "Response_to_Reviewers_1008.pdf",
        "Response_to_Reviewers_1008.docx": REVIEW / "Response_to_Reviewers_1008.docx",
        "LaTeX_Source_1008.zip": REVIEW / "LaTeX_Source_1008.zip",
    }
    for name, src in core.items():
        copy(src, name)

    # Figures named by the active manuscript and supplement, kept upload-ready.
    figure_sources = {
        "fig1_tcas_control.pdf": REVISION / "figures/fig1_tcas_control.pdf",
        "fig2.pdf": REVISION / "fig2.pdf",
        "fig3.pdf": REVISION / "fig3.pdf",
        "fig4_freshc_context_roi.pdf": REVISION / "figures/fig4_freshc_context_roi.pdf",
        "fig5_freshc_context_roi.pdf": REVISION / "figures/fig5_freshc_context_roi.pdf",
        "fig6_color_diagnostic_freshc_context_roi.pdf": REVISION / "figures/fig6_color_diagnostic_freshc_context_roi.pdf",
        "fig7_c3_development.pdf": REVISION / "figures/fig7_c3_development.pdf",
        "figS1_adverse_c3_gfl.png": REVISION / "figures/figS1_adverse_c3_gfl.png",
    }
    for name, src in figure_sources.items():
        copy(src, f"Figures/{name}")

    # Remove superseded color panels that were retired from the active package.
    for name in (
        "fig8_color_failure_01549.pdf",
        "figS1_color_detail_failure.png",
    ):
        (OUT / "Figures" / name).unlink(missing_ok=True)

    author_review_files = [
        "01549_TO_1008_CHANGELOG.md",
        "FIGURE_TABLE_DISPOSITION.csv",
        "FIGURE_ASSET_CREDITS.csv",
        "FIGURE_ASSET_PROVENANCE.md",
        "FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv",
        "REVIEWER_CLAIM_EVIDENCE_MATRIX.csv",
        "REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv",
        "FINAL_REVIEWER_CLOSURE_MATRIX.md",
        "UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.md",
        "UNRESOLVED_REVIEWER_RISKS_AND_EXPERIMENT_DECISIONS.pdf",
        "REVIEW_PACKAGE_INDEX.md",
        "SOURCE_PACKAGE_BUILD_CHECK.md",
    ]
    for name in author_review_files:
        copy(REVIEW / name, f"Author_Review/{name}")
    cross_backbone_source = ROOT / "1008/audits/source_evidence/r2/cross_backbone_20261010"
    cross_backbone_dest = OUT / "Author_Review/Cross_Backbone_Evidence_20261010"
    if cross_backbone_dest.exists():
        shutil.rmtree(cross_backbone_dest)
    shutil.copytree(cross_backbone_source, cross_backbone_dest)
    direction_source = ROOT / "1008/audits/MVDIFFUSION_RAW_DIRECTION_CORRECTION_20261010"
    direction_dest = OUT / "Author_Review/MVDIFFUSION_RAW_DIRECTION_CORRECTION_20261010"
    if direction_dest.exists():
        shutil.rmtree(direction_dest)
    shutil.copytree(direction_source, direction_dest)
    preflight_source = ROOT / "1008/audits/source_evidence/r2/applied_budget_preflight_20261010"
    preflight_dest = OUT / "Author_Review/Applied_Budget_Preflight_20261010"
    if preflight_dest.exists():
        shutil.rmtree(preflight_dest)
    shutil.copytree(preflight_source, preflight_dest)
    dimension_source = ROOT / "1008/audits/source_evidence/r2/audits/residual_norm_dimension_20261010"
    dimension_dest = OUT / "Author_Review/Residual_Norm_Dimension_Audit_20261010"
    if dimension_dest.exists():
        shutil.rmtree(dimension_dest)
    shutil.copytree(dimension_source, dimension_dest)
    copy(ROOT / "1008/audits/source_evidence/r2/reviewer_materials/SECOND_ROUND_REVIEWER_COMMENTS.txt",
         "Author_Review/Reviewer_Source/SECOND_ROUND_REVIEWER_COMMENTS.txt")
    copy(REVIEW / "figures/FIGURE_ASSET_CREDITS.csv",
         "Author_Review/FIGURE_ASSET_CREDITS.csv")
    copy(REVIEW / "figures/FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv",
         "Author_Review/FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv")
    copy(ROOT / "1008/audits/source_evidence/r1/fresh_c_visual/FRESH_C_COLOR_FIGURE_SELECTION.csv",
         "Author_Review/FRESH_C_COLOR_FIGURE_SELECTION.csv")

    # Keep the copy-forward forms visible but clearly separated from approved files.
    for name in (
        "Titlepage_0907.pdf",
        "Acknowledgements_0907.docx",
        "Declaration_of_Interest_0907.docx",
        "Original_Conference_Submission_0907.pdf",
        "CARRYOVER_STATUS.md",
    ):
        if not (OUT / "Administrative_Carryover_0907" / name).is_file():
            raise FileNotFoundError(OUT / "Administrative_Carryover_0907" / name)

    # Produce combined convenience copies.
    run(["pandoc", str(OUT / "Cover_Letter_1008_DRAFT.md"),
         "-o", str(OUT / "Cover_Letter_1008_DRAFT.docx")])
    run(["pandoc", str(OUT / "Cover_Letter_1008_DRAFT.md"),
         "--pdf-engine=xelatex", "-o", str(OUT / "Cover_Letter_1008_DRAFT.pdf")])
    run(["pandoc", str(OUT / "Research_Highlights_1008_DRAFT.md"),
         "-o", str(OUT / "Research_Highlights_1008_DRAFT.docx")])
    run(["pandoc", str(OUT / "Research_Highlights_1008_DRAFT.md"),
         "--pdf-engine=xelatex", "-o", str(OUT / "Research_Highlights_1008_DRAFT.pdf")])
    run(["pdfunite", str(OUT / "Response_to_Reviewers_1008.pdf"),
         str(OUT / "Manuscript_1008.pdf"),
         str(OUT / "Manuscript_with_Response_1008.pdf")])

    with tempfile.TemporaryDirectory(prefix="titlepage_1008_") as tmp:
        tmpdir = Path(tmp)
        tex = OUT / "Titlepage_1008_DRAFT.tex"
        run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={tmpdir}", str(tex)])
        shutil.copy2(tmpdir / "Titlepage_1008_DRAFT.pdf",
                     OUT / "Titlepage_1008_DRAFT.pdf")

    graphical_abstract = OUT / "Graphical_Abstract_1008_DRAFT.pdf"
    graphical_abstract_preview = OUT / "Author_Review/Graphical_Abstract_1008_DRAFT_preview.png"
    if not graphical_abstract.is_file() or not graphical_abstract_preview.is_file():
        run(["python3", str(OUT / "supporting_scripts/build_graphical_abstract_1008.py")])

    # Verify the included source archive is a paper package, not a data dump.
    forbidden = (".json", ".npz", ".pt", ".pth", ".ckpt", ".glb")
    with zipfile.ZipFile(OUT / "LaTeX_Source_1008.zip") as archive:
        bad = [n for n in archive.namelist() if n.lower().endswith(forbidden)]
    if bad:
        raise SystemExit(f"Unexpected generated/data artifacts in source archive: {bad[:5]}")

    captured = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = f"""# 1008 submission package status

**Status:** `DRAFT`

**Captured:** `{captured}` UTC

**Journal submission:** not made

**Submission approval:** `NO`

This is the full local 1008 package layout for author review. It contains the current paper files, response, supplementary material, source archive, upload-ready figures, and clearly separated administrative carry-overs from the 7 September 2026 submission. The carry-over files have not been represented as newly approved author declarations.

## Authoritative paper files

- Active source: `1008/manuscript/revision_01549_restored/manuscript_1008.tex`
- Package TeX SHA-256: `{digest(OUT / 'Manuscript_1008.tex')}`
- Package PDF SHA-256: `{digest(OUT / 'Manuscript_1008.pdf')}`
- Package TeX is byte-identical to the active source. This packaging step did not edit the paper source.

## Before any journal upload

- Confirm current manuscript ID and editor instructions.
- Verify the carried-forward title page, author metadata, funding acknowledgements, and declaration of interests.
- Approve the cover letter and research highlights drafts.
- Confirm whether the 0907 conference-paper attachment is still required.
- Confirm any current graphical-abstract or demo-media requirement. The 0907 graphical abstract, highlights, cover letter, and demo were not reused because they contain superseded claims or have no authenticated 1008 update.
- Review the response and all PDF page/line references before submission.

No journal submission was made. `SUBMISSION_APPROVED=NO`.
"""
    (OUT / "SUBMISSION_PACKAGE_STATUS.md").write_text(status, encoding="utf-8")

    # Keep the package's newly authored text metadata free of trailing whitespace.
    for rel in (
        "README.md",
        "Cover_Letter_1008_DRAFT.md",
        "Research_Highlights_1008_DRAFT.md",
        "Titlepage_1008_DRAFT.tex",
        "Administrative_Carryover_0907/CARRYOVER_STATUS.md",
        "supporting_scripts/build_graphical_abstract_1008.py",
    ):
        path = OUT / rel
        text = path.read_text(encoding="utf-8")
        normalized = "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"
        path.write_text(normalized, encoding="utf-8")

    # Manifest is generated after payload and status files; it intentionally excludes itself.
    manifest = OUT / "SUBMISSION_FILE_MANIFEST.csv"
    status_by_prefix = {
        "Administrative_Carryover_0907/": ("CARRYOVER_VERIFY", "0907 form/attachment; verify before 1008 upload"),
        "Author_Review/": ("AUTHOR_REVIEW_MATERIAL", "Internal traceability/provenance support"),
        "Figures/": ("CURRENT_MANUSCRIPT_ASSET", "Exact image asset referenced by active TeX/Supplement"),
        "Cover_Letter_1008_DRAFT": ("DRAFT_AUTHOR_APPROVAL", "Updated for current second-round evidence; author checks remain"),
        "Research_Highlights_1008_DRAFT": ("DRAFT_AUTHOR_APPROVAL", "Scoped to the current manuscript claims"),
        "Graphical_Abstract_1008_DRAFT": ("DRAFT_AUTHOR_APPROVAL", "Vector figure generated from the current Fresh C result and limits"),
        "Titlepage_1008_DRAFT": ("DRAFT_AUTHOR_APPROVAL", "Metadata reconstructed from 0907; author verification required"),
        "Manuscript_": ("CURRENT_AUTHOR_REVIEW", "Current 1008 author-review build"),
        "Marked-up_": ("CURRENT_AUTHOR_REVIEW", "Current 01549-to-1008 tracked-additions PDF"),
        "Supplementary_": ("CURRENT_AUTHOR_REVIEW", "Current 1008 supplement"),
        "Response_to_Reviewers_": ("CURRENT_AUTHOR_REVIEW", "Current second-round response"),
        "Manuscript_with_Response_": ("CURRENT_AUTHOR_REVIEW", "Convenience bundle: response followed by manuscript"),
        "LaTeX_Source_": ("CURRENT_SOURCE_PACKAGE", "Clean 1008 source archive; generated/raw data excluded"),
    }
    payload = [p for p in OUT.rglob("*") if p.is_file()
               and p.name not in {manifest.name, "SHA256SUMS.txt"}]
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["path", "bytes", "sha256", "status", "notes"])
        for path in sorted(payload):
            rel = path.relative_to(OUT).as_posix()
            status_value, note = ("PACKAGE_SUPPORT", "Package instructions or build source")
            for prefix, item in status_by_prefix.items():
                if rel.startswith(prefix) or path.name.startswith(prefix):
                    status_value, note = item
                    break
            writer.writerow([rel, path.stat().st_size, digest(path), status_value, note])

    checksum_path = OUT / "SHA256SUMS.txt"
    checksum_files = [p for p in OUT.rglob("*") if p.is_file() and p != checksum_path]
    with checksum_path.open("w", encoding="utf-8") as stream:
        for path in sorted(checksum_files):
            stream.write(f"{digest(path)}  {path.relative_to(OUT).as_posix()}\n")
    print(f"Package assembled at {OUT}")
    print(f"Captured {captured}; files={len(checksum_files)}; bytes={sum(p.stat().st_size for p in checksum_files)}")


if __name__ == "__main__":
    main()
