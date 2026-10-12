"""Integrate completed descriptive evidence without changing inherited facts."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]


def main():
    stability=json.loads((ROOT/"data/gap_closure015/STABILITY_AND_DOMINANCE.json").read_text())
    variance=json.loads((ROOT/"data/gap_closure015/CROSS_VIEW_DIAGNOSTICS.json").read_text())
    gate=json.loads((ROOT/"data/gap_closure015/CROSS_VIEW_VALIDATION.json").read_text())
    fac=json.loads((ROOT/"data/gap_closure015/FAC_COMPONENT_VALIDATION.json").read_text())
    assert gate["status"].startswith("PASS_80") and gate["max_absolute_replay_error"]==0
    assert fac["status"].startswith("PASS_")
    assert stability["freshC_dominance"]["dominated_by_at_least_one"]==270
    for key in ["facts","validation"]:
        old=json.loads((ROOT/"history/round_014/FACTS_round_014.json").read_text())[key]
        new=json.loads((ROOT/"data/FACTS_round_015.json").read_text())[key]
        assert old==new,key
    parent=ROOT/"history/round_014"
    text=(parent/"manuscript_round_014.tex").read_text()
    text=text.replace("These findings quantify the effects and limits of geometry-control allocation and provide application-specific evidence for evaluating operating points.","Fixed-seed and shared-UV diagnostics distinguish group-average gains, objectwise repeatability and incoming-view consistency from fidelity. These findings quantify application-specific effects and limits of geometry-control allocation.")
    text=text.replace("Both the ten-object gain and the twenty-object non-detection are reported.","Both the ten-object gain and the twenty-object non-detection are reported. Known-color controls check the incoming-view disagreement diagnostic, which remains distinct from fidelity.")
    text=text.replace("They reveal endpoint-dependent effects and limits to transfer, without pooling cohorts or claiming a common residual dose.","They reveal endpoint-dependent effects and limits to transfer; fixed-seed sensitivity separates an aggregate effect from objectwise repeatability. Cohorts are not pooled and identical scale labels are not treated as a common residual dose.")
    anchor="The equal-budget comparison identifies an allocation total effect."
    paragraph=r"""A descriptive four-endpoint comparison complements these winner counts. On 270/300 objects, at least one of the other five controls weakly dominates C3 on all four recorded composite endpoints and improves at least one. Fixed High alone does so on 173 objects, but C3 dominates it on 16; their remaining 111 objects have competing endpoints. This post-inspection, point-estimate analysis is not statistical separation on each object or a ranking of unmeasured material quality. Full counts are in Supplementary Section~S2.

"""
    assert text.count(anchor)==1;text=text.replace(anchor,paragraph+anchor)
    anchor=r"\paragraph{Native controls and protocol sensitivity.}"
    paragraph=r"""\paragraph{Incoming-view consistency.}
The ten-object bake also records the mean linear-RGB variance across cameras at UV texels receiving at least two visible source views. Replaying the frozen projection code reproduces all 80 object--condition values exactly. On the first two input-order objects, a shared constant-black control gives zero variance; known camera-specific gray levels match an independent analytic variance within $1.1\times10^{-8}$. A wrong constant appearance can therefore be fully consistent by this measure. Late-high minus Fixed Mean is $-0.002448$ (descriptive object interval $[-0.003473,-0.001604]$; additional post-inspection Holm21 $p=0.041$). Fixed High has still lower mean disagreement than Late-high, but a higher baked LPIPS. Resampling, natural texture and overlapping UVs contribute to this diagnostic: it assesses incoming-view disagreement and does not validate seams, a faithful texture or PBR. Formula, all controls and contrasts are in Supplementary Section~S5.

"""
    assert text.count(anchor)==1;text=text.replace(anchor,paragraph+anchor)
    anchor="All fifteen specified GSO projection-minus-baseline"
    paragraph=r"""\paragraph{Fixed-seed sensitivity.}
A post-inspection analysis retains all three recorded sampling seeds. GSO100 Late--Mean PSNR averages are positive at each seed ($+0.057,+0.038,+0.039$ dB), but only 27/100 objects improve at all three and 68/100 have mixed or tied directions. Its nonreference LPIPS averages change direction ($-0.000389,-0.000269,+0.000398$). For the GSO20 bake, only 1/20 objects has lower Late--Mean LPIPS at all three seeds; 14/20 have mixed or tied directions. Sign agreement has no practical-effect threshold. These conditional, object-level summaries do not estimate training randomness or revise the original primary tests; full seed intervals and deltas are in Supplementary Section~S4.

