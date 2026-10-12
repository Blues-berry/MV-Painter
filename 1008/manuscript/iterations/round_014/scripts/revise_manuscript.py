"""Author the independent round014 manuscript from its frozen parent."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "history/round_013"
TITLE = ("Timestep-Conditioned Adapter Scaling for Multi-view Diffusion "
         "Texture Generation: A Controlled Empirical Study")
MAP = {1:9, 2:2, 3:2, 4:1, 5:3, 6:5, 7:5, 8:1, 9:7, 10:7,
       11:7, 12:7, 13:6, 16:2, 17:3, 18:5, 19:5, 20:5, 21:6,
       22:6, 23:6, 24:6, 25:6, 26:8, 27:8, 28:8, 29:8, 30:8, 31:4, 32:7, 33:4}


def remap(text):
    text = text.replace("Supplementary Table~S16", "Supplementary Section~S11")
    text = text.replace("Supplementary Table S1", "Supplementary Section S1")
    text = text.replace("Supplementary Table~S1", "Supplementary Section~S1")
    text = text.replace("Supplementary Figure~S1", "the retained RGB displays in Supplementary Section~S1")
    text = text.replace("Supplementary Figure~S2", "the complete bake displays in Supplementary Section~S18")
    text = text.replace("Supplementary Table~S12", "the MVDiffusion contrast tables in Supplementary Section~S5")
    pattern = r"(?:Supplementary |Supplement )?Sections?(?:~| )S(\d+)(?:--S(\d+))?"
    def replace(match):
        a = MAP[int(match[1])]
        b = MAP[int(match[2])] if match[2] else a
        return f"Supplementary Section~S{a}" if a == b else f"Supplementary Sections~S{a} and S{b}"
    return re.sub(pattern, replace, text)


def block(text, start, end, replacement):
    assert text.count(start) == text.count(end) == 1, (start, end)
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement + "\n\n" + text[b:]


def main():
    source = (PARENT / "manuscript_round_013.tex").read_text()
    text = remap(source)
    text = text.replace(r"\usepackage{lineno}", r"\usepackage[switch]{lineno}")
    text = text.replace(r"\usepackage{placeins}", r"\usepackage{placeins}" + "\n" + r"\setlength{\emergencystretch}{2em}")
    text = text.replace(
        r"\title{Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation}",
        r"\title{" + TITLE + "}")
    abstract = r"""\begin{abstract}
Geometry-conditioned multi-view diffusion provides an inference-time strength control, but its practical effect depends on temporal allocation, the conditioning interface, and the evaluated output. We conduct a controlled empirical study of Timestep-Conditioned Adapter Scaling (TCAS), carrying forward the historical middle-high profile C3 without further schedule selection. On 300 held-out objects with a frozen retrained GeoTex checkpoint, C3 improves foreground PSNR by 0.52 dB over fixed low, while competitive fixed and linear controls have better means on all four image endpoints. Matching applied-scale budgets changes the interpretation: C3 is 0.13 dB below fixed mean and 0.56 dB below late-high. Native MV-Adapter studies on 50 Fresh C inputs and 100 GSO objects detect endpoint-specific stage effects but do not detect the primary middle-window benefit over fixed mean. A ten-object native-UV bake pilot finds a small late-high LPIPS reduction of 0.00265 on unseen views; a separate twenty-object GSO evaluation with revised calibration does not detect this benefit. Generated-view and baked-output method rankings remain positively associated, although the preferred point estimates often differ. These findings quantify the effects and limits of geometry-control allocation and provide application-specific evidence for evaluating operating points. They support neither a universally preferred schedule nor physically faithful materials.
\end{abstract}"""
    text = block(text, r"\begin{abstract}", r"\begin{keyword}", abstract)
    intro = r"""\section{Introduction}
\label{sec:intro}

Multi-view diffusion generates images that are projected onto a 3D mesh to form a texture. Geometry conditions help align the images with a known surface, while a reference image supplies appearance. The strength of geometric injection is an accessible inference-time control. Choosing it is an application decision: better generated-view agreement is useful only to the extent that the resulting textured asset retains appropriate appearance under the evaluation views.

