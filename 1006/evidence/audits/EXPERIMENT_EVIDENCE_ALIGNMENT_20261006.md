# Experiment evidence alignment — pre-Fresh-C status snapshot

> **Superseded status note:** This report preserves the strategy/cohort map as
> it stood before Fresh C method outputs. Its statements that Fresh C had no
> method output, the addendum was awaiting the primary gate, and the final
> gallery was pending are historical. The current post-run authority report is
> [`FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md`](/4T/CXY/MV-Painter/1006/evidence/audits/FRESH_C_STRATEGY_COMPARISON_REPORT_20261006_ZH.md),
> which records both PASS integrity gates, the independent direction audit,
> completed analyses, the final 20-group gallery, and remaining reviewer gates.

This is a compact navigation and claim-boundary map for the strategy and
cohort audit. It does not change any experimental rows, register a new
hypothesis retroactively, or edit the submitted 01549 manuscript. Where
reports and source rows disagree, use the source rows, run manifest, frozen
protocol, and signed direction errata in that order.

## Strategy semantics

| Strategy | Requested profile | Native-cap execution | Evidence role |
|---|---|---|---|
| GFL | Constant 1.25 at deep, middle, shallow | Shallow is capped at 0.8 | Fixed-low baseline; not the same realized residual dose as LLH. |
| GFH | Constant 2.50 at all three groups | Shallow is capped at 0.8 | Fixed-high comparator; several full-image endpoints trade against foreground behavior. |
| C3 / `native_gc3` | Deep/middle 1.25, 2.50, 1.25 by early/middle/late stages; shallow requests the same | Shallow is capped to 0.8 throughout; this is not an uncapped 1.25/2.50/1.25 intervention | Original tested strategy. Its Fresh C−GFL FG-PSNR contrast remains the unchanged primary confirmation. |
| LLH / `layer_llh` | Deep/middle 1.25, 1.25, 2.50; shallow 0.50, 0.50, 0.75 | All listed shallow values are below the 0.8 cap | Registered temporal profile; neither a universal optimum nor a method contribution by name alone. |
| LHL / `layer_lhl` | Deep/middle 1.25, 2.50, 1.25; shallow 0.50, 0.75, 0.50 | Native cap remains enabled | Timing comparator; same nominal layer means do not imply equal realized residual dose. |
| LLL / `layer_lll` | Constant low profile (1.25, 1.25, 0.50) | Native cap enabled | All-low profile; LLH−LLL changes overall requested intensity as well as placement. |
| HLL / `layer_hll` | High early then low (2.50, 1.25, 1.25; shallow 0.75, 0.50, 0.50) | Native cap enabled | Early-high contrast; the full “early hurts/late helps” conjunction is not supported across endpoints. |
| LFM-exact | Constant requested per-layer means (1.675, 1.675, 0.585) | Native cap enabled | Closest requested-mean control for LLH; requested means do not equalize realized residual norms. |
| Endpoint-matched generic linear | Ramps linearly from each layer's LOW to HIGH over 50 steps | Shallow cap clips the ramp above 0.8 | Strong simple competitor. The C and B LPIPS direction is corrected in [the erratum](LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md). |
| Other generic schedules | Frozen cosine, trapezoid, Gaussian, with endpoint-matched and nominal-budget-matched variants | Native cap enabled | C compares the frozen schedule family; B's dose-sensitivity addendum is post-lock. Do not form a global leaderboard. |
| A2 / A3 / A3b maps | Window-specific layer perturbations at registered native or stress scales | A3b has no three-layer common-dose support; A3 shallow is an extreme stress regime | A2 is discovery at native dose; A3 is stress; A3b supports bounded response heterogeneity, not dose-independent optimality. |
| E5 / E6 | Residual-dose feasibility and cap-internal calibration candidates | E5 did not achieve a three-group dose match; E6 stopped at the method-difference/value gate | Feasibility/negative-result evidence only; no E6 Fresh D. |

## Cohort and design boundaries

