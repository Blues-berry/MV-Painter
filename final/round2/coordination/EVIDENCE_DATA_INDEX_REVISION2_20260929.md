# Evidence and data index — revision 2

| Claim or reviewer need | Primary evidence | Paper location | Boundary |
|---|---|---|---|
| TCAS is an implementable training-free control | Eq. (injection), stage definitions, fixed scales and 50-step protocol | Method; abstract; contributions | No learned selector or causal derivation |
| Conditional image-level value | strict-276 four-condition table | Table `strict276` | Fixed-low remains stronger on several metrics |
| Stage placement changes output | paired fixed-mean/HLL/LHL/LLH table | Table `stage276` | 17/16/17 is not equal-effective-budget |
| Saved-artifact metric provenance | fixed-GT decomposition and serialized Full-SSIM table | Table `serialized276`; Supplementary S3 | Diagnostic trace, no historical retrofit |
| R1 visual quality | complete-object panels and full contact sheet | Fig. `complete0066`, `completefailures`; Supplementary S4a | Qualitative panels are not population statistics |
| Real 3D path | 48 GLBs, 528 unseen-view rows, coverage/failure table | Table `bake12`; Supplementary S4 | Case study; no population-level TCAS advantage |
| Generic schedule comparison | linear warm-up/cosine bump original-protocol rows | Main generic-schedule paragraph; Supplementary S5 | Separate adapter/protocol, not clean-v2 pooled result |
| Cross-backbone scope | MV-Adapter 76-object/11-condition audit | Table `mvadapter`; Supplementary S6 | CAI undefined; no universal transfer claim |
| Learned extension | FAC paired re-examination | Supplementary S7 | Negative extension, not TCAS mainline |
| Adaptive controller exploration | TRB 24-object development pilot | Supplementary S8; response R2.5 | No holdout, normalized-image PSNR, stopped |

Source records, hashes, manifests, and CSV/PNG pairing remain under
`final/round2/coordination/` and the evidence directories named in the
manuscript and supplement. Missing historical files are recorded as provenance
limitations, not silently replaced by new claims.
