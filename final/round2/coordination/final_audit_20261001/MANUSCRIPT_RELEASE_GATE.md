# Manuscript Release Gate (Final Evidence Convergence, 2026-10-01)

Branch `codex/round2-evidence-integrated-20261001`. Scope: the last governance gate
before the manuscript-rewrite window. **No manuscript text (tex/letter) was modified in
this gate** — this document records (a) the evidence-convergence state, (b) a high-risk
claim-word scan of the current manuscript files, (c) the banned/replacement wording
table, and (d) the claim-width release rule that the rewrite must obey. A rewrite
window may start only against the frozen claim set below.

Inputs verified at this gate: M3 mapping runs and LHL-forensics stage-2 are committed
in-tree at `75a4068` (both were found already merged during convergence; governance
docs updated in the same convergence commit as this gate). Authoritative inventory:
`final_round2_evidence_inventory.md` (re-signed at the convergence commit).

## 1. Evidence-convergence status (what changed at this gate)

| Item | Pre-gate state | Post-gate state |
|---|---|---|
| M3 frozen-value mapping run (3 × 76) | governance docs said "not yet run" | **RESOLVED** — committed at `75a4068` (`results/holdout_exact_mapM3_{llh,lhl,fix}_76/`, 77-row CSVs); 16/18 MAPPING_STABLE, primary effects slightly stronger; incorporated into `MVADAPTER_LAYER_MAPPING_SENSITIVITY_REPORT.md`, readiness report §2/§3, claim matrix |
| LHL-forensics stage-2 | "only under reviewer pressure" | **RESOLVED** — committed at `75a4068` (`lhl_forensics/`): aug-ON regen bit-exact; aug-OFF still −6.96 dB on hexuid → cond-augmentation hypothesis refuted; Case B strengthened (`ARCHIVED_LHL_PROVENANCE_AUDIT.md` §8) |
| Metric convention contradiction | Finding 1 said "all active surfaces share one convention" while the table showed two | **FIXED** — `metric_direction_audit.md` now states two coexisting presentation conventions + manuscript single-convention rule (Finding 6) |
| "invariant to the exact layer partition" | used in readiness report / narrative / mapping report | **NARROWED** — "robust to the tested contiguous layer partitions" (budget-neutral B′ + frozen-value M3 axes); "invariant" banned |
| Bake cross-view metric | risk of being read as texture fidelity | **NARROWED** — "render-time cross-view color-stability descriptor" only; UV-seam ΔE00 is the direct texture-space evidence (`baking_consistency_report.md` §4) |
| Evidence inventory | recorded HEAD `d30ed4f`, no M3/stage-2 rows | **RE-SIGNED** at the convergence commit with M3 + stage-2 rows and full deliverable re-verification |
| Experiment phase | partially open | **FROZEN** — no further GPU runs without an explicit reviewer requirement (fourth backbone, schedule search, seed expansion, bake enlargement all closed) |

## 2. High-risk word scan of the current manuscript files

Scanned: `final_round2.tex`, `supplementary_round2.tex`, `response_letter_round2.md`
(blob SHAs identical to the 0930-frozen `edfb8d0` versions). Verdicts: **PASS** = safe
at current width; **FIX-AT-REWRITE** = mandatory change in the rewrite window;
**WATCH** = allowed in this context, re-check after edit.

| # | Hit (file:line) | Context | Verdict | Required width / action |
|---|---|---|---|---|
| 1 | final_round2.tex:604-605 | "archived **unseeded** layer-LHL record (e.g. FG-PSNR 12.97 vs **14.78**; Pearson r=0.66)" | **FIX-AT-REWRITE** | Case-B sentence only: record excluded because complete provenance cannot be guaranteed (uncommitted, unreconstructible runner-time state); never quote 14.78 in a comparison; "unseeded realization" is retired as a standalone cause (contradicted by stage-2 and R0/R1) |
| 2 | supplementary_round2.tex:471-475 | "an **unseeded** Python RNG … archived **14.78** … a single **unseeded** run" | **FIX-AT-REWRITE** | Same Case-B replacement; the r=0.66 restart-scatter fact may stay only if explicitly framed as cross-restart irreproducibility, not as the cause of the mean-level gap |
| 3 | response_letter_round2.md:113-116 | "archived **unseeded** layer-LHL record (FG-PSNR 12.97 vs **14.78** …) … a single **unseeded** run" | **FIX-AT-REWRITE** | Same Case-B replacement in the letter |
| 4 | final_round2.tex:69, 429; response_letter_round2.md:186 | "robust directions (late-high helps, early-high hurts)" | PASS | Correctly scoped to the factorial directions; keep this width |
| 5 | final_round2.tex:83 | "cross-category generalization" | PASS | Describes prior cited work, not our method |
| 6 | final_round2.tex:660, 774; response_letter_round2.md:43 | "cross-view/source-fusion colour inconsistency" | WATCH | Describes a failure mode of source-fusion (problem statement), not our bake cross-view metric; keep distinct wording at rewrite |
| 7 | supplementary_round2.tex:257 | "without claiming optimality across adapters" | PASS | Correct bounded denial; keep |
| 8 | response_letter_round2.md:190 | "uniquely optimal, universally superior, or CAI-derived" | PASS | Denial sentence; keep |
| 9 | response_letter_round2.md:17, 69-73 | "legacy numbers (+0.96 dB …) retired" | PASS | Retirement statement; keep |
| 10 | final_round2.tex:34 (abstract) | "representative rather than an optimum … rather than as a universal schedule selector … bound where stage effects replicate" | PASS | Exactly the frozen narrative width; keep |
| 11 | final_round2.tex:206, 209, 504, 743, 815 | CAI as diagnostic, set-valued rule, "no universal schedule, no layer-wise cross-backbone [universal claim]" | PASS | Matches the CAI bound (`undefined_set_valued`); keep |
| 12 | (absent) mapping-partition sentence | no partition/mapping claim exists in the manuscript yet | **ADD-AT-REWRITE** | One sentence at tested-partition width (see §4.4 of narrative recommendation); never "invariant" |
| 13 | (absent) Core-7 baseline family | manuscript baseline numbers predate Core-7 completion | **ADD-AT-REWRITE** | Replace baseline-family numbers with the Core-7 same-runner matrix per narrative §4.2 |

