#!/usr/bin/env python3
"""Legacy restoration generator; not the current package build entry point.

It reads the immutable source_01549 TeX and refuses to run if its SHA-256
differs from BASELINE_LOCK.json. The current deliverables are built with
build_revision_01549_restored.sh. Keep this script only for historical source
reconstruction; the locked hash guard prevents it from replacing a newer
active manuscript with a different generated body.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROOT = PROJECT_ROOT / "1008"
LOCK_PATH = ROOT / "manuscript" / "BASELINE_LOCK.json"
lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
source = PROJECT_ROOT / lock["authoritative_original_tex"]["path"]
target = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / lock["active_main_tex"]
ACTIVE_TARGET = PROJECT_ROOT / lock["active_main_tex"]
ACTIVE_SHA = next(
    item["sha256"] for item in lock["active_revision_sources"]
    if item["path"] == lock["active_main_tex"]
)
sys.path.insert(0, str(PROJECT_ROOT / "1008" / "manuscript"))
from verify_baseline_lock import verify as verify_baseline_lock

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

expected = lock["authoritative_original_tex"]["expected_sha256"]
if not verify_baseline_lock():
    raise SystemExit("Baseline verification failed; no files written.")
if sha256(source) != expected:
    raise SystemExit("Protected 01549 source hash mismatch; no files written.")
if not target.exists():
    raise SystemExit("The explicit active revision path does not exist.")
active_target = target.resolve() == ACTIVE_TARGET.resolve()
if active_target and sha256(target) != ACTIVE_SHA:
    raise SystemExit("Active TeX differs from its lock hash; refusing to overwrite it.")

text = source.read_text(encoding="utf-8")

def replace_once(old, new, label="replace_once"):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}: {old[:160]!r}")
    text = text.replace(old, new, 1)

def replace_between(start, end, new, label="replace_between"):
    global text
    left = text.find(start)
    right = text.find(end, left + len(start))
    if left < 0 or right < 0:
        raise SystemExit(f"{label}: section boundary not found ({start!r} -> {end!r})")
    text = text[:left] + new.rstrip() + "\n\n" + text[right:]

replace_once(
    r"\newtheorem{proposition}{Proposition}" + "\n" + r"\newtheorem{remark}{Remark}" + "\n",
    "",
    "retire CAI theorem declarations",
)

replace_between(
    r"\begin{abstract}",
    r"\end{abstract}",
    r"""\begin{abstract}
Inference-time geometry adapters can improve the alignment of generated views to a 3D shape, but their residual scale also changes the image-space appearance produced by a multi-view diffusion pipeline. This paper studies Timestep-Conditioned Adapter Scaling (TCAS), a training-free, piecewise scale profile for an existing geometry-adapter path. The submitted 01549 manuscript records C3 $=(1.25,2.50,1.25)$ as the choice from a 24-object, 17-variant development probe; because its row-level outputs and selection-time provenance are incomplete in the current evidence archive, we treat that choice as historical development evidence rather than a verified optimum. A revision-era, matched image-space study on 300 objects finds that C3 exceeds global fixed-low scaling (GFL) by $0.522352$~dB in the registered FG-PSNR comparison (95\% object-bootstrap CI $[0.404160,0.640669]$). The same cohort also gives counter-results: global fixed-high scaling (GFH) and Generic Linear have more favorable means than C3 on all four reported endpoints. Requested scales, native caps, and post-scale residual magnitudes are distinct implementation quantities. Additional stage-placement and layer-window analyses indicate sensitivity to the tested intervention, but do not establish a dose-independent mechanism or a universally preferred schedule. Fresh C measures rendered images only; it does not validate baked textures, seams, PBR appearance, or human preference.
""",
    "abstract",
)

replace_once(
    "This problem is related to, but not solved by, existing guidance scheduling strategies. CFG scheduling changes the extrapolation between conditional and unconditional predictions, while a geometry adapter injects residuals into intermediate representations. Generic ControlNet or adapter scale scheduling similarly treats condition strength mainly as a condition-adherence knob. In texture generation, however, the key question is not only how strongly to follow the geometry, but also when geometric residuals should dominate and when they should recede so that the base model can synthesize color, material, and high-frequency texture. Simple monotonic schedules such as linear or cosine decay do not explicitly address this non-monotonic requirement. Even the recent finding that classifier-free guidance is most useful only in a limited noise interval \\cite{kynkanniemi2024limited} does not answer this question: it identifies where conditioning helps for CFG, but not which stages of a geometry-conditioned texture pipeline require strong geometric residuals, where the late-stage risk is texture suppression rather than diversity loss.\n\nThe goal of this paper is not to propose a new full texture generation system, but to analyze and improve inference-time adapter scaling within a fixed geometry-controlled multi-view diffusion pipeline.",
    r"""Scheduling control strength already has direct precedents. Classifier-free guidance scheduling changes the mixture of conditional and unconditional predictions, while Scheduled Style Injection (SSI) studies schedules across decoder layers and denoising time for style injection and also schedules geometry-conditioned ControlNet strength \cite{kynkanniemi2024limited,kulkarni2026ssi}. We therefore do not claim to introduce general layer-by-time scheduling. TCAS addresses a narrower task: the requested temporal profile of an existing geometry-adapter residual in a multi-view texturing pipeline, with the adapter wrapper's native execution semantics made explicit.

The goal of this paper is to examine this inference-time control problem within a fixed geometry-conditioned multi-view diffusion pipeline. The evidence is limited to image-space outcomes in the tested MVPainter-style system; downstream texture baking is shown as pipeline context, not as a validated outcome.""",
)

replace_once(
    "In multi-view texture generation, however, stronger adapter scaling is not necessarily better. Texture generation requires not only contours and structures to be consistent with geometry, but also surface color variations, material details, and high-frequency patterns to be preserved. Overly strong geometric control may force the model to follow normal, depth, or edge conditions too aggressively, thereby suppressing the intrinsic texture synthesis capability of the base diffusion model. In this case, some structural metrics may still improve, while the visual result suffers from texture flattening, reduced color variation, and detail loss.",
    """Changing adapter strength can alter both structural and appearance-related image measurements, but the direction and visual consequence depend on the adapter, its wrapper, and the residuals being scaled. The submitted paper reported texture flattening under some high-scale settings; because its underlying audit records are incomplete, this revision does not treat that pattern or its frequency as a verified general result. This motivates keeping structural scores, signal similarity, and texture-variation diagnostics distinct, and evaluating the actual pipeline with matched comparisons.""",
)

replace_between(
    r"\section{Related Work}",
    r"\section{Method}",
    r"""\section{Related Work}
\label{sec:related}

\subsection{3D Texture Generation and Multi-view Diffusion}
\label{subsec:3dtex}

