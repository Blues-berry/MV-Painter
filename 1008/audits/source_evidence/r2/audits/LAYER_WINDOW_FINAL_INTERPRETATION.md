# Layer × Window final interpretation

**Disposition: secondary characterization only.** The permitted conclusion is **measurable response heterogeneity under the tested intervention regime**.

## Corrected interaction evidence and magnitude

A2's object-cluster GEE and independently validated object-cluster Wald test agree for the observed 3×5 response map. For FG-LPIPS, GEE χ²(8)=482.708, p=3.6×10⁻⁹⁹; Wald W(8)=481.081, p=8.04×10⁻⁹⁹; interaction share 43.5%, cell RMSE 0.001695. For FG-PSNR, GEE χ²(8)=1886.250, p<10⁻³⁰⁰ (reported tail probability underflowed); Wald W(8)=1879.963, p<10⁻³⁰⁰; share 56.8%, cell RMSE 0.1222 dB. A2 is exploratory discovery evidence.

A3 is a higher-dose stress regime on the same cohort, not an independent replication. Its validated object-cluster Wald results are: FG-LPIPS W(8)=657.237, p=1.14×10⁻¹³⁶, interaction share 11.9%, cell RMSE 0.00643; FG-PSNR W(8)=1389.118, p=1.28×10⁻²⁹⁴, share 0.8%, cell RMSE 0.207 dB. The large test statistics do not make the magnitude practically large; in particular, the PSNR interaction share is small. A3's shallow dose is stress-only and cannot support a normal-use mechanism claim.

A3b is the bounded Fresh B map on N=150 objects. Its corrected object-cluster Wald tests and GEE cross-checks detect response heterogeneity: FG-LPIPS Wald W=225.015, Holm p=5.37×10⁻⁴³, share 14.0%, RMSE 0.000342; GEE W=226.717, p=1.46×10⁻⁴⁴. FG-PSNR Wald W=525.700, Holm p=3.43×10⁻¹⁰⁷, share 36.0%, RMSE 0.0205 dB; GEE W=529.230, p=3.75×10⁻¹⁰⁹. These estimates describe the tested bounded map, not an equal-dose mechanism.

## Dose and causal limits

- The earlier A3b common-support statistic (0/2,250) and central-90% ranges came from integrated raw $L_2$ norms across feature groups with spatial sizes 24×16, 48×32, and 96×64; channel counts were not logged. These raw-norm comparisons are not dimension-normalized across layer groups and are withdrawn as evidence about cross-layer dose support.
- The probe-24 development calibration that set A3b's fixed scale values also used cross-layer raw $L_2$. Its equal-dose target and approximate-balance failure labels are not dimension-validated; retain the frozen values only as the tested bounded profiles.
- The post-hoc per-entry mean-absolute sensitivity remains descriptive, not a validated dose metric. The A3b linear/log models used the dimension-sensitive raw-$L_2$ covariate and are post-treatment associations; they do not identify an independent dose effect.
- A3 is a higher-scale stress intervention on the same underlying cohort, not an independent replication of A2. Its within-layer image-space stress observations remain reportable, but cross-layer equal-dose interpretations are not.

## Interface boundary

MV-Adapter has 98/99 planned inputs available (one missing). Its global interaction cluster-bootstrap p=0.6523; exploratory object-cluster Wald FG-LPIPS p=0.1012 and four-metric Holm p=0.3037. Per-cell local patterns do not establish a global interaction, and a non-significant global test is not equivalence.

MVDiffusion is a separate correspondence-aware conditioning interface evaluated on 75 objects. Its negative/mixed results are reported only within that interface. It is not a matched architecture test and cannot identify architecture as the cause of differences.

## Allowed and prohibited interpretation

Allowed: **measurable response heterogeneity under the tested intervention regime**.

Prohibited: **dose-independent layer×time mechanism**, **universal architecture law**, or **optimal schedule follows from interaction significance**. Keep the full maps and cross-interface limits secondary; do not make A2/A3/A3b the paper's central contribution.
