# Cross-backbone mapping and claim boundary — 2026-10-01

## MV-Adapter mapping

The four ordered injection points were grouped into three contiguous depth
groups by a mechanical topology-derived rule (shallow `{p0}`, middle `{p1}`,
deep `{p2,p3}`). The rule and layer-wise protocol were written before the
first layer-wise MV-Adapter holdout rows. The only earlier MV-Adapter rows
were global-scale conditions and could not select among mappings. Profile
values came from the frozen main-backbone layer profile and point-count
normalization, not MV-Adapter outcomes.

Classification: **`PRESPECIFIED_TOPOLOGY_DERIVED`**. Existing registered
mapping-sensitivity tests cover the defensible contiguous alternatives; this
task ran no new mapping inference. The claim must nevertheless remain bounded
to the prespecified grouping and tested contiguous alternatives. Do not write
“mapping-independent.”

Evidence references: `core7_same_runner_completion_20261001/MAPPING_CHRONOLOGY_AUDIT.md`,
`core7_same_runner_completion_20261001/MAPPING_SENSITIVITY_PROTOCOL.md`,
`core7_same_runner_completion_20261001/MAPPING_SENSITIVITY_REPORT.md`, and
`final_audit_20261001/MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md`.

## MVDiffusion is an interface boundary, not a direct replication

MVPainter scales an additive geometry residual:

```text
h' = h + s A(h,G)
```

MVDiffusion's CPBlock intervention interpolates the serial module output:

```text
y' = (1-α)x + α CPBlock(x)
```

Although both expressions can be written algebraically as input plus a scaled
difference, the intervention object differs: one scales a separately
injected additive geometry residual; the other reweights a serial replacement
module whose internals run at full strength. Therefore MVDiffusion is
**`INTERFACE-BOUNDARY EXPERIMENT`**, with its negative/mixed outcomes
preserved—not a direct replication or positive transfer result.

## Allowed bounded conclusion

> Layer redistribution partially transfers to MV-Adapter under a prespecified
> topology-derived grouping, with metric-dependent support; temporal placement
> is not consistently separated there. On MVDiffusion's non-isomorphic serial
> correspondence-module interface, the layer-wise result does not replicate,
> defining an architecture-dependent applicability boundary.

Forbidden: “universally generalizes across backbones,” “mapping-independent
transfer,” pooling absolute scores across backbones, or calling the
MVDiffusion experiment a direct replication.

## Gate 5 disposition

`PASS`. The mapping is prespecified/topology-derived, the sensitivity evidence
already exists, and the cross-backbone wording is bounded. No additional
mapping experiment is mandatory.