The difficulty is that strength, temporal allocation and the final evaluation endpoint can change together. A schedule compared with a weaker constant may simply inject a larger scalar budget. A wrapper may cap some requested scales, leaving a different applied profile. A generated-view metric can also improve while color errors remain visible, and baking adds sampling and coverage losses. Establishing the value of a setting therefore requires competitive controls and actual textured-mesh evaluation.

We study these questions through Timestep-Conditioned Adapter Scaling (TCAS), an intervention on an existing GeoTex-Adapter residual interface. C3, the low--high--low profile recorded in the original development study, is retained without another selection search. Scheduling strength across time or layers is established prior work, including geometry-conditioning schedules in Scheduled Style Injection (SSI) \cite{kulkarni2026ssi}. Here the contribution is the quantitative evidence for geometry-guided multi-view texturing under stated interfaces and protocols.

The complete comparisons change the original practical recommendation. On 300 held-out objects, C3 improves over fixed low but loses to competitive fixed and linear controls. At equal applied-scale sums, fixed mean and late-high outperform its middle window. Native MV-Adapter evaluations on fifty Fresh C inputs and one hundred GSO objects do not detect the primary middle-window advantage, although some secondary stage effects are measurable. Actual baking finds a small late-high benefit on ten compatible GeoTex objects and no detected LPIPS benefit on a separate twenty-object GSO cohort. These findings delimit when an allocation result has application value.

The contributions are:

(1) \textbf{A controlled assessment of strength and temporal allocation.} Matched comparisons with competitive fixed and linear controls distinguish the recorded C3 intervention from a timing-only interpretation. Equal per-group applied sums identify stage-allocation total effects within the frozen GeoTex pipeline.

(2) \textbf{An application-level evaluation of those effects.} Actual native-UV meshes, matched-resolution GT self-bakes and eleven unseen cameras quantify small local gains, persistent appearance errors and changes in the preferred operating point. Both the ten-object gain and the twenty-object non-detection are reported.

(3) \textbf{An evaluation of interface and protocol boundaries.} Native MV-Adapter matrices and retained MVDiffusion results test related allocation questions on different conditioning operators. They reveal endpoint-dependent effects and limits to transfer, without pooling cohorts or claiming a common residual dose.

Object-level records and runnable analyses support these findings. TCAS remains the study intervention and C3 a historical operating point; neither the scheduling concept nor the existence of an audit archive is presented as an independently new algorithm."""
    text = block(text, r"\section{Introduction}", r"\section{Related Work}", intro)
    text = text.replace(
        "The GeoTex-Adapter path in the 01549 study already exposes",
        "The studied GeoTex-Adapter path already exposes")
    text = text.replace(
        "The native temporal comparison is summarized in Table~\\ref{tab:new-mva}; the complete historical panels are retained in Supplementary Section~S3 and S32.",
        "The native temporal comparisons are summarized in Tables~\\ref{tab:new-mva} and \\ref{tab:interface-effects}; historical panels remain in Supplementary Section~S3.")
    text = text.replace(
        "Fresh C evaluates target-view images; the separate ten-object pilot evaluates calibrated unlit baked meshes.",
        "Fresh C evaluates generated target views; the ten-object GeoTex pilot and twenty-object GSO evaluation separately assess unlit baked meshes.")
    text = text.replace(
        "used here to illustrate the interface. Conceptual artwork",
        "used here to illustrate the interface. This control schematic is not an end-to-end application result. Conceptual artwork")
    text = text.replace(
        "We use separate terms for separate outcomes.",
        "The endpoints describe different outcomes.")
    a = text.index("The first-round 01549 revision also reported")
    b = text.index(r"\section{Experiments}", a)
    text = text[:a] + r"""Previously reported Full Adaptive Correction (FAC) training is retained as an auxiliary negative result in Section~\ref{subsec:facreported}. It is distinct from the frozen inference interventions evaluated here.

The recorded analysis and display code uses fixed object-level inputs and the original comparison families. Actual experimental images are preserved without appearance retouching. Software identities and the AI-assistance disclosure are supplied with the reproduction materials.

""" + text[b:]

    setup = r"""\subsection{Study Cohorts, Sampling and Statistical Units}
\label{subsec:setup}

Table~\ref{tab:study-design} separates the studies and their evidence classes. Fresh C contains 300 UIDs disjoint from the historical schedule-selection/evaluation pool, the recorded 1,118-object training list and the earlier clean-v2 evaluation list. Its primary four-condition comparison uses one frozen controlled-retraining checkpoint, shared inputs and per-object seeds. It does not reproduce the historical adapter's reported $+0.96$ dB estimate. The original checkpoint's exact identity remains unavailable.