"""
    assert text.count(anchor)==1;text=text.replace(anchor,paragraph+anchor)
    text=text.replace("Later new geometry training does not restore historical FAC identity.","Recovered FAC source is now supplied with standalone controller checks. An earlier entry requires an explicit flag to freeze the base adapter, whereas the later entry freezes it by construction; the executed historical source/CLI cannot be authenticated from their names. Later new geometry training does not restore historical FAC identity.")
    anchor="Generated-view metrics remain informative:"
    paragraph=r"""The evidence suggests a practical evaluation sequence rather than a new selection algorithm: compare native/default and competitive fixed settings inside the same deployed protocol; use matched applied budgets to assess timing; check reference appearance and the actual unseen-view bake; and repeat the named comparison across fixed seeds before claiming repeatable objectwise improvement. The tested GeoTex image setting supports stronger fixed controls than historical C3. The native-interface and GSO bake results provide no general reason to replace a deployment's fixed setting with the middle window. These bounded conclusions do not depend on a universally winning schedule.

"""
    assert text.count(anchor)==1;text=text.replace(anchor,paragraph+anchor)
    text=text.replace("seed repetitions do not estimate training-checkpoint variation.","seed repetitions do not estimate training-checkpoint variation. The new seed, dominance and UV-overlap summaries were proposed after observing the original outcomes and remain descriptive; their diagnostic checks do not change that chronology.")
    text=text.replace("The standalone reproduction archive supports statistic recomputation without model weights;", "Recovered FAC source and its source/entry audit are supplied separately; standalone controller tests do not constitute historical full-model replay. The standalone reproduction archive supports statistic recomputation without model weights;")
    (ROOT/"manuscript_round_015.tex").write_text(text)

    sections={
    "S2":r"""\subsection*{Objectwise four-endpoint dominance: descriptive addendum}
The five controls in the complete matched six-condition matrix are compared with C3 on the recorded FG-PSNR, foreground LPIPS, FG-SSIM and Edge-SSIM composite values. A control weakly dominates C3 if it is no worse on all four and better on at least one. LPIPS is reversed when forming the comparison. We use no effect threshold or fitted quality score. This is a post-inspection analysis of point estimates, not inference that every object has a resolved quality winner.

\begin{table}[ht]\centering\small
\caption{Fresh C300: all four-endpoint pairwise dominance counts. Incomparable/equal includes competing endpoint directions. Counts use the complete object matrix.}\label{tab:dominance015}
\begin{tabular}{lrrr}\toprule Control & Dominates C3 & C3 dominates & Incomparable/equal \\
\midrule\input{tables/dominance015.tex}\bottomrule\end{tabular}
\end{table}
At least one other control dominates C3 on 270/300 objects (90.0\%; descriptive object-bootstrap interval [86.3,93.3]\%). This fraction is over the tested controls and endpoints, not the fraction with failed materials or a confidence level for overall superiority. C3 can dominate a particular fixed control while another control dominates C3. The supplied per-object Boolean matrix permits independent reconstruction of the union count. All five pairs, including cases favoring C3, are retained.

""",
    "S4":r"""\subsection*{Fixed-seed stability: complete descriptive addendum}
This analysis was proposed after inspection of the completed GSO results. Each seed-specific value averages the appropriate views within object. Its pointwise 95\% interval resamples objects (20,000 draws; seed 20261012). All three fixed seeds and all four named rows are retained; seeds are not additional independent objects. The all-six-view image primaries, five-nonreference-view LPIPS and eleven-unseen-view bake remain distinct. Direction agreement uses zero only and is not a meaningful-effect or non-inferiority threshold. We define no new confirmatory test or significance family for these descriptive intervals.

\begin{table}[ht]\centering\scriptsize\setlength{\tabcolsep}{3pt}
\caption{Fixed-seed conditional mean A minus B and number of objects with favorable/adverse directions at all three seeds. Higher favors PSNR; lower favors LPIPS. The remaining objects have mixed or tied directions.}\label{tab:seed-stability015}
\begin{tabular}{lrrrrr}\toprule Contrast / endpoint & 42 & 2026 & 31415 & All favorable & All adverse \\
\midrule\input{tables/seed_stability015.tex}\bottomrule\end{tabular}
\end{table}
\begin{figure}[ht]\centering
\includegraphics[width=.95\textwidth]{figures/fig_seed_stability015.pdf}
\caption{Seed-specific paired means with pointwise object intervals. Three fixed seeds do not estimate the complete distribution of inference or training randomness. The original seed-averaged tests remain unchanged.}\label{fig:seed-stability015}
\end{figure}
For Late--Mean PSNR, all three cohort means are positive, yet 68/100 objects have mixed/tied signs. For nonreference LPIPS, the third seed reverses the cohort-average direction. In GSO20, one object has favorable LPIPS at all seeds, five adverse at all seeds and fourteen mixed/tied. Small average effects therefore provide limited assurance of repeatable per-object improvement. Complete per-object seed deltas and descriptive intervals are supplied in the data addendum; no seed or object is removed for its outcome.

