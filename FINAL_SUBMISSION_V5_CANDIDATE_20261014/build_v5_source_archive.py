"""Build the flat LaTeX source archive required for Editorial Manager."""
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Manuscript_LaTeX_Sources_V5.zip"
JOURNAL_PACKAGE = Path(
    "/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/"
    "1014v4_TEXT_FINAL_REVISION_20261014/journal_upload_v5_candidate"
)
DOCUMENTS = ("FINAL_V5_MANUSCRIPT.tex", "FINAL_V5_SUPPLEMENTARY.tex")
DEPENDENCIES = ("cag.sty", "elsarticle.cls", "cag-logo.pdf", "elsevier-logo.pdf")
GRAPHIC = re.compile(r"\\includegraphics(\[[^]]*\])?\{([^{}]+)\}")
INPUT = re.compile(r"\\(?:input|include)\{([^{}]+)\}")


def resolve(root: Path, relative: str, kind: str) -> Path:
    source = root / relative
    candidates = [source]
    if kind == "graphic" and not source.suffix:
        candidates.extend(source.with_suffix(ext) for ext in (".pdf", ".png", ".jpg", ".jpeg"))
    if kind == "input" and not source.suffix:
        candidates.append(source.with_suffix(".tex"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Missing {kind} dependency: {relative}")


def flat_name(relative: str) -> str:
    return "__".join(PurePosixPath(relative).parts)


def collect_and_rewrite(root: Path, filename: str, staged: dict[str, bytes]) -> None:
    text = (root / filename).read_text()

    def rewrite_graphic(match: re.Match) -> str:
        relative = match.group(2).strip()
        source = resolve(root, relative, "graphic")
        archive_name = flat_name(source.relative_to(root).as_posix())
        staged[archive_name] = source.read_bytes()
        return rf"\includegraphics{match.group(1) or ''}{{{archive_name}}}"

    def rewrite_input(match: re.Match) -> str:
        relative = match.group(1).strip()
        source = resolve(root, relative, "input")
        archive_name = flat_name(source.relative_to(root).as_posix())
        staged[archive_name] = source.read_bytes()
        return rf"\input{{{Path(archive_name).with_suffix('').as_posix()}}}"

    text = GRAPHIC.sub(rewrite_graphic, text)
    text = INPUT.sub(rewrite_input, text)
    staged[filename] = text.encode()


def main() -> None:
    staged: dict[str, bytes] = {}
    for filename in DOCUMENTS:
        collect_and_rewrite(ROOT, filename, staged)
    for filename in DEPENDENCIES:
        staged[filename] = (ROOT / "vendor" / filename).read_bytes()
    staged["README_SOURCE_ARCHIVE.txt"] = (
        "V5 manuscript source archive\n\n"
        "This archive contains the main manuscript and Supplement sources, all figures and tables they require, "
        "and the local Elsevier class/style/logo files. All files are stored at one directory level for Editorial Manager.\n\n"
        "Compile from this directory with pdfLaTeX, running each command three times:\n"
        "  pdflatex -interaction=nonstopmode -halt-on-error FINAL_V5_MANUSCRIPT.tex\n"
        "  pdflatex -interaction=nonstopmode -halt-on-error FINAL_V5_SUPPLEMENTARY.tex\n"
        "The bibliography is embedded in FINAL_V5_MANUSCRIPT.tex; no separate .bib or .bst is needed.\n"
    ).encode()

    if any("/" in name or "\\" in name for name in staged):
        raise RuntimeError("The upload archive must not contain subfolders.")
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sorted(staged):
            archive.writestr(name, staged[name])
    if JOURNAL_PACKAGE.is_dir():
        shutil.copy2(OUTPUT, JOURNAL_PACKAGE / OUTPUT.name)
    print(f"Wrote flat source archive with {len(staged)} files: {OUTPUT}")


if __name__ == "__main__":
    main()
