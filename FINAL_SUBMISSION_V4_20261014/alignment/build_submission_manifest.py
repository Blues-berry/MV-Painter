"""Validate the final V4 files and record their identities and page locations."""
from pathlib import Path
import hashlib
import json
import subprocess

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "alignment/SUBMISSION_MANIFEST_V4.json"
BASELINE_HEAD = "11006e003842b25976e20cafd51a7970770f269f"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pages(path):
    rows = subprocess.check_output(["pdfinfo", str(path)], text=True).splitlines()
    return int(next(row.split(":", 1)[1] for row in rows if row.startswith("Pages:")))


def page_text(path):
    return subprocess.check_output(["pdftotext", "-raw", str(path), "-"], text=True).split("\f")


def locate(texts, prefix):
    found = [index + 1 for index, page in enumerate(texts) if any(line.startswith(prefix) for line in page.splitlines())]
    if len(found) != 1:
        raise RuntimeError(f"Expected one location for {prefix!r}, got {found}")
    return found[0]


def main():
    pdfs = {
        "main": ROOT / "FINAL_V4_MANUSCRIPT.pdf",
        "supplement": ROOT / "FINAL_V4_SUPPLEMENTARY.pdf",
        "response": ROOT / "FINAL_V4_RESPONSE_TO_REVIEWERS.pdf",
        "marked": ROOT / "FINAL_V4_MARKED_MANUSCRIPT.pdf",
    }
    counts = {name: pages(path) for name, path in pdfs.items()}
    expected = {"main": 13, "supplement": 71, "response": 5, "marked": 20}
    if counts != expected:
        raise RuntimeError(f"Unexpected current PDF page counts: {counts}")

    main_text = page_text(pdfs["main"])
    supplement_text = page_text(pdfs["supplement"])
    locations = {
        "Figure 2": locate(main_text, "Fig. 2. Fresh C"),
        "Figure 3": locate(main_text, "Fig. 3. GeoTex Bake10"),
        "Figure 4": locate(main_text, "Fig. 4. Fresh C"),
        "Table 2": locate(main_text, "Table 2. Fresh C"),
        "Table 3": locate(main_text, "Table 3. Selected paired"),
        "Table 4": locate(main_text, "Table 4. Ten-object"),
        "Table 5": locate(main_text, "Table 5. Unseen-view"),
        "Table 6": locate(main_text, "Table 6. Native-camera"),
        "Table 7": locate(main_text, "Table 7. Study-specific"),
        "Table S35": locate(supplement_text, "Table S35:"),
        "Table S36": locate(supplement_text, "Table S36:"),
    }
    if "[41]" not in "\n".join(main_text):
        raise RuntimeError("Final reference [41] is missing from the main manuscript")
    if "full v29" in main_text[0].lower():
        raise RuntimeError("The abstract should not foreground the full-v29 boundary")
    table7 = main_text[locations["Table 7"] - 1]
    for value in ("0.033877", "0.117170", "0.051422", "0.432378"):
        if value not in table7:
            raise RuntimeError(f"Frozen timing primary value missing from Table 7 page: {value}")

    frozen = json.loads((ROOT / "quality_review/FROZEN_CONTENT_CHECK_V4.json").read_text())
    if frozen.get("status") != "PASS" or not frozen.get("table_data_blocks_unchanged") or not frozen.get("supplement_source_unchanged"):
        raise RuntimeError("Frozen-content validation did not pass")

    selection_path = ROOT / "quality_review/FIGURE3_B_SELECTION_V4.json"
    selection = json.loads(selection_path.read_text())
    if selection.get("selected_candidate") != "B" or len(selection.get("rows", [])) != 2:
        raise RuntimeError("Figure 3 candidate B is not the recorded selection")
    if [row["title"].split(" - ")[0] for row in selection["rows"]] != ["Tire", "Baptisimal Font"]:
        raise RuntimeError("Figure 3 candidate B object identity mismatch")
    for row in selection["rows"]:
        expected_conditions = ["gt", "budget_fixed_mean", "budget_late16"]
        if [panel["condition"] for panel in row["panels"]] != expected_conditions:
            raise RuntimeError(f"Unexpected Figure 3 conditions for {row['title']}")
        cameras = {panel["camera_sha256"] for panel in row["panels"]}
        if len(cameras) != 1:
            raise RuntimeError(f"Camera mismatch in Figure 3 row {row['title']}")
        for panel in row["panels"]:
            source = ROOT / panel["source_asset"]
            display = ROOT / panel["display_asset"]
            with Image.open(source) as source_image:
                source_pixels = source_image.convert("RGB")
            with Image.open(display) as display_image:
                display_pixels = display_image.convert("RGB")
            bounds = tuple(panel["crop"])
            if sha(source) != panel["source_sha256"] or source_pixels.size != (512, 512):
                raise RuntimeError(f"Figure 3 source image identity/resolution mismatch: {source}")
            if sha(display) != panel["display_sha256"]:
                raise RuntimeError(f"Figure 3 display image identity mismatch: {display}")
            if ImageChops.difference(source_pixels.crop(bounds), display_pixels).getbbox() is not None:
                raise RuntimeError(f"Figure 3 display is not an exact crop of the source pixels: {display}")

    for name in ("FIGURE3_IDENTITY_VALIDATION_V4.json", "MARKED_MANUSCRIPT_CHECK_V4.json", "VIDEO_VALIDATION_V4.json"):
        record = json.loads((ROOT / "quality_review" / name).read_text())
        if record.get("status") != "PASS":
            raise RuntimeError(f"Required quality record did not pass: {name}")
    marked = json.loads((ROOT / "quality_review/MARKED_MANUSCRIPT_CHECK_V4.json").read_text())
    if marked.get("marked_pages") != 20:
        raise RuntimeError("Marked manuscript identity record has a stale page count")
    readiness = json.loads((ROOT / "quality_review/FINAL_READINESS_V4.json").read_text())
    if readiness.get("AUTHOR_REVIEW_READY") != "YES" or readiness.get("SUBMISSION_READY") != "YES":
        raise RuntimeError("Final readiness decision is not recorded")

    files = {}
    excluded_parts = {"build", "build_response", "__pycache__", ".git", "candidate_a_build", "candidate_b_build"}
    for path in sorted(item for item in ROOT.rglob("*") if item.is_file()):
        relative = path.relative_to(ROOT)
        if path in (OUTPUT, ROOT / "FINAL_V4_BUILD_REPORT.json") or excluded_parts.intersection(relative.parts):
            continue
        files[relative.as_posix()] = {"bytes": path.stat().st_size, "sha256": sha(path)}

    out = {
        "version": "V4",
        "revision": "final_text_quality_continuation_20261014",
        "source_baseline_head": BASELINE_HEAD,
        "status": "PASS",
        "pdf_pages": counts,
        "actual_locations": locations,
        "original_timing_primary": {
            "table": 7,
            "contrast": "Middle − mean(Early, Late)",
            "estimate_db": -0.0338775,
            "ci95_db": [-0.117170, 0.051422],
            "p": 0.432378,
        },
        "figure3_selection": selection,
        "author_review_ready": readiness["AUTHOR_REVIEW_READY"],
        "submission_ready": readiness["SUBMISSION_READY"],
        "scientific_readiness_record": "quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md",
        "files": files,
        "note": "Manifest records source/output identities and build locations. Build success is not the basis of scientific readiness.",
    }
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"V4 manifest PASS: pages={counts}; {len(files)} files hashed")


if __name__ == "__main__":
    main()
