from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent
BASE = SRC / "vendor" / "source_01549" / "final_0903.tex"
TARGET = SRC / "1014finalv1.tex"
EXPECTED = "203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01"
OUTPUT = ROOT / "Marked_up_Manuscript_01549.tex"
BUILD = ROOT / "build"


def main():
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != EXPECTED:
        raise RuntimeError("The authenticated 01549 baseline hash does not match.")
    BUILD.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as tex, (BUILD / "latexdiff_generation.log").open("w") as log:
        subprocess.run([
            "latexdiff", "--type=CFONT", "--subtype=SAFE", "--floattype=FLOATSAFE",
            "--graphics-markup=none", "--math-markup=0", "--disable-citation-markup",
            "--exclude-textcmd=section,subsection,subsubsection,paragraph,title",
            r"--config=PICTUREENV=(?:picture[\w\d*@]*|tikzpicture[\w\d*@]*|DIFnomarkup|figure\*?|table\*?|tabular\*?|longtable)",
            "--flatten", "--no-label", str(BASE), str(TARGET),
        ], cwd=SRC, stdout=tex, stderr=log, check=True)

    raw = OUTPUT.read_text()
    (ROOT / "Marked_up_Manuscript_01549.raw.tex").write_text(raw)
    active_tex = TARGET.read_text()
    aux = (SRC / "build" / "1014finalv1.aux").read_text()
    active_citations = set(re.findall(r"\\bibitem\{([^}]+)\}", active_tex))
    active_labels = set(re.findall(r"\\newlabel\{([^}]+)\}", aux))
    start = raw.index(r"\begin{document}")
    head, body = raw[:start], raw[start:]
    removed = {"citations": set(), "labels": set()}

    def citation(match):
        keys = match[1].split(",")
        active = [key for key in keys if key in active_citations]
        missing = [key for key in keys if key not in active_citations]
        if not missing:
            return match[0]
        removed["citations"].update(missing)
        label = " ".join(r"\texttt{" + key.replace("_", r"\_") + "}" for key in missing)
        active_part = r"\cite{" + ",".join(active) + "}" if active else ""
        return active_part + r"\textit{[removed citation: }" + label + r"\textit{]}"

    def reference(match):
        if match[2] in active_labels:
            return match[0]
        removed["labels"].add(match[2])
        return r"\textit{[removed reference: }\texttt{" + match[2].replace("_", r"\_") + r"}\textit{]}"

    body = re.sub(r"\\cite\{([^}]+)\}", citation, body)
    body = re.sub(r"\\(eqref|ref|pageref)\{([^}]+)\}", reference, body)
    OUTPUT.write_text(head + body)

    expanded = re.sub(
        r"\\input\{([^}]+)\}",
        lambda match: (SRC / (match[1] if match[1].endswith(".tex") else match[1] + ".tex")).read_text(),
        active_tex,
    )
    diff = difflib.unified_diff(
        BASE.read_text().splitlines(), expanded.splitlines(),
        fromfile="authenticated_01549/final_0903.tex",
        tofile="final_1014finalv1/expanded.tex", lineterm="",
    )
    (ROOT / "CHANGES_FROM_01549.diff").write_text("\n".join(diff) + "\n")
    (ROOT / "MARKED_DIFF_SCOPE.json").write_text(json.dumps({
        "baseline": "01549_revision_workspace/baseline_01549/final_0903.tex",
        "baseline_sha256": EXPECTED,
        "mode": "CFONT text additions/deletions; figure/table bodies are treated atomically; full expanded source changes are in CHANGES_FROM_01549.diff.",
        "removed_only_citations_and_labels": {key: sorted(values) for key, values in removed.items()},
    }, indent=2) + "\n")

    with tempfile.TemporaryDirectory(prefix="marked-01549-") as temp:
        stage = Path(temp)
        for folder in ("figures", "tables", "sections", "vendor"):
            shutil.copytree(SRC / folder, stage / folder)
        for path in BASE.parent.iterdir():
            if path.is_file() and path.name != BASE.name:
                shutil.copy2(path, stage / path.name)
        shutil.copy2(OUTPUT, stage / OUTPUT.name)
        for i in range(1, 4):
            with (BUILD / f"marked_pass{i}.log").open("w") as log:
                subprocess.run([
                    "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                    f"-output-directory={BUILD}", OUTPUT.name,
                ], cwd=stage, stdout=log, stderr=subprocess.STDOUT, check=True)
    shutil.copy2(BUILD / f"{OUTPUT.stem}.pdf", ROOT / "Marked_up_Manuscript_01549.pdf")
    print("Built marked manuscript against the authenticated 01549 source.")


if __name__ == "__main__":
    main()
