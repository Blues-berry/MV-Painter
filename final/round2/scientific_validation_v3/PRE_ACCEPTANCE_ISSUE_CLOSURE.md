# PRE_ACCEPTANCE_ISSUE_CLOSURE — Scientific Validation V3

Created: 2026-10-05 (V3 protocol §2). Source ledger:
`PRE_ACCEPTANCE_AUDIT_20261005.md` §15. Rule: every P0 closed before any new
formal experiment; every scientifically relevant P1 closed or explicitly
justified. No formal campaign or corrected-bake rerun was performed. The
existing seam generator was independently rerun to a temporary directory for
byte-level reproducibility; its stored outputs were not changed.

Current status as of 2026-10-06: **P0 = 0. Scientific P1 = 0 for the
explicitly scoped N=20 stored-GLB evaluation. P1-9's renderer mismatch is
closed by a hash-checked EGL render of all 20 × 8 × 11 stored GLBs.** The
four pre-bake no-UV exclusions still prevent a strict N=24 claim. P1-1,
P1-3–P1-8 remain closed with their recorded scopes. Operational P1-2 remains
open: the remote is reachable but has no target branch ref; push is deferred
until absolute-path and ignored-artifact hygiene is resolved. Manuscripts
remain unchanged.

Historical status as of 2026-10-05: **P0 = 0. Scientific P1 = 1 open.** The
initial refresh detected the clamp-versus-repeat mismatch and invalid seam
casts; its then-current status and required action are retained below.

---

## P0-1 — Production interaction test has zero power → **CLOSED**

- Root cause: `analyze_v3.py cmd_layermap` builds its bootstrap null by
  resampling objects and recomputing the weighted SS_interaction of the
  OBSERVED values. The interaction is an object-shared fixed pattern;
  resampling objects cannot dilute it, so the null tracks the alternative
  and p ≈ 0.5 regardless of truth. Synthetic demonstration: 0/40 rejections
  at 0.6σ injected interaction (`STATISTICAL_PIPELINE_UNIT_TESTS.json`,
  test B); production output's null mean equals its observed statistic.
- Affected artifacts (interpretation layer only; no data rows affected):
  `LAYER_TIME_CAUSAL_MAP_REPORT.md` (A2/A3 interaction statements),
  `SCIENTIFIC_VALIDATION_DECISION_REPORT.md` (CLAIM 2 failure-cases line,
  CLAIM 3 block, final ruling), `NARRATIVE_RESTRUCTURE_REQUIRED.md`
  (point 1 and supported-story paragraph),
  `AUTHORITATIVE_GENERIC_SCHEDULE_REPORT.md` ("A3 no interaction" clause),
  `CROSS_BACKBONE_MECHANISM_REPORT.md` (G interaction p = 0.58 from the
  same zero-power test; also carried the N=99 misstatement, see P1-5),
  `CLAIM_TEST_MATRIX.md` (Claim 3 row frozen — resolution added as a
  dated addendum, frozen rows untouched).
- Remediation (all completed 2026-10-05):
  1. Valid size- and power-validated cluster-robust Wald test applied to
     the real maps (`audit_scripts/audit_interaction_valid_test.py`, results
     `AUDIT_INTERACTION_VALID_TEST.json`): A2 FG-LPIPS W=481.1, p=8.0e-99,
     interaction SS share 43.5%; A2 FG-PSNR W=1880.0, p≈0, 56.8%; A3
     FG-LPIPS W=657.2, p=1.1e-136, 11.9%; A3 FG-PSNR W=1389.1, p=1.3e-294,
     0.8%. Cross-checks: naive ANOVA F=117.8 (p=1.9e-179); 90%-subsample
     stable; winsorization-stable.
  2. Initial Wald analysis on G n=81 was superseded by the frozen completion.
     The completed n=98 exploratory output is
     `g_formal_complete/AUDIT_INTERACTION_VALID_TEST_G_COMPLETE.json`:
     FG-LPIPS W=13.322, p=0.101; PSNR W=7.995, p=0.434; FG-SSIM W=16.243,
     p=0.039 (Holm p=0.156 across four metrics); CIEDE2000 W=3.945,
     p=0.862. This post-discovery re-test is exploratory, not a confirmatory
     test of interaction presence or absence.
  3. All five interpretation documents revised with dated amendment notes
     (2026-10-05); the frozen manuscripts were NOT touched.
