from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent
BASE = ROOT / "original_submission" / "final_0903.tex"
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--target", type=Path, default=SRC / "FINAL_V4_MANUSCRIPT.tex")
parser.add_argument("--output", type=Path, default=ROOT / "FINAL_V4_MARKED_MANUSCRIPT.tex")
args = parser.parse_args()
TARGET = args.target.resolve()
EXPECTED = "203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01"
OUTPUT = args.output.resolve()
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
    (BUILD / "FINAL_V4_MARKED_MANUSCRIPT_RAW.tex").write_text(raw)
    active_tex = TARGET.read_text()
    aux = (SRC / "build" / "FINAL_V4_MANUSCRIPT.aux").read_text()
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
        tofile="final_v4/expanded.tex", lineterm="",
    )
    (ROOT / "CHANGES_FROM_01549_V4.diff").write_text("\n".join(diff) + "\n")
    (ROOT / "MARKED_DIFF_SCOPE_V4.json").write_text(json.dumps({
        "baseline": "marked/original_submission/final_0903.tex",
        "target_tex_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "expanded_source_diff": "marked/CHANGES_FROM_01549_V4.diff",
        "baseline_sha256": EXPECTED,
        "mode": "CFONT text additions/deletions; figure/table bodies are treated atomically; full expanded source changes are in CHANGES_FROM_01549_V4.diff.",
        "removed_only_citations_and_labels": {key: sorted(values) for key, values in removed.items()},
    }, indent=2) + "\n")

    print("Generated V4 marked source and complete source diff against authenticated 01549.")


if __name__ == "__main__":
    main()
