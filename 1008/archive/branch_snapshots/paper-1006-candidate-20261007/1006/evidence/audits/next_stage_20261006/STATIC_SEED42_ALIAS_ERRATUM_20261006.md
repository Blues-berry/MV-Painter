# Seed-42 alias trace clarification — 2026-10-06

The frozen `STATIC_SEED42_REUSE_GATE.json` contains an inaccurate descriptive
string in `forward_path`: “requested scales below/equal layer ceilings.” The
raw traces for all 48 reused objects show that `native_gfl` requests shallow
scale 1.25 and the adapter cap applies 0.80. The `a3_baseline` shallow request
and applied scale are both 0.50. This erratum supplements the hash-locked gate;
the original gate and E2 execution lock remain unchanged.

The factorial's F01 level is interpreted as the **applied/effective** profile
(deep 1.25, middle 1.25, shallow 0.80). The two-object preflight ran F01 with a
requested shallow scale of 0.80, produced a 0.80 effective trace, and matched
the official `native_gfl` predictions byte-for-byte. The official seed-42
`native_gfl` source used request 1.25 but the same effective 0.80 trace. Thus
the alias is exact for model-applied control and output, but not for the
requested-scale log field.

The formal E2 generated rows for seeds 43 and 44 use the requested/effective
0.80 F01 profile. Report the seed-42 source and this requested-scale difference
alongside E2; do not describe all three seeds as having identical requested
scales. This distinction does not support equal realized residual dose and
does not change the frozen output rows or their factor contrasts.