""",
    "S5":r"""\subsection*{Incoming-camera disagreement on shared UV texels}
This additional diagnostic uses the already recorded source-view projection, before filling holes or rendering the exported atlas. For camera $v$ and texel $t$, let $c_{vt}$ be its linear-RGB average after visible-pixel bilinear UV splatting. Let $V_t$ be the cameras with accumulated weight exceeding $10^{-8}$. We retain only texels with $|V_t|\geq2$, average cameras equally within each texel and then average population channel variance equally across the retained texels:
\[
D=\frac{1}{3|T|}\sum_{t\in T}\sum_{k=1}^3\left[\frac{1}{|V_t|}\sum_{v\in V_t}c_{vtk}^{2}-\left(\frac{1}{|V_t|}\sum_{v\in V_t}c_{vtk}\right)^2\right]_+ .
\]
The nonnegative clamp handles rounding. One-camera texels do not contribute. Six original cameras, GT-256 resolution/masks, 1024 atlas, original material and sampler, and the repaired REPEAT interpolation are shared with the bake. We copied the actual archived baker with SHA256 \texttt{f7eeb7cc4efb166cd4138b832e91356f36f775ac18badedefde5610aafdb8db4}, rather than silently substituting a later implementation. All 80 previously recorded values reproduce exactly.

On the first two input-order objects, known camera-constant gray inputs ($c_v=v/5$, $v=0,\ldots,5$) yield 0.12721819 and 0.12461645; independent camera-incidence calculations agree to at most $1.1\times10^{-8}$. A shared constant-black input gives exactly zero in both cases. The diagnostic can therefore return perfect agreement for an incorrect, flat appearance. These controlled input substitutions are formula/path checks, not newly generated model outputs or quality evidence. Inputs and original method images are unaltered.

\begin{table}[ht]\centering\small
\caption{Ten-object recorded incoming-camera variance and actual baked LPIPS means. GT-256 is a path reference, not a perfect oracle. Lower disagreement does not imply better reference agreement.}\label{tab:cross-view015}
\begin{tabular}{lrr}\toprule Condition & Shared-UV variance & Unseen FG-LPIPS \\
\midrule\input{tables/cross_view_diagnostic015.tex}\bottomrule\end{tabular}
\end{table}
Late--Mean variance is $-0.002448$ (pointwise descriptive interval $[-0.003473,-0.001604]$; all ten negative). Its exact sign-flip $p=0.001953$ becomes 0.041016 in the additional 21-pair Holm family. This family was specified after seeing the original bake endpoints and is exploratory. The two tested color controls do not certify arbitrary assets: UV overlap/repetition, natural texture, source-view dependence and sampling can produce disagreement. No quantitative seam or PBR endpoint is validated.

\begin{longtable}{p{.43\textwidth}rrr}
\caption{All generated-condition pairs for the additional shared-UV diagnostic. A minus B; pointwise descriptive object intervals, 20,000 draws with seed 20261012; exact $2^{10}$ paired sign flips and one Holm21 family.}\label{tab:cross-view-all015}\\
\toprule Contrast & Mean & 95\% interval & Holm $p$ \\
\midrule\endfirsthead\toprule Contrast & Mean & 95\% interval & Holm $p$ \\
\midrule\endhead
\input{tables/cross_view_contrasts015.tex}
\bottomrule\end{longtable}

""",
    "S7":r"""\subsection*{Recoverable FAC code and bounded component validation}
The separate recovered-source archive supplies byte-preserved controller, training/evaluation entries, local source dependencies and configuration snapshots, with a per-file source/hash manifest. It distinguishes an earlier entry whose default also optimizes the base adapter/geometry encoder unless \texttt{--freeze\_adapter} is used, from the later controller-only entry that freezes these modules. Both remain unbound to the historical reported run; filenames and their existence cannot establish which complete CLI, weights and sampling order produced the old table.

