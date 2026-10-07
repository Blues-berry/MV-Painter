# Point-by-point response draft for the supplied reviewer comments

**Internal working draft — not ready to submit.** This file contains proposed replies and manuscript actions. The manuscript `01549` has not been edited, so page and line references are intentionally omitted. Do not present proposed actions as completed revisions.

**Review-source note.** The file named `第二轮审稿意见.txt` is labeled “Initial submission” inside its R1–R3 sections and gives dates 14, 24, and 28 September 2026. I use it as the supplied comment set, but cannot verify that it is a distinct second-round decision.

**Scope note.** This response uses non-human evidence only. It does not analyze participant answers or reinterpret human-study outcomes. The R1 visual-fidelity concern can be answered only in part without that evidence.

## Reviewer 1

### R1.1 — Visible artifacts, full-object comparisons, unseen viewpoints, seams, and the supplementary video

**Proposed response**

> Thank you for pointing out the visible color shifts, repeated patterns, and differences from the references. We inspected a frozen 24-object, six-view image-space panel containing the ground truth, the no-adapter pipeline, fixed low and high scales, C3, and the tested layerwise conditions. The same reference draw and latent seed were used across conditions. In this author visual audit, color or material mismatch was marked in 18/24 panels and fine-detail loss in 21/24. These are descriptive counts from a fixed sample, not population rates; the audit did not separately count repeated-pattern frequency, and it did not show a stable visible winner across schedules. A metric-ranked example also retained a visible material mismatch.
>
> We agree that these comparisons do not establish unseen-view or baked-texture quality. The proposed Fresh C 24-object bake panel was retired: the available path re-unwraps UVs, 9/24 assets have coordinates outside `[0,1]`, and 5 assets (27 primitives) use unsupported `BLEND` alpha semantics. The seam metric also did not pass tests covering UV-island, repeat, mirrored-repeat, clamp, and mipmapped/minified boundaries. The separate historical N=20 result is limited to unlit base-color unseen-view evidence and has mixed endpoints; it does not establish PBR fidelity or seam consistency. We will therefore remove or narrow unseen-view, seam, and broad 3D-quality claims. We will not use the supplementary video as evidence in place of inspectable still comparisons.

**Action before submission:** Use a rights-cleared multi-method visual panel if the cited Fresh C contact sheet is confirmed to map to the 20 CC BY-cleared assets. The rights ledger covers two 24-asset panels (48 assets total): 43 are `FIGURE_ONLY` and five are `UNKNOWN`; specifically, two `UNKNOWN` assets belong to the legacy visual panel and three to the Fresh C GLB panel. The other 22 legacy visual assets are marked `FIGURE_ONLY` with attribution, but anonymous-supplement release status is still unresolved. Do not attach the complete 24-object panel to an anonymous supplement until that status is cleared. Keep the audit as internal claim-scope evidence in the meantime.

**Current status:** Partially answerable through existing non-human panels; unseen-view/PBR/seam claims must be withdrawn or separately validated. No new bake or seam experiment was run in this task.

### R1.2 — Main-adapter evaluation outside schedule-selection objects

**Proposed response**

> We agree that the previous pooled 300-object result included the 24 schedule-selection objects, and that the earlier strict-276 comparison changed the adapter/competing-schedule setup. We now have a revision-era Fresh C follow-up using the main adapter on 300 frozen objects disjoint from the historical UID sets. Its registered primary C3−GFL foreground PSNR contrast is +0.522 dB (95% object-bootstrap CI [+0.404, +0.641], p = 5.70×10⁻¹⁶; 68.7% of objects favor C3). The corresponding four-condition run passed its 1,200/1,200 row-integrity checks.
>
> This follow-up was motivated by results already observed in the earlier work. It is not a replication under the original registration and should not be described as validating the original +0.96 dB estimate or as proof that the estimate is unbiased or portable. The strict-276 C3−GFL result remains retrospective support with incomplete legacy input-tensor/runner provenance. We will report the Fresh C result separately and keep those historical estimates clearly labeled.

**Action before submission:** Present cohort provenance, the main-adapter identity, the prespecified Fresh C endpoint, and all available comparator results with endpoint-specific uncertainty. Keep the strict-276 estimate in a retrospective category.

**Current status:** Direct non-human follow-up evidence exists, with the stated registration and provenance limits.

### R1.3 — Texture variation is not texture fidelity

**Proposed response**

> We agree. Gradient magnitude, Laplacian variance, color variation, and related texture statistics measure variation; they do not by themselves show faithful reproduction. The visual audit records color/material mismatch in 18/24 panels and fine-detail loss in 21/24, and the metric-ranked example with the strongest selected PSNR result still had a visible material mismatch. We will describe these quantities as texture-variation diagnostics, report image endpoints separately, and remove language that treats larger gradients or Laplacian variance as evidence of fidelity. The image-space results and visual panels do not establish perceptual fidelity, so we will state that limitation explicitly.

