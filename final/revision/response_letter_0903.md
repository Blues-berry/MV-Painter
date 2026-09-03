# Response to Reviewers (v2, 2026-09-03) — aligned with final_0903.tex

> Status: aligned with the 0903 revision strategy (original submitted structure and
> conclusions preserved; all changes are additions or clarifications). All statistics
> quoted below are verified against the genuine per-trial records and output artifacts.

**Response to Reviewers**

Manuscript: *Adapter Scaling Trade-off and Timestep-Conditioned Scheduling in Multi-view Diffusion Texture Generation* (CAD/Graphics 2026, Paper 75; recommended to *Computers & Graphics* as VSI: CAG_SS_CAD/Graphics 2026)

Dear Editors and Reviewers,

We thank the CAD/Graphics 2026 program committee for recommending this manuscript, upon revision, for publication in *Computers & Graphics*, and we thank all three reviewers for their careful and constructive comments. **This revised manuscript is recommended by CAD/Graphics 2026.** All original results and conclusions are retained; following the reviewers' suggestions we have added new analyses, documentation, and controlled experiments, as detailed below.

## Summary of additions

1. **Implementation and dataset details (Sec. 4.1).** New paragraphs specify the data pipeline (Objaverse objects; ground truth rendered with Blender Cycles, 17 views at 512×512; six target views), the training/evaluation split (1,118 training objects and 300 evaluation objects, with **zero identifier overlap**, verified), the probe/holdout structure within the 300-object pool, the adapter architecture and scale-application semantics, the scheduler (Euler discrete, 50 steps), the fixed seed (42) with shared initial latents, and the exact metric implementations.
2. **A formal stage-utility model (CAI) (Sec. 3.3).** The low–high–low schedule is now *derived* rather than assumed: finite-difference stage utilities with structural guardrails, a bang–bang selection argument under an additive stage approximation, and the measured utilities with 95% CIs.
3. **Disjoint holdout verification (Secs. 4.1, 4.7).** We disclose that the 24-object probe is part of the 300-object pool, and we now verify all transfer claims on a **disjoint 276-object holdout** ($\mathrm{obj}_{0024}$–$\mathrm{obj}_{0299}$); the full-pool tables are retained unchanged.
4. **FAC controlled re-examination (Sec. 4.6).** Following the reviewers' request, we report the complete FAC training configuration (roughly 6×10³ trainable parameters; the same enhanced denoising objective as the base adapter; Adam, 2,000 steps; training pool strictly disjoint from all evaluation objects) and a strictly paired re-evaluation with controls that localize the failure. A warm-start control (gate initialized at the exact C3 envelope, untrained) is statistically indistinguishable from TCAS; a two-stage control that freezes the gate at the C3 envelope and trains only the spatial/frequency controllers still loses 2.6 dB; and further configurations (envelope-penalty joint training, fidelity-weighted objectives, gentle schedules) confirm the same pattern, with degradation increasing monotonically in the amount of controller training. Preserving the envelope is therefore necessary but not sufficient: the limitation lies in the learned-modulation training signal itself, and TCAS — training-free — remains the main and sole method.
5. **Adapter-dependence analysis (Sec. 4.7).** New mechanism probes (three adapter regimes; a per-layer cap ablation; a residual-magnitude sweep; a cross-adapter stage ablation), a boundary/peak sensitivity sweep (15 candidates), and the reviewer-suggested generic schedules (linear warm-up, cosine bump) transferred to the 300-object pool with disjoint-holdout statistics.
6. **Statistical reporting clarified (Secs. 4.1, 4.5).** The meaning of ±, the exact paired tests, and the bootstrap procedures (10,000 resamples, percentile CIs) are now stated; the aggregation order of the texture tables is written explicitly in their captions.

---

## Reviewer #1

### R1-C1. Data splits and FAC evaluation are unclear; FAC requires a fully described training objective and separate train, tuning, and test sets.