Three distinct standalone CPU controller fixtures pass finite forward/gradient-path and bitwise state-save/load checks. The two recovered entries share byte-identical controller source; duplicate copies are not counted as independent validation. For nine adapters with 64-channel geometry and the delivered defaults, LTAG, LTAG+GSG and full FAC contain 3,433, 4,018 and 6,322 parameters. These tests exercise one injection point with synthetic 16-by-16 tensors, without a diffusion model, base weights or data. They validate component execution, not full-model training, old experiment identity or quality. The archived FSC actually uses real FFT rather than the DCT named in comments; its initial mask attenuates the test tensor and is not an exact identity. Current claims follow executable operations, not archival comments.

The supplied recovered 1,200-object configuration, missing historical seed/checkpoint and 1,706-object discrepancy remain unresolved. We provide code and an offline component rerun command, while explicitly withholding a complete historical FAC replay claim. The already reported FAC negative results are not reclassified as newly confirmed measurements.

"""}
    supplement=(parent/"Supplementary_round_014.tex").read_text()
    for group,section in sections.items():
        anchor={"S2":r"\section*{S3.","S4":r"\section*{S5.","S5":r"\section*{S6.","S7":r"\section*{S8."}[group]
        index=supplement.index(anchor)
        supplement=supplement[:index]+section+"\\FloatBarrier\n"+supplement[index:]
    supplement=supplement.replace("We retain the original values as reported, disclose this reproducibility limit, and make no code-release claim.","We retain the original values as reported and disclose this reproducibility limit. Recoverable code is now supplied with the bounded source/component checks below; a complete historical training replay remains unverified.")
    (ROOT/"Supplementary_round_015.tex").write_text(supplement)

    reply=(parent/"Response_to_Reviewers_round_014.md").read_text().replace("round_014","round_015")
    reply=reply.replace("No validated quantitative seam endpoint or PBR-fidelity claim is made.","We additionally replay the shared-UV incoming-camera RGB variance: all 80 archived values reproduce exactly, and known-color controls check its formula/path. Late-high minus Fixed Mean is -0.002448 (descriptive 95% interval [-0.003473,-0.001604]; additional exploratory Holm21 p=0.041). Fixed High has lower disagreement yet higher baked LPIPS than Late-high. A shared constant-black control has zero variance, so consistency alone does not establish fidelity. Natural texture, resampling and UV overlap remain contributors. No validated quantitative seam endpoint or PBR-fidelity claim is made.")
    reply=reply.replace("Views and seeds are averaged within object; they are not independent samples.","Native-interface and bake views, and GSO seeds, are averaged within object; Fresh C's image endpoints are computed once on its six-view composite. They are not independent samples.")
    reply=reply.replace("We cannot claim a complete FAC training replay or substitute the later new geometry-training studies for FAC reproduction.","We now supply a separate byte-preserved FAC source archive, including two distinct recovered training entries, their configuration/dependency files and per-file hashes. The earlier entry needs an explicit flag to freeze the base adapter; the later one is controller-only. Their controller source is byte-identical; three distinct standalone CPU controller fixtures pass forward, gradient-path and state-roundtrip checks. These do not authenticate the historical executed source/CLI or establish isolated full-model replay. We cannot claim a complete FAC training replay or substitute the later new geometry-training studies for FAC reproduction.")
    reply=reply.replace("These comparisons produce quantitative operating-point conclusions that differ from the original C3 recommendation.","New post-inspection analyses also quantify objectwise limits. In Fresh C, at least one other tested control weakly dominates C3 on all four recorded point-estimate endpoints for 270/300 objects; this is neither resolved per-object superiority nor material quality. GSO100 Late--Mean PSNR is positive on average at all three fixed seeds, while only 27/100 objects improve at every seed and 68/100 have mixed/tied signs. Nonreference LPIPS changes average direction across seeds, and only 1/20 GSO bake objects improves at all three. These findings distinguish small average effects from repeatable objectwise benefit, retaining all seeds and outcomes. Together with the new incoming-view diagnostic, these comparisons produce quantitative operating-point conclusions that differ from the original C3 recommendation.")
    reply=reply.replace("The delivered README distinguishes verified recomputation, available inference records and the missing historical training artifacts.","The delivered README distinguishes verified recomputation, recovered code/component execution, available inference records and missing historical training artifacts. The new Supplement S7 and source audit give the explicit executed-test scope and source-entry differences.")
    (ROOT/"Response_to_Reviewers_round_015.md").write_text(reply)
    print("Integrated validated gap-closing evidence; inherited facts unchanged.")


if __name__=="__main__":
    main()