\begin{table*}[t]
\centering\scriptsize\setlength{\tabcolsep}{3pt}
\caption{Studies, implemented protocols and evidence scope. Rows are studies rather than disjoint populations: the bake pilots and some interface tests reuse image-study inputs. Object is the statistical unit; views and seeds are nested within object.}
\label{tab:study-design}
\begin{tabular}{p{0.16\textwidth}p{0.23\textwidth}p{0.20\textwidth}p{0.32\textwidth}}
\toprule Study / objects & Interface and sampling & Endpoint & Selection and scope \\
\midrule
Fresh C / 300 & Capped GeoTex residual; 256 pixels; 50 Euler steps; conditional-only prediction; cached image features & Six target-view foreground endpoints & UID-disjoint held-out cohort; original primary C3--GFL frozen; linear and equal-budget comparisons are same-cohort addenda \\
GeoTex bake / 10 & Same controlled generator; six 256-pixel bake cameras; native UVs & Eleven unseen unlit views & Input/compatibility-selected subset; primary Late--Mean specified before new bake outcomes; two later native controls exploratory \\
MV-Adapter / 50 & Native condition-guider features; 512 pixels; 50 steps; CFG 3 & Six native-camera target views & Fresh C inputs not previously viewed through this interface; input-only selection; thirteen legal white targets retained \\
GSO / 100 & Native MV-Adapter; 512 pixels; 50 steps; CFG 3; three seeds & All-six PSNR primary; five nonreference LPIPS secondary & Source-ordered convenience cohort; four inherited profiles frozen after earlier baseline exposure; external sensitivity \\
GSO bake / 20 & Same fixed GSO inputs; native UVs; three seeds & Eleven unseen unlit views & Revised GT-only calibration after fifteen original outcomes; full twenty retained; no GT-error subtraction \\
Reference-protocol / 50 & New frozen GeoTex checkpoint; native reference conditions; 512 pixels; 50 steps; CFG 2 & Five nonreference views & Supporting protocol/checkpoint sensitivity on previously studied inputs; not another independent backbone \\
MVDiffusion / 75 & Partial correspondence-block control; depth concatenation unscaled & Recorded six-view endpoints & Retrospective third-interface panel; narrow native-mirror identity check; not exact GeoTex operator transfer \\
\bottomrule
\end{tabular}
\end{table*}

Within each comparison, object inputs, targets, initialization and endpoint code are shared. Fresh C uses seed $42+\texttt{object\_idx}$, held constant across conditions for that object. Its capped residual groups have deep/middle/shallow limits of 3.0/3.5/0.8. MV-Adapter uses a different feature injection operator and numerical scale range; its native target cameras and actual default-path identity are checked separately. Scale labels are not common physical doses across interfaces.

Fresh C's controlled sampler differs from the complete base pipeline, which uses online image features, classifier-free guidance and 512-pixel views. Constant 1.0 under the GeoTex caps also differs from the unset-scale residual branch. We therefore name these controls by their executed configuration. The source records and sampling/default-path diagnostics are in Supplementary Sections~S1 and S6.

FG-PSNR, LPIPS, SSIM and Edge-SSIM measure agreement on the named image regions. Baked evaluation renders actual exported meshes; unlit base color does not establish PBR or material fidelity. Views are averaged within object, with GSO sampling seeds also averaged within object. Paired intervals resample objects and are pointwise 95\% intervals. Preserved primary, secondary and exploratory families use their stated Holm adjustments; the distinct families do not imply one overall experiment-wide error guarantee. Non-detection is not equivalence or non-inferiority. Complete comparison rules are supplied in Supplementary Sections~S2--S5."""
    text = block(text, r"\subsection{Experimental Setup}", r"\subsection{Development origin and historical scope}", setup)
    text = text.replace(
        "The submitted 01549 study selected C3",
        "The historical study selected C3")
    text = text.replace("Supplementary Section~S7 and S32", "Supplementary Section~S7")

    results = r"""\subsection{Competitive Controls and Matched Temporal Allocation}
\label{subsec:largescale}