**Response.**
*(a) Data splits.* Sec. 4.1 now documents the complete pipeline: all objects come from Objaverse; ground truth is rendered with Blender (Cycles, 512×512, white background); the training pool contains 1,118 rendered objects and the evaluation pool contains 300 rendered objects, and we verified that the two identifier sets intersect in zero objects, so no evaluation object was seen in adapter training. Within the 300-object pool, the 24-object probe is $\mathrm{obj}_{0000}$–$\mathrm{obj}_{0023}$; we now disclose that the probe is part of the pool, and we verify every transfer claim on the strictly disjoint 276-object holdout $\mathrm{obj}_{0024}$–$\mathrm{obj}_{0299}$ (Secs. 4.5, 4.7). The CLIP-IQA (50 objects) and preference-study (30 objects) subsets are drawn from the same pool. The 50-object scale-sweep set comprises the first 50 objects of the pool, and the 26-object audit set is a purposive subset of these 50 selected to span the observed range of per-object ΔFG-SSIM behaviour; all evaluation sets are subsets of the 300-object pool, and no training object appears in any of them.
*(b) FAC.* Sec. 4.6 now provides the full configuration: roughly 6×10³ trainable parameters (LTAG/GSG/FSC controllers only; base model, VAE, and adapter frozen), the same enhanced denoising objective as the base adapter, Adam with 2,000 training steps, and a training pool strictly disjoint from all evaluation objects (no evaluation object is used for training or model selection). We additionally report five controls spanning the most favourable training conditions we could construct: a warm-start control (gate initialized at the exact C3 schedule; recovers baseline-level results, validating the evaluation path), a two-stage control with the gate frozen at the C3 envelope (−2.6 dB, wins 4/300), an envelope-penalty joint training (−2.7 dB), a fidelity-weighted objective (−2.4 dB), and a gentle schedule with fourfold-reduced training (−1.1 dB). The degradation increases monotonically with the amount of controller training, and no configuration reaches the training-free schedule; the limitation lies in the learned-modulation training signal itself, which trades foreground fidelity for denoising-objective loss. The controlled outcome, its mechanism, and its scope are reported transparently in Sec. 4.6, and the complete dose–response table over all seven trained configurations is provided in the supplementary material.

### R1-C2. Provide the exact implementation and checkpoints, conditioning, resolution, sampler, scheduler, prompts or references.

**Response.** The new "Implementation and dataset details" paragraph (Sec. 4.1) specifies: the base pipeline (MVPainter-style joint six-view latent diffusion UNet, used frozen together with its VAE), the adapter input (5-channel normal/depth/mask) and multi-scale injection levels, the adapter checkpoint used for all tables and its scale-application semantics (the requested scale is applied multiplicatively at every injected layer), the scheduler (Euler discrete, 50 steps), the fixed seed (42) with shared initial latents, the six target views and ground-truth rendering configuration, and the exact metric implementations (foreground-masked SSIM/PSNR, edge masks from depth/normal discontinuities, LPIPS-Alex, foreground Laplacian-variance/RGB-std/gradient diagnostics). The pipeline is reference-image-conditioned; no text prompts are used.

### R1-C3. Preference decisions are clustered by participant and object; use mixed-effects analysis or participant- and object-level bootstrap intervals, and report study instructions, randomization, and other design details.

**Response.** The study design is now fully reported (Sec. 4.5): blinded 3AFC, three criteria, per-trial randomization of the left-to-right condition order, participants not informed which method produced which image, instructions, and the fact that every participant judged all 30 objects under all three criteria (720 = 24 × 30 × 3 first-choice decisions per criterion). We additionally report **two-level cluster-bootstrap 95% CIs** (resampling participants and objects with replacement, 10,000 resamples) for the preference shares: C3's overall-quality share is 58.0% (CI [50.1%, 65.8%]), exceeding the conservative and aggressive baselines by +33.6 points (CI [19.3, 47.2]) and +40.5 points (CI [29.4, 51.8]) — both significant — while the baselines' single-criterion advantages are not significant (texture: +6.7 points, CI [−7.9, 21.5]; shape: +5.3 points, CI [−6.7, 17.9]). Overall quality is the only criterion with a significant preference, supporting the interpretation of TCAS as the preferred balance. We report the cluster bootstrap rather than a binomial test, since the latter would overstate significance under clustering.

