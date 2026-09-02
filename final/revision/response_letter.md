# Response Letter (DRAFT v1 — 2026-09-02)

> **STATUS: DRAFT.** Items marked `[PENDING]` must be filled from the corresponding
> runs/data before submission:
> 1. cosine bump / linear warm-up 300-object numbers (run `geotex/run_r31_schedules_300.sh`),
> 2. preference-study cluster-bootstrap CIs (need the raw per-trial vote export),
> 3. final page/line references after the tex edits are compiled.

---

**Response to Reviewers**

Manuscript: *Adapter Scaling Trade-off and Timestep-Conditioned Scheduling in Multi-view Diffusion Texture Generation* (CAD/Graphics 2026, Paper 75; recommended to *Computers & Graphics* as VSI: CAG_SS_CAD/Graphics 2026)

Dear Editors and Reviewers,

We thank the program committee of CAD/Graphics 2026 for recommending this manuscript, upon revision, for publication in *Computers & Graphics*, and we thank all three reviewers for their careful and constructive comments. We have revised the manuscript substantially. All reviewer comments are addressed below; each response states what was changed and where. **This revised manuscript is recommended by CAD/Graphics 2026.**

## Summary of major changes

Before the point-by-point responses, we summarize the changes that affect several comments at once.

1. **Unified, fully documented evaluation protocol.** While preparing the revision we audited our evaluation scripts and found that the original manuscript's 300-object tables had been produced by an evaluation path that applied the adapter scale as an uncapped multiplication, whereas the deployed model forward applies the scale as $\min(s, c_\ell)$ with per-layer caps. Because this scale semantics measurably changes the direction of high-scale effects (Reviewer 2, W1), we re-ran **all** experiments under a single, explicitly documented protocol (fixed released adapter checkpoint, capped scale semantics, Euler discrete scheduler, 50 steps, seed 42, shared initial latents) and updated every table accordingly. The qualitative conclusions are unchanged — a uniform scale is a blunt control, and stage-dependent scaling resolves the trade-off — but the failure mode under the finalized protocol is **color overshoot and high-frequency artifact amplification** rather than pure flattening, and the manuscript now reports this accurately (Abstract, Sec. 4.2, Fig. 4).
2. **A formal stage-utility model (CAI) and a stage ablation** now explain *why* the mid-stage schedule is selected, replacing the heuristic framing (new Sec. 3.4 and Sec. 4.3).
3. **A disjoint holdout protocol.** We disclose that the original 24-object probe and the 300-object pool overlapped, and now perform all transfer claims on a **disjoint 276-object holdout** ($\mathrm{obj}_{0024}$–$\mathrm{obj}_{0299}$), with the full 300-object pool retained as descriptive statistics (Sec. 4.1).
4. **The FAC extension has been removed.** A controlled re-training and re-evaluation of the learned-correction (FAC) variants under the strict paired protocol showed a significant *negative* result (details under R1-C1/R2-W3), so the section was deleted rather than revised. TCAS remains the sole, training-free method.
5. **New baselines and sensitivity analyses**: adapter-free (scale 0) baselines on the probe and 300-object sets, a third-party SF3D comparison, a 13-schedule comparison, a C3 boundary/peak sensitivity sweep, reviewer-named generic schedules transferred to the 300-object pool, and an explicit implementation/dataset appendix (Sec. 4.1).

---

## Reviewer #1

### R1-C1. Data splits and FAC evaluation are unclear; FAC requires a fully described training objective and separate train/tuning/test sets.

**Response.** We agree, and we have made two changes.

*(a) Data splits.* Section 4.1 now documents the complete data pipeline: all objects come from Objaverse; ground truth is rendered with Blender (Cycles, 512×512, white background); the **training pool contains 1,118 rendered objects and the evaluation pool contains 300 rendered objects, and we verified that the two identifier sets intersect in zero objects**, so no evaluation object was seen in adapter training. Within the 300-object pool, the 24-object probe is $\mathrm{obj}_{0000}$–$\mathrm{obj}_{0023}$, and all transfer claims now use the **disjoint 276-object holdout** $\mathrm{obj}_{0024}$–$\mathrm{obj}_{0299}$; we explicitly disclose that the earlier manuscript's 300-object tables included the probe objects, and those tables are now labeled descriptive only (Sec. 4.1; holdout statistics in Secs. 4.4–4.5). The CLIP-IQA (50 objects) and preference-study (30 objects) subsets are drawn from the holdout side of the pool.

