"""Apply the final visual/submission edits to the preserved completed round014."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "history/pre_submission_visual_review"


def replace_caption(text, label, caption):
    end = text.index(r"\label{"+label+"}")
    start = text.rfind(r"\caption{", 0, end)
    assert start >= 0
    return text[:start]+r"\caption{"+caption+"}\n"+text[end:]


def main():
    main = (PARENT/"manuscript_round_014.tex").read_text()
    main = main.replace(r"\linenumbers", r"\raggedbottom"+"\n"+r"\linenumbers",1)
    # Let ordinary experiment text fill space beneath floats; keep the final
    # boundary before Discussion so result figures cannot trail the paper.
    start=main.index(r"\section{Experiments}")
    end=main.index(r"\section{Discussion and Limitations}")
    experiment=main[start:end].replace(r"\FloatBarrier", "")
    main=main[:start]+experiment+r"\FloatBarrier"+"\n"+main[end:]
    main = replace_caption(main, "fig:overview",
        r"TCAS on the existing GeoTex residual path. Reference-image and five-channel geometry conditioning enter separate paths. The requested C3 profile is $(1.25,2.50,1.25)$ over steps 0--16, 17--32 and 33--49; native group caps act before residual injection into the frozen UNet. Fresh C shallow requests are capped at 0.8. This editable vector schematic abstracts multiple ResNet sites and is not an experimental result or end-to-end application demonstration.")
    main = replace_caption(main, "fig:c3compare",
        r"Fresh C view 0: (a) Octa\`edre, a fixed-scale endpoint trade-off; (b) Cube 01, a Generic Linear counterexample. Each column shows the complete object in a common frame and the same pixel ROI enlarged below. Object-level C3 minus Generic Linear in (b) is $-3.491$~dB FG-PSNR and $+0.08172$ FG-LPIPS, favoring Linear on both. Added patterns visibly differ from the low-variation target. These retained outcome-selected examples illustrate behavior, not prevalence or material fidelity. Composite object metrics use all six views, not only the displayed crop. Source hashes, camera/seed identities and display frames are in the final visual manifest; credits are in Supplementary Section~S9.")
    main = replace_caption(main, "fig:color-failure",
        r"Fresh C view 0, E5-5-2: target, Fixed Low, C3 and layer LLH share a complete-object frame and an identical pixel crop. The generated brown pattern does not reproduce the gray target; changing its variation does not establish color fidelity. This previously viewed example came from an existing C3--GFL LPIPS stratum and was not selected for color. It does not reproduce the legacy purple-shift cases. The malformed disabled-adapter panel is omitted from this display; its numerical results remain in the full analysis. Source/display identities and attribution are supplied with the final visual manifest and Supplementary Section~S9.")
    main = replace_caption(main, "fig:baked-context",
        r"Unseen camera 004: (a) LG Remote and (b) Tire. Source and matched GT-256 bake separate projection loss from generated appearance; Fixed Mean and Late-high show the specified allocation comparison. Columns share a full-object frame determined from source, GT and every original condition, without color or detail editing. These are the first two input-order objects with verified publication licenses, not quality-selected examples. Persistent brown-pattern and material errors remain visible. Complete seven-condition displays for all seven rights-cleared objects are in Supplementary Section~S5; all ten objects enter the numerical analysis. Credits: mohd.akmal.mahyudin and Koto3D Stephane Vogley, CC Attribution (full source links in Supplementary Section~S5).")
    marker = r"\paragraph{External-input native schedule comparison.}"
    insert = main.index(marker)
    visual = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/fig9_mvadapter_native014.pdf}
\caption{Native MV-Adapter view 0 for the same first two input-order rights-cleared objects: (a) LG Remote, (b) Tire. Target, Fixed Mean, Middle-high and Late-high use the native camera, object seed and a common complete-object frame. Original backgrounds and research pixels are retained. The remote preserves recognizable details while the tire retains a marked appearance mismatch; the neighboring scheduling outputs are visually similar. These illustrative cases do not establish cross-interface superiority; the fifty-object primary interval includes zero. All seven controls are displayed in Supplementary Section~S3. Credits: mohd.akmal.mahyudin and Koto3D Stephane Vogley, CC Attribution (Supplementary Sections~S5 and S9).}
\label{fig:native50-visual}
\end{figure*}

"""
    main = main[:insert]+visual+main[insert:]
    main = main.replace("Software identities and the AI-assistance disclosure are supplied with the reproduction materials.",
        "Software identities and the AI-assistance disclosure are supplied with the reproduction materials. Final displays are checked against source hashes, shared cameras/crops and object-level metrics; visual assessment illustrates appearance limitations and is not an additional quality endpoint.")
    main = main.replace("Views are averaged within object, with GSO sampling seeds also averaged within object.",
        r"Fresh C image endpoints are evaluated once on each frozen $3\times2$ six-view composite. Native-interface and baked endpoints average their recorded per-view scores within object, with GSO sampling seeds also averaged within object.")
    main = main.replace("Panel (a) uses six-view PSNR except the reference-protocol row, which excludes its reference view;",
        "Panel (a) uses Fresh C composite PSNR and native-interface mean-view PSNR; the reference-protocol row excludes its reference view;")
    main = main.replace("OpenAI Images supplied conceptual artwork for Figure~\\ref{fig:overview}; the service did not expose a model version in the preserved generation record. Actual input/output thumbnails and experimental displays come from the recorded research runs and were not retouched with an image-generation tool.",
        "The final interface diagram uses reproducible vector elements; research displays come from the recorded runs without image-generation retouching. A vision-capable AI assistant inspected final figures and rendered pages for legibility and consistency with the named comparisons; this check does not certify scientific validity or replace author review.")
    main = main.replace("Sadat S, Hilliges O, Weber R M. Eliminating oversaturation and artifacts of high guidance scales in diffusion models. arXiv:2410.02416, 2024.",
        r"Sadat S, Hilliges O, Weber R M. Eliminating oversaturation and artifacts of high guidance scales in diffusion models. \textit{International Conference on Learning Representations}, 2025.")
    (ROOT/"manuscript_round_014.tex").write_text(main)

    supplement = (PARENT/"Supplementary_round_014.tex").read_text()
    mapping = json.loads((ROOT/"SUPPLEMENT_SECTION_CROSSWALK.json").read_text())["old_to_new"]
    # Plain old IDs survived the original Section-only remapping.
    supplement = re.sub(r"(?<![A-Za-z0-9])S(?:[12]\d|3[0-3])(?!\d)", lambda m: mapping.get(m[0], m[0]), supplement)
    supplement = supplement.replace("The full fixed twenty-object bake evaluation is completed and reported in Supplementary Section~S1.",
                                    "The full fixed twenty-object bake evaluation is completed and reported in Supplementary Section~S4.")
    supplement = supplement.replace("Figure~6 shows one of the 20 Fresh C panels", "The main manuscript's color-diagnostic figure shows one of the 20 Fresh C panels")
    supplement = supplement.replace("Generic Linear counterexample, Generic Linear counterexample", "Generic Linear counterexample")
    supplement = supplement.replace("Image, checkpoint, run, seed, ROI, and output hashes are listed in \\texttt{FRESH\\_C\\_FIGURE\\_SOURCE\\_ROI\\_MANIFEST.csv}.",
        r"The inherited Fresh C manifest retains the original layout lineage. Current source bytes, conditions, views, shared frames and ROI coordinates are indexed in \path{FINAL_VISUAL_SOURCE_MANIFEST.json}. Malformed No Adapter visual columns are omitted; their metric rows, exploratory contrasts and failure records remain unchanged.")
    start = supplement.rfind(r"\begin{figure}", 0, supplement.index("figures/figS2_baked_full_conditions.png"))
    end = supplement.index(r"\end{figure}", start)+len(r"\end{figure}")
    original_block = supplement[start:end]
    assert "figS2_baked_full_conditions" in original_block
    captions = []
    for i in range(1, 8):
        captions.append(r"\begin{figure}[p]\centering"+"\n"+
            r"\includegraphics[width=\textwidth,height=0.72\textheight,keepaspectratio]{figures/figS_bake014_"+f"{i:02d}"+r".pdf}"+"\n"+
            r"\caption{Rights-cleared GeoTex bake object "+str(i)+r" of seven, unseen camera 004. Source, matched GT-256 reference bake and all seven original generated conditions share one whole-object frame. These input/rights-selected displays retain visible failures and do not estimate prevalence. All ten eligible objects, including the three without verified display rights, remain in the numerical analysis. Source identities, native materials and credits are retained in the bake manifest and license ledger.}"+"\n"+r"\end{figure}"+"\n")
    supplement = supplement[:start]+"\n".join(captions)+supplement[end:]
    supplement = supplement.replace("figures/figS3_native_controls.pdf", "figures/figS_native_controls014.pdf")
    supplement = supplement.replace("Complete generated six-view grids for the same first two input-ordered, rights-cleared objects used in the earlier bake display.",
        "Generated six-view grids for the same first two input-ordered, rights-cleared objects used in the earlier bake display. The malformed No Adapter visual column is omitted; all its numerical contrasts remain reported.")
    for old, new, caption in [
        ("figS4_native_base_diagnostic.pdf", "figS_base_diagnostic014",
         "Retained complete grids for a fixed input-order failure object. The disabled-adapter visual column is omitted; its records remain available. Native base outputs use a different sampler and unverified camera conventions, so these are protocol diagnostics rather than aligned GT comparisons or complete default GeoTex results. No reference-fidelity inference follows from the better front-looking native color."),
        ("figS7_native_geometry_matrix.pdf", "figS_geometry_diagnostic014",
         "Retained complete native-loop geometry grids for a fixed input-order object. All seven enabled geometry settings are shown; the malformed disabled-adapter visual column is omitted, without changing any numerical results or failure records. Full-grid source pixels are preserved. The two input-order rights-cleared objects and their attribution remain the same; these observed outputs establish no general quality repair."),
        ("figS5_guidance_embedding_factorial.pdf", "figS_guidance_diagnostic014",
         "Guided cached/online-feature outputs for the fixed failure object. The two malformed unguided disabled-adapter columns are omitted from the display; all four original factorial arms and identity tests remain reported. Complete generated grids are resized only for presentation. The dark incorrect shapes remain, and online features do not establish a quality repair. These are previously inspected diagnostic examples, not a new holdout."),
        ("figS6_target_resolution_bridge.pdf", "figS_resolution_diagnostic014",
         "Guided 256/512-view outputs for the fixed failure object. Malformed unguided disabled-adapter columns are omitted; all original resolution arms remain in the protocol and numerical record. The complete grids preserve their contents. Camera identity has not been independently calibrated across target resolutions, so these are protocol/appearance diagnostics, not aligned GT comparisons or an established repair."),
    ]:
        loc=supplement.index("figures/"+old)
        start=supplement.rfind(r"\begin{figure}",0,loc)
        end=supplement.index(r"\end{figure}",loc)+len(r"\end{figure}")
        figures=[]
        for j in [1,2]:
            figures.append(r"\begin{figure}[p]\centering"+"\n"+r"\includegraphics[width=\linewidth,height=0.72\textheight,keepaspectratio]{figures/"+new+f"_{j:02d}"+r".pdf}"+"\n"+r"\caption{"+caption+f" Object {j} of two."+"}\n"+r"\end{figure}"+"\n")
        supplement=supplement[:start]+"\n".join(figures)+supplement[end:]
    start=supplement.index(r"\subsection*{Historical record disposition}")
    end=supplement.index(r"\end{document}",start)
    supplement=supplement[:start]+r"""
\subsection*{Historical record index}
Unique historical selections remain in Section S7; duplicate parent discussions are archived in \path{history/retained_parent_section32.tex}. Original protocol/attempt filenames retain their historical statuses. The release completion and validation manifests index the current completed experiment chain.

"""+supplement[end:]
    new_native = r"""
\begin{figure}[p]\centering
\includegraphics[width=\textwidth,height=0.72\textheight,keepaspectratio]{figures/figS_native50_all014.pdf}
\caption{Native MV-Adapter targets and all seven controls for the two fixed input-order rights-cleared examples in the main text. All images use native view 0 and the same object seed; each object has one shared frame spanning target and every condition. Previously observed illustrative outputs do not establish the primary effect or a generally best schedule. Source hashes and display frames are in the final visual manifest; full attribution is in Sections S5 and S9.}
\label{fig:supp-native50-full}
\end{figure}
\FloatBarrier
"""
    loc = supplement.index(r"\section*{S4.")
    supplement = supplement[:loc]+new_native+supplement[loc:]
    (ROOT/"Supplementary_round_014.tex").write_text(supplement)

    response = (PARENT/"Response_to_Reviewers_round_014.md").read_text()
    response = response.replace("Each display states its selection rule and preserves recorded RGB contents; outcome-selected illustrations do not estimate failure prevalence.",
        "Each display states its selection rule and preserves recorded RGB contents; outcome-selected illustrations do not estimate failure prevalence. We adopted clearer shared full-object frames from the conservative visual revision, added the matched GT-256 bake beside source/Fixed Mean/Late-high, and show the native MV-Adapter cases with their complete seven-control Supplement display. Conspicuously malformed No Adapter visual columns are omitted for legibility; all conditions, negative results and numerical comparisons remain reported. Source-image hashes, crops and object/condition identities are preserved, and a vision-capable assistant checked the actual figures and rendered PDFs for label, caption and appearance consistency. This presentation check is not a validation of texture fidelity or a substitute for author assessment.")
    (ROOT/"Response_to_Reviewers_round_014.md").write_text(response)
    manifest = json.loads((ROOT/"ROUND_MANIFEST.json").read_text())
    manifest["final_submission_visual_phase"] = {"parent_commit": "b19420b40aab18e36b51fc5156648f6ba0556a1f", "plan": "03_FINAL_SUBMISSION_PLAN.md", "No_Adapter": "Visual columns omitted; numerical evidence retained", "statistics_changed": False}
    (ROOT/"ROUND_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print("Synchronized final manuscript, Supplement and response; retained original numerical conclusions.")


if __name__ == "__main__":
    main()