---

## Reviewer #2

### R2-W1. Generalizability is insufficiently demonstrated; all experiments run on a single pipeline.

**Response.** We agree that the main experiments use a single pipeline, and the revision addresses this directly rather than claiming unsupported generality. New Sec. 4.7 ("Adapter Dependence of High-Scale Failure Modes") reports controlled mechanism probes on additional adapter checkpoints of the same architecture under an identical inference protocol: across three regimes, uniform high scale produced (i) texture flattening with the main adapter studied in the paper, (ii) high-frequency artifact amplification and color overshoot with a strong-residual adapter under per-layer caps, and (iii) no appreciable effect with a deliberately weakened adapter. A per-layer cap ablation reproduces both directions on a single checkpoint, isolating the scale semantics as a determining factor; a residual-magnitude sweep shows the intervention strength is monotone in the trained residual magnitude; and a cross-adapter stage ablation shows that even the most sensitive denoising stage is adapter-dependent. What remains stable is stated precisely: in every regime where scaling had a non-negligible effect, the low–high–low temporal structure (C3) yielded the best fidelity–structure balance, because concentrating correction in the middle stage exploits the stage-dependent roles of the diffusion process itself. We explicitly acknowledge in the response and in the Limitations that the evidence remains within one architecture family and that cross-backbone validation is future work; the contribution is now framed as a conditional structural rule (with re-estimable stage utilities) rather than a universal optimum.

### R2-W2. TCAS is heuristic; the boundaries and values are not explained.

**Response.** The revision replaces the heuristic framing with a formal derivation plus robustness checks: (1) the CAI model (Sec. 3.3), now stated as **Proposition 1 with a proof** — under the additive stage-utility approximation and per-stage structural guardrails, the admissible schedule maximizing fidelity is bang–bang, and the measured utilities select the low–high–low assignment ($U_e=-0.788$ dB, CI $[-1.420,-0.156]$, guardrail-violating; $U_m=+0.574$ dB $[0.391,0.756]$; $U_l=+0.077$ dB $[0.006,0.149]$, conservative tie-break); the proposition is explicitly conditional on the measured adapter regime; (2) a boundary/peak sensitivity sweep (three windows × five peaks = 15 candidates, Sec. 4.7) shows the canonical middle-third window lies in a stable high-performance region (2.50: 16.71 dB; best-in-window 2.75: 16.79 dB, with worse diagnostics and lower FG-SSIM), so C3 is a robust region rather than a boundary-sensitive point estimate; (3) Table 3 already rules out monotonic decay/warm-up and smooth-bump alternatives, and the holdout transfers below rule out the remaining candidates.

### R2-W3. Subset sources/construction/overlap and FAC training details are insufficient.

**Response.** Addressed in Sec. 4.1 (see R1-C1a): pool construction, zero train–eval overlap, and the probe/holdout split with the overlap now disclosed. For FAC, Sec. 4.6 provides the complete training configuration and the controlled re-examination (see R1-C1b), including the warm-start control and the scoped interpretation; TCAS remains the main and sole method.

---

## Reviewer #3

### R3-C1. Competing schedules are validated only on the probe set; evaluate cosine bump and linear warm-up on the large independent set.

**Response.** Done. Linear warm-up and the cosine bump were evaluated on the 300-object pool, on the strong-residual, per-layer-capped adapter instance described in Sec. 4.7 (the only instance for which all competing schedules were regenerated at the 300-object scale), and the transfer claims use the disjoint 276-object holdout (Sec. 4.7): C3 improves PSNR over linear warm-up by +0.323 dB (95% CI $[0.263, 0.386]$, 214/276 wins) while matching its structure (FG-SSIM difference −0.001), and over the cosine bump by +0.902 dB (95% CI $[0.824, 0.981]$, 253/276 wins) with a higher FG-SSIM (+0.046). Together with the transferred trapezoid (+0.258 dB, CI $[0.207,0.308]$) and Gaussian-peak (+0.324 dB, CI $[0.281,0.367]$) schedules, the holdout ordering matches the probe: warm-up approaches C3 in structure but loses in signal fidelity, and the smooth bump loses in both because its effective high-scale duration is shorter than the full middle third.

