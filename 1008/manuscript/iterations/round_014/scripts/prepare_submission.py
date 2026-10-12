"""Prepare synchronized submission attachments and compile a flat LaTeX archive."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
PACK = ROOT / "submission_package"
UPLOAD = PACK / "Upload"
EDIT = PACK / "Editable"
OLD = Path("/4T/CXY/MV-Painter/final/submission_new_0907")
TITLE = "Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation: A Controlled Empirical Study"
FUNDING = "This work was supported by the Key R&D Program of Jiangsu Province under Grant BE2023010-3, the Basic Research Program of Jiangsu under Grant BK20253037, the Advanced Technology Research and Development Program of Jiangsu under Grant BF2025018, the Modern Agricultural Machinery Equipment and Technology Promotion Project of Jiangsu under Grant NJ2025-10, and the Wuxi Key Laboratory of Integrated Vehicle-Road-Cloud Smart Transportation System."
INTEREST = "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper."


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(path, folder):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(folder)))
    with zipfile.ZipFile(path) as z: assert z.testzip() is None


def convert(name, text):
    md = EDIT / (name+".md")
    md.write_text(text.strip()+"\n")
    subprocess.run(["pandoc", str(md), "--standalone", "-o", str(UPLOAD/(name+".docx"))], check=True)
    subprocess.run(["pandoc", str(md), "--standalone", "--pdf-engine=pdflatex", "-V", "geometry:margin=0.8in", "-V", "fontsize=11pt", "-o", str(UPLOAD/(name+".pdf"))], check=True)


def graphical_abstract():
    facts = json.loads((ROOT/"data/FACTS_round_014.json").read_text())["facts"]
    fig = plt.figure(figsize=(13, 5.2), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.text(.03, .94, "When does temporal geometry control help?", fontsize=21, weight="bold", color="#203d50")
    descriptions = [("Matched controls", "300 GeoTex objects\nFixed strength + stage allocation"),
                    ("Native interface checks", "50 MV-Adapter inputs + GSO100\nMiddle-window primary gains not detected"),
                    ("Actual baked meshes", "10 GeoTex + 20 GSO objects\nSame unseen views within each study")]
    for i, (heading, detail) in enumerate(descriptions):
        x = .03+i*.323
        ax.add_patch(FancyBboxPatch((x, .63), .29, .23, boxstyle="round,pad=.01", facecolor="#eef4f7", edgecolor="#92a8b4"))
        ax.text(x+.015, .80, heading, fontsize=15, weight="bold", color="#203d50")
        ax.text(x+.015, .73, detail, fontsize=11, va="top", linespacing=1.6)
        if i < 2: ax.annotate("", (x+.315, .745), (x+.295, .745), arrowprops={"arrowstyle":"->", "color":"#4f6b7a", "lw":2})
    ax.text(.03, .53, "Late-high minus Fixed Mean on baked unseen-view foreground LPIPS", fontsize=15, weight="bold")
    forest = fig.add_axes([.25, .24, .66, .22])
    for y, key in [(1, "bake10_late_mean"), (0, "bake20_late_mean")]:
        f = facts[key]; mean=f["mean"]*1000; lo, hi=[x*1000 for x in f["ci95"]]
        forest.errorbar(mean, y, xerr=[[mean-lo], [hi-mean]], fmt="o", color="#2e607c", capsize=4, lw=2)
    forest.axvline(0, color="#777777", ls="--", lw=1)
    forest.set_yticks([1,0], ["GeoTex: 10 objects", "GSO: 20 objects"])
    forest.set_ylim(-.4,1.4); forest.set_xlim(-4.8,.6)
    forest.set_xlabel("Paired difference × 1,000; lower favors Late-high", fontsize=11)
    forest.spines[["top","right"]].set_visible(False)
    ax.text(.03, .065, "A small within-protocol benefit does not establish a universally preferred schedule.", fontsize=14, color="#203d50")
    ax.text(.03, .015, "Pointwise 95% object intervals; separate cohorts and protocols are not pooled.", fontsize=10, color="#4f6b7a")
    for ext in ["pdf", "png", "svg"]: fig.savefig(UPLOAD/("Graphical_Abstract_round_014."+ext), dpi=180)
    plt.close(fig)
    (EDIT/"Graphical_Abstract_Provenance.json").write_text(json.dumps({"tool":"Matplotlib; reproducible vector/plot code", "data":"data/FACTS_round_014.json", "displayed_records":[facts[k] for k in ["bake10_late_mean","bake20_late_mean"]], "no_general_purpose_image_generation":True},indent=2)+"\n")


def flatten_latex():
    source = PACK / "LaTeX_Source_Flat"
    source.mkdir(exist_ok=True)
    for name in ["cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf"]:
        shutil.copy2(ROOT/"vendor/source_01549"/name, source/name)
    asset_map = {}

    def rewrite(text):
        def include(m):
            p=ROOT/m[1]
            if not p.suffix: p=p.with_suffix(".tex")
            assert p.is_file(), str(p)
            flat=str(p.relative_to(ROOT)).replace("/", "__")
            (source/flat).write_text(rewrite(p.read_text()))
            return r"\input{"+flat+"}"
        text=re.sub(r"\\input\{([^}]+)\}", include, text)
        return re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}",picture,text)

    def picture(m):
        rel=m[2]; p=ROOT/rel
        if not p.is_file(): p=ROOT/"vendor/source_01549"/rel
        assert p.is_file(), str(p)
        flat=rel.replace("/", "__")
        assert "/" not in flat and ".." not in flat
        if flat in asset_map: assert asset_map[flat] == sha(p)
        asset_map[flat]=sha(p); shutil.copy2(p,source/flat)
        return r"\includegraphics"+(m[1] or "")+"{"+flat+"}"

    names = {"manuscript_round_014":"Manuscript", "Supplementary_round_014":"Supplementary_material", "manuscript_round_014_marked":"Marked-up_manuscript"}
    checks = {}
    for original, target in names.items():
        tex=rewrite((ROOT/(original+".tex")).read_text())
        (source/(target+".tex")).write_text(tex)
    assert all(p.is_file() for p in source.iterdir())
    source_log = PACK / "source_build_logs"
    source_log.mkdir(exist_ok=True)
    for original, target in names.items():
        for number in [1, 2, 3]:
            with (source_log/f"{target}.pass{number}.txt").open("w") as out:
                subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error",f"-output-directory={source_log}",target+".tex"],cwd=source,stdout=out,stderr=subprocess.STDOUT,check=True)
        a=subprocess.check_output(["pdftotext","-layout",str(BUILD/(original+".pdf")),"-"],text=True)
        b=subprocess.check_output(["pdftotext","-layout",str(source_log/(target+".pdf")),"-"],text=True)
        assert a == b, f"Flat-source text/layout differs: {target}"
        log=(source_log/(target+".log")).read_text(errors="replace")
        assert "undefined" not in log.lower() and not re.search(r"^!",log,re.M)
        checks[target]="PASS_THREE_PASS_BUILD_AND_IDENTICAL_EXTRACTED_TEXT_LAYOUT"
    archive(UPLOAD/"LaTeX_Source_round_014.zip",source)
    with zipfile.ZipFile(UPLOAD/"LaTeX_Source_round_014.zip") as z:
        assert all("/" not in n for n in z.namelist())
    return checks


def reproduction():
    with tempfile.TemporaryDirectory(prefix="cg14-reproduction-") as tmp:
        stage=Path(tmp)
        for name in ["primary_studies","completed_supplement013/analysis","completed_supplement013/scripts"]:
            shutil.copytree(ROOT/"data"/name,stage/"data"/name)
        for name in ["GSO100_UID_ORDER.json","FACTS_round_014.json","final_supplement_audit013/ALL_GSO100_VIEW_METRICS.csv"]:
            dest=stage/"data"/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/"data"/name,dest)
        (stage/"scripts").mkdir();(stage/"tables").mkdir();(stage/"figures").mkdir()
        shutil.copy2(ROOT/"scripts/build_evidence.py",stage/"scripts/build_evidence.py")
        shutil.copy2(ROOT/"requirements-statistics.txt",stage/"requirements-statistics.txt")
        with (PACK/"reproduction_build_log.txt").open("w") as out:
            subprocess.run(["python",str(stage/"scripts/build_evidence.py")],cwd=stage,stdout=out,stderr=subprocess.STDOUT,check=True)
        recalculated=json.loads((stage/"data/FACTS_round_014.json").read_text())
        original=json.loads((ROOT/"data/FACTS_round_014.json").read_text())
        assert recalculated == original, "Extracted reproduction changes facts"
        (stage/"README.md").write_text("# Revision evidence recomputation\n\nInstall requirements-statistics.txt; run python scripts/build_evidence.py. This package was tested in isolation without a GPU or model weights, and reproduces all current facts and the allocation plot. Source metric records are unaltered.\n\nInference/calibration scripts under data/completed_supplement013/scripts are preserved exercised components and require the recorded upstream project, model weights, licensed inputs and original runtime; they are not a standalone model distribution. Historical FAC training replay remains incomplete. No participant-level data, bulk model weights or complete generated-image archive is included.\n")
        archive(UPLOAD/"Reproduction_round_014.zip",stage)


def main():
    UPLOAD.mkdir(parents=True,exist_ok=True);EDIT.mkdir(exist_ok=True)
    convert("Title_Page_round_014",f"# {TITLE}\n\n**Xueyuan Che; Libo Sun (corresponding author)**\n\nSchool of Instrument Science and Engineering, Southeast University, No. 2 Sipailou, Xuanwu District, Nanjing, 210096, Jiangsu, China\n\nCorrespondence: sunlibo@seu.edu.cn\n\n## Acknowledgements and funding\n\n{FUNDING}\n\n## Declaration of competing interests\n\n{INTEREST}")
    convert("Acknowledgements_round_014",f"# Acknowledgements\n\n{FUNDING}")
    convert("Declaration_of_Interest_round_014",f"# Declaration of interests\n\n{INTEREST}")
    convert("Cover_Letter_round_014",f"""Dear Editor,