- Rerun required: NO (audit mandate: re-analysis only).
- Independent verification: the Wald implementation passed null calibration
  (test A/F, ~5% rejection under null), injected-interaction recovery
  (≥32/40), sign-reversal, duplicate-object, and shard-order invariance
  unit tests; audit seeds 20261002 (production) / 20261005 (audit) recorded.
- Status: **CLOSED.**

---

## P1-1 — Duplicate source-asset pair in FRESH_CONFIRM_300 — **CLOSED (documented)**

- Issue: UIDs `0099ab6d44…` / `0130e5149b…` are pixel-identical renders
  (51/51 views) from different source assets → 299 unique contents / 300
  UIDs.
- Remediation: documented here and in `CLAIM_EVIDENCE_CLOSURE_MATRIX.md`
  (cross-cutting item 5). The paired object-level design is unaffected
  (both members appear on both sides of every paired contrast; duplicates
  add weight but cannot manufacture a directional effect). Optional
  leave-one-out sensitivity on summary statistics may be run during any
  future re-analysis; it is not required for validity of the paired tests.
- Status: **CLOSED (documented).**

## P1-2 — Branch not pushed — **OPEN (operational)**

- Current evidence: `git ls-remote` succeeds for the repository, but the
  target branch `codex/scientific-validation-v3-20261002` has no remote ref.
  The earlier proxy-502 explanation is stale. Local artifacts also contain
  machine-absolute paths, ignored deliverables, and untracked IDE directories.
- Remediation: do not push the present tree. Resolve portable-artifact
  selection and provenance, then decide whether a push is needed. No
  scientific impact.
- Status: **OPEN (operational; not a scientific gate).**

## P1-3 — Narrative restructure report rested on P0-1 — **CLOSED**

- `NARRATIVE_RESTRUCTURE_REQUIRED.md` revised (2026-10-05): the
  "interaction NOT supported" premise removed; supported story restated as
  "depth-aware allocation first-order; interaction real but dose-dependent
  and of bounded scheduling value; the linear ramp was not detectably
  different on FG-PSNR, with no registered equivalence margin; thirds
  heuristic; texture-rich failure boundary mandatory."
- Status: **CLOSED.**

## P1-4 — 300M-line log incident unverifiable — **CLOSED (documented)**

- No retroactive action possible (audit §13: no >20 MB log on disk or in
  history; current shard logs complete and small; reproducibility proven
  bit-level). Recorded in the lab journal via this document.
- Status: **CLOSED (documented).**

## P1-5 — G cohort coverage and N misstatement — **CLOSED WITH SCOPE LIMIT**

- Discovery (2026-10-05): the original ledgers held 1,600 rows but only 81
  unique objects. There were 304 repeated object-condition rows across the
  two shards; all repeats matched on source UID and metrics, excluding only
  elapsed time. Eighteen planned objects had no rows.
- Frozen completion: all 18 identities were attempted under the original
  16-condition design. Seventeen completed all 272 rows. `g_0098` failed
  before producing any output because its hash-verified frozen GLB loads as
  `Path3D` line geometry with no triangles and the unchanged surface-mesh
  loader raises `Unknown mesh type`. This failure is outcome-independent;
  no alternative object, mesh conversion, or loader change was introduced.
- Recomputed cohort: **98 of 99 planned objects**, 1,568 unique
  object-condition rows. The merged row ledger, deduplication checks, exact
  source hashes, and technical exclusion are recorded under `g_formal_complete/`.
- Recomputed primary FG-LPIPS cell family: shallow W3–W5 small adverse
  deltas (+0.00045 to +0.00046) survive the registered 15-cell Holm
  correction. Exploratory cluster-robust interaction results are p=0.101 for
  FG-LPIPS, p=0.434 for PSNR, p=0.039 for FG-SSIM (p=0.156 across four
  metrics), and p=0.862 for CIEDE2000. They do not establish a confirmatory
  interaction result or its absence.
- Remediation completed to the limit of the frozen input set. The one
  remaining exclusion is explicitly scoped in the cross-backbone claim as
  98/99; the option-C language has been replaced with a bounded result for
  this scale range. P1-5 is closed for evidence accounting and report
  accuracy; the unobserved `g_0098` remains a stated limitation, not an
  imputed or substituted result.