The registered Fresh C primary is C3 minus Fixed Low (GFL) FG-PSNR. The paired gain is $+0.52$ dB (95\% interval $[+0.40,+0.64]$), with 206/300 objects favorable. All conditions use the same frozen retrained checkpoint and object inputs. This gain combines increased strength and temporal allocation: C3's deep/middle applied sums are 82.5 each, versus 62.5 for GFL, while both have shallow sum 40.

\begin{table*}[t]
\centering\scriptsize\setlength{\tabcolsep}{4pt}
\caption{Fresh C competitive-control means on the same 300 objects. Early/Middle/Late-high and Fixed Mean share exactly the same per-group applied sums. The equal-budget study is a post-inspection addendum, not a second holdout. Each budget entry for deep/middle applies separately to both groups. $^\dagger$Generic Linear is a competitive same-cohort addendum, not part of the matched-budget family; its budget is not asserted to match.}
\label{tab:freshc-absolute}\label{tab:matched-budget300}
\begin{tabular}{lrrrrrr}
\toprule Control & Deep/middle sum & Shallow sum & FG-PSNR$\uparrow$ & FG-LPIPS$\downarrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ \\
\midrule
\input{tables/matched_controls014.tex}
\bottomrule
\end{tabular}
\end{table*}

Competitive controls change the recommendation. Fixed High has better means than C3 on all four endpoints: C3 minus Fixed High is $-0.748$ dB FG-PSNR (pointwise interval $[-0.885,-0.609]$), with FG-SSIM difference $-0.04553$ ($[-0.04937,-0.04167]$). Generic Linear also has better means on all four; C3 minus Generic Linear is $-0.593$ dB ($[-0.837,-0.351]$). Its positive median of $+0.074$ dB and 155/300 favorable objects show why mean and object-level distributions must both be considered. Complete original paired endpoints and their comparison families are in Supplementary Section~S2.

\paragraph{Equal applied budgets.}
\label{subsec:matched-budget300}
Early-, middle-, and late-high move the same sixteen high steps to updates 0--15, 17--32, and 34--49. Deep/middle low and high are 1.25 and 2.50; shallow stays at its 0.8 cap. Fixed Mean uses 1.65 before the cap. Each allocation therefore has per-group sums $(82.5,82.5,40)$. The completed six-condition matrix contains 1,800 paired rows with common-input and seed checks.

C3 minus Fixed Mean is $-0.133$ dB (pointwise interval $[-0.170,-0.096]$); C3 minus Late-high is $-0.559$ dB ($[-0.625,-0.493]$). C3 also trails both on LPIPS, FG-SSIM and Edge-SSIM. It improves over Early-high by approximately 0.50 dB. Within these six conditions Fixed High wins FG-PSNR on 172 objects, Late-high on 64, and C3 on none; this is an endpoint-specific count, not a universal quality ranking.

The equal-budget comparison identifies an allocation total effect. Evolving residual amplitudes remain trajectory-dependent, preventing a residual-dose-independent mechanism interpretation. Late-high is not universally preferred: Fixed Mean has higher FG-SSIM, and Generic Linear is a strong unmatched-budget practical control. The historical LLH layer/time addendum and complete object distributions remain in Supplementary Section~S2."""
    fact = json.loads((ROOT / "data/FACTS_round_014.json").read_text())["facts"]["matched_middle_late"]
    results = results.replace("-0.559", f'{fact["mean"]:+.3f}').replace(
        "-0.625,-0.493", f'{fact["ci95"][0]:+.3f},{fact["ci95"][1]:+.3f}')
    anchor = source.index(r"\label{fig:c3compare}")
    figure_start = source.rfind(r"\begin{figure*}", 0, anchor)
    figure_end = source.index(r"\end{figure*}", anchor) + len(r"\end{figure*}")
    results += "\n\n" + remap(source[figure_start:figure_end]) + "\n" + r"\FloatBarrier"
    text = block(text, r"\subsection{Large-Scale Matched Image-Space Evaluation}", r"\subsection{Appearance and Color Failure Analysis}", results)

    # Retain color failures while moving process-level traces and old pilots to the Supplement.
    a = text.index("A locked P0 trace reproduced")
    b = text.index(r"\paragraph{Fresh C full-object and same-ROI examples.}", a)
    text = text[:a] + r"""LLH--GFL increased mean CIEDE2000 while reducing foreground gradient magnitude, high-frequency energy and color entropy. Lower variation therefore did not imply closer reference appearance. The denoising/runtime isolates and three failed correction candidates remain in Supplementary Section~S6; they localize observations but do not validate a cause or repair.