Please consider our revised manuscript, **{TITLE}**, for the Virtual Special Issue CAG_SS_CAD/Graphics 2026. This continues the same manuscript submitted on 7 September 2026; the title now states its empirical scope. A point-by-point response and a marked copy against that authenticated submission are provided.

The paper addresses a practical graphics question: when does allocating geometry-control strength across denoising stages improve generated views and the appearance of the final textured mesh? The revision adds strong fixed/linear comparisons, matched applied-scale budgets, native conditioning-interface checks and actual exported-mesh evaluation. The 300-object GeoTex comparison changes the preferred image-space setting. A ten-object bake finds a small late-allocation benefit; a separate twenty-object GSO study does not detect the same benefit. Native MV-Adapter primaries do not establish a middle-window advantage. These limits and visible appearance failures remain in the paper.

The closest prior work includes Shao et al., *MVPainter* (arXiv:2505.12635, 2025); Huang et al., *MV-Adapter* (ICCV, 2025); and Kulkarni, *Scheduled Style Injection* (CVPR Workshops/NTIRE, 2026). We acknowledge existing layer/time strength schedules. Our contribution is their controlled evaluation in this texturing task, including competitive controls, implemented scale accounting and downstream application limits; we do not claim a new general scheduling principle or universally optimal C3. Sadat et al.'s adaptive projected guidance (ICLR, 2025) is also included in the separate external comparison.