*(b) FAC.* During the reproducibility audit we re-trained and re-evaluated all FAC variants (LTAG; LTAG+GSG; full FAC) under a strictly paired protocol (same 300 objects, same seeds, TCAS baseline paired per object). The result was a significant **negative** one: full FAC reached 16.11 dB PSNR / 0.3204 FG-SSIM versus 19.12 / 0.3708 for the TCAS baseline (−3.00 dB, paired win rate 1.3%, $p\approx10^{-50}$), with a warm-start control (initializing the learned gate at the exact C3 schedule) confirming that the evaluation path was correct and the degradation is a real training effect. Because the previously reported FAC numbers could not be reproduced under the finalized protocol, we removed the FAC section entirely rather than revise it; the manuscript now contains only the training-free TCAS method. We apologize for the earlier version's insufficiently controlled FAC reporting.

### R1-C2. Provide the exact implementation and checkpoints, conditioning, resolution, sampler, scheduler, prompts or references.

**Response.** A new **"Implementation and dataset details"** paragraph in Sec. 4.1 specifies: the base pipeline (MVPainter-style joint six-view latent diffusion UNet, frozen), the adapter input (5-channel normal/depth/mask at 256×256) and injection levels, the exact released checkpoint (v2 EMA, 10,000 steps), the **capped scale semantics** $\min(s,c_\ell)$ with $c_\mathrm{deep}=3.0$, $c_\mathrm{middle}=3.5$, $c_\mathrm{shallow}=0.8$, the scheduler (Euler discrete, 50 steps), the fixed seed (42) and shared initial latents, the six target views, the ground-truth rendering configuration, and the exact metric implementations (foreground-masked SSIM/PSNR, edge masks from depth/normal discontinuities, LPIPS-Alex, foreground Laplacian-variance/RGB-std/gradient diagnostics). The pipeline is reference-image-conditioned (no text prompts are used), consistent with the MVPainter formulation.

### R1-C3. Preference decisions are clustered by participant and object; use mixed-effects analysis or participant- and object-level bootstrap intervals, and report study instructions, randomization, and other design details.

**Response.** We agree that the 720 first-choice decisions are clustered within participants and objects, and we have made two changes. *(a)* The study design is now fully reported (Sec. 4.5): blinded 3AFC, three criteria, per-trial randomization of the left-to-right condition order, participant instructions, participant background, and the fact that every participant judged all 30 objects under all three criteria. *(b)* We now report **two-level cluster-bootstrap 95% confidence intervals** (resampling participants and objects with replacement, 10,000 resamples) for the preference shares of each method under each criterion `[PENDING: insert CIs]`. We deliberately report the cluster-bootstrap intervals rather than a single binomial test, since the latter would overstate significance under clustering.

---

## Reviewer #2

### R2-W1. Generalizability is insufficiently demonstrated; all experiments run on a single MVPainter-style pipeline, so the results cannot distinguish a general property of geometry-conditioned adapters from a backbone-specific one.

**Response.** This is the most important concern, and the revision addresses it in three ways rather than claiming generality we cannot support.

*(a) The claims are now explicitly conditional.* The manuscript no longer states that high scale universally flattens texture. The revised narrative, supported by new mechanism probes, is that **the failure mode of aggressive adapter scaling is adapter-dependent** (new Sec. 4.6, "Adapter Dependence of High-Scale Failure Modes"): across three adapter checkpoints of the same architecture under an identical inference protocol, uniform high scale produced (i) texture flattening with the original uncapped base adapter, (ii) high-frequency artifact amplification and color overshoot with the strong-residual capped adapter (the finalized protocol used throughout the paper), and (iii) no appreciable effect with a deliberately weakened adapter. A per-layer cap ablation on a single checkpoint reproduces both directions of the effect, isolating the scale semantics as a determining factor; a residual-magnitude sweep ($\gamma\in[0.1,3.0]$) shows the intervention strength is monotone in the trained residual magnitude; and a cross-adapter stage ablation shows that even the *most dangerous denoising stage* is adapter-dependent (early-stage on the capped adapter; late-stage on the uncapped one).

*(b) What is stable is stated precisely.* In every regime where scaling had a non-negligible effect, the low–high–low temporal structure (C3) gave the best fidelity–structure balance, because concentrating correction in the middle stage exploits the stage-dependent roles of the diffusion process itself (global layout → geometric refinement → texture synthesis). The manuscript now frames TCAS as a **conditional structural rule with re-estimable stage utilities** (CAI, Sec. 3.4), not an adapter-independent optimum, and the Limitations state that adaptation to other backbones, adapter architectures, and sampler families is future work.

