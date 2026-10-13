# Independent expert review — layer-wise author-review package

Date: 2026-09-29  
Version: `final_round2_layerwise_author_review_20260929.pdf` and matching
supplementary PDF.

## Overall judgment

The revision is materially more defensible than the C3/LHL-centered version.
It now has a visible method object—layer-wise stage-aware adapter scaling—an
actual shared-input ablation, and explicit negative controls. The method claim
is plausible as a training-free inference-control contribution, but the paper
must be positioned as a conditional method and controlled empirical study,
not as a universal schedule-selection paper.

## Reviewer-1 audit

- Practical image quality is answered directly by the visible fixed-low,
  C3, layer-fixed, layer-LHL, and layer-LLH comparisons and by Table 1.
- The new paired result supports a foreground benefit over global fixed-low:
  layer-LHL gives +3.083 dB FG-PSNR and -0.0267 FG-LPIPS in the 72 paired
  object-seed records.
- The answer is deliberately conditional. Layer-fixed-mean is better on
  FG-LPIPS, and layer-LLH is better than layer-LHL on all seven reported
  development metrics. This prevents the visual and numerical evidence from
  being presented as a universal win.
- The baking section honestly shows an operational GLB/unseen-view path but
  no demonstrated population-level 3D advantage. This is a remaining risk,
  not a hidden success claim.

## Reviewer-2 audit

- The new equation $h'_{l,t}=h_{l,t}+s_l(p_t)A_l(h_{l,t},G)$ makes the
  implementation-level distinction from one shared scale explicit.
- Shared target, geometric features, and initial latent hashes make the
  layer-wise comparison more than an uncontrolled schedule anecdote.
- The ablation does not prove a unique temporal rule. The manuscript states
  this limitation and keeps CAI as empirical analysis rather than a selector.
- The second-backbone material remains a boundary audit. It does not prove
  cross-backbone transfer of layer-LHL, which is correctly stated as absent.

## Novelty and acceptance risk

The novelty is credible at the level of a reusable inference-control
mechanism—layer-dependent residual scaling without retraining—provided the
paper does not oversell the particular layer-LHL schedule. The main risks are
that reviewers may regard the depth partition and scales as empirical
engineering, and that the new ablation is still a development study. These
risks are mitigated by the explicit controls, provenance, and counterexamples,
but not eliminated.

Recommended editorial decision: suitable for author review and a focused
返修 submission package after final source/PDF checks; do not describe the
package as evidence of universal superiority or guaranteed acceptance.