Single-image 3D generation is often decomposed into geometry generation and texture generation. Single-image-to-3D, multi-view diffusion, and sparse-view reconstruction methods have improved structural stability and view synthesis \cite{liu2023zero1to3,shi2023zero123pp,liu2023syncdreamer,long2023wonder3d,shi2024mvdream,wang2023imagedream,xu2024instantmesh,ke2024era3d}. Texture synthesis remains a distinct challenge for asset realism and usability \cite{perla2026survey}. Many systems generate RGB views with 2D diffusion and project or bake them onto a surface \cite{chen2023text2tex,richardson2023texture,poole2023dreamfusion,chen2023fantasia3d}. Recent work also explores exemplar-based texture synthesis and diffusion-based procedural materials \cite{guzman2026adaptive,lv2025interpretable}.

Paint3D, MVPaint, Hunyuan3D 2.0, and MVPainter use geometry-conditioned multi-view generation in 3D texturing pipelines \cite{zeng2024paint3d,cheng2024mvpaint,lai2025hunyuan3d,shao2025mvpainter}. MV-Adapter and synchronized multi-view methods address multi-view consistency through different adapter and denoising designs \cite{huang2024mvadapter,liu2024synchronized,xu2026wondertex}. These systems establish the graphics context for this work. The present evidence does not compare final baked-texture quality across those systems.

\subsection{Adapter-Augmented Diffusion Models and Geometric Control}
\label{subsec:adapter}

T2I-Adapter and ControlNet inject spatial conditions into pretrained diffusion models through controllable branches \cite{mou2023t2iadapter,zhang2023controlnet}. IP-Adapter introduces image prompts through decoupled attention \cite{ye2023ipadapter}; LoRA and related methods use scaled low-rank updates \cite{hu2022lora,liu2024dora,zhang2023adalora}. These methods establish condition and residual scaling as common implementation controls. TCAS does not introduce adapter conditioning or a new multi-view backbone; it studies a requested scale on the existing GeoTex-Adapter residual path.

\subsection{Diffusion Guidance Scheduling and Timestep Control}
\label{subsec:guidance}

Diffusion denoising is often discussed in terms of coarse-to-fine evolution, and prior work varies guidance strength over sampling progress to study quality, diversity, or fidelity \cite{ho2020ddpm,song2021ddim,ho2022cfg,castillo2023adaptive}. Limited-interval classifier-free guidance is one example; it changes the combination of conditional and unconditional score predictions \cite{kynkanniemi2024limited}.

Scheduled Style Injection (SSI) is the closest scheduling precedent: it schedules style injection across decoder layers and denoising time and also studies schedules for geometry-conditioned ControlNet strength \cite{kulkarni2026ssi}. Thus, layer-by-time conditioning schedules and time-varying geometry control are established ideas. TCAS is narrower: it applies a three-stage requested multiplier to the GeoTex-Adapter residual in a multi-view texture-generation pipeline. The paper evaluates that task-specific intervention and its implementation boundaries; it does not claim a new general scheduling primitive or first use of layer/time control. SSI and TCAS use different models, interventions, datasets, and endpoints, so their quantitative results are not directly comparable.""",
)

replace_once(
    "The diffusion denoising process is stage-dependent: early steps mainly establish the global layout and coarse contours; middle steps refine geometric structure and cross-view alignment; late steps are more responsible for color, material, and local texture synthesis. Based on this observation, we propose Timestep-Conditioned Adapter Scaling (TCAS), which replaces a globally fixed adapter scale with a stage-dependent scale function. TCAS is not intended as a generic smooth guidance schedule. Its low-high-low form encodes the adapter-specific hypothesis that geometry residuals should be strongest only after coarse structure becomes stable and before late texture synthesis dominates.",
    """TCAS replaces a globally fixed requested adapter scale with a piecewise profile over normalized sampling progress. The early/middle/late partition is an operational description, not a universal claim about the function of every denoising stage. C3's low--high--low profile is the specific development choice evaluated in this revision; it is not presented as an independently derived optimum.""",
)

replace_between(
    r"\subsubsection{Implementation and dataset details}",
    r"\paragraph{Statistical reporting}",
    r"""\subsubsection{Implementation and dataset details}

Fresh C uses the frozen MVPainter-style joint six-view latent UNet and VAE with the GeoTex-Adapter checkpoint \texttt{geotex\_refattn\_v1/geotex\_step\_0002000.pt}. It uses the Euler discrete scheduler for 50 denoising steps, a shared seed of 42 within each matched comparison, and six target views per object. The 300-object cohort manifest, per-condition row counts, input hashes, and metric outputs are indexed in the Supplementary reproduction map. The primary run has 1,200/1,200 expected condition rows; the same-cohort Generic Linear/LLH addendum has 600/600 rows.

Fresh C's native wrapper caps are deep 3.0, middle 3.5, and shallow 0.8. The recorded scale request, applied value, and post-scale residual norm are separate fields. The requested C3 profile is $(1.25,2.50,1.25)$; its shallow value is clipped to 0.8 in this run. The Generic Linear and LLH addendum conditions are separately defined and do not equalize realized residual dose. Detailed step- and layer-group records are supplied in the Supplement.

FG-PSNR, FG-LPIPS, FG-SSIM, and Edge-SSIM are computed per object after averaging the six target views. The registered primary comparison is C3--GFL FG-PSNR; secondary and addendum tests follow their locked comparison families as documented in Supplementary Section S2. The original 50-object sweep and 24-object probe used separate historical records whose complete current row-level lineage is unavailable, so the implementation details of those runs are not inferred from Fresh C.""",
)

replace_between(
    r"\subsection{Shape-Texture Diagnostic Metrics}",
    r"\subsection{Timestep-Conditioned Adapter Scaling}",
    r"""\subsection{Image-Space Metrics and Texture-Variation Diagnostics}
\label{subsec:metrics}

We distinguish structure and signal-similarity measures from texture-variation proxies. FG-SSIM, Edge-SSIM, and Crop-SSIM quantify structural similarity on the indicated image regions; PSNR measures pixel error; LPIPS compares learned image features \cite{wang2004ssim,zhang2018lpips}. These endpoints describe agreement with target-view renderings, not complete perceptual or material fidelity.

Laplacian variance, RGB standard deviation, and gradient magnitude can describe local high-frequency or color variation. For example, a foreground Laplacian statistic may be written as
\begin{equation}
M_{\mathrm{var}}=\operatorname{Var}\!\left(\operatorname{Lap}(I_{\mathrm{out}}\odot G_{\mathrm{mask}})\right),
\end{equation}
where $G_{\mathrm{mask}}$ is the foreground mask. A larger value is not necessarily better: detail, noise, repeated patterns, or artifacts can all increase local variation. We therefore do not interpret these proxies as texture fidelity or use them alone to claim that a schedule better preserves reference appearance.""",
)