- Status: **CLOSED WITH SCOPE LIMIT.**

## P1-6 — Uncapped residual-log scale field mislabels the cap — **CLOSED**

- Root cause: `geotex.explore_contradiction` records
  `eff_scale=min(requested, cap)` even for B3 conditions whose manifest marks
  `uncapped=true`. The B3 runner's `uncapped_forward` actually multiplies by
  the requested scale and bypasses the cap; logged correction norms therefore
  reflect the real uncapped path while the `eff_scale` field is hypothetical.
  The old residual audit inferred 100% shallow cap hits for TGU from that
  hypothetical field.
- Affected artifacts: B3 residual-budget cap-rate interpretation and any
  derived text calling TGU cap-activated.
- Remediation: `analyze_residual_budgets.py` now reads each condition's
  `uncapped` flag from the manifest, reports requested and actual effective
  scales, and sets cap activation to zero on the bypass path. Recomputed
  `residual_budget_audit.json`; residual norms and metric rows were unchanged.
- Independent verification: manifest flag checked against the
  `uncapped_forward` code path; native GFL shallow effective scale is 0.80
  with 100% cap activation, while all three TGU conditions apply their
  requested scale with 0% cap activation.
- Rerun required: **NO** (analysis-only; generated outputs are unchanged).
- Status: **CLOSED (analysis and interpretation corrected).**

## P1-7 — B3 additive cap/layer/temporal claim combines different endpoints — **CLOSED**

- Root cause: the earlier report added GFL−TGU-1.25 (+1.60),
  LFM-EXACT−TGU-1.675 (+2.99), and LLH−LFM-EXACT (+0.435) as if they formed
  LLH−GFL. They use different comparator endpoints; the sum is not the
  observed +1.288 dB LLH−GFL effect.
- Remediation: raw paired CSVs were independently recomputed. The valid
  same-endpoint identity is LLH−GFL (+1.288) =
  LLH−LFM-EXACT (+0.435) + LFM-EXACT−GFL (+0.853). The latter combines layer
  doses and shallow-cap state and is not a pure component. The B3 report,
  decision report, narrative report, and claim matrix now use named contrasts
  and forbid an additive decomposition.
- Rerun required: **NO** (contrast arithmetic and interpretation only).
- Status: **CLOSED (analysis and interpretation corrected).**

## P1-8 — H5 Spearman family lacked finite-bootstrap and Holm closure — **CLOSED**

- Root cause: the old `cmd_spearman` reported zero when none of 10,000
  bootstrap resamples crossed zero and did not apply the pre-registered Holm
  correction across the 2 × 5 test family.
- Affected artifacts: the initial `formal/campaign_B3/spearman_texture_boundary.json`
  and the first texture-boundary summary. The original JSON is preserved as
  `spearman_texture_boundary_legacy_unadjusted.json` for provenance.
- Remediation: added the plus-one Monte Carlo correction, the frozen
  10-test Holm family, and direction-aware favorable rates to the canonical
  Spearman output; wrote `PROSPECTIVE_FAILURE_BOUNDARY_REPORT.md`. Nine of ten
  tests remain significant after Holm; FG-LPIPS versus coverage does not.
  Raw ledgers and images were unchanged.
- Rerun required: **NO** (re-analysis of frozen, pre-registered contrasts).
- Status: **CLOSED (statistical correction and report complete).**

## P1-9 — Unified bake renderer does not match exported GLB — **CLOSED for stored N=20/8 outputs**

- Finding: `geotex/cpu_texture_bake.py` clamps UVs in bake splatting and
  unseen rendering. Six of 20 baked objects have substantial coordinates
  outside [0,1]; two more have minor excursions. Exported GLBs omit `wrapS`
  and `wrapT`, so glTF 2.0 defaults to repeat. All 160 inspected GLBs encode
  `magFilter=9729` and `minFilter=9987`; the CPU unseen renderer uses
  bilinear sampling without mipmaps. The old render therefore fails faithful
  GLB validation for both addressing and minification filtering. The seam
  analyzer also clamps samples and overflows integer casts on the finite
  ~1e36 UV values in `01e3b853f0f74bd0b44d34ac5106a84f` (28 warnings across
  seven conditions).