Historical twenty-object results, the earlier five-object bake, invalidated camera/mask attempts and the corrected REPEAT sampler are reported separately in Supplementary Section~S5. They are not pooled with the new ten-object cohort. The actual unset-scale GeoTex residual branch differs from Constant 1.0 (capped), so the latter is not labeled an unmodified pipeline.

""" + text[b:]
    a = text.index(r"\paragraph{Fresh C full-object and same-ROI examples.}")
    b = text.index(r"\subsection{Calibrated Baked Appearance on New Objects}", a)
    retained = text[a:b]
    assert retained.count(r"\includegraphics") == 1
    (ROOT / "sections/retained_weak_control_display014.tex").write_text(
        r"\subsection*{Retained C3--Fixed Low favorable and adverse examples}" + "\n" +
        retained[retained.index(r"\begin{figure*}"):].replace(r"\begin{figure*}", r"\begin{figure}").replace(
            r"\end{figure*}", r"\end{figure}").replace(r"\label{fig:qualitative}", r"\label{fig:supp-primary-examples}"))
    text = text[:a] + r"""\paragraph{Full-object evidence and its selection.}
The strong-fixed and Generic Linear examples in Figure~\ref{fig:c3compare} and the color failure in Figure~\ref{fig:color-failure} use common framing and exact shared pixel crops. Favorable/adverse C3--GFL examples are retained in Supplementary Section~S9. Outcome-selected displays illustrate behavior, not prevalence. The unrecoverable historical texture audit's 92\% prevalence claim and its texture-loss classifications are withdrawn; variation statistics alone would not validate fidelity even if their lineage were complete.
\FloatBarrier

""" + text[b:]
    text = text.replace(r"\subsection{Calibrated Baked Appearance on New Objects}",
                        r"\subsection{Actual Baked Appearance: Local Benefit and External Limits}")
    text = text.replace(
        "Their mapping to the original submitted panels cannot be recovered;",
        "Their mapping to the original submitted panels cannot be recovered;")

    # Add the complete second application cohort beside the ten-object gain.
    marker = r"\paragraph{Exploratory native residual controls.}"
    external_bake = r"""\paragraph{Separate twenty-object GSO evaluation.}
The GSO/MV-Adapter study completes twelve conditions by three seeds on twenty fixed inputs, plus twenty matched GT self-bakes: 740 unique baked meshes and 8,140 unseen-view records. The objects, source meshes, projection cameras, texture resolution and eleven unseen cameras are shared across controls; unseen cameras do not contribute to baking.

The original attempt stopped after fifteen objects because a discontinuous UV-ramp diagnostic failed on a Hair Dryer. Subsequent GT-only tests identify finite-resolution mixing across UV jumps and validate continuous nonlinear surface-color fields, an independent multi-island analytic fixture, and a deliberate image-flip negative control. The resulting calibration addendum is post hoc. It keeps projection, masks, cameras, material semantics, resolutions and the fixed twenty objects unchanged; all 375 original GLB hashes and metric records reproduce exactly. The original failure and remaining UV/coverage limitations are retained in Supplementary Section~S4.

Late-high minus Fixed Mean unseen-view LPIPS is $+0.000084$ (pointwise interval $[-0.000103,+0.000286]$; original comparison-family Holm $p=0.788$). This study does not detect the ten-object pilot's benefit. It changes both input domain and conditioning/projection protocol, so it is neither a direct same-protocol replication nor evidence assigning the difference to backbone alone. Table~\ref{tab:bake-cohorts} presents both application comparisons.