## 3. Banned / replacement wording table (binding for the rewrite)

| Do NOT write | Write instead | Authority |
|---|---|---|
| "generalizes across backbones" | "transfers to one additional adapter architecture (MV-Adapter); does not replicate on MVDiffusion" | claim matrix; MVDiffusion negative preserved |
| "CAI automatically discovers the schedule" | "CAI provides diagnostic motivation; the frozen rule is set-valued" | `undefined_set_valued` |
| "universal optimal schedule" / "the optimal LLH" | "architecture-dependent effective residual allocation; on the main pipeline LLH is best of seven same-runner conditions" | Core-7 matrix |
| "improves texture quality" (unqualified) | "generated texture statistics closest to GT (distance-to-GT framing), with listed exceptions" | texture audit |
| "invariant to the exact layer partition" / "robust to arbitrary layer grouping" | "robust to the tested contiguous layer partitions (budget-neutral re-partition indistinguishable; degenerate partition bitwise; frozen-value M3 direction-preserving and slightly stronger)" with the PSNR-nuance | mapping reports (B′ + M3) |
| "unseeded realization" as the archived-record cause | Case-B sentence: excluded because complete provenance cannot be guaranteed | Case-B forensics + stage-2 refutation |
| "+0.96 dB" / "14.78" as comparisons | never quote; all baselines from the Core-7 same-runner table | Case-B exclusion |
| "cross-view texture consistency/fidelity" (our bake metric) | "render-time cross-view color-stability descriptor"; seam ΔE00 is the direct texture-space evidence | bake report §4 |
| blanket "robust/stable conclusions" | "stable across two frozen realization sets (R0/R1): 27/28 STABLE_STRONG, 1 STABLE_DIRECTIONAL" | robustness-1 |
| "all phases closed" (unqualified) | "all mandatory audit phases closed for the frozen claim set" | this gate |

## 4. Claim-width release rule (frozen set; a sentence may be written only inside these)

1. Fidelity: "best of seven same-runner conditions on the 276-object strict holdout"
   (FG-PSNR/FG-LPIPS/Full-PSNR/Full-SSIM) — Core-7 matrix.
2. Texture: "closest to GT statistics" (distance-to-GT) with the four enumerated
   exception cells.
3. Transfer: "one additional adapter architecture (MV-Adapter), layer redistribution
   supported, temporal placement not separated; not replicated on MVDiffusion".
4. Partition: "robust to the tested contiguous layer partitions …, with the
   PSNR-significance nuance" — never "invariant".
5. Stability: "stable across two frozen realization sets".
6. Baking: "12-object stratified case study; layer_llh lowest seam ΔE00 and lowest
   render-time cross-view stability descriptor of eight variants" — cross-view named
   as a render-time descriptor.
7. History: Case-B exclusion sentence only; archived numbers never quoted.

## 5. Presentation conventions (single-source rules)

- **Metric convention:** the manuscript uses the benefit-oriented convention
  everywhere (`metric_direction_audit.md` Finding 6). Any number imported from the
  Core-7 raw-delta surface must be re-expressed (or the table carries one explicit
  convention note). Readers must never see "+0.0308 LPIPS = better" and "−0.0449
  LPIPS = better" side by side.
- **Evidence-type labels:** seam ΔE00 = direct texture-space evidence; cross-view ΔE00
  = render-time stability descriptor; M3 = budget-changing axis vs B′ =
  budget-neutral axis (never mixed in one comparison sentence).
- **Status precision:** "all mandatory audit phases closed for the frozen claim set"
  is the strongest permitted closure statement; unqualified "all phases closed" is
  forbidden.

## 6. Verdict

**GATE: PASS** for entering the manuscript-rewrite window, subject to the three
FIX-AT-REWRITE clusters (rows 1-3 of §2) and the two ADD-AT-REWRITE items (rows 12-13)
being executed in that window. The experiment phase is frozen: no new runs without an
explicit reviewer requirement. Rewrite order per the narrative recommendation:
Core-7 main evidence → texture/robustness → MV-Adapter bounded transfer (with the
mapping-robustness sentence) → MVDiffusion boundary.