**Action before submission:** Recheck every abstract, results, and discussion sentence that equates texture richness or metric change with fidelity. Any claim based on human preference remains outside this non-human response draft and must not be presented as verified here.

**Current status:** The image-metric interpretation can be corrected with existing evidence. This draft does not close any human-perception claim.

### R1.4 — Paired intervals, Edge-SSIM trade-off, and non-inferiority

**Proposed response**

> We agree that a confidence interval crossing zero cannot establish equivalence or non-inferiority. No non-inferiority margin was specified, so we will not make either claim. To quantify the C3-versus-high-fixed-scale trade-off using existing main-adapter outputs, we added a post-hoc paired analysis of the disjoint FRESH_CONFIRM_B cohort (N=150). For C3−GFH, Edge-SSIM was −0.01849 (nominal 95% paired object-bootstrap CI [−0.02146, −0.01553]); only 26/150 objects favored C3 on this endpoint. FG-PSNR was also lower for C3 by 0.753 dB [−0.928, −0.579], while full-image PSNR was higher by 0.749 dB [+0.655, +0.841]. This endpoint-specific pattern reinforces that there is no single cross-metric winner.
>
> This is a post-hoc analysis of a separate 150-object cohort, not a replacement estimate for the original 300-object Table 4 comparison. We will label it accordingly, report the Edge-SSIM cost, and moderate any broad “structure preservation” or “texture preservation” wording. We will not substitute the Fresh C C3−GFL Edge-SSIM contrast for the requested C3−GFH comparison.

**Action before submission:** Report paired estimates and intervals with direction conventions for every endpoint; state that no equivalence/non-inferiority margin was defined. Treat the new C3−GFH interval and its multiplicity results as exploratory, not confirmatory.

**Current status:** The requested high-scale contrast now has an existing-data paired interval, but it is post-hoc and uses N=150 rather than the original N=300. Full calculation details and source hash are in [the R1.4 audit note](R1_4_C3_minus_GFH_posthoc_audit_20261007.md).

### R1.5 — Reproducibility of FAC and code release

**Proposed response**

> We agree that the FAC experiments need enough detail to be reproducible, and that code release would help. FAC is not a load-bearing contribution in the current evidence disposition. However, the current submission candidate has not passed a clean-checkout rebuild: the candidate is not yet a compact committed package, complete generation provenance is unavailable for all historical outputs, and the current release disposition is FAIL. We therefore cannot claim that a reproducible FAC package is presently released. Before making such a claim, we must provide the exact FAC source, configuration, checkpoint and seed identifiers, training/inference commands, and required logs in a rights-cleared package and verify that package from a clean checkout. If these artifacts cannot be recovered, FAC should be removed from the paper rather than described as reproducible.

**Action before submission:** Close the reproducibility gate or remove FAC from the submission. Do not use “code released” or “fully reproducible” until a clean build has actually passed.

**Current status:** Open. The existing audit explicitly reports `REPRODUCIBILITY=FAIL` for the current candidate.

## Reviewer 2

### R2.1 — Methodological contribution and novelty

**Proposed response**