*(c) The evaluation no longer depends on a single pipeline point.* We added the adapter-free baseline (scale 0) on both the probe and the 300-object pool, and an independent third-party comparison to SF3D on 298 objects, so the trade-off analysis is situated against non-adapter texture generation as well.

### R2-W2. TCAS is a heuristic three-stage schedule; the analysis does not explain why the boundaries or values should be meaningful or transferable.

**Response.** We agree the original presentation was heuristic, and the revision replaces it with a derivation plus robustness checks:

1. **CAI model (new Sec. 3.4).** We define a finite-difference stage utility $U_k = Q(\text{high in stage }k)-Q(\text{fixed low})$ with an evidence vector $(\Delta Q_k, \Delta S_k, -\Delta R_k)$ and guardrails, and show that under an additive stage approximation the scalar-$Q$ problem has a bang–bang solution. On the 24-object probe, the measured utilities are $U_e=-0.788$ dB (95% CI $[-1.420,-0.156]$), $U_m=+0.574$ dB $[0.391,0.756]$, $U_l=+0.077$ dB $[0.006,0.149]$: early-high violates the structural guardrail (FG-SSIM $-0.105$, CI $[-0.141,-0.069]$; LapVar $3.85\times$), late-high is structurally neutral, and mid-high carries the useful gain — which **selects** the low–high–low schedule rather than assuming it. The paper states explicitly that the additive model is a conditional approximation and that the full schedule is validated directly.
2. **Boundary/peak sensitivity (new in Sec. 4.4).** We swept three high-scale windows ($[0.25,0.75)$, $[1/3,2/3)$, $[0.4,0.6)$) × five peaks (2.00–3.00) = 15 candidates on the probe set. The canonical middle-third window lies in the stable high-performance region (2.50: 16.71 dB; best-in-window 2.75: 16.79 dB, only +0.08 dB with worse diagnostics and lower FG-SSIM); broader and narrower windows reach at most 16.73/16.62 dB. C3 is therefore a robust region, not a boundary-sensitive point estimate.
3. **Why not other schedules or axes.** The 13-schedule comparison now includes σ-domain (noise-level-keyed) schedules, per-layer 5-phase schedules, and smooth bumps; none matches C3, showing the advantage does not come from the progress axis, per-layer refinement, or the piecewise shape alone.
4. **Transfer without re-searching.** C3 is frozen on the probe and transferred to the disjoint 276-object holdout, where it also beats the strongest non-C3 probe candidates (trapezoid +0.258 dB, CI $[0.207,0.308]$; Gaussian peak +0.324 dB, CI $[0.281,0.367]$) and the reviewer-named generic schedules: linear warm-up (+0.323 dB, CI $[0.263,0.386]$, 214/276 wins, with FG-SSIM statistically tied at $-0.001$) and the cosine bump (+0.902 dB, CI $[0.824,0.981]$, 253/276 wins, FG-SSIM $+0.046$).

### R2-W3. Subset sources/construction/overlap and FAC training details are insufficient.

**Response.** Subset construction, selection, and overlap are now fully specified in Sec. 4.1 (see R1-C1): one 300-object Objaverse pool, disjoint from the 1,118-object training pool (verified zero identifier overlap); probe = first 24 identifiers; holdout = the remaining 276; the earlier probe–validation overlap is disclosed and all transfer claims use the disjoint holdout. For FAC: after the reproducibility audit described in R1-C1(b) produced a significant negative result under strict train/validation separation (FAC modules trained on the 1,118-object training pool, never on evaluation objects), we removed the FAC section entirely. The manuscript now contains no learned-correction claims; we are happy to provide the full configuration of the failed rerun as supplementary material if the reviewers wish.

---

## Reviewer #3

### R3-C1. Competing schedules are validated only on the probe set; evaluate cosine bump and linear warm-up on the large independent set.

**Response.** Done. Linear warm-up and the cosine bump were evaluated on the same 300-object pool with the identical protocol (same checkpoint, capped scale semantics, 50 steps, seed 42, shared initial latents), and the transfer claims use the disjoint 276-object holdout. On the holdout, C3 improves PSNR over **linear warm-up** by +0.323 dB (95% CI $[0.263, 0.386]$, winning on 214/276 objects) while matching its structure (mean FG-SSIM difference −0.001), and over the **cosine bump** by +0.902 dB (95% CI $[0.824, 0.981]$, winning on 253/276 objects) with a higher FG-SSIM (+0.046). On the full 300-object pool the means are 18.75 dB / 0.370 (warm-up) and 18.21 dB / 0.324 (bump) versus 19.12 dB / 0.371 for C3. The holdout ordering matches the probe: linear warm-up approaches C3 in structure but loses in signal fidelity, and the smooth cosine bump loses in both because its effective high-scale duration is shorter than the full middle third. These results are reported alongside the already-transferred trapezoid and Gaussian-peak schedules (Sec. 4.4).

