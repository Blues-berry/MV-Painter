"""Generate a marked manuscript against the authenticated journal submission."""
from pathlib import Path
import hashlib
import difflib
import json
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
BASE = ROOT / "vendor/source_01549/final_0903.tex"
EXPECTED = "203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01"


def main():
    assert hashlib.sha256(BASE.read_bytes()).hexdigest() == EXPECTED
    output = ROOT / "manuscript_round_014_marked.tex"
    with output.open("w") as tex, (BUILD / "latexdiff_generation.log").open("w") as log:
        subprocess.run([
            "latexdiff", "--type=CFONT", "--subtype=SAFE", "--floattype=FLOATSAFE",
            "--graphics-markup=none", "--math-markup=0", "--disable-citation-markup",
            "--exclude-textcmd=section,subsection,subsubsection,paragraph,title",
            r"--config=PICTUREENV=(?:picture[\w\d*@]*|tikzpicture[\w\d*@]*|DIFnomarkup|table\*?|tabular\*?|longtable)",
            "--flatten", "--no-label", str(BASE), str(ROOT / "manuscript_round_014.tex"),
        ], cwd=ROOT, stdout=tex, stderr=log, check=True)
    # Deleted-only links have no target in the revised bibliography/label set.
    # Show their old identifiers rather than misleading new reference numbers.
    raw = output.read_text()
    (ROOT / "history/marked_raw_current.tex").write_text(raw)
    new = (ROOT / "manuscript_round_014.tex").read_text()
    active_citations = set(re.findall(r"\\bibitem\{([^}]+)\}", new))
    active_labels = set(re.findall(r"\\newlabel\{([^}]+)\}", (BUILD / "manuscript_round_014.aux").read_text()))
    at = raw.index(r"\begin{document}")
    head, body = raw[:at], raw[at:]
    removed = {"citations": set(), "labels": set()}

    def citation(match):
        keys = match[1].split(",")
        active = [k for k in keys if k in active_citations]
        missing = [k for k in keys if k not in active_citations]
        if not missing:
            return match[0]
        removed["citations"].update(missing)
        label = " ".join(r"\texttt{" + key.replace("_", r"\_") + "}" for key in missing)
        return (r"\cite{" + ",".join(active) + "}" if active else "") + r"\textit{[removed citation: }" + label + r"\textit{]}"

    def reference(match):
        if match[2] in active_labels:
            return match[0]
        removed["labels"].add(match[2])
        return r"\textit{[removed reference: }\texttt{" + match[2].replace("_", r"\_") + r"}\textit{]}"

    body = re.sub(r"\\cite\{([^}]+)\}", citation, body)
    body = re.sub(r"\\(eqref|ref|pageref)\{([^}]+)\}", reference, body)
    output.write_text(head + body)
    expanded = re.sub(r"\\input\{([^}]+)\}", lambda m: (ROOT / (m[1] if m[1].endswith(".tex") else m[1]+".tex")).read_text(), new)
    diff = difflib.unified_diff(BASE.read_text().splitlines(), expanded.splitlines(),
        fromfile="authenticated_submission/final_0903.tex", tofile="round_014/manuscript_expanded.tex", lineterm="")
    (ROOT / "CHANGES_FROM_AUTHENTICATED_SUBMISSION.diff").write_text("\n".join(diff) + "\n")
    (ROOT / "MARKED_DIFF_SCOPE.json").write_text(json.dumps({
        "baseline_sha256": EXPECTED,
        "mode": "CFONT text additions/deletions; table environments treated atomically; deleted display equations suppressed for safe rendering.",
        "complete_source_change_record": "CHANGES_FROM_AUTHENTICATED_SUBMISSION.diff",
        "deleted_only_citations_and_refs": {k: sorted(v) for k,v in removed.items()},
        "label_scope": "Removed-only links display identifiers; existing revised references remain standard."
    }, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="cg-round014-marked-") as name:
        stage = Path(name)
        for path in (ROOT / "vendor/source_01549").iterdir():
            if path.is_file() and path.name != "final_0903.tex":
                shutil.copy2(path, stage / path.name)
        for dirname in ["figures", "tables", "sections"]:
            shutil.copytree(ROOT / dirname, stage / dirname)
        shutil.copy2(output, stage / output.name)
        for i in [1, 2, 3]:
            with (BUILD / f"manuscript_round_014_marked.pass{i}.txt").open("w") as log:
                subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                                f"-output-directory={BUILD}", output.name],
                               cwd=stage, stdout=log, stderr=subprocess.STDOUT, check=True)
    print("Marked PDF built against authenticated submitted source.", flush=True)


if __name__ == "__main__":
    main()