replace_once(
    "This design follows three principles. First, the early stage uses a conservative scale to avoid disrupting global structure formation with strong geometric residuals. Second, the middle stage uses a higher scale to strengthen geometric constraints from normals, depth maps, and foreground contours. Third, the late stage reduces the scale again to prevent geometric residuals from suppressing color variation, material detail, and high-frequency texture synthesis. This non-monotonic schedule is therefore different from simply decaying or increasing the adapter strength across all timesteps. TCAS introduces no new parameters and does not modify the base model or adapter weights; it only replaces the scaling factor during inference, so its computational overhead is negligible.",
    """The low--high--low profile is a concrete inference-time intervention motivated by the submitted development analysis. Its stage interpretation is a task-specific hypothesis: early, middle, and late sampling may respond differently to geometry residuals. Fresh C evaluates the recorded profile against matched controls but does not prove that each stage has a universal functional role. TCAS adds no trained parameters and does not modify base-model or adapter weights; it replaces the requested scaling value during inference.""",
)

replace_between(
    r"\section{Related Work}",
    r"\section{Method}",
    r"""\section{Related Work}
\label{sec:related}

\subsection{3D Texture Generation and Multi-view Diffusion}
\label{subsec:3dtex}

Single-image 3D generation is often decomposed into geometry generation and texture generation. Single-image-to-3D, multi-view diffusion, and sparse-view reconstruction methods have improved structural stability and view synthesis \cite{liu2023zero1to3,shi2023zero123pp,liu2023syncdreamer,long2023wonder3d,shi2024mvdream,wang2023imagedream,xu2024instantmesh,ke2024era3d}. Texture synthesis remains a distinct challenge for asset realism and usability \cite{perla2026survey}. Many systems generate RGB views with 2D diffusion and project or bake them onto a surface \cite{chen2023text2tex,richardson2023texture,poole2023dreamfusion,chen2023fantasia3d}. Recent work also explores exemplar-based texture synthesis and diffusion-based procedural materials \cite{guzman2026adaptive,lv2025interpretable}.

Paint3D, MVPaint, Hunyuan3D 2.0, and MVPainter use geometry-conditioned multi-view generation in 3D texturing pipelines \cite{zeng2024paint3d,cheng2024mvpaint,lai2025hunyuan3d,shao2025mvpainter}. MV-Adapter and synchronized multi-view methods address multi-view consistency through different adapter and denoising designs \cite{huang2024mvadapter,liu2024synchronized,xu2026wondertex}. These systems establish the graphics context for this work. The present evidence does not compare final baked-texture quality across those systems.

\subsection{Adapter-Augmented Diffusion Models and Geometric Control}
\label{subsec:adapter}

T2I-Adapter and ControlNet inject spatial conditions into pretrained diffusion models through controllable branches \cite{mou2023t2iadapter,zhang2023controlnet}. IP-Adapter introduces image prompts through decoupled attention \cite{ye2023ipadapter}; LoRA and related methods use scaled low-rank updates \cite{hu2022lora,liu2024dora,zhang2023adalora}. These methods establish condition and residual scaling as common implementation controls. TCAS does not introduce adapter conditioning or a new multi-view backbone; it studies a requested scale on the existing GeoTex-Adapter residual path.

\subsection{Diffusion Guidance Scheduling and Timestep Control}
\label{subsec:guidance}

Diffusion denoising is often discussed in terms of coarse-to-fine evolution, and prior work varies guidance strength over sampling progress to study quality, diversity, or fidelity \cite{ho2020ddpm,song2021ddim,ho2022cfg,castillo2023adaptive}. Limited-interval classifier-free guidance is one example; it changes the combination of conditional and unconditional score predictions \cite{kynkanniemi2024limited}.

Scheduled Style Injection (SSI) is the closest scheduling precedent: it schedules style injection across decoder layers and denoising time and also studies schedules for geometry-conditioned ControlNet strength \cite{kulkarni2026ssi}. Thus, layer-by-time conditioning schedules and time-varying geometry control are established ideas. TCAS is narrower: it applies a three-stage requested multiplier to the GeoTex-Adapter residual in a multi-view texture-generation pipeline. The paper evaluates that task-specific intervention and its implementation boundaries; it does not claim a new general scheduling primitive or first use of layer/time control. SSI and TCAS use different models, interventions, datasets, and endpoints, so their quantitative results are not directly comparable.""",
)

replace_between(
    "The main contributions of this paper are as follows:",
    r"\section{Related Work}",
    r"""The contributions are deliberately scoped to the submitted TCAS study and its revision-era evidence:

(1) We retain the original fixed-scale and schedule-selection questions and identify which reported development results can be retained only as historical diagnostics because the underlying row-level records are incomplete.

(2) We specify TCAS as a training-free, three-stage requested-scale profile on an existing geometry-adapter residual path, and distinguish the request, wrapper-applied scale, and resulting residual magnitude.

(3) We add a matched 300-object image-space comparison of the recorded C3 profile with fixed and scheduled controls. The registered C3--GFL FG-PSNR result is positive, while GFH and Generic Linear provide counter-results on all four displayed cohort means; no universal winner is claimed.

(4) We report stage-placement, layer-window, and interface analyses with their cohort, adapter, and dose limitations. These analyses bound the tested intervention and do not establish a dose-independent scheduling law or cross-backbone generality.

""",
)

replace_once(
    r"\includegraphics[width=\textwidth,trim=0 24pt 0 0,clip]{fig1.pdf}",
    r"\includegraphics[width=\textwidth,trim=0 40pt 0 0,clip]{figures/fig1_tcas_restored.pdf}",
    "restore and minimally edit Figure 1",
)
replace_once(
    "Method overview. GeoTex-Adapter generates geometric residuals and injects them into UNet features. TCAS dynamically adjusts the residual strength according to denoising stages to balance geometric consistency and texture fidelity. FAC is an optional learned extension module. The final multi-view outputs are projected and baked into a textured 3D mesh.",
    "Method overview. The original pipeline maps a reference image and rendered geometry conditions through a frozen multi-view diffusion UNet and geometry adapter. TCAS specifies a three-stage requested residual-scale profile; projection and baking are shown as downstream pipeline context. The Fresh C evidence in this revision evaluates generated target images only and does not validate the baked mesh. The FAC extension shown in the original schematic has been omitted from this revision.",
)

