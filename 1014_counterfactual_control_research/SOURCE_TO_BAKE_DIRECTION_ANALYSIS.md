# Reference-Error to Unseen-Bake Direction Analysis

## Design and analysis unit

Six previously exposed GeoTex objects were evaluated with one paired seed and three conditions (B0, B+, B−). The object is the analysis unit. The 11 unseen camera scores are first averaged inside each object; views, adapter blocks and sampler steps are not counted as independent observations. No expansion to the other four exposed objects was made after the six-object result failed the action-direction gate.

Reference errors are computed from the known reference tile in the saved generation panel. Baked quality is the mean foreground LPIPS over 11 native-EGL renders from the unchanged GLB UV bake. The GT and unseen images were opened only after all 18 generations and all bake outputs were complete. RGB MAE and CIEDE2000 were both reported; neither was selected post hoc as the “winning” feedback signal.

## Per-object counterfactual response

`Δ` is B+ minus B−. Negative baked LPIPS means B+ scores better. The final columns give the LPIPS change from B0 for the candidate chosen by the corresponding reference error; negative is better.

| Object | Δ reference RGB MAE | Δ reference CIEDE2000 | Δ baked 11-view LPIPS | MAE-selected action; Δ vs B0 | CIEDE-selected action; Δ vs B0 |
|---|---:|---:|---:|---|---|
| `1dc2c857` | −0.001784 | −0.1731 | −0.000463 | B+; −0.000284 | B+; −0.000284 |
| `21678bd6` | +0.002656 | +0.0915 | −0.000076 | B−; −0.000083 | B−; −0.000083 |
| `238ff3e4` | +0.001152 | −0.0522 | −0.000072 | B−; **+0.000140** | B+; **+0.000068** |
| `2dd9bc81` | −0.001711 | −0.1704 | −0.000331 | B+; −0.000163 | B+; −0.000163 |
| `2f6c9448` | +0.006258 | +0.2040 | **+0.000050** | B−; **+0.000042** | B−; **+0.000042** |
| `e261c0fe` | +0.002529 | +0.0425 | −0.000027 | B−; −0.000087 | B−; −0.000087 |

Lower reference error identifies the baked-quality direction in only **3/6 objects for RGB MAE** and **4/6 for CIEDE2000**. Exact 95% binomial intervals are wide: 0.118–0.882 and 0.223–0.957, respectively. One object (`238ff3e4`) has opposite MAE and CIEDE decisions. The feedback signal therefore does not specify a stable action direction on this cohort.

## Effect versus B0 and uncertainty

| Policy or paired contrast | Mean object-level Δ baked FG-LPIPS | Object bootstrap 95% interval | Objects with lower LPIPS |
|---|---:|---:|---:|
| Fixed B+ vs B0 | −0.000093 | [−0.000195, +0.000012] | 4/6 |
| Fixed B− vs B0 | +0.000060 | [−0.000027, +0.000146] | 2/6 |
| Pick lower reference RGB MAE from B+/B− vs B0 | −0.000072 | [−0.000178, +0.000036] | 4/6 |
| Pick lower reference CIEDE2000 from B+/B− vs B0 | −0.000085 | [−0.000178, +0.000008] | 4/6 |
| B+ vs B− | −0.000153 | [−0.000311, −0.000018] | B+ lower in 5/6 |

The B+ versus B− contrast shows a small local effect, favoring B+ in five objects. Its exact 95% interval for the fraction favoring B+ is 0.359–0.996. Against B0, the fixed B+ interval includes zero; the two reference-error-selected rules also include zero. The point estimates are below 0.0001 LPIPS for both selected policies versus B0. These are descriptive intervals on a small purposive cohort, not a confirmation claim.

The interventions changed generated RGB outputs: across objects, 32–48% of saved RGB channels differ from B0, with panel mean absolute differences about 0.0016–0.0027 on `[0,1]` scale. The output change is real, but the resulting 11-view bake-quality change is very small. This separates “the control affects pixels” from “the control improves the product.”

