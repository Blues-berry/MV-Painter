# MV-Adapter Layer-wise Smoke (technical)

Objects: obj_0024,obj_0025,obj_0026. Conditions: L-FIX,L-LHL,L-LLH.
Seed 20260928, 50 steps, low 0.75, high 1.00, frozen layer profile.

**SMOKE = PASS**

| check | result |
|---|---|
| rows_present_9 | True |
| all_metrics_finite | True |
| methods_pairwise_distinct | True |
| norm_ratios_match_frozen_multipliers | True |
| all_views_generated | True |

- frozen multipliers: `[0.4195298372513563, 1.193490054249548, 1.193490054249548, 1.193490054249548]`
- observed norm ratios: `[0.41952932500109474, 1.193488978006394, 1.193489924537051, 1.1934905325084035]`

No parameter may be changed based on this smoke; formal commands are frozen.