replace_once(
    r"""\mathbf{h}'_t = \mathbf{h}_t + s(p_t) \cdot A_\phi(\mathbf{h}_t, \mathbf{G}),""",
    r"""\mathbf{h}'_{t,\ell} = \mathbf{h}_{t,\ell} + s_{\mathrm{app}}(p_t,\ell)\, A^\ell_\phi(\mathbf{h}_{t,\ell}, \mathbf{G}),""",
    "scale equation",
)
replace_once(
    r"s(p) = \begin{cases} s_e, & 0 \leq p < 1/3 \\ s_m, & 1/3 \leq p < 2/3 \\ s_l, & 2/3 \leq p \leq 1 \end{cases}.",
    r"s_{\mathrm{req}}(p) = \begin{cases} s_e, & 0 \leq p < 1/3 \\ s_m, & 1/3 \leq p < 2/3 \\ s_l, & 2/3 \leq p \leq 1 \end{cases}.",
    "requested TCAS profile",
)
replace_once(
    r"where $\mathbf{h}_t$ and $\mathbf{h}'_t$ denote the hidden states before and after injection, $p_t$ denotes the sampling progress, and $s(p_t)$ is the adapter scaling strength at the current denoising stage. This formulation highlights a key difference from CFG-style guidance: changing $s(p_t)$ does not reweight two predicted scores, but changes the magnitude of a geometry-conditioned residual added to the feature stream. A larger $s$ usually enhances geometric condition adherence. However, if strong residuals are continuously applied in the late denoising stage, they may suppress the synthesis of color, material, and high-frequency details by the base diffusion model. This paper therefore studies how to schedule $s$ during denoising to balance shape consistency and texture detail preservation.",
    r"""where $\ell$ indexes an injected layer group, $p_t$ is normalized sampling progress, and $s_{\mathrm{app}}$ is the scale actually applied by the wrapper. We distinguish it from the requested profile $s_{\mathrm{req}}$: when a native cap $c_\ell$ is active, $s_{\mathrm{app}}(p_t,\ell)=\min(s_{\mathrm{req}}(p_t,\ell),c_\ell)$; otherwise the wrapper applies the request. The scaled residual's magnitude also depends on $A^\ell_\phi$ and is not determined by the scale label alone. In the Fresh C implementation, the logged caps are 3.0 (deep), 3.5 (middle), and 0.8 (shallow). Thus C3's requested shallow value 1.25 is applied as 0.8, while its deep and middle requests pass unchanged. GFL and GFH also clip at the shallow cap. These cap values describe the audited Fresh C wrapper; row-level cap semantics for the historical 24-object probe are not fully recoverable. TCAS changes a residual added to feature activations, rather than reweighting conditional and unconditional score predictions as CFG does.""",
)

replace_between(
    r"\paragraph{Why mid-stage concentration is selected: the CAI model}",
    r"\subsection{GeoTex-Adapter and FAC Adaptive Extension}",
    r"""\paragraph{Development origin and scope of C3}
The submitted 01549 paper records C3 $=(1.25,2.50,1.25)$ as the selected profile from a 24-object development probe containing 17 uniform, layer-wise, and time-conditioned variants. We retain that development record because it explains the origin of the profile studied here. The complete row-level outputs and selection-time provenance are not available in the current evidence authority, so the historical ranking and labels cannot be independently checked. We therefore make no formal optimality or uniqueness claim based on this probe. Fresh C evaluates the recorded profile without further schedule search.""",
    "remove CAI claim and preserve the empirical development origin",
)

replace_between(
    r"\subsection{GeoTex-Adapter and FAC Adaptive Extension}",
    r"\section{Experiments}",
    r"""\subsection{Geometry Adapter and Inference Interface}
\label{subsec:adapterimpl}

GeoTex-Adapter is treated as the fixed geometry-residual backbone, not as a new contribution of this paper. It receives a five-channel input comprising a three-channel normal map, a one-channel depth map, and a one-channel foreground mask. A multi-scale encoder produces residual features that are injected into the frozen UNet. TCAS acts on the requested multiplier along denoising progress; it does not retrain the adapter, the UNet, or the VAE and introduces no learned parameters.

The original submission also described a learned FAC extension. Its positive claim did not pass the revision's provenance and controlled-reproduction audit, and the manuscript no longer presents FAC as a method or validated result. Figure~\ref{fig:overview} retains the original pipeline context while omitting that unsupported module.""",
    "remove FAC as an unsupported active method",
)

replace_between(
    r"\subsubsection{Experimental protocol and comparisons}",
    r"\subsubsection{Evaluation sets and metrics}",
    r"""\subsubsection{Experimental protocol and comparisons}

The original 01549 submission reports fixed-scale experiments, a 24-object schedule-development probe, and a 300-object pooled evaluation. The source figures and tables are authentic submission artifacts, but the current evidence archive does not contain a complete object-level manifest and run record for every historical result. We therefore preserve the fixed-scale and C3-selection questions as historical development evidence and do not present their unrecovered numbers as newly verified confirmatory results.

The revision-era Fresh C comparison is a separate matched image-space study on 300 frozen object identifiers. Within each Fresh C run, the compared conditions share reference and target inputs, object IDs, initial latents, target views, and seed; the registered primary endpoint is the paired C3--GFL foreground PSNR difference. Generic Linear and layer-conditioned LLH were run in a separate addendum on the same 300 IDs, not as an independent cohort. Fresh C still includes the historical development objects, so it is not a probe-disjoint confirmation of the original main-adapter claim. The separate strict-276 stage-placement analysis uses a different adapter/run lineage and is reported only as a bounded follow-up.""",
)

replace_between(
    r"\subsubsection{Evaluation sets and metrics}",
    r"\subsubsection{Implementation and dataset details}",
    r"""\subsubsection{Evaluation sets and metrics}

The submitted paper describes a 50-object, 13-scale sweep; a purposive 26-object texture audit; a 24-object, 17-variant development probe; and a pooled 300-object evaluation. We retain the 50-object sweep and the 24-object probe as historical diagnostics because they motivate the scale-allocation question. Their object-level raw outputs, full selection provenance, or metric implementation records are incomplete in the current archive. The 26-object audit's object IDs, selection trace, and proxy definitions also cannot be reconstructed; its prevalence and texture-loss claims are withdrawn.

Fresh C adds a revision-era 300-object image-space comparison with foreground PSNR, LPIPS, SSIM, and Edge-SSIM. These measure agreement with target-view renderings on their named endpoints; they do not measure texture fidelity, material appearance, seams, or human preference. Laplacian variance, RGB standard deviation, and gradient magnitude are treated only as variation diagnostics, since larger values can also reflect artifacts. Object is the inferential unit; views are averaged within object and are not independent samples.""",
)

