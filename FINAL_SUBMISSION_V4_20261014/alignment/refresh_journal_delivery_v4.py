"""Create a versioned local journal-delivery directory without altering history."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = Path("/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4")
J = Path("/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v4")
VIDEO = json.loads((ROOT / "quality_review/VIDEO_VALIDATION_V4.json").read_text())
PDFS = (
    "FINAL_V4_MANUSCRIPT.pdf",
    "FINAL_V4_SUPPLEMENTARY.pdf",
    "FINAL_V4_RESPONSE_TO_REVIEWERS.pdf",
    "FINAL_V4_MARKED_MANUSCRIPT.pdf",
)
ANCILLARY = (
    "Declaration_of_Interest_V4.docx",
    "Highlights_V4.docx",
    "Highlights_V4.txt",
    "Title_Page_V4.docx",
    "Title_Page_V4.pdf",
    "Research_Evidence_V4.zip",
    "Supplementary_GeoTex_Baked_Comparison.mp4",
    "Supplementary_GeoTex_Baked_Comparison_Still.png",
    "Supplementary_GSO_Baked_Comparison.mp4",
    "Supplementary_GSO_Baked_Comparison_Still.png",
    "Supplementary_Video_Captions_V4.txt",
)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_video(path):
    result = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=codec_name,width,height,r_frame_rate,nb_frames", "-show_entries",
        "format=duration", "-of", "json", str(path),
    ], text=True)
    info = json.loads(result)
    stream = info["streams"][0]
    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if decode.returncode != 0:
        raise RuntimeError(f"Video decode failed for {path}: {decode.stderr}")
    return {
        "codec": stream.get("codec_name"),
        "width": stream["width"],
        "height": stream["height"],
        "frame_rate": stream.get("r_frame_rate"),
        "frames": int(stream["nb_frames"]) if stream.get("nb_frames", "N/A") != "N/A" else None,
        "duration_seconds": float(info["format"]["duration"]),
        "full_decode": "PASS",
    }


def write_source_archive():
    archive = J / "Manuscript_LaTeX_Sources_V4.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for name in ("FINAL_V4_MANUSCRIPT.tex", "FINAL_V4_SUPPLEMENTARY.tex", "build_v4_manuscript.py", "fig2.pdf", "fig3.pdf"):
            output.write(ROOT / name, name)
        for folder in ("figures", "tables", "sections"):
            for path in sorted((ROOT / folder).rglob("*")):
                if path.is_file() and not any(part in {"__pycache__", "build"} for part in path.relative_to(ROOT).parts):
                    output.write(path, path.relative_to(ROOT).as_posix())
        if not (ROOT / "sections/.keep").is_file():
            output.writestr("sections/.keep", "")
        for path in sorted((ROOT / "vendor").rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as source:
        if source.testzip() is not None:
            raise RuntimeError("The manuscript source archive is corrupt")
        required = {"FINAL_V4_MANUSCRIPT.tex", "FINAL_V4_SUPPLEMENTARY.tex", "figures/fig3_bake10_two_object_v4.pdf", "tables/matched_controls014.tex", "vendor/cag.sty", "vendor/elsarticle.cls", "sections/.keep"}
        missing = required.difference(source.namelist())
        if missing:
            raise RuntimeError(f"Required current source files are missing from archive: {sorted(missing)}")
        if source.read("FINAL_V4_MANUSCRIPT.tex") != (ROOT / "FINAL_V4_MANUSCRIPT.tex").read_bytes():
            raise RuntimeError("Archived main source differs from the official source")
    return archive


def main():
    if not OLD.is_dir():
        raise RuntimeError(f"Prior prepared delivery is missing: {OLD}")
    if J.exists():
        prior_manifest = J / "JOURNAL_SUBMISSION_MANIFEST_V4.json"
        if not prior_manifest.is_file():
            raise RuntimeError(f"Refusing to overwrite an unrecognized delivery directory: {J}")
        previous = json.loads(prior_manifest.read_text())
        if previous.get("version") != "V4 final text revision" or previous.get("source_baseline_head") != "11006e003842b25976e20cafd51a7970770f269f":
            raise RuntimeError(f"Refusing to overwrite a delivery directory from another revision: {J}")
    else:
        J.parent.mkdir(parents=True, exist_ok=False)
        shutil.copytree(OLD, J)

    for name in PDFS:
        shutil.copy2(ROOT / name, J / name)
    for name in ANCILLARY:
        if not (J / name).is_file():
            raise RuntimeError(f"Expected ancillary submission file is missing: {J / name}")
    subprocess.run(["pandoc", str(ROOT / "review/FINAL_V4_RESPONSE_TO_REVIEWERS.md"), "-o", str(J / "FINAL_V4_RESPONSE_TO_REVIEWERS.docx")], check=True)
    source_archive = write_source_archive()

    videos = {}
    for key, recorded in VIDEO.items():
        if not isinstance(recorded, dict):
            continue
        path = J / recorded["filename"]
        if not path.is_file() or sha(path) != recorded["sha256"]:
            raise RuntimeError(f"Prepared video identity changed: {path}")
        still = J / recorded["filename"].replace(".mp4", "_Still.png")
        if not still.is_file():
            raise RuntimeError(f"Representative video still is missing: {still}")
        from PIL import Image
        with Image.open(still) as image:
            still_size = image.size
        metadata = probe_video(path)
        if still_size != (metadata["width"], metadata["height"]):
            raise RuntimeError(f"Video still dimensions do not match the video: {still}")
        videos[key] = {
            **recorded,
            **metadata,
            "local_path": str(path),
            "still_local_path": str(still),
            "still_sha256": sha(still),
            "still_resolution": list(still_size),
            "portal_instruction": "Upload as a separate supplemental video item with its matching representative still; do not rely on the GitHub repository as the media delivery location.",
        }

    files = {}
    for path in sorted(J.iterdir()):
        if path.is_file() and path.name != "JOURNAL_SUBMISSION_MANIFEST_V4.json":
            files[path.name] = {"local_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}
    manifest = {
        "version": "V4 final text revision",
        "status": "PASS",
        "source_baseline_head": "11006e003842b25976e20cafd51a7970770f269f",
        "journal_directory": str(J),
        "pdf_pages": {"main": 13, "supplement": 71, "response": 5, "marked": 20},
        "source_archive": {"filename": source_archive.name, "main_tex": "FINAL_V4_MANUSCRIPT.tex"},
        "videos": videos,
        "files": files,
        "media_submission": "Submit both MP4s and their matching stills separately in the journal portal's supplementary-media workflow; verify each file role and preview in the portal. Portal submission has not been performed.",
        "portal_submission": "NOT_PERFORMED",
    }
    (J / "JOURNAL_SUBMISSION_MANIFEST_V4.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    shutil.copy2(J / "JOURNAL_SUBMISSION_MANIFEST_V4.json", ROOT / "quality_review/JOURNAL_DELIVERY_MANIFEST_V4.json")
    print(f"Created new V4 journal delivery: {J}; {len(files)} files hashed; both videos decoded")


if __name__ == "__main__":
    main()
