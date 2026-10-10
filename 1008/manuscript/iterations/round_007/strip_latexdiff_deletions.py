#!/usr/bin/env python3
"""Remove deleted-text markup from a latexdiff file, keeping additions visible."""

from __future__ import annotations

import argparse
from pathlib import Path


TOKENS = (
    r"\DIFdelbeginFL",
    r"\DIFdelendFL",
    r"\DIFdelbegin",
    r"\DIFdelend",
    r"\DIFmodbegin",
    r"\DIFmodend",
)


def remove_deleted_body(body: str) -> str:
    out: list[str] = []
    i = 0
    debt = 0

    while i < len(body):
        if body.startswith(("%DIFDELCMD", "%DIFAUXCMD"), i):
            end = body.find("\n", i)
            i = len(body) if end == -1 else end + 1
            continue

        if body[i] == "{" and body.startswith("%DIFAUXCMD", i + 1):
            debt += 1
            end = body.find("\n", i)
            i = len(body) if end == -1 else end + 1
            continue

        matched = False
        for token in TOKENS:
            if body.startswith(token, i):
                i += len(token)
                matched = True
                break
        if matched:
            continue

        token = next(
            (name for name in (r"\DIFdelFL", r"\DIFdel") if body.startswith(name + "{", i)),
            None,
        )
        if token is not None:
            j = i + len(token)
            depth = 0
            while j < len(body):
                char = body[j]
                if char == "\\":
                    j += 2
                    continue
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:
                raise ValueError(f"unbalanced {token} group")
            i = j + 1
            continue

        if body[i] == "}" and debt:
            debt -= 1
            i += 1
            continue

        out.append(body[i])
        i += 1

    if debt:
        raise ValueError("unclosed DIFAUXCMD brace group")

    result = "".join(out)
    cleaned_lines = []
    for line in result.split("\n"):
        for marker in ("%DIFDELCMD", "%DIFAUXCMD"):
            position = line.find(marker)
            if position > 0 and line[position - 1] != "\\":
                line = line[:position]
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    text = args.source.read_text(encoding="utf-8")
    marker = r"\begin{document}"
    if text.count(marker) != 1:
        raise SystemExit("Expected one document start in latexdiff output")
    split = text.index(marker)
    result = text[:split] + remove_deleted_body(text[split:])
    args.destination.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
