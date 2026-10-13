# Retained Counterexamples and Failure Cases

These cases were identified from the frozen six-object paired study. They are not excluded from the aggregate and were not used to retune the perturbation, time window, layer groups, or selection metric. The object is the unit of analysis.

## Reference error fails to choose the better bake direction

| Object | Reference-error choice | Better baked LPIPS action | Result |
|---|---|---|---|
| `21678bd6` | B− by RGB MAE and CIEDE2000 | B+ | Both legal source metrics choose the action with higher unseen-bake LPIPS; B+−B− is −0.000076. |
| `238ff3e4` | RGB MAE chooses B−; CIEDE2000 chooses B+ | B+ | The source metrics disagree. Both source-selected actions are worse than B0: +0.000140 LPIPS for MAE selection and +0.000068 for CIEDE selection. |
| `e261c0fe` | B− by both source metrics | B+ | The baked difference is tiny (B+−B− = −0.000027), but the selected sign is wrong. |

The source-to-bake direction matches for only 3/6 objects with RGB MAE and 4/6 with CIEDE2000. The exact binomial intervals are wide and overlap chance. Full object-level values are in `ACTION_RESPONSE_RESULTS.csv` and `SOURCE_TO_BAKE_DIRECTION_ANALYSIS.md`.

## A better reference view can come with worse other views and bake

- **`238ff3e4`, B− versus B0:** reference RGB MAE falls by 0.000811, but the mean LPIPS over the five nonreference generated views rises by 0.00011 and the 11-view baked LPIPS rises by 0.000140. Reference CIEDE2000 moves the opposite way, worsening by 0.0359.
- **`2f6c9448`, B− versus B0:** both reference RGB MAE (−0.003360) and CIEDE2000 (−0.1313) improve, while nonreference-view LPIPS rises by 0.00013 and baked LPIPS worsens by 0.000042. B0 is the best of the three conditions for this object's baked LPIPS.
- **`21678bd6` and `e261c0fe`:** both source metrics prefer B−, but the unseen bake slightly prefers B+.

These are direct counterexamples to treating source-view appearance as a sufficient proxy for the action's unseen-surface effect. The raw six-view generation panels and per-view metrics are retained in `generation/`; native-EGL object views are linked below.

## No useful gain against the one-call baseline

The RGB-MAE-selected and CIEDE-selected two-call policies each lower baked LPIPS relative to B0 on 4/6 objects, but their mean improvements are small and both object-bootstrap intervals include zero. Fixed B+ uses one generation, has a slightly lower mean LPIPS than either feedback-selected policy, and also has an interval crossing zero versus B0. The two-call rule therefore has no demonstrated quality-per-compute advantage.

## Output change is not product improvement

The interventions do change generated panels: 32–48% of RGB channel values differ from B0, with mean absolute panel differences around 0.0016–0.0027 on `[0,1]`. That visible/model-output response does not translate into a useful feedback rule. Across this fixed-geometry cohort, silhouette IoU and raw UV coverage are identical across conditions by construction; UV variance and seam metrics shift slightly in mixed directions. This rules out an obvious coverage or silhouette failure in this setup, but does not establish general structural safety or full PBR quality.

## Visual evidence

Each per-object sheet compares all 11 native-EGL unseen-camera renders for B0, B+ and B−. Full-resolution 512×512 renders, UV textures, textured GLBs and their hash records remain under `bake/`.

- [All six objects, all three conditions, 11 views](visuals/ALL_OBJECTS_ALL_CONDITIONS_11VIEWS.png)
- [Per-object comparison index](visuals/README.md)
- [Object `238ff3e4` render comparison](visuals/UNSEEN_11VIEW_COMPARE_238ff3e41c964655b83aa9c8770cc766.png)
- [Object `238ff3e4` UV texture comparison](visuals/UV_TEXTURES_238ff3e41c964655b83aa9c8770cc766.png)
- [Object `2f6c9448` render comparison](visuals/UNSEEN_11VIEW_COMPARE_2f6c94487ee54cb88021f4643409d849.png)
- [Object `2f6c9448` generated six-view panels](visuals/GENERATED_SIX_VIEW_PANELS_2f6c94487ee54cb88021f4643409d849.png)

The visualizations are a presentation of the retained files, not a basis for selecting conditions. GT and unseen-camera renders were used only after all 18 generations and the paired bake outputs were complete.
