# Final reviewer closure matrix — 1008

**Review identity and source.** The verbatim text below is taken from the preserved local plain-text reviewer source, `Reviewer_Source/SECOND_ROUND_REVIEWER_COMMENTS.txt` (SHA-256 `52d5a02718cbcf1b452293fe5a6953231f10fc9ce4cdf6cce400e86deb521245`). Its inherited headings say “Initial submission”; those labels are retained exactly. The round assignment is author-confirmed in `1008/audits/ROUND1_01549_TO_ROUND2_1008_MAPPING.md`: 01549 was submitted after round one on 7 September 2026, this R1/R2/R3 packet reviews that version, and 1008 is the second-round revision. The separately extracted PDF text is secondary and is not represented here as a second-round original.

Page numbers refer to the final 16-page manuscript, 16-page Supplement, and 4-page response PDF. Evidence labels distinguish Fresh C from historical 01549 results and retrospective interface probes.

## Reviewer 1

### R1.1 — Appearance artifacts, full objects, and 3D evidence

> “Figures 4 and 6 show pronounced purple color shifts, repeated patterns, and substantial discrepancies from the reference appearance. Please provide full-object comparisons across a broader set of objects, including the unmodified pipeline and a competitive fixed-scale baseline. Baked meshes rendered from unseen viewpoints and an assessment of seams or cross-view consistency would help establish practical value. The supplementary video could not be assessed.”

- **01549 issue and 1008 action:** The submitted panels and texture-variation proxies did not establish broad appearance fidelity or downstream mesh quality. 1008 adds paired full-object/shared-ROI Fresh C examples (Figures 5 and 7), one hash-traced color-diagnostic panel (Figure 6), and a six-view/seven-condition Supplement panel. “No Adapter” means adapter scale zero; it is not the unset-scale native-default path. The selected Figure 6 case is not a reconstruction of the two unmapped legacy pink-shift cases.
- **Evidence identity:** The color diagnosis is a failure-enriched 26-object set (six legacy cases plus 20 Fresh C panels; three conditions, 78 object-condition records). GFL lowers mean foreground CIEDE2000 from No Adapter by 19.65 (95% CI [−26.37, −13.25]; 24/26 objects), but two legacy pink/purple cases remain. The attempted Fresh C bake failed its native-input gate; no valid Fresh C bake, unseen-view render, seam, or PBR result is reported. The video access issue remains unverified.
- **Locations:** Main Figures 5–7 (pp. 9, 12–13), Table 7 (p. 11), Limitations (p. 15); Supplement Figure S1 and S6–S7 (p. 12), S8 (p. 13), Table S1 (pp. 1–2), S13/Table S18 (p. 16); response pp. 1–2.
- **Closure:** `PARTIAL`. Visual evidence is broader and traceable, but it is still selected 2D evidence. No native-default comparison, validated color repair, valid Fresh C bake, seam/PBR assessment, or population-prevalence estimate is available.

### R1.2 — Same held-out protocol for the main adapter

> “Tables 4–6 evaluate the main adapter on 300 objects, including the 24 schedule-selection objects; Tables 7–8 use subsets of that pool. Table 9 uses the probe-disjoint 276-object subset but changes the adapter and competing schedules. It therefore does not directly confirm the main adapter’s reported 0.96 dB gain outside the selection set. Please evaluate the main adapter and relevant baselines under the same held-out protocol.”

- **01549 issue and 1008 action:** The original pooled estimate mixed the schedule-selection probe with evaluation, while the strict-276 table used a different adapter. Fresh C now supplies a disjoint matched evaluation; the historical +0.96 dB result is not claimed as numerically reproduced.
- **Evidence identity:** Fresh C uses 300 frozen UIDs disjoint from the original 24-object probe, prior eval300, training list, and clean-v2 eval300. The primary No Adapter/GFL/GFH/C3 run has 1,200/1,200 rows; Generic Linear and LLH are a 600/600 same-cohort addendum. Conditions share the frozen checkpoint, runner, inputs, target views, metric implementation, and object-seed policy. C3−GFL FG-PSNR is +0.522352 dB (95% object-bootstrap CI [+0.404160,+0.640669]); GFH and Generic Linear have more favorable means than C3 on all four displayed endpoints. C3/GFL applied deep/middle sums differ (82.5 vs. 62.5), so this is not a timing-only comparison.
- **Locations:** Main Methods (pp. 3–5), Tables 3–4 (p. 8), stage placement (pp. 10–11), Limitations (p. 15); Supplement S2 (p. 2), S3 (pp. 3–5), S4–S5 (pp. 6–11), S8–S9 (p. 13); response p. 2.
- **Closure:** `ADDRESSED UNDER THE MATCHED FRESH C PROTOCOL`, with the historical checkpoint/endpoint distinction disclosed. The result supports the named within-run comparison, not reproduction of +0.96 dB or schedule optimality.