| Evidence block | Cohort and status | Allowed interpretation |
|---|---|---|
| 01549, clean-v2, strict-276, stage-placement | Historical/reviewed cohorts; runner and provenance details differ across stages; strict-276 has incomplete per-object input-hash chain | Historical and execution-semantics context. Do not pool uncapped and native-capped absolute scores or call strict-276 a new held-out confirmation. |
| Registered Experiment C generic comparison | N=300 from the FRESH_CONFIRM_300 UID list; LLH rows are in the sibling `campaign_B1B2` run and generic-linear rows in `campaign_C`; 300/300 UID, index, seed, and six input-tensor hashes match | The raw comparison is reproducible as a paired same-input estimate. Both old run manifests omit the config hash. Its LPIPS direction is governed by the source-row audit and erratum, not the superseded summary sentence. |
| A2/A3/A3b | A2 discovery; A3 stress; A3b Fresh B bounded-map follow-up | Separate scale regimes and estimands. Significance is not mechanism strength; report interaction magnitude and relation to realization variability. |
| FRESH_CONFIRM_B registered B1/B2/B3 | N=150, disjoint cohort; frozen primary LLH contrasts; additional C3−GFL selected after unblinding | Registered LLH contrasts and retrospective C3 supplement stay separate; objects are the units, not views or repeated seeds. This is distinct from the older 300-object directory named `campaign_B1B2`. |
| Fresh B generic extension | Same N=150 cohort, added post-lock | Sensitivity only; LLH−linear is near zero on FG-PSNR and favors linear on FG-LPIPS. No new-cohort replication. |
| E1 multi-seed / E2 static factorial | Reused fixed 48-object B subset; 3 seeds | Within-object realization sensitivity and static scale response; do not add 48 objects or claim a temporal interaction from E2. |
| MV-Adapter / MVDiffusion | Separate backbone/control-interface protocols and cohorts | Interface boundary only. A significant result in one and a null in another do not identify an architecture-caused difference. |
| Human study | Old LLH package never distributed; no responses received | No human-fidelity conclusion. Any future supplied response file must be checked against the frozen response-format guide before analysis. |
| GLB, visual panels, seam, FAC | N=20 sampler-conformant unlit base-color re-render; 24-object author panel; seam integration unresolved; FAC not in current method | GLB is a bounded artifact endpoint, panel is descriptive, neither substitutes for blind human fidelity or full PBR. |
| Fresh C primary and addendum | New disjoint cohort is at cohort freeze/identity audit; latest renderer ledger has 246 newly completed, 337 complete skips, 11 timeouts, and 593/594 depth conversions. No method output or integrity PASS exists. | C3−GFL primary is unchanged. LLH/linear are a separately locked revision-era prospective extension, not the original preregistration. The failed rows and any predeclared reserve use remain in the audit trail. |

## Direction and analysis safeguards

All pairwise estimates are condition A minus condition B. FG-PSNR and
similarity metrics are higher-is-better; LPIPS and other error metrics are
lower-is-better. A positive LPIPS contrast therefore favors condition B.
Use each contrast's object-level paired estimate and interval; do not infer
significance for a selected object image. Distinguish statistical support,
effect magnitude, favorable-object fraction, and practical/artifact scope.

The Fresh C addendum is frozen in
`../protocols/FRESH_C_COMPARISON_ADDENDUM_20261006.md` and enforced by its JSON
lock and separate runner namespace. Manuscript, figures, tables, and reviewer
response stay frozen until Fresh C plus the addendum pass their separate
integrity gates and the scientific evidence map is revalidated.

## Recomputed strategy comparisons and narrative implications

The historical formal pairwise audit rebuilt 19 saved pairwise files from the
raw shard ledgers: 18 formally labeled comparisons and one exploratory
HLL-versus-LLL comparison. All means, medians, percentile intervals,
bootstrap sign p-values, direction-aware favorable fractions, UID counts,
object indices, seeds, and shared-input hashes reproduced. Five stored Holm
families comprising 28 tests also reproduce. See
`FORMAL_PAIRWISE_DIRECTION_AUDIT_20261006.md` and
`FORMAL_HOLM_FAMILY_AUDIT_20261006.md`.

