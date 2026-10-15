from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent
BASE = ROOT / "original_submission" / "final_0903.tex"
TARGET = SRC / "FINAL_V5_MANUSCRIPT.tex"
OUTPUT = ROOT / "FINAL_V5_MARKED_MANUSCRIPT.tex"
BUILD = ROOT / "build"
EXPECTED_BASELINE = "203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01"


def main():
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != EXPECTED_BASELINE:
        raise RuntimeError("The authenticated 01549 baseline hash does not match.")
    BUILD.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w") as tex, (BUILD / "latexdiff_generation.log").open("w") as log:
        subprocess.run([
            "latexdiff", "--type=CFONT", "--subtype=SAFE", "--floattype=FLOATSAFE",
            "--graphics-markup=none", "--math-markup=0", "--disable-citation-markup",
            "--exclude-textcmd=section,subsection,subsubsection,paragraph,title,textit",
            r"--config=PICTUREENV=(?:picture[\w\d*@]*|tikzpicture[\w\d*@]*|DIFnomarkup|figure\*?|table\*?|tabular\*?|longtable)",
            "--flatten", "--no-label", str(BASE), str(TARGET),
        ], cwd=SRC, stdout=tex, stderr=log, check=True)

    raw = OUTPUT.read_text()
    (BUILD / "FINAL_V5_MARKED_MANUSCRIPT_RAW.tex").write_text(raw)
    active_source = TARGET.read_text()
    aux = (SRC / "build" / "FINAL_V5_MANUSCRIPT.aux").read_text()
    active_citations = set(re.findall(r"\\bibitem\{([^}]+)\}", active_source))
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

    # Citation-order renumbering moves nearly every reference. The ordinary
    # line matcher pairs unrelated entries and produces a misleading list, so
    # render the final bibliography as one added block. The exact old-to-new
    # bibliography remains visible in CHANGES_FROM_01549_V5.diff.
    target_bibliography = re.search(
        r"\\begingroup\s*\\linespread\{0\.94\}\\selectfont\s*"
        r"\\begin\{thebibliography\}\{[^}]+\}.*?"
        r"\\end\{thebibliography\}\s*\\endgroup",
        active_source,
        re.S,
    )
    marked_bibliography = re.compile(
        r"\\DIFdelbegin %DIFDELCMD < \\begin\{thebibliography\}\{[^}]+\}.*?"
        r"\\end\{thebibliography\}\s*\\DIFaddbegin\s*\\endgroup\s*\\DIFaddend",
        re.S,
    )
    if target_bibliography is None or len(marked_bibliography.findall(body)) != 1:
        raise RuntimeError("Could not atomically mark the reordered reference list.")
    target_bibliography_text = target_bibliography.group(0).replace(
        r"\begingroup", r"\begingroup" + "\n" + r"\color{blue}\sffamily", 1
    )
    marked_block = r"\DIFaddbegin" + "\n" + target_bibliography_text + "\n" + r"\DIFaddend"
    body = marked_bibliography.sub(lambda _: marked_block, body, count=1)
    OUTPUT.write_text("\n".join(line.rstrip() for line in (head + body).splitlines()) + "\n")

    expanded = re.sub(
        r"\\input\{([^}]+)\}",
        lambda match: (SRC / (match[1] if match[1].endswith(".tex") else match[1] + ".tex")).read_text(),
        active_source,
    )
    diff = difflib.unified_diff(
        BASE.read_text().splitlines(), expanded.splitlines(),
        fromfile="authenticated_01549/final_0903.tex",
        tofile="final_v5/expanded.tex", lineterm="",
    )
    (ROOT / "CHANGES_FROM_01549_V5.diff").write_text("\n".join(diff) + "\n")
    (ROOT / "MARKED_DIFF_SCOPE_V5.json").write_text(json.dumps({
        "baseline": "marked/original_submission/final_0903.tex",
        "target_tex_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "expanded_source_diff": "marked/CHANGES_FROM_01549_V5.diff",
        "baseline_sha256": EXPECTED_BASELINE,
        "mode": "CFONT text additions/deletions; figure/table bodies are atomic; the renumbered bibliography is shown as one added block because linewise matching pairs unrelated reordered entries; the full expanded source diff records every reference change.",
        "removed_only_citations_and_labels": {key: sorted(values) for key, values in removed.items()},
    }, indent=2) + "\n")
    print("Generated V5 marked source and source diff against the authenticated 01549 submission.")


if __name__ == "__main__":
    main()