replace_between(
    r"\subsubsection{Implementation and dataset details}",
    r"\paragraph{Statistical reporting}",
    r"""\subsubsection{Implementation and dataset details}

Fresh C uses the frozen MVPainter-style joint six-view latent UNet and VAE with GeoTex-Adapter checkpoint \texttt{geotex\_refattn\_v1/geotex\_step\_0002000.pt}. It uses the Euler discrete scheduler for 50 denoising steps, a shared seed of 42 within each matched comparison, and six target views per object. The 300-object cohort manifest, per-condition row counts, input hashes, and metric outputs are indexed in the Supplementary reproduction map. The primary run has 1,200/1,200 expected condition rows; the same-cohort Generic Linear/LLH addendum has 600/600 rows.

Fresh C's native wrapper caps are deep 3.0, middle 3.5, and shallow 0.8. The recorded scale request, applied value, and post-scale residual norm are separate fields. The requested C3 profile is $(1.25,2.50,1.25)$; its shallow value is clipped to 0.8 in this run. The Generic Linear and LLH addendum conditions are separately defined and do not equalize realized residual dose. Detailed step- and layer-group records are supplied in the Supplement.

FG-PSNR, FG-LPIPS, FG-SSIM, and Edge-SSIM are computed per object after averaging the six target views. The registered primary comparison is C3--GFL FG-PSNR; secondary and addendum tests follow their locked comparison families as documented in Supplementary Section S2. The original 50-object sweep and 24-object probe used separate historical records whose complete current row-level lineage is unavailable, so the implementation details of those runs are not inferred from Fresh C.""",
)

replace_between(
    r"\paragraph{Statistical reporting}",
    r"\subsection{Shape-Texture Trade-off of Adapter Scaling}",
    r"""\paragraph{Statistical reporting}
Fresh C reports the object-level paired mean difference and percentile-bootstrap 95\% interval from 10{,}000 object resamples. The registered primary C3--GFL FG-PSNR contrast is unadjusted as the single primary endpoint. Secondary and addendum families and their multiplicity adjustments are detailed in Supplementary Section S2. CIs outside that prespecified family are pointwise and descriptive. The original human-preference claim is withdrawn and is not part of the current statistical analysis.""",
)

replace_once(
    r"Table~\ref{tab:sweep} reports the results of a 13-scale uniform adapter sweep on 50 objects.",
    r"""Table~\ref{tab:sweep} reproduces the 13-scale sweep reported in the submitted 01549 manuscript. We retain it to preserve the original development question, but the object-level outputs, full run manifest, and metric implementation mapping are not available in the current authority. Its values and Figures~\ref{fig:curve}--\ref{fig:heatmap} are therefore historical diagnostics, not a new reanalysis or confirmatory evidence.""",
)
replace_once(
    "Uniform adapter scale sweep results.",
    "Historical 01549 report of a 13-scale sweep on the stated 50-object set. Values are reproduced from the submission and have not been independently recomputed from row-level outputs; they are retained as development diagnostics.",
)
replace_once(
    "Structural metric changes under uniform adapter scaling. The curves show that FG-SSIM keeps increasing with adapter scale, while Crop-SSIM saturates and slightly decreases at high scales. Stronger geometric control therefore mainly improves structural alignment, but does not necessarily keep improving local foreground quality.",
    "Historical fixed-scale diagnostic from the submitted 01549 paper. The plotted source reports FG-SSIM and Crop-SSIM over adapter scales; the underlying object-level run records are not available for independent reanalysis. It motivates measuring more than one endpoint, but is not a current confirmatory result.",
)
replace_once(
    r"$\Delta$FG-SSIM heatmap for 50 objects under 13 adapter scales. Most objects obtain higher structural gains as the scale increases, but there are clear object-level differences.",
    r"Historical per-object $\Delta$FG-SSIM heatmap reproduced from the 01549 submission (50 objects, 13 scales). The plot illustrates the originally reported response variation; row-level provenance is incomplete, so it is not used for a current population inference.",
)
replace_once(
    r"As the scale increases from $s = 0.75$ to $s = 2.50$, $\Delta$FG-SSIM rises from $-$0.013 to +0.145, and the number of objects with positive improvement increases from 20/50 to 44/50. This indicates that stronger adapter residuals indeed improve the model's adherence to geometric conditions such as normals, depth maps, and foreground contours. Figure~\ref{fig:curve} visualizes this trend: FG-SSIM keeps increasing with adapter scale, while Crop-SSIM saturates and slightly decreases at high scales.",
    r"""The submitted table reports a rising $\Delta$FG-SSIM over most of the listed scale range and a near-plateau in the crop metric at higher settings. We retain this reported pattern only as historical motivation: absent row-level outputs and a complete run manifest, we do not treat it as an independently confirmed scale-response law. It motivates asking whether a single aggregate structural score fully describes the effect of adapter scaling.""",
)
replace_once(
    r"Overall, the FG-SSIM improvement is stable, but the marginal benefit becomes smaller in the high-scale region. For example, increasing the scale from $s = 2.25$ to $s = 2.50$ yields only a limited FG-SSIM gain, while Crop-SSIM already decreases. This suggests that the nature of the high-scale benefit may change: the gain comes more from contour smoothing and foreground alignment than from preservation of local texture details. Figure~\ref{fig:heatmap} shows the per-object $\Delta$FG-SSIM heatmap, confirming that most objects gain higher structural scores as the scale increases, but with clear object-level differences.",
    r"""The submitted heatmap depicts object-level variation across the reported scales, but its underlying rows cannot be reconstructed from the current evidence archive. We retain the visual diagnostic as part of the 01549 research history and do not infer a population-level response distribution from it. The updated Fresh C analysis below uses its own frozen cohort and matched inputs.""",
)