The B temporal evidence has a narrow but coherent reading. On the disjoint
N=150 FRESH_CONFIRM_B cohort, registered LLH−LFM-EXACT improves both mean
foreground endpoints, but both intervals fall inside the predeclared practical
margins; requested means match while realized residual norms do not. LLH−HLL
also favors LLH on both means after the frozen four-test Holm family, but only
45.3% of objects favor LLH on FG-PSNR and its median is negative. LLH−LLL
favors LLH on both endpoints, though this also changes requested intensity.
The post-unblinding HLL−LLL check is exploratory: FG-PSNR crosses zero, while
FG-LPIPS favors LLL. These data do not establish a complete “early harmful,
late beneficial” rule or a dose-independent temporal mechanism. The exact
estimates and chronology limits are in `FRESH_B_TEMPORAL_CONFIRMATION_REPORT.md`.

Generic linear remains a serious comparator. In the older N=300 same-cohort
Experiment C pairing, LLH−linear FG-PSNR is near zero with an interval spanning
zero and no equivalence margin; LLH−linear FG-LPIPS is positive and Holm
significant, which favors linear because LPIPS is lower-is-better. The
post-lock N=150 B extension also favors linear on FG-LPIPS, but it is not an
independent replication. Neither result makes linear a universal winner; both
prevent claiming LLH as the unique winner. The 300-object C comparison also
has a legacy config-hash gap and must remain retrospective.

Together with the corrected signs, dose-support limits, GLB endpoint trade-offs,
and descriptive panel failures, the current evidence supports a bounded
empirical description of requested-versus-applied residual allocation and
contrast-specific object responses. It does not yet select C3, LLH, or linear
as an overall winner. Fresh C may strengthen or weaken C3's new-object
FG-PSNR result, while the separately frozen addendum tests LLH and linear on
that same new cohort. The final evidence freeze and all narrative text remain
pending those gates.

## Visual-comparison implementation status

One seven-column layout prototype (reference plus GFL, GFH, no-adapter, C3,
LLH, and generic linear; six shared views) was generated from the first UID in
the pre-outcome Visualization-24 list and manually inspected. It is explicitly
tagged as retrospective layout QA, not Fresh C evidence; source rows confirm
the same UID, seed, and six input hashes, while the legacy config-hash gap
remains. The final gallery builder refuses to run until both Fresh C integrity
gates pass. It will emit separate endpoint and multiplicity-family rankings,
individual C3/LLH/linear-versus-GFL endpoint pages, a cohort forest plot, and
up to 20 unique example objects balanced across C3−GFL, LLH−C3, LLH−linear,
and C3−linear (or all objects for a smaller cohort). Each object has a focal
contrast and separate PSNR/LPIPS deltas; no object-level significance or
cross-metric champion score is used. The registered cohort-level tests are
ranked by adjusted p-value within their endpoint/family, with effect size,
interval, and favorable-object fraction alongside. Outcome-ranked examples
are not used to select human-study stimuli. See
`../../figures/strategy_comparison_gallery/` and
`../../scripts/generate_strategy_comparison_gallery.py`.

Source-checked historical comparison figures are stored separately under
`../../figures/evidence_alignment/`. They include B's four per-object endpoint
tradeoffs, the retrospective same-UID Campaign C LLH–linear comparison, GT
texture-complexity heterogeneity, and separate MV-Adapter and MVDiffusion
interface-boundary plots. Each plot labels its delta direction, cohort and
unit; associated object-level tables retain UIDs and source cohort. These
figures reproduce already observed evidence only. They do not replace the
Fresh C gates or form a cross-metric/backbone ranking. Figure-specific claims
and limitations are recorded in
`next_stage_20261006/STRATEGY_FIGURE_ALIGNMENT_20261006_ZH.md`; source hashes
and generation details are in
`../../figures/evidence_alignment/FIGURE_SOURCE_MANIFEST.json`.