### R1.3 — Texture variation versus texture fidelity

> “The paper acknowledges PSNR’s limitations and includes perceptual evaluations. However, the connection between the metric gains and faithful texture reproduction remains unclear given the visible artifacts. Please distinguish texture variation from texture fidelity: larger gradients or Laplacian variance can reflect unwanted artifacts as well as meaningful detail.”

- **01549 issue and 1008 action:** 1008 labels gradient, RGB variance, Laplacian variance, and high-frequency energy as variation diagnostics. They are not fidelity endpoints. The submitted 01549 3AFC remains a separate subjective-preference result and is not used as evidence of Fresh C fidelity or baked 3D quality.
- **Evidence identity:** Fresh C measures target-view image-space agreement. The failure-enriched color set and selected examples are descriptive; no Fresh C texture-fidelity ground truth is available.
- **Locations:** Main metric definitions (p. 3), Figures 4–7 (pp. 8–13), Table 9 (p. 14), Limitations (p. 15); Supplement S2 (p. 2), S7 (p. 12), S12 (p. 15); response p. 2.
- **Closure:** `ADDRESSED WITH LIMIT`. Image agreement, variation, subjective preference, color agreement, fidelity, and baked appearance remain distinct outcomes.

### R1.4 — Paired intervals, Edge-SSIM, and non-inferiority

> “A confidence interval crossing zero for the FG-SSIM difference does not establish equivalence or non-inferiority. Table 4 also shows lower Edge-SSIM for TCAS than for aggressive scaling, 0.529 versus 0.559. Please report paired intervals, acknowledge this trade-off, and either justify a non-inferiority margin or moderate the preservation claim.”

- **01549 issue and 1008 action:** 1008 reports paired object-bootstrap intervals and no longer uses a zero-crossing interval as an equivalence or non-inferiority claim. It labels the Fresh C endpoint trade-off and does not present historical Table 4 values as a replicated comparison.
- **Evidence identity:** Fresh C C3−GFH Edge-SSIM is −0.01881 (95% object-bootstrap CI [−0.02084, −0.01683]). No non-inferiority margin was prespecified.
- **Locations:** Main Table 4 and endpoint discussion (p. 8); Supplement S2 (p. 2); response p. 3.
- **Closure:** `ADDRESSED WITH LIMIT`. Paired uncertainty and the trade-off are reported; equivalence/non-inferiority is not established or claimed.

### R1.5 — FAC reproducibility and code

> “Section 4.1.3 provides useful details, but it is still hard to reproduce the FAC experiments. The code is encouraged to be released,”

- **01549 issue and 1008 action:** The negative FAC re-examination is retained as a first-round 01549 result, not a new 1008 rerun. The response discloses the recovered training-list discrepancy and missing run-bound provenance; it makes no public-code-release claim.
- **Evidence identity:** The submitted protocol reports seven trained configurations and a separate 12-object untrained control. A recovered configuration references 1,200 training objects rather than the reported 1,706; a run-bound seed/output/checkpoint/runtime manifest was not recovered.
- **Locations:** Main FAC discussion (p. 14) and Limitations (p. 15); Supplement S11/Table S16 (p. 14); response p. 3.
- **Closure:** `PARTIAL`. The historical result and limits are transparent, but a complete independent FAC replay and public code release are not available.

## Reviewer 2

### R2.1 — Contribution beyond schedule selection

> “The core methodological contribution remains quite limited. I am not yet convinced that this constitutes a sufficiently substantial methodological contribution beyond schedule selection for an existing adapter.”