## Source-view gains with cross-view or bake loss

- **`238ff3e4`, B−:** reference RGB MAE improves by 0.000811 versus B0, but nonreference-view mean LPIPS rises by 0.00011 and the unseen bake LPIPS worsens by 0.000140. CIEDE2000 moves the other way, increasing by 0.0359 versus B0. The two source metrics disagree, and neither yields a dependable bake decision.
- **`2f6c9448`, B−:** both reference RGB MAE (−0.003360) and CIEDE2000 (−0.1313) improve versus B0. Nonreference-view LPIPS rises by 0.00013 and baked LPIPS worsens by 0.000042. B0 is better than both counterfactual actions on unseen-bake LPIPS for this object.
- **`21678bd6`, B−:** both reference metrics prefer B− to B+, but the unseen-bake metric slightly prefers B+ (−0.000076 for B+ minus B−).
- **`e261c0fe`, B−:** both reference metrics prefer B−, while the bake slightly prefers B+ (−0.000027 for B+ minus B−).

The selected actions lower reference error and baked LPIPS versus B0 for four of six objects, but they also lose on two. The wins are small, the action direction is inconsistent, and the fixed B+ policy has a slightly better mean LPIPS than either feedback selection while requiring one generation instead of two.

## Same-generation-count simple-selection control

The Phase C compute comparison was completed on the same six objects. Each feedback policy uses two full trajectories (B+ and B−); the no-view-budget-control baseline also uses two trajectories (Fixed Mean B0 at latent seeds 42 and 43) and chooses by the same reference error. The legal source metric selected the same seed on all six objects for both RGB MAE and CIEDE2000 in this realization.

| Two-call policy | Mean object LPIPS | Object-bootstrap 95% interval | Action minus Fixed Mean best-of-two |
|---|---:|---:|---:|
| Fixed Mean best-of-two, MAE selected | 0.139807 | [0.094898, 0.185240] | reference |
| B+/B−, MAE selected | 0.141199 | [0.096696, 0.187384] | +0.001392 [−0.004838, +0.007499] |
| B+/B−, CIEDE selected | 0.141187 | [0.096647, 0.187384] | +0.001380 [−0.004838, +0.007499] |

The view-action policy has lower LPIPS than the equal-cost Fixed Mean selector on 3/6 objects for either source metric. Its mean is worse and no interval establishes an advantage. This control removes the objection that the action selector's result is due simply to paying for a second trajectory; it still does not show that geometry-budget feedback helps.

## Quality, UV and inference cost

- Mean unseen-view FG-LPIPS is 0.141271 for B0, 0.141178 for B+, and 0.141331 for B−. Fixed B+ is the best simple one-call profile on this cohort, but its paired difference from B0 is uncertain and tiny.
- Raw UV coverage is identical among GT, B0, B+ and B− for each object because geometry, cameras and masks are fixed. Cross-view texel variance and seam discontinuity move by small, mixed amounts; neither shows a consistent control benefit.
- The generation ledger reports 154.91 s of measured generation time across 18 calls (model loading and the later metric pass excluded). Median per-call time after the first B0 call is about 7.2–7.4 s. Choosing between B+ and B− therefore costs about two complete trajectories, while fixed B+ needs one.
- The 24 native UV bakes span approximately 470 s from first to last bake metadata output. The 264-image EGL render completed in 11.1 s; the per-view generation scorer took 6.95 s. All B0 generations, baked textures and unseen renders reproduced the frozen historical baseline pixel-for-pixel.

## Decision for the feedback hypothesis

**Not supported as an actionable controller signal.** The opposing actions create a small bake-LPIPS difference in this cohort, but the reference error chooses the lower-bake-quality action in several objects, sometimes disagrees across RGB MAE and CIEDE2000, and does not beat a fixed one-call B+ policy. The counterexamples in `FAILURE_CASES.md` are retained in full. Do not expand the cohort or tune the action rule.