\begin{table*}[t]\centering\scriptsize\setlength{\tabcolsep}{4pt}
\caption{Late-high minus Fixed Mean on unseen-view foreground LPIPS. Lower is favorable. All views/seeds are nested within object. The ten-object specified primary uses its original exact sign-flip test; GSO uses the original Holm16 comparison family. Pointwise intervals are not simultaneous. The two cohorts and protocols are not pooled.}
\label{tab:bake-cohorts}
\begin{tabular}{lrrrrl}
\toprule Study & Objects & Fixed Mean & Late-high & Paired difference [95\% CI] & Test \\
\midrule
GeoTex compatibility pilot & 10 & 0.1303 & 0.1277 & $-0.002652\ [-0.004144,-0.001367]$ & exact $p=0.00195$ \\
GSO revised-calibration study & 20 & 0.10089 & 0.10098 & $+0.000084\ [-0.000103,+0.000286]$ & Holm $p=0.788$ \\
\bottomrule\end{tabular}\end{table*}

Across all twelve GSO conditions, mean within-object image/bake LPIPS-rank correlation is 0.601 (object interval $[0.440,0.733]$). A post hoc sensitivity restricted to the seven original scale/time controls gives 0.396 ($[0.175,0.582]$), with the minimum-mean LPIPS condition changing on 11/20 objects. These are positively associated rankings with changing point-estimate winners, not general rank reversal or statistically resolved winner changes. The GT self-bake has mean LPIPS 0.0602 and PSNR 19.36 dB; average complete-bilinear-footprint coverage is about 78.7\%. All foreground remains scored and GT errors are not subtracted. These losses contextualize the small method effects without defining a theoretical quality bound.

"""
    assert text.count(marker) == 1
    text = text.replace(marker, external_bake + marker)
    a = text.index(r"\paragraph{Exploratory native residual controls.}")
    b = text.index(r"\subsection{Transfer to other conditioning interfaces}", a)
    text = text[:a] + r"""\paragraph{Native controls and protocol sensitivity.}
Subsequently added Native residual and No Adapter outputs on the same ten GeoTex objects are exploratory. They retain matched geometry and GT coverage, and the repeated Constant 1.0 (capped) outputs are bitwise identical. Their apparent PSNR/LPIPS gains for the schedules do not separate under the fifteen-test exploratory family. The complete data are in Supplementary Section~S5.

A supporting fifty-object comparison uses a newly trained frozen GeoTex checkpoint with 512-pixel supervision, actual positive/negative reference conditions and CFG 2. Late-high minus Fixed Mean has nonreference PSNR $-1.184$ dB (interval $[-1.587,-0.849]$) and LPIPS $+0.00266$ ($[-0.00003,+0.00640]$; adjusted $p=0.080$). C3 has no corrected advantage over Fixed Mean or Fixed High. This previously studied cohort and changed checkpoint/protocol supply a sensitivity boundary, not an independent backbone confirmation. Training and full-v29 strong-baseline results remain in Supplementary Section~S8.

""" + text[b:]
    # The main native50 table and its complete primary/secondary results are retained.
    text = text.replace(
        "Targets are unlit native-camera albedo, not Fresh C's differently normalized reference renders.",
        "Targets are unlit native-camera base color, not Fresh C's differently normalized reference renders or certified physical albedo.")
    text = text.replace("white-albedo targets", "legal constant-white base-color targets")
    a = text.index(r"\paragraph{Additional condition-correction stress test.}")
    b = text.index(r"\subsection{First-round cluster-aware preference study}", a)
    text = text[:a] + r"""\paragraph{External-input native schedule comparison.}
The source-ordered GSO100 convenience cohort uses the same native MV-Adapter control path and three shared seeds. Native/Fixed High, Fixed Low, Fixed Mean, Early-high, Middle-high, Late-high and Generic Linear include the four inherited profiles frozen before their outputs, after earlier baseline exposure. The full dataset contains 3,600 generated cells and 21,600 view records, including three archived projection corrections and two separately frozen APG baselines \cite{sad2024apg}. The scheduling extension is external sensitivity, not pristine independent confirmation or parameter search.

The specified all-six-view Middle-high minus Fixed Mean primary is $-0.014$ dB (interval $[-0.031,+0.004]$; paired $p=0.122$). A secondary Late-high--Fixed Mean contrast is $+0.045$ dB ($[+0.024,+0.065]$; Holm83 $p=0.00335$), with SSIM $+0.00134$ (adjusted $p=0.000415$). Its five-nonreference-view LPIPS difference is $-0.000086$ ($[-0.000551,+0.000413]$; separate Holm21 $p=1$). Thus a small detected image effect does not establish a perceptual or baked-appearance benefit. Table~\ref{tab:interface-effects} and Figure~\ref{fig:allocation-effects} put these named comparisons in context.