- Provenance: the tracked seam generator reproduces the stored CSV and JSON
  byte-for-byte in a temporary output location. This closes output
  reproducibility only; it does not make the addressing or seam measurements
  valid.
- Provenance nuance: `BAKE_RUN_SUMMARY.json` lists 16 objects and 128 method
  records, while the frozen handoff minus four no-UV exclusions, per-object
  metadata, GLBs, and unseen ledger cover 20 objects and 160 rows. The four
  omitted IDs are recorded in `UV_ADDRESSING_AUDIT.json`; the run summary is
  preserved unchanged.
- Historical impact: the old CPU unseen-view, seam, and practical 3D results
  remain diagnostics only. The prior N=19 result is superseded by a fixed
  sensitivity on the UID already identified for extreme UV magnitude; native
  GLB metrics now include all 20 supported objects.
- Original closure requirement: use GLB-consistent repeat addressing and
  minification filtering, validate the unseen renderer against exported GLBs,
  and reevaluate the supported 20-object/8-condition set. The native-render
  evaluation below completes this requirement for the stored outputs. No
  repeat-aware rebake or UV unwrap was performed; the four no-UV sources
  remain outside the frozen original-UV bake.
- Environment at the original refresh: no Blender executable was available,
  so the source import/export bake path could not be rerun. A separate EGL
  OpenGL context was subsequently available and used for native GLB sampling.
- Closure update 2026-10-06: `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`
  documents 1,760 renders with the exported sampler, default repeat addressing,
  `magFilter=9729`, `minFilter=9987`, and the frozen camera/normalization. A
  synthetic UV orientation/repeat probe passed; render masks have at least
  0.999768 pairwise IoU against the legacy geometry masks. Every render and
  source GLB hash passed. LLH has no PSNR advantage over `native_gfl`; LPIPS
  favors LLH while CIEDE2000 does not. The results describe stored clamp-baked
  GLBs, not a repeat-aware rebake or full PBR/human study.
- Scope: **CLOSED for the frozen supported N=20, eight-condition outputs.**
  Strict N=24 coverage remains unsupported because four original assets lacked
  UV layers before bake generation.

---

## P2 ledger (carried, no validity impact)

- P2-1 wording "|Δ| ≤ 0.006" → fixed to "≤ 0.0064" in the decision-report
  amendment.
- P2-2 SHA index for prediction PNGs — before archival.
- P2-3 50 MB contact sheet committed — prefer SHA-index + artifact location.
- P2-4 G ledgers lack `input_hashes` (source_uid only) — note in methods.
- P2-5 hygiene (vestigial `mask_gt_cache/`, untracked IDE dirs, in-cell
  permutation dependence on frozen cohort row order) — no action.
- P2-6 historical `win_rate` fields in `analyze_v3.py` are raw positive-delta
  fractions, not favorable rates for lower-is-better metrics. Inferential
  statistics are unchanged; affected report wording was corrected or made
  explicit in `WIN_RATE_SEMANTICS_AUDIT.md`. Future FRESH_CONFIRM_B reporting
  uses direction-aware favorable rates. Closed without rerun.

---

## Post-closure gate accounting

| Requirement (protocol §2 / §25) | State |
|---|---|
| P0 = 0 | YES (P0-1 closed) |
| Scientific P1 = 0 | YES for the explicitly supported N=20 stored-GLB scope; strict N=24 remains unsupported |
| Operational P1 | P1-2 open; remote reachable, target ref absent, hygiene unresolved |
| Manuscript untouched | YES (SHA-verified; edits confined to interpretation docs + audit scripts) |
| New artifacts created by this refresh | UV addressing audit, EGL renderer and analysis, GLB-native render report, and updated readiness/reviewer records; no source bake pipeline or manuscript was changed |

The G cohort completion and reanalysis closed its scoped issue. The A3b,
generic-schedule, and failure-boundary analyses are complete, but B safeguards
written after outcome exposure remain retrospective. The 2026-10-05 UV
addressing mismatch is closed for the supported stored GLBs by the
2026-10-06 native-render audit; the four no-UV exclusions remain a declared
scope boundary.
