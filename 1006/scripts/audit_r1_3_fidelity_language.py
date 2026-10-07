#!/usr/bin/env python3
"""Create a sentence-level audit of fidelity and texture-variation language."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "1006/review/R1_3_FIDELITY_LANGUAGE_AUDIT.csv"
TERMS = re.compile(
    r"fidel\w*|preserv\w*|texture[ -]rich|rich[ -]texture|detail[ -]preserv\w*|"
    r"structure[ -]preserv\w*|gradients?|gradient magnitude|laplacian|variation\w*|"
    r"color variation|texture[ -](?:detail|loss|flatten\w*|degrad\w*|retention|retained|quality|naturalness|variation)|"
    r"more texture|texture retained|preference\w*|percept\w*|clip-iqa|blinded readers|human study|"
    r"blinded first choices",
    re.IGNORECASE,
)
SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"(])")
FIELDS = [
    "record_id",
    "original_location",
    "source_file",
    "source_sha256",
    "companion_source_file",
    "companion_source_sha256",
    "audit_script_file",
    "audit_script_sha256",
    "original_sentence",
    "evidence_type",
    "fidelity_measured",
    "disposition",
    "proposed_wording",
    "reason",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return [part.strip() for part in SENTENCE_BREAK.split(text) if part.strip()]


def tex_records(path: Path, display_pdf: str, pdf_hash: str) -> list[dict[str, str]]:
    text_hash = sha256(path)
    section = "Preamble"
    abstract = False
    records = []
    for line_no, original in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = re.sub(r"(?<!\\)%.*$", "", original).strip()
        if not line:
            continue
        if r"\begin{abstract}" in line:
            abstract = True
            section = "Abstract"
        for command in ("section", "subsection", "subsubsection", "paragraph"):
            prefix = "\\" + command + "{"
            if line.startswith(prefix):
                section = line[len(prefix):].split("}", 1)[0]
        if r"\end{abstract}" in line:
            abstract = False
        location_type = "caption" if r"\caption{" in line else "text"
        if abstract:
            section = "Abstract"
        for sentence in split_sentences(line):
            if not TERMS.search(sentence):
                continue
            location = f"{display_pdf}; {path.relative_to(ROOT)}:{line_no} ({section})"
            if location_type == "caption":
                location = f"{display_pdf}; figure/table caption; {path.relative_to(ROOT)}:{line_no} ({section})"
            records.append({
                "original_location": location,
                "source_file": display_pdf,
                "source_sha256": pdf_hash,
                "companion_source_file": str(path.relative_to(ROOT)),
                "companion_source_sha256": text_hash,
                "original_sentence": sentence,
                "document_kind": "supplement" if "supplementary" in path.name else "manuscript",
            })
    return records


def docx_records(path: Path, companion: Path, label: str) -> list[dict[str, str]]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs = [
        "".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
        for paragraph in root.findall(".//w:p", ns)
    ]
    rows = []
    for para_no, paragraph in enumerate(paragraphs, start=1):
        for sentence in split_sentences(paragraph):
            if TERMS.search(sentence):
                rows.append({
                    "original_location": f"{label}; paragraph {para_no}",
                    "source_file": str(path.relative_to(ROOT)),
                    "source_sha256": sha256(path),
                    "companion_source_file": str(companion.relative_to(ROOT)),
                    "companion_source_sha256": sha256(companion),
                    "original_sentence": sentence,
                    "document_kind": "review_response" if "response" in path.name.lower() else "highlights",
                })
    return rows


def graphical_abstract_records(path: Path, companion: Path) -> list[dict[str, str]]:
    extracted = subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True, errors="replace")
    blocks = [re.sub(r"\s+", " ", block).strip() for block in extracted.splitlines() if block.strip()]
    # The graphic uses line breaks as layout, so these three text boxes are kept intact.
    claims = [
        "Uniform high scale: structure up, texture down (Lap. var. 67.8%, RGB std 64.3% of conservative)",
        "C3: +0.96 dB PSNR vs. s=2.50, FG-SSIM comparable (n.s.); texture retained (Lap. var. 83.5%)",
        "58.1% blinded first choices (cluster bootstrap CI excludes zero)",
    ]
    if not blocks:
        raise SystemExit(f"Could not extract text from graphical abstract: {path}")
    extracted_text = re.sub(r"\s+", " ", extracted).casefold()
    anchors = (
        "uniform high scale: structure up, texture down",
        "lap. var. 67.8%",
        "rgb std 64.3%",
        "c3: +0.96 db psnr",
        "texture retained",
        "83.5%",
        "58.1% blinded first choices",
    )
    missing_anchors = [anchor for anchor in anchors if anchor not in extracted_text]
    if missing_anchors:
        raise SystemExit(f"Graphical-abstract text changed; re-review these extracted anchors: {missing_anchors}")
    rows = []
    for box_no, claim in enumerate(claims, start=1):
        rows.append({
            "original_location": f"{path.relative_to(ROOT)}; page 1; text box {box_no}",
            "source_file": str(path.relative_to(ROOT)),
            "source_sha256": sha256(path),
            "companion_source_file": str(companion.relative_to(ROOT)),
            "companion_source_sha256": sha256(companion),
            "original_sentence": claim,
            "document_kind": "graphical_abstract",
        })
    return rows


def annotate(row: dict[str, str]) -> dict[str, str]:
    sentence = row["original_sentence"]
    lower = sentence.lower()
    kind = row["document_kind"]
    if kind in {"highlights", "graphical_abstract", "review_response"} and any(term in lower for term in ("preference", "blinded first choices", "blinded readers")):
        evidence = "Manuscript-reported human preference; not reanalyzed here"
        measured = "NO_DIRECT_FIDELITY (preference is relative, not reference fidelity)"
        disposition = "REMOVE"
        proposed = "Remove from reviewer-facing materials in this non-human closure; keep separate from any manuscript human-evidence review."
        reason = "The revision plan excludes current human results from this reviewer response; preference is not a direct measure of reference fidelity."
    elif "preference" in lower or "naturalness" in lower or "blinded" in lower:
        if any(term in lower for term in ("psnr", "laplacian", "gradient", "rgb standard", "texture retained", "more texture")):
            evidence = "Mixed image-space metric and manuscript-reported human preference; participant data not reviewed"
            measured = "NO_DIRECT_FIDELITY (separate proxies and preference only)"
            disposition = "REWRITE"
            proposed = "If retained after separate human-evidence clearance, report image-space metrics and relative preference separately; neither establishes reference fidelity."
            reason = "The sentence combines proxy metrics with a relative preference result; this audit does not verify the study or interpret participant responses."
        else:
            evidence = "Human preference study as described in the manuscript; participant data not reviewed"
            measured = "NO_DIRECT_FIDELITY (preference only)"
            disposition = "REWRITE"
            proposed = "If retained after separate human-evidence clearance, describe only relative preference for the tested outputs and criteria; do not call it fidelity."
            reason = "Preference ranks alternatives but does not establish reference fidelity, material correctness, or general visual quality; this audit does not verify the study results."
    elif "clip-iqa" in lower:
        evidence = "No-reference learned image-quality score"
        measured = "NO_DIRECT_FIDELITY (model score only)"
        disposition = "REWRITE"
        proposed = "Report the CLIP-IQA score and sample as a separate no-reference model score; do not describe it as validated perceptual fidelity."
        reason = "A learned no-reference score is not direct evidence of reference matching or universal perceptual correctness."
    elif kind == "manuscript" and any(phrase in lower for phrase in ("faces challenges", "texture generation requires", "the task is", "the goal is")) and not any(metric in lower for metric in ("psnr", "lpips", "laplacian", "gradient magnitude", "rgb standard")):
        evidence = "Problem formulation / task motivation"
        measured = "NO_DIRECT_FIDELITY (not an outcome claim)"
        disposition = "KEEP"
        proposed = "Keep as task motivation; make clear that this describes an objective rather than evidence that fidelity was achieved."
        reason = "The sentence states a challenge or design goal and does not report a measured outcome."
    elif any(term in lower for term in ("epsilon-equivalent", "fidelity-equivalent", "fidelity-equivalence", "fidelity objective", "fidelity-optimal", "maximize fidelity", "fidelity optimum")):
        evidence = "PSNR-based stage-selection rule / heuristic"
        measured = "NO_DIRECT_FIDELITY (PSNR objective only)"
        disposition = "REWRITE"
        proposed = "Name foreground PSNR explicitly; call epsilon a selection tolerance and remove statistical-equivalence wording."
        reason = "PSNR is an image-space endpoint, and an epsilon selection rule does not establish perceptual fidelity, equivalence, or non-inferiority."
    elif any(term in lower for term in ("psnr", "lpips")) and any(term in lower for term in ("texture", "laplacian", "gradient", "rgb standard", "color variation", "high-frequency")):
        evidence = "Mixed image-space metrics: signal/feature distance and texture-variation diagnostics"
        measured = "NO_DIRECT_FIDELITY (separate image-space endpoints only)"
        disposition = "REWRITE"
        proposed = "Report each named metric separately; do not combine PSNR and variation statistics into a claim of preserved texture or reference fidelity."
        reason = "Image-space endpoints describe distinct pixel, feature-distance, or variation properties and do not establish material correctness or human fidelity."
    elif "lpips" in lower:
        evidence = "Learned deep-feature image-distance metric"
        measured = "NO_DIRECT_FIDELITY (feature distance only)"
        disposition = "REWRITE"
        proposed = "Describe LPIPS as a learned feature-distance endpoint and report it separately; do not treat it as universal visual correctness."
        reason = "LPIPS measures a learned feature distance and does not establish reference correctness or human fidelity."
    elif "percept" in lower:
        evidence = "Perceptual proxy or broad quality interpretation"
        measured = "NO_DIRECT_FIDELITY (model score or relative judgment only)"
        disposition = "REWRITE"
        proposed = "Name the perceptual proxy or preference measure and limit the conclusion to that measure; do not claim general perceptual fidelity."
        reason = "CLIP-IQA, LPIPS, and relative preference do not establish universal visual correctness or reference fidelity."
    elif any(term in lower for term in ("laplacian", "gradient", "rgb standard", "lap. var.", "texture metric", "texture-preservation", "texture preservation", "texture loss", "texture degradation", "texture flattening", "texture-flattening", "texture quality", "high-frequency", "color variation", "texture detail", "texture retention", "texture retained", "more texture")):
        evidence = "Image-space texture-variation statistic and/or fixed-view visual comparison"
        measured = "NO_DIRECT_FIDELITY (proxy/illustration only)"
        if any(phrase in lower for phrase in ("taking laplacian variance", "where lap denotes", "computed on foreground", "bottom: gradient magnitude", "proxy metrics for texture degradation")):
            disposition = "KEEP"
            proposed = "Keep as a metric definition or limitation, explicitly stating that these diagnostics summarize image-space variation and do not measure fidelity."
            reason = "The statement defines or limits the proxy statistics; it does not claim that the values establish reference or perceptual fidelity."
        else:
            disposition = "REWRITE"
            proposed = "Report the named image-space metric changes separately as variation diagnostics; do not call them texture preservation, fidelity, or material correctness."
            reason = "Laplacian variance, RGB standard deviation, and gradient magnitude quantify image variation/frequency content, not semantic material accuracy or perceived fidelity."
    elif any(term in lower for term in ("preserv", "retained", "retains more", "texture down")) and not ("envelope" in lower and "texture" not in lower and "color" not in lower):
        evidence = "Author interpretation of image-space appearance or variation"
        measured = "NO_DIRECT_FIDELITY (proxy/illustration only)"
        disposition = "REWRITE"
        proposed = "Replace 'preserve/retain' with the named observed metric or visible example, and state that it does not establish reference fidelity."
        reason = "A change in image-space variation or a selected still does not show that reference details or materials were faithfully reproduced."
    elif any(term in lower for term in ("psnr", "signal fidelity", "signal quality")):
        evidence = "Pixel-space image metric (PSNR / FG-PSNR)"
        measured = "NO_DIRECT_FIDELITY (image-space endpoint only)"
        disposition = "REWRITE"
        proposed = "Replace general 'fidelity' or 'signal quality' wording with the exact PSNR/FG-PSNR endpoint and its comparator."
        reason = "PSNR summarizes pixel error and does not establish human perceptual fidelity, material correctness, or 3D appearance."
    elif "visual fidelity" in lower or "texture fidelity" in lower or "fidelity" in lower:
        evidence = "Conceptual statement or broad image-space interpretation"
        measured = "NO_DIRECT_FIDELITY"
        disposition = "REWRITE"
        proposed = "Frame this as a task objective or a bounded image-space observation, not as measured visual fidelity."
        reason = "No single endpoint in this sentence measures reference fidelity across appearance, materials, views, and human perception."
    elif kind == "graphical_abstract":
        evidence = "Graphical summary of image-space metric contrasts"
        measured = "NO_DIRECT_FIDELITY (metric summary only)"
        disposition = "REWRITE"
        proposed = "State the separate metric contrast and avoid 'texture down/retained' as a fidelity conclusion."
        reason = "The displayed Laplacian-variance and RGB-standard-deviation ratios are image-variation summaries, not direct texture-fidelity measures."
    elif kind == "conclusion_tradeoff":
        evidence = "Cohort-level image-space metric interpretation"
        measured = "NO_DIRECT_FIDELITY (endpoint pattern only)"
        disposition = "REWRITE"
        proposed = "Describe the observed endpoint-specific pattern and limit the conclusion to the tested schedules and image-space diagnostics."
        reason = "A metric-defined shape/texture trade-off does not establish improved reference or perceptual fidelity."
    elif kind == "review_response":
        evidence = "Reviewer-response summary of image-space evidence"
        measured = "NO_DIRECT_FIDELITY"
        disposition = "REWRITE"
        proposed = "State the named endpoint and its scope; do not use 'fidelity' as a synonym for a proxy metric."
        reason = "The reviewer response must separate image-space endpoints from human or material fidelity."
    else:
        evidence = "Problem statement / method description"
        measured = "NO_DIRECT_FIDELITY (not an outcome claim)"
        disposition = "KEEP"
        proposed = "Keep as task motivation or method description; do not present it as evidence that fidelity was achieved."
        reason = "This wording describes a research goal or control property rather than a measured fidelity result."
    row.update({
        "evidence_type": evidence,
        "fidelity_measured": measured,
        "disposition": disposition,
        "proposed_wording": proposed,
        "reason": reason,
    })
    return row


def main() -> int:
    main_pdf = ROOT / "CAG-S-26-01549 (1)(1).pdf"
    manuscript_tex = ROOT / "final/final_0903.tex"
    supplement_pdf = ROOT / "final/submission_new_0907/Supplementary material 0907.pdf"
    supplement_tex = ROOT / "final/supplementary_0903.tex"
    reviewer_docx = ROOT / "final/submission_new_0907/response to comments of reviewers 0907.docx"
    highlights_docx = ROOT / "final/submission_new_0907/Research Highlights 0907.docx"
    graphical_pdf = ROOT / "final/submission_new_0907/Graphical abstract 0907.pdf"
    required = [main_pdf, manuscript_tex, supplement_pdf, supplement_tex, reviewer_docx, highlights_docx, graphical_pdf]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing R1.3 audit source(s): " + ", ".join(missing))

    rows = []
    rows.extend(tex_records(manuscript_tex, str(main_pdf.relative_to(ROOT)), sha256(main_pdf)))
    rows.extend(tex_records(supplement_tex, str(supplement_pdf.relative_to(ROOT)), sha256(supplement_pdf)))
    rows.extend(docx_records(reviewer_docx, main_pdf, "Prior reviewer response (submitted packet pp. 6–13)"))
    rows.extend(docx_records(highlights_docx, main_pdf, "Research Highlights (submitted packet p. 44)"))
    rows.extend(graphical_abstract_records(graphical_pdf, main_pdf))

    # Include the conclusion's bounded claim and its adjacent endpoint-based trade-off statement.
    conclusion_line = manuscript_tex.read_text(encoding="utf-8").splitlines()[547]
    for sentence in split_sentences(conclusion_line)[:2]:
        rows.append({
            "original_location": f"{main_pdf.relative_to(ROOT)}; {manuscript_tex.relative_to(ROOT)}:548 (Conclusion)",
            "source_file": str(main_pdf.relative_to(ROOT)),
            "source_sha256": sha256(main_pdf),
            "companion_source_file": str(manuscript_tex.relative_to(ROOT)),
            "companion_source_sha256": sha256(manuscript_tex),
            "original_sentence": sentence,
            "document_kind": "conclusion_tradeoff" if "shape-texture trade-off" in sentence.lower() else "manuscript",
        })
    rows = [annotate(row) for row in rows]
    for row in rows:
        row["audit_script_file"] = str(Path(__file__).relative_to(ROOT))
        row["audit_script_sha256"] = sha256(Path(__file__).resolve())
    for number, row in enumerate(rows, start=1):
        row["record_id"] = f"R1_3_{number:03d}"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["disposition"] for row in rows)
    print(f"R1_3_LANGUAGE_AUDIT=PASS; records={len(rows)}; dispositions={dict(counts)}; output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
