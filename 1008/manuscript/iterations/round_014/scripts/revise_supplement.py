"""Group retained evidence by scientific question and remove stale status claims."""
from pathlib import Path
import json
import re
from revise_manuscript import MAP, TITLE, remap

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "history/round_013"


def subblock(body, title):
    body = remap(body.strip())
    body = re.sub(r"\\subsection\*\{S20\.1 ([^}]+)\}", r"\\subsection*{\1}", body)
    return r"\subsection*{" + title + "}\n" + body + "\n\n"


def main():
    source = (PARENT / "Supplementary_round_013.tex").read_text()
    heads = list(re.finditer(r"^\\section\*\{S(\d+)\. ([^\n]+)\}\n", source, re.M))
    blocks = {}
    titles = {}
    for i, match in enumerate(heads):
        number = int(match[1])
        end = heads[i+1].start() if i+1 < len(heads) else source.index(r"\end{document}")
        body = source[match.end():end]
        body = body.replace(r"\input{sections/development_round012.tex}", "")
        body = body.replace(r"\input{sections/completed_supplement013.tex}", "")
        blocks[number] = body
        titles[number] = match[2]
    assert set(blocks) == set(MAP) - {31, 33}
    blocks[2] = (
        "The original Generic Linear source manifest is delivered in "
        r"\path{data/primary_studies/GENERIC_LINEAR_SOURCE_MANIFEST_shard0.json}. "
        "Its SHA256 matches the lineage record attached to the retained Generic Linear figure. "
        "Across fifty steps, deep/middle requests ramp from 1.25 to 2.50 and shallow requests "
        "from 0.50 to 0.75. All pass the stated native caps. Applied sums are "
        "(93.75,93.75,31.25), different from C3 and the equal-budget family. "
        "This is a competitive layer/time control, not a timing-only matched-dose contrast.\n\n"
        + blocks[2])
    archived = ROOT / "history/retained_parent_section32.tex"
    archived.parent.mkdir(exist_ok=True)
    archived.write_text(blocks[32])
    unique32 = blocks[32].split(r"\subsection*{Applied-Scale Budget and Temporal Placement}", 1)[0]
    assert r"\includegraphics" in unique32

    old31 = (PARENT / "sections/development_round012.tex").read_text()
    marker = r"\paragraph{Completed GSO100 external comparison.}"
    assert old31.count(marker) == 1
    development31, external31 = old31.split(marker, 1)
    development31 = re.sub(r"^\\section\*\{[^}]+\}\n", "", development31)
    development31 = development31.replace(
        "observations and completed external-input comparisons; the external bake evaluation remains incomplete.",
        "observations and external-input comparisons. The full fixed twenty-object bake evaluation is completed and reported in Section~S4.")
    external31 = marker + external31
    external31 = external31.replace(
        r"\paragraph{Incomplete external bake evaluation.}",
        r"\paragraph{Archived original bake attempt and subsequent completion.}")
    external31 = external31.replace(
        "The supervisor and final delivery stop on that failure. No complete twenty-object comparison, final ranking analysis or automatic evidence-delivery package is claimed.",
        "The original supervisor and delivery stop on that failure. A documented GT-only calibration addendum subsequently completes all twenty fixed inputs, including four inherited schedule controls, for 740 unique bakes and 8,140 unseen-view rows. All 375 earlier GLB hashes and metric records reproduce exactly. The full results, raw failure and revised-calibration scope are reported above in this section.")
    external31 = external31.replace(
        "All primary comparisons favor the baselines;",
        "All fifteen primary correction comparisons favor the baselines;")

    completed = (PARENT / "sections/completed_supplement013.tex").read_text()
    completed = re.sub(r"^\\section\*\{[^}]+\}\n", "", completed)
    completed = completed.replace("Other83", "The other 83").replace("the21", "the 21")
    completed = completed.replace("pointwise95", "pointwise 95").replace("object-bootstrap95", "object-bootstrap 95")
    completed = completed.replace("all20", "all twenty").replace("after15", "after fifteen")
    completed = completed.replace("All375", "All 375").replace("740 unique", "740 unique")
    completed = completed.replace("contains740", "contains 740").replace(":12 existing", ": twelve existing")
    completed = completed.replace("all375", "all 375").replace("on common coverage", "on common diagnostic coverage")
    completed = completed.replace("bounds of0.03/0.15", "bounds of 0.03/0.15")
    completed = completed.replace("all20 fixed", "all twenty fixed")
    facts = json.loads((ROOT / "data/FACTS_round_014.json").read_text())["facts"]
    late = facts["bake20_late_mean"]
    text = (
        "The specified Late-high minus Fixed Mean unseen-view FG-LPIPS difference is "
        + f'{late["mean"]:+.8f}, with pointwise 95\\% object interval '
        + f'[{late["ci95"][0]:+.8f},{late["ci95"][1]:+.8f}] and original Holm16 '
        + f'adjusted $p={late["p_adjusted"]:.5f}$. This study does not detect the '
        "ten-object GeoTex pilot's benefit; it uses a different domain and interface/projection protocol."
    )
    completed += "\n\n" + text + "\n\n"
    rank = facts["GSO20_schedule_rank"]
    completed += (
        r"\paragraph{Post hoc sensitivity of image/bake rank agreement.}" + "\n"
        "The all-twelve-method estimate includes auxiliary corrections that differ markedly in quality. "
        "Restricting the same twenty objects to native, fixed low, fixed mean, early-high, middle-high, "
        "late-high and generic linear gives mean within-object Spearman "
        + f'{rank["mean"]:.6f}, with pointwise object-bootstrap 95\\% interval '
        + f'[{rank["ci95"][0]:.6f},{rank["ci95"][1]:.6f}] '
        "(20,000 resamples, seed 131313). The minimum-mean LPIPS condition changes on "
        "11/20 objects. This is a post hoc descriptive analysis, retaining every object. "
        "It changes neither the primary endpoint nor the original adjusted families; point-estimate "
        "winner changes do not establish statistically resolved best methods. Raw pairs and a portable "
        "recomputation are delivered in data/FACTS\\_round\\_014.json and scripts/build\\_evidence.py.\n"
    )

    credits = blocks[1]
    credits = credits.replace(
        "Display numbers in inherited credit rows identify the archived parent displays. The current main figures are the control schematic (1), paired C3/strong-control examples (2), color diagnosis (3), and baked context (4); object identities, licenses and selection status are unchanged.",
        "Object identities, licenses and selection rules are unchanged. Figure references below use scientific display roles rather than obsolete parent figure numbers; the current figure/asset mapping is supplied in FIGURE\\_ASSET\\_PROVENANCE.md.")
    credits = credits.replace(
        "Main Figures~4--7 use Fresh C reference and method-level RGB outputs in a compact context-plus-shared-ROI layout. The original six-view, seven-condition panels remain in Supplementary Figure~S1.",
        "The retained Fresh C comparisons use reference and method-level RGB outputs with shared pixel crops. Complete preserved displays and the former main-text C3--GFL examples are supplied in this section.")
    credits = credits.replace(
        "Fresh C contains no separate output for that native-default path, so this part of the R1.1 request remains partially unresolved.",
        "The primary 300-object image matrix contains no separate output for that native-default branch. Later ten-object native-residual controls are exploratory and use the controlled sampler; native MV-Adapter comparisons have a separate default-path identity contract. These checks do not establish complete GeoTex default-pipeline equivalence.")
    for old, new in {
        "main Figures~5--7 and Supplementary Figure~S1": "the retained Fresh C displays",
        "Figure 7(a)": "C3--GFL favorable context",
        "Figure 7(b) and Figure S1(a)": "C3--GFL adverse context",
        "Figure 5(a)": "Strong fixed-control context",
        "Figure 5(b)": "Generic Linear counterexample",
        "Figure 6": "Color-failure context",
        "Table S1": r"Table~\ref{tab:supp-credits}",
    }.items():
        credits = credits.replace(old, new)
    failure = blocks[7]
    credits += "\n\n" + failure[failure.index(r"\begin{figure}"):failure.index(r"\end{figure}")+len(r"\end{figure}")]
    blocks[7] = failure[:failure.index(r"\begin{figure}")] + failure[failure.index(r"\end{figure}")+len(r"\end{figure}"):]
    blocks[7] = blocks[7].replace("Full attribution appears in Table S1.", r"Full attribution appears in Table~\ref{tab:supp-credits}.")

    groups = [
        (1, "Study identities, sampling and applied-scale semantics", [8, 4]),
        (2, "Matched GeoTex controls and complete paired statistics", [2, 16, 3]),
        (3, "Native MV-Adapter and historical cross-interface evaluation", [17, 5]),
        (4, "GSO external-input and complete baked evaluation", []),
        (5, "Calibrated GeoTex baked appearance and earlier attempts", [18, 19, 20, 6, 7]),
        (6, "Appearance failures and executed-protocol diagnostics", [13, 21, 22, 23, 24, 25]),
        (7, "Historical selection, preference and FAC records", [9, 10, 11, 12]),
        (8, "Auxiliary training, deployment and projection exploration", [26, 27, 28, 29, 30]),
        (9, "Figure credits, retained displays and record index", []),
    ]
    preamble = source[:source.index(r"\begin{document}")]
    preamble = re.sub(r"\\title\{.*?\\author", lambda _: (
        r"\title{Supplementary Material for\\" + "\n" + r"\emph{" + TITLE + r"}}" + "\n" + r"\author"),
        preamble, flags=re.S)
    preamble = preamble.replace(r"\date{}", r"\date{}" + "\n" + r"\usepackage[hidelinks]{hyperref}")
    output = preamble + r"""
\begin{document}
\maketitle
\noindent This supplement is organized by scientific question rather than experiment chronology. It supports the controlled empirical study of geometry-control allocation. Fresh C, native MV-Adapter, GSO, the two bake cohorts and historical MVDiffusion records remain separate evidence classes. Views and seeds do not increase the number of independent objects. The original GSO bake failure is preserved alongside the complete post hoc calibration addendum; historical results with incomplete provenance are explicitly labeled.

\tableofcontents
\clearpage
"""
    for number, title, items in groups:
        output += r"\FloatBarrier" + "\n"
        output += r"\section*{S" + str(number) + ". " + title + "}\n"
        output += r"\label{supp:group" + str(number) + "}\n"
        output += r"\addcontentsline{toc}{section}{S" + str(number) + ". " + title + "}\n\n"
        for item in items:
            if item == 11:
                output += r"\clearpage" + "\n"
            output += subblock(blocks[item], titles[item])
        if number == 4:
            output += subblock(completed, "Complete inherited-schedule extension and twenty-object bake")
            output += subblock(external31, "Separate projection/APG comparison and archived original bake failure")
        if number == 7:
            output += subblock(unique32, "Retained original fixed-scale and C3 selection displays")
            output += (ROOT / "sections/historical_preference014.tex").read_text()
        if number == 8:
            output += subblock(development31, "Archived projection development and first-interface evaluation")
        if number == 9:
            output += subblock(credits, "Figure sources, licenses and selection")
            output += (ROOT / "sections/retained_weak_control_display014.tex").read_text()
            output += r"""
\subsection*{Historical record disposition}
The parent section containing repeated main-text discussions is retained verbatim as history/retained\_parent\_section32.tex. Its unique fixed-scale and C3-selection figures appear in Section~S7. Current scale accounting, complete paired results, native-interface comparisons and deployment tests appear once in their corresponding sections above. This reorganization changes presentation and figure numbers, not the observed results or their evidence grades.

Archived protocol and attempt records keep their original filenames and statuses. Current completion is indexed by ROUND\_MANIFEST.json and FINAL\_VALIDATION.json. A failed archived status is not the current status of the completed supplementary experiment chain.
"""
    output += "\n" + r"\end{document}" + "\n"
    output = output.replace(r"\subsection*{S20.1 Complete exploratory contrast family}", r"\subsection*{Complete exploratory native-control contrast family}")
    output = output.replace(r"history/retained\_parent\_section32.tex", r"\path{history/retained_parent_section32.tex}")
    # Uniform display scaling preserves the stored pixels and avoids clipped tall panels.
    for width in [r"\textwidth", r"\linewidth"]:
        output = output.replace(
            r"\includegraphics[width=" + width + "]",
            r"\includegraphics[width=" + width + r",height=0.74\textheight,keepaspectratio]")
    output = output.replace(r"height=0.84\textheight", r"height=0.74\textheight")
    output = output.replace(
        r"\includegraphics[width=\textwidth,trim=0 36pt 0 0,clip]",
        r"\includegraphics[width=\textwidth,height=0.74\textheight,keepaspectratio,trim=0 36pt 0 0,clip]")
    (ROOT / "Supplementary_round_014.tex").write_text(output)
    (ROOT / "SUPPLEMENT_SECTION_CROSSWALK.json").write_text(json.dumps(
        {"old_to_new": {f"S{k}":f"S{v}" for k,v in MAP.items()},
         "S32_disposition": "Unique historical figures in S7; repeated parent discussion preserved in history/retained_parent_section32.tex",
         "table_figure_numbers": "Recomputed in question-grouped order; semantic credits replace obsolete parent display numbers."},
        indent=2) + "\n")
    print("Supplement grouped into nine questions; all unique evidence retained; original bake failure and completion reconciled.")


if __name__ == "__main__":
    main()