CAI's independent derivation and optimality claims have been removed. Historical results are distinguished from new checkpoints and protocols; the original +0.96 dB estimate is not called reproduced. The remaining historical FAC training-replay gap is disclosed. The materials provide reproducible object-level statistics, editable sources, attributed real outputs and playable mesh-comparison videos. The original CAD/Graphics conference submission is retained as a separate historical attachment.

Thank you for considering the revised evidence and its application implications.

Sincerely,\nThe Authors
""")
    highlights=["Matched budgets separate temporal allocation from increased control strength.","Strong fixed and linear controls outperform the historical middle window.","A small bake benefit is not detected in a separate twenty-object cohort.","Native interface studies reveal endpoint and protocol limits."]
    assert all(len(x)<=85 for x in highlights)
    (ROOT/"Highlights_round_014.txt").write_text("\n".join(highlights)+"\n")
    convert("Highlights_round_014","# Highlights\n\n"+"\n".join("- "+x for x in highlights))
    convert("Response_to_Reviewers_round_014",(ROOT/"Response_to_Reviewers_round_014.md").read_text())
    shutil.copy2(UPLOAD/"Response_to_Reviewers_round_014.pdf",BUILD/"Response_to_Reviewers_round_014.pdf")
    for original,name in [("manuscript_round_014","Manuscript_round_014"),("manuscript_round_014_marked","Marked-up_Manuscript_round_014"),("Supplementary_round_014","Supplementary_Material_round_014")]:
        shutil.copy2(BUILD/(original+".pdf"),UPLOAD/(name+".pdf"))
    graphical_abstract()
    checks=flatten_latex()
    reproduction()
    mesh_archive=UPLOAD/"Mesh_Examples_round_014.zip"
    with zipfile.ZipFile(mesh_archive,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name in ["gt_seed0.glb","native_seed42.glb","fixed_mean_seed42.glb","late_high_seed42.glb"]:
            p=ROOT/"data/completed_supplement013/example_glbs"/name
            z.write(p,"data/completed_supplement013/example_glbs/"+name)
        for p in (ROOT/"data/completed_supplement013/source_attribution").rglob("*"):
            if p.is_file():z.write(p,"source_attribution/"+str(p.relative_to(ROOT/"data/completed_supplement013/source_attribution")))
        z.writestr("README.md","Four original exports for the fixed first input object: GT, Native, Fixed Mean and Late-high. All method metrics/video are in the full evidence; this is a compact licensed example rather than the complete mesh archive. Source attribution and original protocol identifiers are included.\n")
    with zipfile.ZipFile(mesh_archive) as z:assert z.testzip() is None
    historical=UPLOAD/"Original_Conference_Submission_0907.pdf"
    if not historical.exists(): shutil.copy2(OLD/"Original conference submission 0907.pdf",historical)
    assert sha(historical)==sha(OLD/"Original conference submission 0907.pdf")
    oldvideo=Path("/4T/CXY/MV-Painter/CG_revision_20261011_conservative_submission_r2/manuscript/Supplementary_Video_conservative_submission_r2.mp4")
    geo=UPLOAD/"Video_1_GeoTex_Baked_round_014.mp4"
    if not geo.exists(): shutil.copy2(oldvideo,geo)
    assert sha(geo)=="6191b81e6336c6be62fcd8962a33f1e84245667b68ae6346be2815da1d9502a3"
    shutil.copy2(ROOT/"data/completed_supplement013/Real_Baked_Comparison.mp4",UPLOAD/"Video_2_GSO_Exported_Mesh_round_014.mp4")
    for number in [1,2]:
        video=next(UPLOAD.glob(f"Video_{number}_*.mp4"))
        subprocess.run(["ffmpeg","-v","error","-i",str(video),"-f","null","-"],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
        subprocess.run(["ffmpeg","-v","error","-i",str(video),"-frames:v","1","-y",str(UPLOAD/f"Video_{number}_Still_round_014.png")],check=True)
    carryover={"facts":"Author order, affiliation, corresponding email, funding and competing-interest declaration are carried unchanged from the submitted title page/declarations; no new author roles or approvals inferred.",
               "historical_files":{n:sha(OLD/n) for n in ["Titlepage 0907.pdf","Acknowledgements 0907.docx","Declaration of Interest Statement 0907.docx","Cover letter 0907.docx"]},"title_changed":TITLE}
    (EDIT/"ADMINISTRATIVE_CARRYOVER.json").write_text(json.dumps(carryover,indent=2)+"\n")
    data={"checked_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"flat_latex":checks,"isolated_statistics_recomputation":"PASS_IDENTICAL_FACTS","source_zip_root_files_only":True,"video_full_decode":"PASS_BOTH","historical_conference":"BYTE_IDENTICAL","admin_scope":"Historical confirmed facts carried forward; final author approval is not asserted."}
    (PACK/"PACKAGE_BUILD_VALIDATION.json").write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data))


if __name__=="__main__": main()
