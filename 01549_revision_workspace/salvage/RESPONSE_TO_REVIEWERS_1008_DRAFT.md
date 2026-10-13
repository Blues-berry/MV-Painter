# Response to Reviewers — 1008 revision

**Status: response text complete; submission metadata still requires verification.** Page and line references below point to the compiled 9-page main PDF built from `final_0903.tex` and the 8-page Supplementary Material PDF.

## Submission metadata to verify

- **Identifier supplied by the author and present in the reviewer-packet name:** CAG-D-26-00962. Confirm that this is the current Editorial Manager manuscript number before submission.
- **Target 01549 source manuscript:** CAG-S-26-01549, as linked to the source baseline in the local authority record.
- **Reviewer source:** `CAG-D-26-00962-reviews.pdf` and its text companion, SHA-256 `fac855473563faf5dc35cc5d24fd084a56a8961e9c390ec12462fe351a7781eb` and `1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5`. The three comments are labelled “Initial submission.”
- **Formal revision round, editorial decision, and decision date:** pending verification against the editor’s decision letter. No formal decision letter was present in the verified coordinator materials.

Dear Editor and Reviewers,

We thank the reviewers for their careful assessment. We have revised the 01549 manuscript while preserving its TCAS identity and its existing MVPainter-style geometry-adapter pipeline. The revised text defines TCAS as a training-free three-stage residual-control method, reports the revision-era Fresh C comparison with object-level uncertainty and counter-results, and states where the evidence remains image-space or implementation-specific. We have removed the unsupported CAI optimality proof, FAC results, pooled +0.96 dB claim, 92% texture-fidelity claim, and human-preference superiority claim.

## Reviewer 1

### Comment 1 — Color shifts, repeated patterns, broader visual comparisons, unseen views, seams, and video access

**Response.** We added rights-cleared whole-object render panels comparing the reference and all six tested conditions, including No Adapter, GFL, GFH, C3, LLH, and Generic Linear. Figure 2 shows a near-median and a C3-favourable case; Figure 3 shows a C3–GFH endpoint trade-off and a Generic Linear advantage case. Supplementary Figure S1 records adverse cases. These panels are selected illustrations, not a representative visual sample or a frequency estimate; the aggregate object-level comparisons remain the quantitative evidence.

The revision does not claim that Fresh C validates baked 3D appearance or seams. Its 24-object bake attempt failed the input/output gate: 9/24 sources had out-of-range native UVs and 5 assets across 27 primitives used unsupported BLEND materials. No Fresh C bake or seam measurement was generated. Supplementary Table S8 provides a separate, bounded historical N=20 unlit base-color comparison over 11 frozen unseen views, with four objects excluded for missing UVs. Its endpoints are mixed and it does not establish population-level 3D, PBR, seam, or material-fidelity superiority. The GLB image collage is omitted because source-asset redistribution rights are unresolved.

**Revision locations.** Main manuscript, pp. 6–7, Figures 2–3 and captions; p. 7, lines 432–461. Supplementary Material, Table S1 credits; p. 7, Table S8 and Figure S1. Reviewer-side access to the supplementary video cannot be verified in this workspace; video access remains an author/editor portal check.

### Comment 2 — Main-adapter evaluation on a probe-disjoint held-out protocol

**Response.** We replaced the old pooled +0.96 dB headline with Fresh C, a matched revision-era follow-up on 300 objects. On its registered primary FG-PSNR contrast, C3–GFL is +0.522352 dB (95% object-bootstrap CI [+0.404160, +0.640669]); the registered secondary FG-LPIPS, FG-SSIM, and Edge-SSIM contrasts also favor C3 over GFL. The main comparison includes No Adapter, GFL, GFH, and C3; a separate addendum adds Generic Linear and LLH on the same 300 identifiers. The addendum is not an independent replication.

We do not present Fresh C as an original-preregistration replication or claim it reproduces the former probe-disjoint 276-object protocol. The original strict-276 C3–GFL result used a different adapter instance and has incomplete runner/input provenance; it appears only as historical, adapter-specific context in Supplementary Section S5. The separate MAIN-STAGE-276 placement follow-up uses four schedules under a common run protocol, but was specified after earlier results were inspected and is not blind or an independent replication. The submitted paper’s 24-object selection is retained as development history, not as an independently verified ranking.

**Revision locations.** Main manuscript, p. 4, lines 261–294; p. 5, lines 295–311 and 331–389; p. 6, Table 2. Supplementary Material, pp. 5–6, Section S5.

### Comment 3 — Distinguish texture variation from texture fidelity

**Response.** We now state that Fresh C reports only FG-PSNR, FG-LPIPS, FG-SSIM, and Edge-SSIM and that these endpoints do not measure direct color variation, high-frequency texture, material realism, seams, or human preference. The earlier Laplacian, RGB-variation, gradient, and human-preference claims have been removed from the main paper. The separate Fresh B PSNR/high-frequency-energy association is labelled exploratory, non-causal, and from a different cohort. Figures 2, 3, and S1 are explicitly selected illustrative cases and do not estimate prevalence.

**Revision locations.** Main manuscript, p. 3, lines 214–225; p. 4, lines 267–271; p. 5, lines 295–302 and 320–330; pp. 6–7, Figures 2–3. Supplementary Material, p. 4, Table S4; p. 7, Table S8 and Figure S1.

### Comment 4 — Paired intervals and the structural-metric trade-off