\begin{table*}[t]\centering\scriptsize\setlength{\tabcolsep}{3pt}
\caption{Selected within-study paired effects. P: the specified primary, unadjusted within its study; S: secondary with its original family adjustment (GSO all-six Holm83, nonreference LPIPS Holm21, reference-protocol secondary Holm18). Intervals are pointwise. Native50 and GSO100 use different inputs/seed policies; the reference-protocol study also changes weights and sampling and is not a separate backbone.}
\label{tab:interface-effects}
\begin{tabular}{lllrrcr}
\toprule Study & Contrast & Endpoint & Mean & 95\% CI & Class & $p$ \\
\midrule
\input{tables/interface_effects014.tex}
\bottomrule\end{tabular}\end{table*}

\begin{figure*}[t]\centering
\includegraphics[width=\textwidth]{figures/fig_allocation_effects014.pdf}
\caption{Paired allocation effects from completed object-level records. Error bars are pointwise 95\% object intervals. Panel (a) uses six-view PSNR except the reference-protocol row, which excludes its reference view; panel (b) uses eleven unseen baked views. The GSO Late--Mean PSNR row is secondary and is explicitly distinguished from the specified middle-window questions. Different studies are shown separately, without pooling or cross-pipeline absolute-score ranking. The small GeoTex bake gain and GSO non-detection both remain visible.}
\label{fig:allocation-effects}
\end{figure*}

All fifteen specified GSO projection-minus-baseline nonreference-LPIPS comparisons favor the scale/APG baselines after their original separate Holm9/Holm6 corrections. The three projection candidates also lose to native on baked LPIPS in the retained twenty-object family. These valid negative auxiliary results are reported completely in Supplementary Sections~S4 and S8; they are not proposed as additional methods.

""" + text[b:]

    a = text.index(r"\subsection{First-round cluster-aware preference study}")
    b = text.index(r"\subsection{FAC controlled re-examination reported in 01549}", a)
    preference = text[a:b]
    (ROOT / "sections/historical_preference014.tex").write_text(
        preference.replace(r"\subsection{First-round cluster-aware preference study}",
                           r"\subsection*{Historical cluster-aware preference study}"))
    text = text[:a] + r"""\subsection{Historical Preference and Training Evidence}
\label{subsec:preference}
The original blinded 3AFC study on thirty objects and twenty-four participants reports C3's overall-quality share as 58.1\% (two-level participant/object-bootstrap interval $[50.1,65.8]\%$). This supports overall preference for the original stimuli, not texture fidelity, the retrained checkpoint or unseen baked appearance. Counts and endpoint-specific results are retained in Supplementary Section~S7.

""" + text[b:]
    a = text.index(r"\subsection{FAC controlled re-examination reported in 01549}")
    b = text.index(r"\FloatBarrier", a)
    text = text[:a] + r"""\paragraph{FAC re-examination.}
\label{subsec:facreported}
Previously reported FAC configurations all reduced FG-PSNR relative to TCAS in their stated controlled re-examination. The original training pool was reported as 1,706 objects, while a recovered configuration refers to 1,200; seed, checkpoint and sampled-run records are incomplete. The results and reproducible inference/statistical components are separated from this remaining training-replay gap in Supplementary Section~S7. Later new geometry training does not restore historical FAC identity.

""" + text[b:]

    discussion = r"""\section{Discussion and Limitations}
\label{sec:limitations}

\paragraph{What the controls establish.}
The Fresh C300 gain over fixed low supports the recorded intervention under its frozen protocol. It changes both budget and timing. The equal-applied-budget matrix then measures a timing-allocation total effect and changes the preferred image-space operating point. It does not identify a state-independent residual dose or an optimal middle window. Competitive fixed and linear controls are necessary before assigning practical value to a selected profile.

\paragraph{Application value and operating points.}
In the GeoTex image protocol, Fixed High and Generic Linear have stronger endpoint means than C3; equal-budget late-high trades higher PSNR and lower LPIPS against lower FG-SSIM than fixed mean. The ten-object bake's approximately 2\% LPIPS reduction closes only 3.7\% of the gap to the matched GT reference bake, while visible appearance errors remain. The separate GSO20 study does not detect that allocation benefit. Its post hoc calibration, GT self-bake loss and incomplete coverage are disclosed; a small image effect alone does not justify replacing an existing deployment setting.

