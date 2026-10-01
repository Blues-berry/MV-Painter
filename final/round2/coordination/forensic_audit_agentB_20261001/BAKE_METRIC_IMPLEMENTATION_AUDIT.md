# BAKE_METRIC_IMPLEMENTATION_AUDIT.md (Phase 10 — agent B)

Trigger: `uv_seam_discontinuity = 0.0` for 48/48 baked records — the task doc
forbids reading all-zeros as a perfect result and demands an evaluator audit
(seam-pair definition, pair counts, fallback, empty-set behavior).

## 1. Root cause of the 48/48 zeros (code-path analysis)

Implementation: `geotex/cpu_texture_bake.py` (runs in Blender 4.2.4 on the
exact GLBs), `seam_discontinuity()` L304–316, pair construction L137–177.

1. **Index-keyed edge matching cannot see UV-chart seams.** Edges are keyed by
   vertex indices `(min(va,vb), max(va,vb))` (L144). glTF geometry *splits*
   vertices along UV chart boundaries, so the two chart copies of the same
   geometric edge carry different vertex indices → different keys → each key
   holds one entry → `len(entries) < 2` → skipped (L167–168). The real chart
   seams are therefore absent from `seam_pairs`.
2. **The 1e-5 UV threshold admits degenerate pairs.** Pairs form only when two
   loop entries on the *same* index-key differ by > 1e-5 in UV (L171) — i.e.
   sub-texel jitter between duplicate loop entries. At 1024², both midpoints
   of such a pair round to the *same texel* → per-pair color difference is
   exactly 0.0 (L309–316 samples one texel per side).
3. **Consequently** the recorded scalar is the mean over degenerate
   same-texel pairs: exactly 0.0 for every object/method — matching the
   literal `0.0` in all 130 `bake_metadata.json` files and both archived CSVs
   (`UNSEEN_OBJECT_METRICS.csv`, `UNSEEN_PER_VIEW_METRICS.csv`).
   Empty-pair → NaN exists in the current code, so pairs were non-empty but
   degenerate; either way the scalar carries no seam information.

Caveat: the degenerate-pair mechanism is established from the code path plus
the archived artifacts; the original extractor was not re-run inside Blender
in this audit. The decisive empirical evidence that the original scalar was
uninformative is the corrected recompute below.

## 2. Corrected metric (already executed, not duplicated here)

`scripts/audit_bake_seams_20261001.py` +
`final/round2/coordination/BAKE_SEAM_AUDIT_20261001/`: position-keyed vertex
matching (UV tolerance 1e-4), CIEDE2000 between chart-side colors of the same
3D edge midpoint, interior-edge control, per-object CSV with real pair counts.
Results on the matched bake generation: layer_llh 4.89 < layer_lhl 5.60 <
global_c3 7.54 < global_fixed_low 8.86 (seam ΔE00 mean), tails p90/frac>10
same ordering, seam/control ratio 1.6–1.8 → the corrected metric is
discriminative and the residual seams are real. **The original seam scalar is
INVALID for any comparison and is superseded.**

## 3. `num_seam_pairs` bookkeeping

- Original `bake_metadata.json` does **not** record a pair count — confirmed
  and already disclosed in the supplement ("the saved seam scalar does not
  include a seam-pair count").
- Corrected audit records pair counts implicitly via its per-object CSV
  (`SEAM_AUDIT_PER_OBJECT.csv`). Any future paper-facing seam number must
  come from that implementation (or a descendant) that reports its denominator.

## 4. `cross_view_texel_variance` semantics

Definition (round2_bake_metrics.py L38–52, computed during baking in
cpu_texture_bake.py L383–387): mean per-channel variance across **source
views** that hit the same texel during splatting. It therefore measures
**multi-view source disagreement at bake time** (generation cross-view
inconsistency projected into texture space) — *not* the variation of the
final baked texture, and *not* a rendered-view stability metric.

Three distinct quantities exist across the evidence base and must not be
conflated in the paper:

| quantity | what it measures | where |
|---|---|---|
| `cross_view_texel_variance` | source-view disagreement per texel at bake time | bake metadata |
| corrected UV-seam ΔE00 | chart-boundary color discontinuity of the final texture | BAKE_SEAM_AUDIT_20261001 |
| render-time cross-view descriptor | color stability of re-rendered views (vertex-colored rendering) | baking_consistency_report.md (parallel session) |

The manuscript's umbrella phrase "cross-view/source-fusion colour
inconsistency" (final_round2.tex L660, L774) is accurate but the
revision window should name which implementation backs each quoted number.

## 5. Paper status check

- final_round2.tex L655–657 already states the zero seam values are "reported
  with the audit's seam definition and denominator and are not treated as
  proof of universal seam-free output" — consistent with this audit.
- Supplementary L164–165, L223–224 disclose the missing denominator.
- Revision-window item: replace/annotate the archived zero seam scalar with
  the corrected texture-space seam ΔE00 (BAKE_SEAM_AUDIT_20261001), keeping
  the 12-object case-study framing.

## Verdict

Original seam metric: `INVALID` (degenerate pairing; superseded).
Corrected seam audit: `VALIDATED`. Cross-view semantics: documented; no
numeric claim in the paper currently rests on the zero seam scalar.