> We agree that a layer-by-timestep strength schedule is not, by itself, a new control primitive. [Scheduled Style Injection](https://openaccess.thecvf.com/content/CVPR2026W/NTIRE/papers/Kulkarni_Scheduled_Style_Injection_Expanding_the_Style-Content_Pareto_Frontier_in_Training-Free_CVPRW_2026_paper.pdf) is direct prior work on scheduling style strength across decoder depth and denoising time, including geometry-conditioned ControlNet use. We will cite this work and remove “first,” “novel control space,” schedule-optimality, and universal-mechanism claims. C3 will be described as a tested configuration on the existing MVPainter adapter path, not as an independently derived algorithm.
>
> The narrower contribution supported by the evidence is an implementation-specific empirical characterization: requested and capped/applied scales can differ; the logged correction magnitudes depend on layer, timestep, and residual; and the measured image endpoints vary by object and comparator. These results do not establish equal-realized-dose causal effects or a universal schedule. We recognize that the narrowed contribution may still be judged incremental for *Computers & Graphics*; the evidence cannot settle that venue-level judgment.

**Action before submission:** Rewrite the title/abstract/contribution paragraph and discussion to state the implementation and cohort boundaries; compare explicitly with Scheduled Style Injection and related adapter/guidance schedules.

**Current status:** Open / venue risk. The literature comparison is complete, but the paper has not been rewritten.

### R2.2 — CAI may formalize a schedule selected empirically

**Proposed response**

> We agree. CAI was not prospectively validated as a schedule selector and did not independently derive C3. We will remove it from the load-bearing contribution and describe it, at most, as a post-hoc descriptive vocabulary in the supplement. We will make no predictive, causal, or optimality claim from CAI.

**Action before submission:** Remove CAI from the core contribution and testable rationale, or remove it entirely if a descriptive supplement does not add value.

**Current status:** Can be closed by claim reduction; no new experiment is required for that correction.

### R2.3 — Generalization to a genuinely different backbone

**Proposed response**

> We agree that the MVPainter-style experiments alone do not establish cross-backbone generality. The existing MVDiffusion panel evaluates 75 objects and is a useful boundary test, but it is not a matched reproduction of the same residual-adapter intervention: the schedule acts on correspondence-aware decoder CPBlocks. The official SD2-depth weights could not be retrieved, so the panel used the unchanged `sd21_depth_compat` deployment base; all within-panel comparisons use that same base. Results are mixed and do not support a universal transfer claim. For example, L-LLH versus G-FL produced an interop-PSNR difference of −0.454 [−0.752, −0.160], while FG-LPIPS was −0.0027 [−0.0076, +0.0018].
>
> The separate MV-Adapter boundary panel contains 98 objects after one documented technical exclusion. Its exploratory corrected interaction tests do not confirm the broad layer-by-time interaction observed on the primary system. We will report these studies as interface-specific boundary tests, avoid pooling scores across systems, and withdraw universal transfer or architecture-causal language.

**Action before submission:** Label the MVDiffusion result exploratory and interface-specific; state the unavailable official depth weights and the compatibility base. Do not treat the MV-Adapter null interaction as proof of no interaction.

**Current status:** Partially addressed by existing cross-interface experiments. The evidence bounds generality; it does not validate a single policy across backbones.

## Reviewer 3

### R3 — Positive assessment

**Proposed response**

> We thank the reviewer for the positive assessment and for recognizing the work invested in the revision.

**Current status:** No additional technical action requested.

## Internal closure summary

| Item | Evidence-based status | What must happen before a submission-ready reply |
|---|---|---|
| R1.1 visuals / 3D / seams | Partial; image panels expose failures, while valid new bake/seam evidence is absent | Narrow or remove 3D/seam claims; clear the visual assets used in any supplement |
| R1.2 held-out main adapter | Fresh C supports a revision-era, disjoint main-adapter contrast | Keep registration and historical-estimate limitations explicit |
| R1.3 fidelity | Image-space evidence supports metric/visual separation only | Remove texture-variation-as-fidelity inference; handle human claims separately |
| R1.4 intervals | Existing-data C3−GFH interval calculated post hoc on N=150 | Add the result with exploratory label; no NI/equivalence claim |
| R1.5 FAC/release | Open; current clean-checkout reproducibility is FAIL | Verify a complete package or remove FAC |
| R2.1 novelty | Open / venue risk | Narrow claims and explicitly compare prior work |
| R2.2 CAI | Closeable by claim reduction | Remove predictive/derivation language |
| R2.3 backbone generality | Partial; different interfaces show bounded, mixed results | Restrict claims to tested interfaces and disclose compatibility base |
| R3 | Positive, no actionable issue | Thank reviewer |

No page/line locations can be supplied until the main manuscript is revised. This draft does not edit `01549`, analyze human-study answers, run a GPU experiment, modify the repository history, or upload anything to GitHub.

## Internal evidence pointers (not part of the reviewer letter)

- The non-human visual audit and 24-object contact sheet are in `/4T/CXY/MV-Painter/1006/evidence/audits/FORMAL_VISUAL_EVIDENCE_REPORT.md`; only its image-space section is relevant here. The corresponding legacy panel has two `UNKNOWN` source assets; the other 22 are `FIGURE_ONLY` with attribution, while anonymous-supplement release remains unresolved.
- Fresh C numerical authority: [FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv](../evidence/audits/FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv). Fresh C 24-object 3D disposition: [3D_CLAIM_RETIRED.md](../evidence/audits/3D_CLAIM_RETIRED.md). Seam disposition: [SEAM_CLAIM_FINAL_DISPOSITION_20261007.md](../evidence/audits/SEAM_CLAIM_FINAL_DISPOSITION_20261007.md).
- Asset rights: [FINAL_ASSET_RIGHTS_DISPOSITION_20261007.md](../evidence/audits/FINAL_ASSET_RIGHTS_DISPOSITION_20261007.md). Clean-checkout reproducibility: [FINAL_CLEAN_CHECKOUT_REPRODUCIBILITY_REPORT.md](../evidence/audits/FINAL_CLEAN_CHECKOUT_REPRODUCIBILITY_REPORT.md).
- Novelty assessment: [FINAL_R21_CONTRIBUTION_AUDIT.md](../evidence/audits/FINAL_R21_CONTRIBUTION_AUDIT.md). MVDiffusion and cross-backbone reports are in `/4T/CXY/MV-Painter/1006/evidence/audits/MVDIFFUSION_STANDARD_PANEL_REPORT.md` and `/4T/CXY/MV-Painter/1006/evidence/audits/CROSS_BACKBONE_MECHANISM_REPORT.md`.
- R1.4 paired calculation: [R1_4_C3_minus_GFH_posthoc_audit_20261007.md](R1_4_C3_minus_GFH_posthoc_audit_20261007.md). Its raw Fresh B input is in the shared checkout at `/4T/CXY/MV-Painter/1006/data/fresh_b/per_object_metrics.csv`; it is not bundled in this clean worktree.