replace_between(
    r"\subsection{Texture Audit: High Scale Causes Texture Flattening}",
    r"\subsection{Timestep-Conditioned Adapter Scaling: Shape-Texture Balance of C3}",
    r"""\subsection{Full-Object Appearance Evidence and Texture-Metric Scope}
\label{subsec:visual}

The submitted 26-object texture audit and its quantitative Figure~5 cannot be re-traced to object IDs, selection criteria, raw values, and an executable metric definition in the current evidence archive. We therefore remove its 92\% prevalence statement, its “true shape gain” classification, and its RGB-standard-deviation/gradient ratios from the scientific claims. Those statistics would describe variation, not texture fidelity, even if their source records were complete.

Figure~\ref{fig:qualitative} provides revision-era full-object target-view comparisons across the reference, No Adapter, GFL, GFH, C3, LLH, and Generic Linear conditions. It includes a near-median case, an adverse C3--GFL case, and a selected Generic Linear counterexample to show visible disagreement as well as favorable outcomes. These outcome-selected examples address the visual-comparison request but do not estimate prevalence. Fresh C has no validated texture-fidelity endpoint, and neither this figure nor the image-space metrics establish baked-texture, seam, PBR, or human-preference quality.

\begin{figure*}[t]
\centering
\small\textbf{(a) Near-median C3--GFL case}\par\vspace{2pt}
\includegraphics[width=\textwidth,trim=0 36pt 0 0,clip]{figures/fig4_typical_c3_gfl.png}\par\vspace{4pt}
\small\textbf{(b) Adverse C3--GFL case}\par\vspace{2pt}
\includegraphics[width=\textwidth,trim=0 36pt 0 0,clip]{figures/fig4_adverse_c3_gfl.png}\par\vspace{4pt}
\small\textbf{(c) Generic Linear counterexample}\par\vspace{2pt}
\includegraphics[width=\textwidth,trim=0 36pt 0 0,clip]{figures/fig4_generic_linear_counter.png}
\caption{Selected full-object Fresh C target-view comparisons. Each contact sheet shows the reference and the same seven inference conditions across matched target views. The cases were selected by outcome for illustration: (a) near the cohort median C3--GFL FG-PSNR difference, (b) the adverse C3--GFL case, and (c) a Generic Linear counterexample. Selection does not estimate case frequency. The images are rendered 2D outputs, not baked meshes or unseen-view PBR results. Asset attribution is listed in Supplementary Table S1.}
\label{fig:qualitative}
\end{figure*}

""",
)

replace_between(
    r"\subsection{Timestep-Conditioned Adapter Scaling: Shape-Texture Balance of C3}",
    r"\subsection{Large-scale Pooled Evaluation}",
    r"""\subsection{Timestep-Conditioned Adapter Scaling: Shape-Texture Balance of C3}
\label{subsec:c3}

The submitted paper records 17 uniform, layer-wise, and timestep-conditioned variants on a 24-object development probe and identifies C3 as its chosen profile. This study question remains relevant: does a stage-dependent request offer a useful control setting beyond a single global scale? Because the complete historical row-level data and selection provenance are not available in the current authority, the original Table~\ref{tab:probe} and Figure~\ref{fig:pareto} are retained as historical development records, not as a verified ranking or proof of optimality. Fresh C evaluates the recorded C3 profile without another schedule search.

\begin{table}[t]
\centering
\caption{Representative values reported for the historical 24-object, 17-variant development probe. The full candidate set is shown in Figure~\ref{fig:pareto}. The underlying row-level outputs and selection-time provenance are not available for independent reanalysis; the table records the submitted development result and does not establish an optimum.}
\label{tab:probe}
\footnotesize\setlength{\tabcolsep}{3pt}
\begin{tabular}{llcc}
\toprule
Variant & Reported category & $\Delta$FG-SSIM & $\Delta$Lap Var \\
\midrule
C4 & Late-stage high & 0.105 & $-$0.0120 \\
C2 & Timestep schedule & 0.104 & $-$0.0110 \\
B2 & Layer-wise schedule & 0.090 & $-$0.0135 \\
A\_s2.00 & Uniform & 0.087 & $-$0.0062 \\
C3 & Mid-stage high & 0.084 & $-$0.0006 \\
A\_s2.25 & Uniform & 0.079 & $-$0.0096 \\
A\_s2.50 & Uniform & 0.078 & $-$0.0108 \\
B6 & Layer-wise schedule & 0.000 & $-$0.0027 \\
\bottomrule
\end{tabular}
\end{table}

The original table and plot use shape and texture-variation proxies to describe the development choice. They do not establish that texture was faithful to the reference, nor that C3 was the unique best candidate. In this revision, C3 is therefore described as the historical profile carried forward for matched evaluation, not as a theorem-derived or globally optimal schedule.

The requested profile is piecewise constant over normalized sampling progress $p$:
\begin{equation}
s_{\mathrm{req}}(p) =
\begin{cases}
1.25, & 0 \le p < 1/3,\\
2.50, & 1/3 \le p < 2/3,\\
1.25, & 2/3 \le p \le 1,
\end{cases}
\qquad \mathrm{C3}=(1.25,2.50,1.25).
\end{equation}
This is an inference-time instruction on the existing adapter path; no weights are trained. Its tested value is task- and implementation-specific. The schedule operation itself is not claimed as a new general primitive.

Figure~\ref{fig:c3compare} presents selected Fresh C full-object comparisons relevant to the original fixed-scale/C3 question: one C3-favourable case and one C3--GFH endpoint trade-off. Both figures are illustrative; the object-paired estimates in Section~\ref{subsec:largescale} carry the quantitative comparison.

\begin{figure*}[t]
\centering
\small\textbf{(a) Selected C3-favourable case}\par\vspace{2pt}
\includegraphics[width=\textwidth,trim=0 36pt 0 0,clip]{figures/fig6_favorable_c3_gfl.png}\par\vspace{4pt}
\small\textbf{(b) C3--GFH endpoint trade-off}\par\vspace{2pt}
\includegraphics[width=\textwidth,trim=0 36pt 0 0,clip]{figures/fig6_c3_gfh_tradeoff.png}
\caption{Selected Fresh C views for the original C3-versus-fixed-scale comparison question. Both contact sheets show matched target views across the reference and seven tested conditions. Panel (a) is an outcome-selected C3-favourable case; panel (b) illustrates an endpoint trade-off against GFH. These examples do not estimate frequency or establish an overall winner. The aggregate image-space comparisons are reported in Tables~\ref{tab:freshc-absolute}--\ref{tab:freshc-contrasts}; asset attribution is listed in Supplementary Table S1.}
\label{fig:c3compare}
\end{figure*}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{figures/fig7_c3_development.pdf}
\caption{Historical 17-variant shape--texture development plot from the submitted 01549 paper, restricted to the 24-object development probe and not an independent validation set. The plot labels have been locally changed to “Development region” and “C3 (probe)” to identify their development-set role; neither the shaded region nor C3 denotes a unique optimum, a texture-fidelity ranking, or a general schedule law. The underlying row-level candidate outputs are not available for independent reanalysis.}
\label{fig:pareto}
\end{figure}

The source Figure~5 and Table~3 (the 26-object and 24-object extended texture-statistic summaries) are not included as active results because their data lineage and metric definitions are incomplete. They remain preserved in the authenticated submission and the forensic archive. The decision is specific to those quantitative diagnostics; it does not remove the fixed-scale research question or the development record of C3.

""",
)