- **01549 issue and 1008 action:** The revision retains TCAS/C3 and the MVPainter/GeoTex task, while removing any claim that layer/time scheduling itself is new. It distinguishes ControlNet/T2I-Adapter conditioning-strength controls, SSI’s existing layer/time and geometry-ControlNet schedules, and the GeoTex residual multiplier already used as a fixed scale in 01549. TCAS reuses that control point; its task-specific contribution is the measured requested/applied/residual account and bounded image-space comparison, not a new branch or selector.
- **Evidence identity:** Fresh C supports C3−GFL on registered FG-PSNR but GFH and Generic Linear have stronger means on all four endpoints and C3/GFL applied sums differ. The separate post-inspection strict-276 placement analysis favors temporal L–L–H on six endpoints, with realized corrections unmatched. A3b retains response heterogeneity only; raw-L2 cross-layer dose interpretations are withdrawn.
- **Locations:** Main Introduction/Related Work (pp. 1–2), TCAS Method (pp. 3–5), evaluation tables (pp. 7–14), Limitations/Conclusion (p. 15); Supplement S3–S5 (pp. 3–11), S9 (p. 13), S12/Table S17 (p. 15); response pp. 3–4.
- **Closure:** `PARTIAL; EDITORIAL NOVELTY RISK`. The task/interface-specific empirical contribution is explicit, but the journal’s novelty threshold remains an editorial judgment. No unreported experiment is used to strengthen it.

### R2.2 — CAI and empirical schedule selection

> “The CAI formulation appears to formalize an empirically selected schedule rather than derive it independently.”

- **01549 issue and 1008 action:** 1008 removes the CAI selector, proposition, proof, and optimality claim. TCAS’s injection equation, three-stage profile, C3 definition, and 24-object development history remain as a historical candidate, not a verified ranking or unique optimum.
- **Evidence identity:** The 24-object development record is retained with its row-level provenance limits; no later result is represented as a preregistered CAI derivation.
- **Locations:** Main TCAS Method (pp. 3–5), Table 2 (p. 7), Figure 4 (p. 8); Supplement S10/Table S15 (p. 14); response p. 4.
- **Closure:** `ADDRESSED BY WITHDRAWING THE CAI DERIVATION/OPTIMALITY CLAIM`; TCAS itself is retained.

### R2.3 — Cross-backbone generalization

> “Cross-backbone generalization remains the most important missing experiment. The main experiments are conducted within a single MVPainter-style architecture family. Section 4.7 expands the analysis to adapters with different residual magnitudes and scale semantics, and shows three possible high-scale behaviors: texture flattening, high-frequency artifact amplification, or negligible effect. This analysis is interesting, but it does not substitute for evaluation on a genuinely different geometry-conditioned multi-view diffusion backbone.”

- **01549 issue and 1008 action:** 1008 keeps the earlier adapter-dependence study distinct from cross-backbone evidence and reports the two auxiliary interfaces separately. It does not claim matched TCAS transfer.
- **Evidence identity:** The 76-object MV-Adapter panel scales condition-guider features before UNet down-block residual injection; its schedule extension is retrospective and endpoint-dependent. MVDiffusion scales/interpolates CPBlock outputs while depth is concatenated into the latent and left unscaled; its 75-object panel used a compatibility base and was not rerun on the native mirror. A separate one-object mirror check is not a panel replication. The 525-row MVDiffusion source was audited; five paired comparisons × six metrics are reported as raw A−B with 30 pointwise, unadjusted CIs. In P1, L–LLH−G–FL CIEDE2000 is +1.373021 [+0.418244,+2.374678], indicating higher/worse color error for L–LLH; the archived −1.373 was improvement-coded. The full table states each metric’s favorable direction.
- **Locations:** Main Cross-Interface Evaluation/Table 8 (pp. 13–14) and Limitations (p. 15); Supplement S5 (pp. 6–11), Tables S10–S12 (pp. 10–11); response p. 4.
- **Closure:** `NOT FULLY ANSWERED`. These are interface-specific sensitivity results, not a matched second-backbone evaluation; cross-backbone generalization remains unestablished.

## Reviewer 3

The source gives a positive assessment and asks for no new technical change. The response acknowledges it on p. 1; no experiment or claim is attributed to Reviewer 3.

## Readiness summary

- `REVIEWER_RESPONSE_READY = YES, WITH EXPLICIT PARTIAL/OPEN ITEMS`: every technical point has a sourced response, verified location, evidence identity, and remaining-risk statement.
- `SUBMISSION_READY = NO`: author metadata/attribution checks and acceptance of the open R1.1, R2.1, and R2.3 risks remain. `SUBMISSION_APPROVED = NO`; no journal submission has been made.