**Response.** Table 2 reports paired object-bootstrap intervals for all displayed Fresh C contrasts. For C3–GFH, the Edge-SSIM difference is −0.01881 (95% CI [−0.02084, −0.01683]); GFH also has higher means than C3 on the other three displayed metrics. We report the endpoint trade-off directly and make no equivalence or non-inferiority claim. The old 0.529 versus 0.559 comparison is not used as current evidence.

**Revision locations.** Main manuscript, p. 5, lines 303–311; p. 6, Table 2 and caption.

### Comment 5 — FAC reproducibility and code release

**Response.** FAC has been removed from the method, results, figures, discussion, and contribution claims because its reproduction provenance did not pass the current evidence gate. The Data Availability statement now says that aggregate numerical results may be requested, excludes participant-level human records and third-party 3D assets from redistribution, and makes clear that no public code-and-data reproduction package has been released.

**Revision locations.** FAC is absent from the revised main manuscript. Data Availability, p. 8, lines 502–507.

## Reviewer 2

### Concern 1 — Methodological novelty beyond schedule selection

**Response.** We agree that scheduling control strength over layers or denoising time is established prior art. In particular, Scheduled Style Injection studies both axes and also evaluates geometry-conditioned ControlNet scale schedules. We have therefore removed any implication that TCAS introduces a general layer-by-time scheduling primitive.

TCAS is defined more narrowly as a training-free inference intervention on the existing GeoTex-Adapter path used by the multi-view texturing pipeline. At each denoising step, the adapter computes a geometry-conditioned feature correction; the wrapper clips the requested scale by its native depth-group cap, multiplies the correction, and adds it to the existing UNet feature. C3 requests (1.25, 2.50, 1.25) over 17/16/17 steps. The base model and adapter weights remain frozen; no trainable parameters or additional UNet forward calls are introduced. This is a distinction in the controlled signal, interface, and task, not a claim that those differences alone create a new scheduling algorithm.

The revision adds evidence that makes this task-specific control question testable. In a separate strict-276 stage-placement follow-up, C3 improves FG-PSNR over a near-matched fixed-mean profile by +0.502875 dB (95% CI [+0.462018, +0.542244]); a temporal L--L--H profile with a similar per-layer applied-scale sum is favored over C3 on all six formal endpoints. The follow-up was specified after earlier clean-v2 inspection and does not match residual-norm dose, so we describe it as bounded stage-sensitivity evidence, not a blind replication or a dose-independent mechanism. On Fresh C, the frozen C3 profile exceeds GFL by +0.522352 dB FG-PSNR (95% CI [+0.404160, +0.640669]), with the registered secondary foreground/edge contrasts also favoring C3. Requested/applied-scale and correction-norm accounting, object-level outcomes, layer/window response, and the 0/2,250 common-support boundary are now reported together to show what the intervention did and what the data cannot identify.

We also report the strongest counter-result directly. Generic Linear has more favorable cohort means than C3 on all four displayed Fresh C endpoints; GFH also has more favorable means on all four. The C3--Generic Linear comparison has different per-layer scale sums and residual trajectories, so it does not isolate schedule shape at a matched dose. The revision makes no claim that C3 is best overall, that the historical probe proved its optimum, that the temporal mechanism is dose-independent, or that the result transfers across backbones. Fresh C remains image-space evidence and supplies no valid new bake, seam, PBR, or human-preference result.

**Revision locations.** Main manuscript: Abstract, p. 1; Introduction contributions, p. 2, lines 48–65; SSI prior-art comparison, p. 3, lines 157–177; residual equation and native caps, p. 3, lines 190–204; exact implementation bins and C3 execution, p. 3, lines 205–212 and p. 4, lines 236–249. Fresh C protocol and requested/applied sums, p. 4, lines 261–294 and p. 5, lines 295–311; paired outcomes and Generic Linear/GFH counter-results, p. 5, lines 345–389 and p. 6, lines 390–427 plus Table 2. Stage-placement follow-up, object-level interpretation, dose limits, and scope, p. 6, lines 390–427 and p. 7, lines 428–477. Supplementary Material: Section S4, p. 5, for requested/applied/residual accounting; Section S5, pp. 5–6, and Table S7, p. 6, for strict-276 placement contrasts and cross-interface boundaries.

### Concern 2 — CAI formalizes a schedule selected empirically

**Response.** We removed the CAI formulation, proposition, proof, and all claims that CAI predicts, derives, or guarantees C3. The revision describes the 24-object/17-variant record as historical development selection with incomplete row-level provenance, and evaluates the fixed C3 profile in Fresh C without additional schedule search.

**Revision locations.** Main manuscript, p. 4, lines 236–249; p. 5, lines 331–339. No CAI proposition or proof remains.

### Concern 3 — No cross-backbone generalization

**Response.** We did not add a new backbone experiment. The Discussion and Limitations state that the evidence is specific to the tested pipeline, adapter, profile, and sampling setup. Supplementary Section S5 reports the MV-Adapter and MVDiffusion checks as separate, mixed boundary analyses with incomplete or different protocols; neither is described as a matched architecture comparison or evidence of general transfer.

**Revision locations.** Main manuscript, p. 7, lines 439–451. Supplementary Material, pp. 5–6, Section S5.

## Reviewer 3

We appreciate the positive assessment. No separate technical change was requested. The revised manuscript addresses the evidence and scope concerns raised by Reviewers 1 and 2 while retaining the 01549 title, TCAS method identity, and original geometry-adapter pipeline.

## Items requiring confirmation before filing

1. Confirm the Editorial Manager manuscript number, revision round, and decision date against the formal decision letter.
2. Confirm that the supplementary video is accessible from the reviewer-facing submission portal.
3. Obtain author acceptance of the revised manuscript and response.