replace_between(
    r"\subsection{Large-scale Pooled Evaluation}",
    r"\section{Limitations}",
    r"""\subsection{Large-Scale Matched Image-Space Evaluation}
\label{subsec:largescale}

Fresh C is a revision-era matched image-space study on $N=300$ objects. Its primary run contains No Adapter, global fixed-low (GFL), global fixed-high (GFH), and the historical C3 profile. A separate addendum evaluates Generic Linear and a layer-conditioned low--high--low profile (LLH) on the same 300 object identifiers; it is not an independent cohort. All conditions within a run share the object, reference/target inputs, six target views, initial latents, and seed. Object is the inferential unit, with views averaged within object.

The registered primary contrast is C3 minus GFL on foreground PSNR (FG-PSNR). The point estimate is $+0.522352$~dB (95\% percentile-bootstrap CI $[+0.404160,+0.640669]$); C3 is higher on 206/300 objects (68.7\%), with median paired difference $+0.554514$~dB. Registered secondary endpoints are reported with the multiplicity treatment and full paired statistics in Supplementary Section S2. PSNR, LPIPS, and SSIM quantify image-space agreement on their respective endpoints; they are not direct measures of texture fidelity or 3D material quality.

\begin{table*}[t]
\centering
\caption{Fresh C image-space condition means. The primary run contains No Adapter, GFL, GFH, and C3. Generic Linear and LLH are revision-era addendum conditions evaluated on the same object identifiers, not a second independent cohort. Values are means of object-level metrics over six target views.}
\label{tab:freshc-absolute}
\scriptsize\setlength{\tabcolsep}{4pt}
\begin{tabular}{lccccc}
\toprule
Method & $N$ & FG-PSNR$\uparrow$ & FG-LPIPS$\downarrow$ & FG-SSIM$\uparrow$ & Edge-SSIM$\uparrow$ \\
\midrule
\multicolumn{6}{l}{Primary run} \\
No Adapter & 300 & 6.9779 & 0.2288 & 0.4086 & 0.4314 \\
GFL & 300 & 11.3077 & 0.2051 & 0.3500 & 0.4728 \\
GFH & 300 & 12.5777 & 0.1891 & 0.4201 & 0.4961 \\
C3 (TCAS) & 300 & 11.8301 & 0.1998 & 0.3746 & 0.4773 \\
\midrule
\multicolumn{6}{l}{Same-cohort revision-era addendum} \\
Generic Linear & 300 & 12.4230 & 0.1862 & 0.4026 & 0.4880 \\
LLH & 300 & 12.4506 & 0.1876 & 0.3911 & 0.4863 \\
\bottomrule
\end{tabular}
\end{table*}

\begin{table*}[t]
\centering
\caption{Fresh C paired differences, condition A minus B. Cells report the mean difference and pointwise 95\% object-bootstrap CI. Positive PSNR/SSIM and negative LPIPS differences favour A. C3--No Adapter and C3--GFH are post-hoc contrasts; the addendum shares the primary run's object identifiers. Multiplicity-adjusted tests and the full endpoint family are in Supplementary Section S2.}
\label{tab:freshc-contrasts}
\scriptsize\setlength{\tabcolsep}{3pt}
\begin{tabular}{lcccc}
\toprule
Contrast & FG-PSNR (dB) & FG-LPIPS & FG-SSIM & Edge-SSIM \\
\midrule
C3 $-$ GFL & $+0.522\ [0.404,0.641]$ & $-0.005345\ [-0.006326,-0.004403]$ & $+0.02453\ [0.02120,0.02805]$ & $+0.004494\ [0.003411,0.005586]$ \\
C3 $-$ No Adapter & $+4.852\ [4.553,5.142]$ & $-0.02905\ [-0.03352,-0.02464]$ & $-0.03401\ [-0.04214,-0.02591]$ & $+0.04586\ [0.04114,0.05054]$ \\
C3 $-$ GFH & $-0.748\ [-0.885,-0.609]$ & $+0.01070\ [0.008958,0.012513]$ & $-0.04553\ [-0.04937,-0.04167]$ & $-0.01881\ [-0.02084,-0.01683]$ \\
C3 $-$ Generic Linear & $-0.593\ [-0.837,-0.351]$ & $+0.01351\ [0.01160,0.01549]$ & $-0.02810\ [-0.03197,-0.02439]$ & $-0.01069\ [-0.01300,-0.00850]$ \\
LLH $-$ C3 & $+0.621\ [0.391,0.855]$ & $-0.01214\ [-0.01386,-0.01048]$ & $+0.01658\ [0.01311,0.02003]$ & $+0.009033\ [0.006867,0.011296]$ \\
LLH $-$ Generic Linear & $+0.028\ [-0.015,0.070]$ & $+0.001372\ [0.000762,0.002081]$ & $-0.01152\ [-0.01337,-0.00996]$ & $-0.001660\ [-0.002096,-0.001256]$ \\
\bottomrule
\end{tabular}
\end{table*}

The C3--GFL comparison supports a bounded statement: on this frozen cohort and image-space endpoint, the recorded C3 intervention improves mean FG-PSNR relative to GFL. It does not isolate temporal placement from scale allocation, and the cohort includes the historical development objects. Fresh C does not establish probe-disjoint replication of the main-adapter result.

The counter-results delimit that finding. GFH has more favorable cohort means than C3 on all four displayed endpoints. Generic Linear also has more favorable means than C3 on all four; for C3 minus Generic Linear, the mean FG-PSNR difference is $-0.593$~dB (95\% CI $[-0.837,-0.351]$), although the median is $+0.073956$~dB and C3 is higher on 155/300 objects (51.7\%). LLH's FG-PSNR mean exceeds C3 by $+0.621$~dB, while its median difference is $-0.153$~dB and only 140/300 objects favour LLH; its lower mean FG-LPIPS favours LLH. For LLH versus Generic Linear, the FG-PSNR CI includes zero, which is not evidence of equivalence; the FG-LPIPS difference favours Generic Linear. The endpoint means and object-level distributions do not identify a universal winner.

Fresh C contains no validated texture-variation or texture-fidelity endpoint. We therefore do not revive the original 300-object RGB/Laplacian/gradient tables or their “retention” interpretation. In those diagnostics, a larger response could represent meaningful detail or an artifact; it cannot by itself establish fidelity.

\subsection{Stage Sensitivity and Applicability Boundaries}
\label{subsec:stageboundaries}

A separate post-inspection strict-276 follow-up compares temporal profiles on a different adapter/run lineage. C3 and temporal L--L--H have near-matched per-layer applied-scale sums (82.5 versus 83.75 for deep/middle, 40 for shallow), but not matched post-scale residual-norm dose; temporal L--L--H favours C3 on all six formal endpoints. Against the fixed-mean profile, C3's FG-PSNR difference is $+0.502875$~dB (95\% CI $[+0.462018,+0.542244]$). This indicates sensitivity to the tested stage allocation, but does not confirm C3 as best or isolate an equal-realized-dose causal effect. Full comparisons are in Supplementary Table S7.

The A2/A3b layer-window maps detect response heterogeneity under their tested bounded interventions. A3b has zero common-support rows across its three layer groups among 2,250 layer-step observations, so dose adjustment cannot identify a dose-independent layer-by-time mechanism. Fresh B is a separate 150-object cohort; its temporal LLH result is not a replication of C3. Core-7's retrospective strict-276 result uses another adapter/run lineage and incomplete runner/input provenance and is retained only as a separately labeled historical diagnostic in the Supplement. None of these analyses establishes cross-backbone generality.

The historical N=20 GLB-native unseen-view check used unlit base color on a UV-compatible subset and produced mixed endpoint results. It is a bounded 3D rendering observation only; it does not establish full PBR, seam, or population-level texture superiority (Supplementary Table S8). Fresh C's attempted 24-object bake did not pass the native-input gate, so no new bake or seam outcome is reported.

""",
)

