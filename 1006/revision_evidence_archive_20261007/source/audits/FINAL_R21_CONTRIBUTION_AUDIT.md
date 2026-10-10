# R2.1 contribution adversarial audit

**Final status: `R2.1 = OPEN / VENUE RISK`.** The literature and evidence comparison is complete; whether the narrowed empirical contribution is sufficient for *Computers & Graphics* remains an editorial judgment.

## Prior-work comparison

| Dimension | Prior work | This paper's defensible scope |
|---|---|---|
| Layer scheduling | Scheduled Style Injection (SSI) directly schedules style strength over decoder depth and denoising time, including geometry-conditioned ControlNet use. | No novelty claim for a layer-by-timestep schedule or a new two-axis control space. |
| Timestep scheduling | SSI and other scheduled guidance/style methods vary strength over denoising steps. | C3 is a concrete tested profile on the existing MVPainter adapter path, not a new temporal-scheduling primitive. |
| Geometry-conditioned adapter | MVPainter already provides the multi-view geometry-conditioned generation and texture-baking system. | The study evaluates scale behavior inside that existing residual adapter path; it does not propose a new generator. |
| Scale control | Guidance/adapter scaling and layer/time allocation are established control patterns; Paint3D, MVPaint, and related texture systems address other parts of the pipeline. | Measure requested, capped/applied, and correction magnitudes for the named MVPainter schedules. No new general scale-control operator is claimed. |
| Native cap semantics | Prior papers establish schedule/control precedents, but their implementation-specific cap execution is not the same as this wrapper. | The new accounting is specific to the tested wrapper and its layer caps; no universal cap law follows. |
| Realized residual accounting | The closest cited schedule papers do not establish this paper's measured Fresh C correction-norm results for this implementation. | A bounded implementation-aware characterization of requested versus applied scales and logged correction norms. It is not equal-realized-dose causal evidence. |
| Multi-view texture endpoint | MVPainter, MVPaint, Paint3D, Make-A-Texture, and Im2SurfTex already study 3D texture generation/appearance from different pipelines. | Fresh C supplies endpoint- and object-dependent image-space evidence for this specific adapter intervention; it does not establish universal texture quality. |
| Fresh object confirmation | Prior work establishes the task and method families, not this exact frozen Fresh C cohort. | Revision-era N=300 image-space evidence: C3−GFL foreground PSNR +0.522 dB (95% object bootstrap CI [+0.404,+0.641]); addendum results show endpoint trade-offs, including LLH−linear FG-LPIPS favoring generic linear. |
| Object heterogeneity | Object-dependent outcomes are a recognized evaluation concern in generative systems. | Report object-level distributions and favorable fractions; do not elevate a positive mean to a typical-object claim. |
| Boundary/failure analysis | Texture pipelines have their own applicability and quality limitations. | Keep the observed texture-complexity and endpoint boundaries as bounded characterization, not a universal failure predictor. |
| Cross-interface test | MV-Adapter and MVDiffusion use different conditioning/correspondence interfaces. | Report each interface only within its own tested protocol; do not infer architecture causality or universal transfer. |

## Questions

### Q1. Is “layer × timestep schedule” itself new?

No. SSI is a direct prior-work counterexample. The manuscript must not use “first,” “novel control space,” or equivalent broad novelty language for layer-by-timestep scheduling.

### Q2. Is C3 an algorithmic innovation?

The current evidence supports C3 as a tested schedule configuration on the existing MVPainter residual path. It does not establish a new general algorithm or an optimal policy. The schedule configuration must not carry the whole novelty claim.

### Q3. What new knowledge is supported?

1. Requested scale and actually applied scale can differ under native layer caps.
2. Layer and timestep allocation changes the implementation's logged correction magnitudes; the correction norm depends on the residual as well as the scale.
3. In the Fresh C cohort, strategy effects vary by endpoint and object. There is no demonstrated cross-metric unique winner, no equal-realized-dose quality design, and no dose-independent mechanism.

These points constitute bounded empirical knowledge about this implementation and cohort. Their broader practical importance is not established by the current experiments alone.

### Q4. Is that enough for C&G?

The available evidence does not justify an automatic “closed.” It narrows the novelty claim and makes the results auditable, but the scope is implementation-specific and the strongest scale-semantic interpretation lacks equal-realized-dose quality comparisons. Therefore the honest status is **`OPEN / VENUE RISK`**.

## Primary literature checked

- [Scheduled Style Injection, CVPRW 2026 paper](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf)
- [MVPainter project](https://amap-cvlab.github.io/MV-Painter/) and [paper](https://arxiv.org/abs/2505.12635)
- [MV-Adapter, ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Huang_MV-Adapter_Multi-View_Consistent_Image_Generation_Made_Easy_ICCV_2025_paper.pdf)
- [MVDiffusion project](https://mvdiffusion.github.io/index.html) and [paper](https://arxiv.org/abs/2307.01097)
- [Paint3D, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/papers/Zeng_Paint3D_Paint_Anything_3D_with_Lighting-Less_Texture_Diffusion_Models_CVPR_2024_paper.pdf)
- [MVPaint, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Cheng_MVPaint_Synchronized_Multi-View_Diffusion_for_Painting_Anything_3D_CVPR_2025_paper.pdf)
- [Make-A-Texture, WACV 2025](https://openaccess.thecvf.com/content/WACV2025/papers/Gorelik_Make-A-Texture_Fast_Shape-Aware_3D_Texture_Generation_in_3_Seconds_WACV_2025_paper.pdf)
- [Im2SurfTex](https://doi.org/10.1111/cgf.70191) and [arXiv record](https://arxiv.org/abs/2502.14006)
