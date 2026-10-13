# FINAL_SCIENTIFIC_NARRATIVE_STUDY.md (Phase 21 — agent B)

Three candidate narratives scored against the audited evidence (not against
attractiveness). Sources: all agent B audits + parallel-session audits.

## Narrative A — "LLH is a better schedule"
- Support: same-runner 7-condition matrix; LLH first on 4 headline metrics;
  robust across realizations and partitions.
- Weakness: budget decomposition shows the LLH−GFL headline is ~3/4 budget
  reallocation; LLH not universal (MV-Adapter temporal ns; MVDiffusion
  negative); novelty thin (schedule engineering).
- Verdict: evidence-supported but narrow; overclaim-prone; rejected as the
  main narrative.

## Narrative B — "Layer-wise × temporal residual allocation (where × when)"
- Support: matched-budget pairs isolate timing (LLH−LHL +1.00 dB, Full-PSNR
  276/0; LLH−LFM +0.88); layer-vs-global isolates distribution; caps
  semantics now explicit; caps make the "where" question precisely a budget-
  distribution question.
- Weakness: "separable factors" holds on the main backbone; cross-backbone
  only partially (MV-Adapter scale dimension; MVDiffusion interface differs).
- Verdict: strongest main-paper core, provided allocation is described as
  "combined allocation effect" with the decomposition available.

## Narrative C — "Adapter residual allocation has architecture-dependent
transfer boundaries"
- Support: main backbone strong; MV-Adapter layer-wise SUPPORTED
  (metric-dependent, scale dimension only, temporal not separated);
  MVDiffusion NOT_REPLICATED with preserved negatives and a documented
  intervention-semantics gap (serial module vs additive branch).
- Weakness: negatives invite "why does this matter"; requires careful
  interface taxonomy (additive branch / serial module / depth-concat).
- Verdict: the necessary framing for the cross-backbone section; too
  defensive as the sole headline.

## Recommended composition (evidence-maximal)

**B as the method/finding core + C as the generality boundary**, with A
demoted to an empirical observation inside B:
1. Contribution: residual allocation (depth-distribution × temporal
   placement) is a controllable, inference-time dimension with separable
   factors at matched budgets; headline numbers always paired with the
   budget decomposition.
2. Generality: architecture-dependent boundary — additive-branch adapters
   transfer the layer dimension (metric-dependent); serial-module interfaces
   do not replicate it; depth-concat conditioning surfaces are out of scope.
3. Honesty anchors: LLH−GFL decomposition; 34-loss analysis; no_adapter
   blur pseudo-advantage; GFH gradient-calibration nuance; Case-B history
   exclusion; legacy-panel regime disclosure.

This composition survives every audit finding delivered in this round and the
parallel session's; no remaining mandatory experiment is required for it
(P1 optional: capped re-run of the four-condition/global panels for
aesthetics of consistency; P2: image archiving for future visual claims).