replace_between(
    r"\section{Limitations}",
    r"\section{Conclusion}",
    r"""\section{Limitations}
\label{sec:limitations}

The current primary evidence is image-space and comes from one MVPainter-style pipeline, one geometry-adapter interface, one sampler setup, and one frozen cohort. Fresh C is revision-era evidence rather than a replication of every original experiment; its $N=300$ includes the historical development objects. The strict-276 follow-up changes adapter/run lineage and is post-inspection. No confirmatory probe-disjoint study of the main adapter is available, and the cross-interface analyses do not establish transfer to another backbone.

Texture variation and texture fidelity are distinct. The submitted RGB standard deviation, Laplacian variance, and gradient summaries are not re-used as fidelity measures; their source records and definitions are incomplete, and such metrics can rise with artifacts. Fresh C reports PSNR, LPIPS, and SSIM endpoints but has no validated texture-fidelity, human-preference, baked-mesh, seam, or PBR measure. Historical N=20 unlit base-color renders provide only a small, mixed unseen-view result.

The requested TCAS profile does not uniquely determine the applied scale or correction magnitude. Fresh C's native wrapper caps shallow requests at 0.8, and residual norms depend on the adapter output. The strict-276 schedule sums are only approximately matched and do not equalize realized dose; A3b has no cross-layer common support. These data do not identify a dose-independent mechanism, an optimal selector, or a schedule that dominates all endpoints and objects.

We also withdraw the original CAI optimality proposition, the FAC positive extension claim, the old pooled $+0.96$~dB headline, the broad texture-retention claim, CLIP-IQA superiority, and the human-preference superiority claim. Their former numerical content is not used as current evidence: the CAI derivation depended on unsupported assumptions, FAC did not pass controlled provenance review, and the old perceptual/human result records are not part of the current authorized evidence set. Their removal is documented in the content-disposition ledger.

""",
)

replace_between(
    r"\section{Conclusion}",
    r"\section*{Data availability}",
    r"""\section{Conclusion}
\label{sec:conclusion}

This revision returns to the submitted TCAS question: how a geometry-adapter residual request is allocated during multi-view diffusion sampling. It preserves the historical fixed-scale sweep and 24-object C3 development record with explicit provenance limits, and specifies the three-stage request on the existing adapter path. It does not treat the old proxy-texture, CAI, FAC, human-preference, or pooled headline claims as established results.

In the revision-era Fresh C image-space comparison, C3 exceeds GFL by $+0.522352$~dB mean FG-PSNR on the registered primary contrast. GFH and Generic Linear have more favorable means than C3 on all four displayed endpoints, and LLH trades endpoint means against object-level response. A separate stage-placement follow-up and the layer-window studies show that tested interventions can have stage- and layer-dependent responses, but their cohort, wrapper, and realized-dose limits prevent a general causal or optimal-schedule conclusion.

The supported contribution is a task-specific, training-free residual-scaling intervention with explicit requested/applied semantics and matched image-space evidence for a bounded comparison. It is not a claim to invent general layer-by-time scheduling, establish a universal schedule, or improve baked texture, seams, PBR appearance, or human preference. These limits define the next validation needed for deployment in 3D texturing.

""",
)

replace_once(
    r"\bibitem{ho2020ddpm}",
    r"""\bibitem{kulkarni2026ssi}
Kulkarni A S, et al. Scheduled Style Injection: Expanding the Style-Content Pareto Frontier in Training-Free Diffusion-Based Style Transfer. \textit{Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW), NTIRE Workshop}, 2026.

\bibitem{ho2020ddpm}""",
)

def remove_uncited_bibliography_items():
    """Keep the manually formatted reference list consistent with citations."""
    global text
    begin = r"\begin{thebibliography}"
    end = r"\end{thebibliography}"
    b0 = text.find(begin)
    b1 = text.find(end, b0 + len(begin))
    if b0 < 0 or b1 < 0:
        raise SystemExit("Expected a thebibliography environment.")

    cited = set()
    citation_pattern = r"\\[A-Za-z]*cite[A-Za-z]*\*?(?:\[[^\]]*\]\s*)*\{([^}]+)\}"
    for match in re.finditer(citation_pattern, text):
        cited.update(key.strip() for key in match.group(1).split(",") if key.strip())
    if r"\nocite{*}" in text:
        return

    body0 = b0 + len(begin)
    body = text[body0:b1]
    entries = list(re.finditer(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", body))
    if not entries:
        raise SystemExit("No bibliography items were found.")

    kept = [body[:entries[0].start()]]
    removed = []
    for i, entry in enumerate(entries):
        stop = entries[i + 1].start() if i + 1 < len(entries) else len(body)
        block = body[entry.start():stop]
        key = entry.group(1).strip()
        if key in cited:
            kept.append(block)
        else:
            removed.append(key)

    expected_removed = {
        "rombach2022ldm", "esser2024scaling", "blackforestlabs2024flux",
        "loshchilov2019decoupled", "cherti2023reproducible", "nichol2022glide",
        "saharia2022photorealistic", "peebles2023scalable", "wang2023clipiqa",
        "radford2021clip",
    }
    if set(removed) != expected_removed:
        raise SystemExit(
            "Uncited bibliography set changed unexpectedly: "
            f"{sorted(removed)!r}"
        )
    text = text[:body0] + "".join(kept) + text[b1:]

remove_uncited_bibliography_items()

output_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
if active_target and output_sha != ACTIVE_SHA:
    raise SystemExit("Generated TeX differs from the locked active source; no files written.")
target.write_text(text, encoding="utf-8")
if not verify_baseline_lock():
    raise SystemExit("Post-write baseline verification failed; preserve outputs and investigate.")
print(f"Wrote active revision: {target}")
print(f"Source SHA-256: {sha256(source)}")
print(f"Output SHA-256: {sha256(target)}")