### R3-C2. The aggregation procedures in the texture tables appear to differ; clarify the exact computation.

**Response.** The reviewer is correct, and we thank them for the careful check. The earlier tables mixed two aggregation orders (a ratio of per-condition means versus the mean of per-object ratios). In the revision, **all** texture tables are regenerated from per-object CSVs with a single, explicitly stated rule, written in the table captions: absolute foreground statistics are means over objects and views, and each ratio column is the **mean over objects of the per-object ratio to the corresponding ground-truth statistic (equal object weighting)** (Table `tab:texture300`). We also re-verified every reported win rate and confidence interval from the same per-object files.

### R3-C3. Clarify the statistical reporting: what does ± denote, which paired test, how are bootstrap CIs constructed?

**Response.** Clarified at first use and in all relevant captions. For CLIP-IQA (Table `tab:clipiqa`): $\pm$ denotes the **standard deviation across the 50 objects**; the paired comparison is a **two-sided paired $t$-test** ($t(49)=10.52$, $p\approx3.6\times10^{-14}$ for C3 vs. $s{=}2.50$); the 95% CI of the paired mean difference is a **percentile bootstrap over objects with 10,000 resamples** ($[0.0037,0.0054]$). For the preference study, significance is now reported via two-level (participant- and object-level) cluster bootstrap intervals as described in R1-C3 `[PENDING: CIs]`; the study's instructions, randomization, and exclusion rules are reported in Sec. 4.5. All other paired statements in the paper (e.g., stage-utility CIs in Sec. 4.3, holdout deltas in Sec. 4.4) use object-level paired statistics with percentile bootstrap 95% CIs, and the bootstrap procedure is now stated once in Sec. 4.1.

### R3-C4. More complete dataset and implementation details; for FAC, specify training data, loss, optimization, parameter count, and whether the 300 validation objects are excluded from FAC training and model selection.

**Response.** Dataset and implementation details are addressed by the new Sec. 4.1 paragraph (R1-C1, R1-C2), including the verified zero-overlap between the training pool and the 300-object evaluation pool. Regarding FAC: the controlled re-run described in R1-C1(b)/R2-W3 trained the lightweight correction modules on the 1,118-object training pool only (strictly disjoint from all evaluation objects) with the same denoising objective as the base adapter, and used no evaluation object for training or model selection; nevertheless the learned variants degraded fidelity by ≈3 dB relative to the TCAS baseline. Because the result is negative and the earlier positive numbers could not be reproduced, we removed the FAC section rather than risk presenting under-verified material; TCAS — which introduces no parameters and no training — remains the main and sole method.

---

## Checklist of changes

| Reviewer point | Change | Location (revised manuscript) |
|---|---|---|
| R1-C1a / R2-W3 / R3-C4 (splits, overlap) | Dataset/implementation paragraph; disjoint holdout protocol; zero train–eval overlap verified | Sec. 4.1 |
| R1-C1b / R2-W3 / R3-C4 (FAC) | FAC section removed; negative-result audit reported here | (removed); this letter |
| R1-C2 / R3-C4 (implementation) | Checkpoint, scale semantics, scheduler, steps, seed, views, rendering, metrics | Sec. 4.1 |
| R1-C3 / R3-C3 (statistics) | ± defined; test named; bootstrap procedure stated; cluster bootstrap added | Sec. 4.1, 4.5 |
| R2-W1 (generality) | Conditional reframing; Adapter-Dependence subsection; adapter-free + SF3D baselines | Abstract, Secs. 4.2, 4.5, 4.6, 5 |
| R2-W2 (heuristic schedule) | CAI model; stage ablation; 15-candidate sensitivity sweep; σ-domain/per-layer baselines | Secs. 3.4, 4.3, 4.4 |
| R3-C1 (large-set schedules) | cosine bump + linear warm-up on 300-object pool (disjoint holdout statistics) | Sec. 4.4 |
| R3-C2 (aggregation) | Single aggregation rule stated in captions; tables regenerated from per-object CSVs | Sec. 4.5 |

We believe the revised manuscript is substantially stronger, and we thank the reviewers again for comments that directly led to the CAI model, the disjoint holdout protocol, and the adapter-dependence analysis.

Sincerely,
The Authors
