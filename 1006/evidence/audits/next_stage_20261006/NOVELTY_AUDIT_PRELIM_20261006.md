# Novelty audit — preliminary primary-source review

Review date: 2026-10-06. Scope: the submitted 01549/0907 manuscript, *Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation*. This is a focused, primary-source review of the most relevant citations and adjacent work; it is not an exhaustive systematic search and does not decide journal fit.

## Finding

The paper's broad framing that layer/time-varying control strength is a new diffusion control space is no longer defensible. The closest overlap is *Scheduled Style Injection* (arXiv May 2026; CVPR 2026 NTIRE workshop): it studies strength schedules across decoder layers and denoising steps and also schedules geometric ControlNet conditioning along those axes. Its public code exposes both per-layer and per-step schedules. This overlaps directly with the general operation and much of the proposed rationale, even though its task, adapter path, and 3D evaluation differ.

The potentially distinct contribution is narrower: an object-level empirical account of how the particular geometry-adapter residual path used in MVPainter changes shape/texture metrics and final baked texture under specified scale schedules, with explicit dose/cap traces and architecture-specific limits. Whether that is enough contribution for the target journal remains open and depends on E1/E2, the 3D scope, real human data, and reviewer expectations. A new name for C3/TCAS does not add novelty.

## Comparison table

| Primary source | What it already establishes | Relation to 01549 | Consequence for claims |
|---|---|---|---|
| [Scheduled Style Injection, arXiv:2605.26538](https://arxiv.org/abs/2605.26538); [official implementation](https://github.com/ameyskulkarni/scheduled_style_injection) | Training-free strength schedules over decoder depth and diffusion time; also layer/time schedules for depth-ControlNet conditioning. The paper reports schedule-shape studies and three SD backbones; the repository includes `gamma_per_layer` and timestep ControlNet-scale interfaces. | Closest conceptual and operational prior art. It is style transfer and SD ControlNet, while 01549 studies a geometry-conditioned multi-view adapter, its residual/cap behavior, and texture baking. | Remove any “first layer/time control schedule” or universal control-space claim. State the domain-specific residual-path and 3D-texture evidence precisely; discuss SSI explicitly and explain what the different injection path/endpoint changes. The paper appeared after the 01549 submission snapshot, so include it in a current revision and distinguish priority from current related work. |
| [Applying Guidance in a Limited Interval, NeurIPS 2024](https://proceedings.nips.cc/paper_files/paper/2024/file/dd540e1c8d26687d56d296e64d35949f-Paper-Conference.pdf) | Diffusion guidance can be harmful early, useful in the middle, and unnecessary late; an interval is a useful schedule. | Establishes the general temporal-window premise for guidance, but studies classifier/guidance weighting rather than MVPainter adapter residual scaling. Already cited in the submitted paper. | Present low–high–low as a tested control schedule in this pipeline, not a new general diffusion principle. Attribute the general middle-interval intuition. |
| [ControlNet](https://arxiv.org/abs/2302.05543) | Spatial conditions are injected through a learned conditional branch and residuals; the paper composes multiple controls and studies architectural alternatives. | Establishes the family of geometric conditioning methods and residual injection; its branch differs from the inference-time scale intervention used in MVPainter. Already cited. | Describe the exact MVPainter adapter residual and effective-scale/cap semantics; do not imply that “scaling a geometry control signal” itself is new. |
| [MVPainter](https://arxiv.org/abs/2505.12635) | Multi-view diffusion for 3D texture generation with ControlNet-based geometric conditioning and PBR mesh output. | The target pipeline and baseline system. | Make the contribution an independent, controlled characterization of inference-time adapter scaling in this pipeline; do not claim to introduce its multi-view geometry-control architecture. |
| [MV-Adapter, ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Huang_MV-Adapter_Multi-View_Consistent_Image_Generation_Made_Easy_ICCV_2025_paper.pdf) | A plug-and-play multi-view adapter with geometry/camera conditions and texturing applications. | Supports the paper's tested second architecture, but it has different injection geometry and a bounded intervention range. Existing V3 results do not establish a matched cross-architecture causal comparison. | Report the measured boundary as architecture-specific. Do not generalize the preferred scale/window or claim transferability. |
| [FlexControl, ICML 2025](https://proceedings.mlr.press/v267/fang25j.html) | Learned block gates select conditional control signals at each denoising step across UNet and DiT tasks. | Related to allocating control across blocks/time, but it is a trained routing method rather than a fixed, training-free scalar schedule. | Acknowledge learned spatiotemporal control allocation as adjacent work; differentiate only on inference-time fixed-scale characterization and final 3D texture endpoints. |
| [T-LoRA, arXiv:2507.05964](https://arxiv.org/abs/2507.05964) | Timestep-dependent rank-constrained LoRA updates for single-image personalization during fine-tuning. | Temporal adaptation of adapters is known, but its intervention changes learned low-rank updates rather than inference-time geometry-residual scale. | Related background; it weakens generic “timestep-dependent adapter” novelty, while remaining methodologically distinct. |
| [DiffCR, CVPR 2025](https://arxiv.org/abs/2412.16822) | Layer- and timestep-adaptive computation/compression ratios. | Shares the layer×time axes but allocates computation, not geometric conditioning strength. | Peripheral prior art; avoid treating the axes themselves as novel. |

## Reviewer-facing claim decision

1. **Withdraw:** “first” or “novel” layer×timestep control space, general diffusion mechanism, universally optimal C3/TCAS, CAI-derived optimal schedule, broad backbone transfer.
2. **Retain provisionally:** the measured response of the specified MVPainter geometry-adapter path to fixed temporal and layer-scale interventions; the exact residual/cap semantics; the observed shape–texture trade-off; the tested schedule's scope and failure boundaries.
3. **Contribution adequacy remains open after E1/E2:** E1 realization sensitivity and the E2 locked static-factor intervention are now complete with integrity PASS. They sharpen a bounded empirical characterization but do not establish broad mechanism novelty or remove the close SSI precedent. The new 40-slot LLH human evaluation still has no responses; its completion may inform fidelity claims but cannot settle novelty by itself. A final contribution decision also requires complete paper-wide evidence reconstruction and explicit comparison with SSI's supplementary/code details.
4. **Narrative option after evidence freeze:** position the work as a domain-specific empirical study of inference-time geometry-adapter scaling for multi-view texture generation, with C3 as one evaluated operating point. If E1/E2 do not yield stable, interpretable effects, the remaining evidence may be too incremental for the target journal; record a venue/contribution risk instead of enlarging claims.

The manuscript remains unchanged pending the scientific evidence freeze.

## E1/E2 evidence update

E1 found endpoint- and comparator-dependent results on the fixed 48-object
subset; seed variability is descriptive, not a new independent cohort. E2
found favorable deep+middle static-scale effects on both endpoints, an
unfavorable shallow-scale LPIPS effect, and a PSNR-only factor interaction.
The fixed factorial has no time-varying intervention and no equal-realized-dose
contrast. These results support a narrower pipeline-specific response
characterization; they do not restore “first layer×time control space,” a
general allocation mechanism, or a unique optimal schedule. See
`MULTISEED_ANALYSIS.md`, `STATIC_FACTORIAL_ANALYSIS.md`, and
`NARRATIVE_DECISION_MAP.md`.
