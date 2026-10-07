# Fresh C3 confirmation protocol (revision-era follow-up)

**Lock date:** 2026-10-06 UTC

**Status:** Frozen before any C-cohort model output is generated or inspected.
**Purpose:** Address Reviewer 1.2 with a new, disjoint Objaverse cohort and the
same main-adapter validation path. This is a prospective follow-up on new
objects, but the hypothesis was motivated by already-seen revision results; it
must not be represented as the original study's preregistered replication.

## Question and scope

Does the frozen native GC3 profile differ from native GFL on the primary
foreground PSNR endpoint when both are run on a newly sampled, technically
valid object cohort that has no UID, source-byte, or decoded-render overlap with
the historical evidence set?

The target is the reviewer-requested GC3-versus-GFL comparison. It does not
test a universal schedule law, a dose-independent layer-by-time mechanism,
human-perceived fidelity, or transfer to another adapter. A positive result
confirms the direction of this named comparison on a new object cohort; it
does not establish that the old +0.96 dB estimate is unbiased or portable.

## Cohort construction and freeze

- Source: Objaverse v1, repository `allenai/objaverse`, pinned to dataset
  revision `21e4e142159e2153706c23a3a02e55cec5591cea`. The revision, exact
  object-path metadata hash, per-object license metadata, downloaded GLB
  hashes, rendering hashes, and selection seed will be recorded in the cohort
  manifest.
- Eligible object licenses are restricted to `cc0`, `by`, and `by-sa` tags.
  Unknown, noncommercial, no-derivatives, and otherwise unrecognized terms are
  excluded. Attribution is retained for every selected asset. Raw assets and
  rendered object panels are not included in the public GitHub package unless
  their individual redistribution terms are separately cleared.
- Candidate UIDs are sampled from the pinned source using seed `20261006`
  after excluding every identifier in the historical training/evaluation,
  Fresh300, Fresh B, MV-Adapter, MVDiffusion, and recorded exploratory result
  sets. The 508-object screened local pool is excluded in full, including
  objects that failed its former technical screen.
- The first 600 license-eligible, UID-disjoint candidates form the frozen
  technical-screen pool. If fewer than 300 pass the frozen technical gates,
  the next candidates in the already frozen shuffled queue are screened in
  blocks of 200, up to 1,000 total. No model outputs, method scores, semantic
  preferences, or visual-quality judgments may affect inclusion or replacement.
- Technical gates match the prior V3 cohort: nonempty finite GLB geometry;
  successful 17-view Blender 4.2.4/Cycles render with image, normal, camera,
  and depth products; foreground coverage in `[0.02, 0.95]` for the frozen
  protocol views; no source-GLB byte hash shared with any screened historical
  GLB; and no exact decoded-RGBA pixel signature shared across the 17 views
  with any historical or selected candidate object.
- Select 300 objects by `numpy.random.default_rng(20261006).choice` from the
  lexicographically sorted, technically valid, identity-deduplicated pool.
  If the final valid pool has 276–299 objects after the 1,000-candidate cap,
  use all of them and mark the 300-object precision target unmet. Fewer than
  276 means stop before model inference and report the cohort gate as blocked.
- Freeze the ordered UID list, manifest, hashes, exclusions, validity audit,
  and source/license registry before model inference. Object indices and the
  runner's `object_seed = 42 + index` are then fixed; no reordering or object
  replacement is allowed after the first method output.

## Frozen methods and execution

Run the unchanged validation-v3 runner and source implementation, with the
same checkpoint, config, metric implementation, reference construction,
six target views, 50 EulerDiscreteScheduler steps, and latent seed 42 recorded
in the Fresh B manifest. Required launch-time SHA-256 values:

| Component | SHA-256 |
|---|---|
| Runner | `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3` |
| Main adapter wrapper | `b6464225ce367e4140d56588ea805921caa1c53bf217898a6a7b05a8e11c13d0` |
| Data utilities | `e078f9e2cb3d85447f036fa4c0158929fa4e5f3c7f17571ed6bf0c6f7e7f94f3` |
| Generation logic | `5da7fff22ea73b6d9500603d0905eda9a1ac9c44406346b259f3aba368b6ca13` |
| Metric implementation | `adb317473f7ba77a71d716a293b00243a2aca2b5caf250b702fcb333f7e019b5` |
| Checkpoint | `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0` |
| Config | `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b` |

The four fixed conditions are `no_adapter`, `native_gfl`, `native_gfh`, and
`native_gc3`. GFL and GC3 form the sole confirmatory pair. GFH and no-adapter
are prespecified context controls. Native cap semantics remain enabled for all
adapter conditions; no scale, window, metric, object, or grouping search is
permitted. Each object-condition row must pass the existing shared-input hash
check. Expected coverage is `N × 4` unique rows.

Before launch, verify all recorded source hashes, checkpoint/config identity,
two-GPU device visibility, complete cohort assets, and a two-object smoke test
that does not inspect comparative quality. Any identity mismatch stops the
run. Incomplete rows may be resumed only with identical hashes and protocol.

## Endpoints and analysis

- **Single primary endpoint:** paired object-level mean difference
  `native_gc3 − native_gfl` in FG-PSNR (dB), with a two-sided paired t-test at
  alpha 0.05 and a 95% percentile object-bootstrap interval (10,000 resamples,
  bootstrap seed `20261006`). A positive confirmatory direction requires the
  lower confidence limit to exceed zero. The point estimate and interval,
  not the p-value alone, determine interpretation.
- **Six secondary Core-7 endpoints:** FG-LPIPS, FG-SSIM, Edge-SSIM, Full-PSNR,
  Full-LPIPS, and Full-SSIM. Report paired mean differences, object-bootstrap
  intervals, and Holm-adjusted p-values as one six-test family. These cannot
  replace the primary endpoint or support an overall-winner claim when
  directions disagree.
- Report median paired change, fraction of objects favoring each condition,
  the full object-level delta file, per-object method failures, and all
  condition-level summaries. Do not treat views, pixels, generation steps, or
  seeds as independent objects.
- No equivalence or non-inferiority claim is allowed; no margin was specified.
  The historical +0.96 dB estimate is shown as a contextual reference only,
  not as an equivalence target.
- First run the integrity gate. Comparative analysis is permitted only after
  unique-key coverage, input hashes, finite metrics, source/checkpoint/config
  hashes, prediction/residual presence, cap traces, and row reconstruction all
  pass. All failures and negative results remain in the evidence package.

## Precommitted interpretation

| Result | Allowed conclusion |
|---|---|
| Primary 95% interval entirely above zero | New-object evidence supports a positive GC3−GFL FG-PSNR difference under this checkpoint, cohort, metric, and native-cap protocol. Compare magnitude and object heterogeneity with earlier cohorts; do not call the old estimate exactly replicated. |
| Interval overlaps zero | The new cohort does not independently establish the primary positive difference. Withdraw the general held-out C3 superiority claim; report the estimate and interval as inconclusive. |
| Interval entirely below zero | The new cohort contradicts the earlier positive direction. Lead with the conflict, retain all cohort estimates, and withdraw a general GC3 advantage claim. |
| Primary positive but secondary endpoints disagree | State the endpoint-specific trade-off; no overall quality or fidelity winner. |

Regardless of result, this follow-up does not close the absent human-response
gate, seam-validation gate, public asset-redistribution review, or R2.1 venue
contribution judgment. Those require separate dispositions.
