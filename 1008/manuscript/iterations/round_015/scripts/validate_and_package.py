"""Validate final scientific artifacts and create the private author-review bundle."""
from pathlib import Path
import datetime
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
DELIVERY = ROOT / "deliverables"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    facts = read(ROOT / "data/FACTS_round_015.json")
    assert all(x == sha(ROOT / name) for name,x in facts["source_sha256"].items())
    documents = {
        "manuscript_round_015": "Manuscript_round_015.pdf",
        "manuscript_round_015_marked": "Manuscript_round_015_marked.pdf",
        "Supplementary_round_015": "Supplementary_round_015.pdf",
        "Response_to_Reviewers_round_015": "Response_to_Reviewers_round_015.pdf",
    }
    DELIVERY.mkdir(exist_ok=True)
    page_counts = {}
    warnings = {}
    for stem, target in documents.items():
        source = BUILD / (stem + ".pdf")
        assert source.exists() and source.stat().st_size > 20000
        info = subprocess.check_output(["pdfinfo", str(source)], text=True)
        page_counts[stem] = int(re.search(r"^Pages:\s+(\d+)", info, re.M)[1])
        log = BUILD / (stem + ".log")
        if log.exists():
            text = log.read_text(errors="replace")
            assert "undefined" not in text.lower() and not re.search(r"^!", text, re.M)
            assert "Overfull \\vbox" not in text
            boxes = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", text)]
            assert max(boxes, default=0) < 3, boxes
            warnings[stem] = {"minor_template_keyword_overflow_pt": boxes}
        shutil.copy2(source, DELIVERY / target)

    title = "Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation: A Controlled Empirical Study"
    for name in ["manuscript_round_015.tex", "Supplementary_round_015.tex", "Response_to_Reviewers_round_015.md"]:
        assert title in (ROOT / name).read_text()
    main_text = (ROOT / "manuscript_round_015.tex").read_text()
    for token in ["twenty-object", "0.000084", "0.122", "0.045", "0.396", "0.564", "0.52"]:
        assert token in main_text, token
    assert "S32" not in main_text and "S33" not in main_text
    supplement = (ROOT / "Supplementary_round_015.tex").read_text()
    assert "external bake evaluation remains incomplete" not in supplement
    assert "No complete twenty-object comparison" not in supplement
    assert len(re.findall(r"\\section\*\{S[1-9]\.", supplement)) == 9
    highlight_lines = (ROOT / "Highlights_round_015.txt").read_text().splitlines()
    assert len(highlight_lines) == 4 and max(map(len, highlight_lines)) <= 85
    shutil.copy2(ROOT / "Highlights_round_015.txt", DELIVERY / "Highlights_round_015.txt")

    # Replay the new GSO primary's frozen pointwise interval and paired test.
    image = read(ROOT / "data/completed_supplement013/analysis/TEMPORAL100_COMPARISONS.json")
    uid_order = read(ROOT / "data/GSO100_UID_ORDER.json")
    import csv
    with (ROOT / "data/final_supplement_audit013/ALL_GSO100_VIEW_METRICS.csv").open() as stream:
        raw = list(csv.DictReader(stream))
    cells = {}
    for row in raw:
        if row["condition"] in ["middle_high", "fixed_mean"]:
            cells.setdefault((row["uid"], int(row["seed"]), row["condition"]), []).append(float(row["fg_psnr"]))
    delta = np.array([np.mean([np.mean(cells[u,s,"middle_high"]) - np.mean(cells[u,s,"fixed_mean"])
                              for s in [42,2026,31415]]) for u in uid_order])
    rng = np.random.default_rng(20261011)
    ci = np.percentile(delta[rng.integers(0,100,(20000,100))].mean(1), [2.5,97.5])
    assert np.allclose(ci, image["primary"]["ci95_pointwise"], rtol=0, atol=2e-12)
    rng = np.random.default_rng(20261011)
    count = 0
    for _ in range(20):
        count += int((abs((rng.choice([-1,1],(10000,100))*delta).mean(1)) >= abs(delta.mean())-1e-12).sum())
    mc_p = (count+1)/200001
    assert abs(mc_p-image["primary"]["p_raw"]) < 1e-12

    # Independent exact enumeration for the full20-object baked comparison.
    baked = read(ROOT / "data/completed_supplement013/analysis/BAKE20_COMPARISONS.json")
    table = {(r["uid"],r["seed"],r["condition"]): r for r in baked["rows"]}
    delta_bake = np.array([np.mean([table[u,s,"late_high"]["mean_unseen"]["fg_lpips"]
                        - table[u,s,"fixed_mean"]["mean_unseen"]["fg_lpips"]
                        for s in [42,2026,31415]]) for u in uid_order[:20]])
    count = 0
    for start in range(0, 2**20, 8192):
        numbers = np.arange(start, min(start+8192, 2**20), dtype=np.uint64)
        signs = ((numbers[:,None] >> np.arange(20,dtype=np.uint64)) & 1).astype(np.int8)*2-1
        count += int((abs((signs*delta_bake).mean(1)) >= abs(delta_bake.mean())-1e-12).sum())
    exact_p = count/2**20
    parent_audit = read(ROOT / "data/final_supplement_audit013/FINAL_INDEPENDENT_VALIDATION.json")
    assert abs(exact_p-parent_audit["late_mean_bake_exact_sign_flip_p"]) < 1e-12

    video_source = ROOT / "data/completed_supplement013/Real_Baked_Comparison.mp4"
    video_provenance = read(ROOT / "data/completed_supplement013/VIDEO_PROVENANCE.json")
    assert sha(video_source) == video_provenance["sha256"]
    video = DELIVERY / "Real_Baked_Comparison_round_015.mp4"
    shutil.copy2(video_source, video)
    probe = json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format",
                                               "-of","json",str(video)], text=True))
    stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    assert stream["codec_name"] == "h264" and int(stream["nb_frames"]) == 11
    subprocess.run(["ffmpeg","-v","error","-i",str(video),"-f","null","-"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    (DELIVERY / "VIDEO_PROVENANCE_round_015.json").write_text(json.dumps(
        {"source_provenance": "data/completed_supplement013/VIDEO_PROVENANCE.json",
         "sha256": sha(video), "frames": 11, "duration_seconds": float(probe["format"]["duration"]),
         "identity": "Renamed byte-identical actual exported-GLB video; no appearance editing."}, indent=2)+"\n")

    parent = read(ROOT / "PARENT_SOURCE_FREEZE.json")
    for name in ["fig4_freshc_context_roi.pdf"]:
        assert sha(ROOT/"figures"/name) == parent["files_sha256"]["figures/"+name]
    visuals = read(ROOT / "FINAL_VISUAL_SOURCE_MANIFEST.json")
    for record in visuals["sources"]:
        assert sha(ROOT/record["packaged_path"]) == record["sha256"]
        assert record["condition"].lower() not in ["no adapter","no_adapter"]
    for record in visuals["displays"]:
        if "asset" in record:
            assert sha(ROOT/record["asset"]) == record["sha256"]
    visual_review = read(ROOT / "VISUAL_MODEL_REVIEW.json")
    assert visual_review["status"] == "PASS_PRESENTATION_WITH_DOCUMENTED_LIMITS"
    assert all(sha(ROOT/name) == digest for name,digest in visual_review["reviewed_files_sha256"].items())

    # The additions are separate from the unchanged inherited inference.
    old_facts=read(ROOT/"history/round_014/FACTS_round_014.json")
    assert facts["facts"]==old_facts["facts"] and facts["validation"]==old_facts["validation"]
    cross=read(ROOT/"data/gap_closure015/CROSS_VIEW_VALIDATION.json")
    assert cross["objects"]==10 and cross["max_absolute_replay_error"]==0
    assert len(cross["controls"])==4 and max(c["formula_error"] for c in cross["controls"])<1.1e-8
    fac=read(ROOT/"fac_code_snapshot/SOURCE_AND_COMPONENT_AUDIT.json")
    assert fac["unique_controller_source_versions"]==1 and fac["unique_controller_fixtures"]==3
    assert all(sha(ROOT/"fac_code_snapshot"/r["path"])==r["sha256"] for r in fac["files"])
    stability=read(ROOT/"data/gap_closure015/STABILITY_AND_DOMINANCE.json")
    assert len(stability["seed_contrasts"])==4
    assert all(r["all_three_favorable"]+r["all_three_adverse"]+r["mixed_or_tied"]==r["objects"] for r in stability["seed_contrasts"])
    assert stability["freshC_dominance"]["dominated_by_at_least_one"]==270

    validation = {
        "status": "PASS_ROUND015_COMPLETE_AUTHOR_REVIEW_ARTIFACTS",
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pages": page_counts, "compilation": "PASS_NO_UNDEFINED_CITATIONS_OR_REFERENCES",
        "layout": "PASS_NO_CLIPPED_VERTICAL_BOXES_OR_LARGE_HORIZONTAL_OVERFLOW",
        "minor_template_warnings": warnings,
        "data_reconstruction": facts["validation"],
        "GSO100_primary_bootstrap_and_signflip": {"status":"PASS", "p":mc_p},
        "GSO20_exact_signflip": {"status":"PASS_ALL_2_POW_20", "p":exact_p},
        "figure_identity": "PASS_ORIGINAL_RESEARCH_BYTES_AND_RECORDED_SHARED_FRAMES; No Adapter display columns omitted only",
        "visual_model_review": "VISUAL_MODEL_REVIEW.json",
        "inherited_facts_unchanged_from_round014":True,
        "cross_view_replay_and_controls":cross,
        "recovered_FAC_source":"84 source/dependency/config files; three unique CPU fixtures, same controller source across the two entry trees; no full-model historical replay",
        "new_analysis_scope":"Post-inspection descriptive seed/dominance/UV-overlap summaries; no new training, generated images, model or parameter search.",
        "video": {"status":"PASS_BYTE_IDENTITY_AND_FULL_DECODE","frames":11},
        "scientific_limits": "Historical adapter/FAC replay incomplete; no validated PBR/seam claim; empirical contribution remains editorial judgment.",
        "release_scope": "Private GitHub author-review upload; no journal submission.",
    }
    (ROOT / "FINAL_VALIDATION.json").write_text(json.dumps(validation,indent=2)+"\n")
    manifest = read(ROOT / "ROUND_MANIFEST.json")
    manifest.update({"status":"COMPLETE_ROUND015_VALIDATED_EMPIRICAL_AUTHOR_REVIEW",
        "new_GPU_experiments":0, "new_algorithm":False, "new_training":False, "source_parent":14,
        "evidence":"Inherited core300/native50/GSO100/bake10/bake20 plus UV-overlap replay/controls, descriptive seed and dominance, recoverable FAC code; negative results retained.",
        "outputs":list(documents.values()), "validation":"FINAL_VALIDATION.json",
        "remaining_risks":"02_RESULTS_RISKS_AND_COMPARISON.md"})
    (ROOT / "ROUND_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")

    # Select source/recomputation evidence; no weights, bulk image archives or raw NPZ.
    selected = set()
    selected.update(ROOT/name for name in visual_review["reviewed_files_sha256"])
    active_graphics = set()
    for path in [ROOT/"manuscript_round_015.tex",ROOT/"Supplementary_round_015.tex",
                 ROOT/"manuscript_round_015_marked.tex",*(ROOT/"sections").glob("*.tex")]:
        for name in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",path.read_text()):
            if (ROOT/name).is_file():active_graphics.add(ROOT/name)
    visual_inputs = {ROOT/r["packaged_path"] for r in visuals["sources"]}
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in [".md",".json",".tex",".py",".txt",".diff",".pdf"]:
            if path.name not in ["FILES_SHA256.json","GIT_UPLOAD_FILES.json"]:
                selected.add(path)
    for directory in ["scripts","figures","tables","sections","vendor","visual_review","history/round_014",
                      "fac_code_snapshot","data/gap_closure015","data/primary_studies","data/gso_mva_external_attempt01",
                      "data/gso_apg_closure_attempt01","data/final_supplement_audit013",
                      "data/completed_supplement013/analysis","data/completed_supplement013/temporal100",
                      "data/completed_supplement013/bake20_revised",
                      "data/completed_supplement013/bake20_additional",
                      "data/completed_supplement013/source_attribution",
                      "data/completed_supplement013/original_failed_bake",
                      "data/completed_supplement013/scripts"]:
        for path in (ROOT/directory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                if directory == "figures" and path not in active_graphics | visual_inputs and path.suffix not in [".json",".csv",".svg"]:
                    continue
                selected.add(path)
    # Four fixed first-object exports support the named application comparison;
    # all method metrics/video remain included and the full mesh archive stays on server.
    mesh_files = {ROOT/"data/completed_supplement013/example_glbs"/name for name in
                  ["gt_seed0.glb","native_seed42.glb","fixed_mean_seed42.glb","late_high_seed42.glb"]}
    for path in (ROOT/"data/completed_supplement013/calibration").rglob("*"):
        if path.is_file() and path.suffix in [".json",".png"]:
            selected.add(path)
    for name in ["data/FACTS_round_015.json","data/GSO100_UID_ORDER.json","data/GSO100_VIEW_METRICS.csv",
                 "data/EXTERNAL_PRIMARY_RECOMPUTATION.json","data/EXTERNAL_ROW_VALIDATION.json",
                 "data/completed_supplement013/Real_Baked_Comparison.mp4",
                 "data/completed_supplement013/VIDEO_PROVENANCE.json","history/retained_parent_section32.tex"]:
        selected.add(ROOT/name)
    selected.update(p for p in DELIVERY.iterdir() if p.is_file() and p.suffix != ".zip" and p.name != "ARCHIVE_SHA256.txt")
    submission_files = set()
    for directory in ["submission_package/Upload","submission_package/Editable"]:
        submission_files.update(p for p in (ROOT/directory).rglob("*") if p.is_file() and p.suffix != ".zip")
    for name in ["submission_package/README_UPLOAD_ZH.md","submission_package/SUBMISSION_FILE_MAP.csv",
                 "submission_package/PACKAGE_BUILD_VALIDATION.json"]:
        selected.add(ROOT/name)
    assert all(p.exists() and p.stat().st_size < 95_000_000 for p in selected)
    secrets = re.compile(r"(?:ghp_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)")
    for path in selected:
        if path.suffix in [".py",".json",".md",".tex",".txt"]:
            assert not secrets.search(path.read_text(errors="replace")), f"Credential-like content in {path.name}"
    hashes = {str(p.relative_to(ROOT)):sha(p) for p in sorted(selected)}
    (ROOT/"FILES_SHA256.json").write_text(json.dumps(hashes,indent=2)+"\n")
    selected.add(ROOT/"FILES_SHA256.json")
    archive = DELIVERY/"Round015_Author_Review_Package.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for path in sorted(selected):
            bundle.write(path,str(path.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    assert archive.stat().st_size < 95_000_000, "Review archive exceeds the repository delivery size budget."
    digest = sha(archive)
    (DELIVERY/"ARCHIVE_SHA256.txt").write_text(digest+"  "+archive.name+"\n")
    selected.update([archive,DELIVERY/"ARCHIVE_SHA256.txt"])
    selected.update(mesh_files)
    selected.update(submission_files)
    # Upload standalone submission archives without nesting large ZIPs in the author bundle.
    selected.update(p for p in (ROOT/"submission_package/Upload").glob("*.zip"))
    selected.update(p for p in (ROOT/"submission_package").glob("Submission_Files_round_015.zip"))
    (ROOT/"GIT_UPLOAD_FILES.json").write_text(json.dumps({
        "scope":"Only completed round015 author-review materials; private MVPainter repository.",
        "files":[str(p.relative_to(ROOT)) for p in sorted(selected)],
        "archive_sha256":digest,"archive_bytes":archive.stat().st_size,
        "zip_integrity":"PASS_ALL_MEMBERS_CRC"
    },indent=2)+"\n")
    print(json.dumps({"status":validation["status"],"pages":page_counts,
        "archive_bytes":archive.stat().st_size,"members":len(selected),"sha256":digest}))


if __name__ == "__main__":
    main()