### R3-C2. The aggregation procedures in the texture tables appear to differ; clarify the computation.

**Response.** The reviewer is correct. The two tables used different aggregation orders (a ratio of per-condition means versus the mean of per-object ratios). The revised captions state the rule explicitly: absolute foreground statistics are means over objects and views, and each ratio in Table 7 is the **mean over objects of the per-object ratio relative to the corresponding $s = 1.25$ statistic** (equal object weighting). All win rates and confidence intervals have been re-verified from the per-object results.

### R3-C3. Clarify the statistical reporting (±, paired test, bootstrap procedure).

**Response.** Clarified at first use (Sec. 4.1) and in the relevant captions. For CLIP-IQA (Table 8): ± denotes the **standard deviation across the 50 objects**; the paired comparison is a **two-sided paired t-test** ($t(49)=10.52$, $p\approx3.6\times10^{-14}$ for C3 vs. $s{=}2.50$); the 95% CI of the paired mean difference is a **percentile bootstrap over objects with 10,000 resamples** ($[0.0037, 0.0054]$). For the preference study, two-level (participant- and object-level) cluster-bootstrap intervals are reported in Sec. 4.5 (see R1-C3): C3's overall-quality advantage is significant, while the baselines' single-criterion advantages are not. All other paired statements (stage utilities, holdout deltas) use object-level paired statistics with percentile bootstrap 95% CIs, and the procedure is stated once in Sec. 4.1.

### R3-C4. More complete dataset/implementation details; FAC training data, loss, optimization, parameter count, exclusion of the 300 validation objects.

**Response.** See R1-C1a/R1-C2 for the dataset and implementation details, including the verified zero train–eval overlap. For FAC, Sec. 4.6 now specifies exactly what is requested: training data (the 1,118-object adapter training pool, strictly disjoint from all evaluation objects; no evaluation object is used for training or model selection), loss (the same enhanced denoising objective as the base adapter), optimization (Adam, 2,000 steps), parameter count (roughly 6×10³ trainable parameters), and the strictly paired evaluation with a warm-start control. The controlled outcome and its scoped interpretation are reported in the manuscript.

---

## Checklist of changes

| Reviewer point | Change | Location (revised manuscript) |
|---|---|---|
| R1-C1a / R2-W3 / R3-C4 (splits, overlap) | Dataset/implementation details; overlap disclosed; disjoint holdout verification | Sec. 4.1, 4.7 |
| R1-C1b / R2-W3 / R3-C4 (FAC) | Full training configuration; controlled re-examination; scoped interpretation | Sec. 4.6 |
| R1-C2 / R3-C4 (implementation) | Checkpoint, scale semantics, scheduler, steps, seed, views, rendering, metrics | Sec. 4.1 |
| R1-C3 / R3-C3 (statistics) | Design details; ± defined; tests named; bootstrap procedures stated | Sec. 4.1, 4.5 |
| R2-W1 (generality) | Adapter-dependence analysis; conditional framing; boundary acknowledged | Sec. 4.7, 5 |
| R2-W2 (heuristic schedule) | CAI model; boundary/peak sensitivity sweep | Sec. 3.3, 4.7 |
| R3-C1 (large-set schedules) | linear warm-up + cosine bump on the 300-object pool (disjoint holdout statistics) | Sec. 4.7 |
| R3-C2 (aggregation) | Aggregation order stated in captions | Sec. 4.5 |

We believe the revision is substantially strengthened, and we thank the reviewers again: their comments directly led to the CAI model, the disjoint holdout protocol, and the adapter-dependence analysis.

Sincerely,
The Authors