Generated-view metrics remain informative: overall baked/image method rankings are positively associated. However, preferred point estimates often change, and the association is weaker when the GSO analysis is restricted to closely competing scale/time settings. Winner changes do not prove significant separation between methods or a general reversal. Actual baked evaluation and full-object reference comparison remain necessary.

\paragraph{Interface and protocol boundaries.}
Native MV-Adapter50 and GSO100 do not detect the primary middle-window advantage. The secondary GSO late-window PSNR change is statistically detectable but small, with no corresponding nonreference LPIPS benefit. The supporting reference-conditioned checkpoint shows a different Late--Mean direction. Historical MVDiffusion supplies a partial-operator boundary. Because weights, inputs, conditioning operators and sampling protocols differ, these studies cannot isolate one backbone or domain as the cause of the varying effects.

\paragraph{Quality, selection and replication limits.}
The bake studies favor compatible native-UV assets, and GSO uses a source-ordered convenience sample. They do not establish representative asset quality, physical albedo, PBR fidelity or a validated seam score. Views and seeds are nested within object, and seed repetitions do not estimate training-checkpoint variation. Separate test families and pointwise intervals retain their stated roles; non-detection is not equivalence.

Fresh C uses retrained weights and a controlled sampler rather than the authenticated historical main adapter or complete default pipeline. The old $+0.96$ dB contrast is not reproduced, and historical FAC training records remain incomplete. The original preference study concerns its own stimuli. These limitations constrain deployment and replication claims, while the matched within-protocol comparisons remain valid.

\section{Conclusion}
\label{sec:conclusion}

Geometry-control allocation changes generated-view agreement, but its effects depend on the tested interface, protocol and endpoint. The matched 300-object study shows that C3's gain over fixed low combines increased strength with timing; equal-budget fixed mean and late-high outperform the historical middle window. Native MV-Adapter studies do not detect the primary middle-window advantage, while some secondary image effects are small but measurable. Actual baking yields a limited late-high benefit on ten compatible GeoTex objects and no detected LPIPS benefit on a separate twenty-object GSO cohort. Method rankings are broadly associated across image and baked evaluation, yet their preferred operating points often differ. Competitive controls and application-level evaluation are therefore necessary when choosing a setting within a deployed pipeline. The results do not identify a universally preferred schedule or establish faithful material reproduction."""
    text = block(text, r"\section{Discussion and Limitations}", r"\section*{Data availability}", discussion)
    # Fix surviving parent section references and case-specific captions.
    text = text.replace("Supplementary Sections S9--S10 and S32", "Supplementary Section~S7")
    text = text.replace("Supplementary Sections S5 and S32", "Supplementary Section~S3")
    text = text.replace("Supplementary Sections S21--S30", "Supplementary Sections~S6 and S8")
    text = text.replace("Supplementary Section~S3 and S32", "Supplementary Section~S3")
    text = text.replace("Supplementary Table S1", "Supplementary Section~S9")
    text = text.replace("not a new 1008 training run", "distinct from the subsequent training diagnostics")
    text = text.replace("in Supplement S2", "in Supplementary Section~S2")
    text = text.replace("its budget is not asserted to match.", "its different group budgets are shown explicitly.")
    text = text.replace(
        "Generic Linear also has better means on all four;",
        "Generic Linear ramps deep/middle requests from 1.25 to 2.50 and shallow requests from 0.50 to 0.75 over the fifty steps. Its applied sums are (93.75,93.75,31.25), so it changes layer allocation and total budget as well as timing. It also has better means on all four;")
    text = text.replace("The registered Fresh C primary", "The internally specified Fresh C primary")
    # The source and data are author-review artifacts; never claim historical replay.
    text = text.replace(
        "Raw generated-image archives, trained checkpoints, source 3D assets whose redistribution rights are not established, and participant-level responses are not included.",
        "The complete raw generated-image archives, trained checkpoints, and participant-level responses are not included. Source assets must be acquired under their recorded licenses; the review evidence includes attributed displays and a small licensed GSO example export.")
    (ROOT / "manuscript_round_014.tex").write_text(text)
    print("Round014 main authored from frozen parent; weak-control figure and preference table retained in Supplement.")


if __name__ == "__main__":
    main()
