# PRE_ACCEPTANCE_AUDIT_20261005 — Scientific Validation V3

**Gate verdict: `PRE_ACCEPTANCE_FAIL`** — exactly one unresolved P0
(interaction-test validity → CLAIM 3). All data, cohorts, identities, and
artifacts pass. Details below; §16 for the verdict logic. **No further
scientific campaign, analysis, or paper edit until the P0 is resolved
(re-analysis only — no experiment reruns are needed).**

> **Superseded snapshot note (2026-10-05):** this audit records the state
> before the user-authorized evidence-closure continuation. Its stop-work
> instruction and its G coverage counts are historical. The frozen G
> completion and corrected n=98/99 analysis are recorded in
> `g_completion18/`, `g_formal_complete/`, and the current
> `PRE_ACCEPTANCE_ISSUE_CLOSURE.md`. Interaction reanalysis after discovery
> of the production test defect remains exploratory; it does not convert the
> replacement test into a preregistered confirmatory analysis. The continuation
> has additional open cohort, boundary, visual, and provenance gates.

---

## 1. Repository state

- Branch `codex/scientific-validation-v3-20261002`, HEAD `7e659c7e`, 36 commits
  since base `29b3a0a6` (`codex/final-evidence-freeze-20261001`).
- All 40,163 changes are additions; zero tracked-file modifications.
- Manuscripts byte-identical to base (SHA256):
  `final_round2.tex` d40b9926…, `supplementary_round2.tex` 98bfe8ed…,
  `response_letter_round2.md` a89f05bc… — **paper untouched** ✓
- Working tree clean except untracked `.codex/`, `.trae/` (IDE state; exclude
  from any push). No scientific process running (all campaigns exited; last
  artifact 10-04 23:32).

## 2. Protocol-freeze chronology

PASS — see `PROTOCOL_DRIFT_AUDIT.md` §1. All protocol locks are write-once,
committed 10-02 10:27–16:49, before every formal outcome (first formal data
16:32; A2 analysis 10-03 01:22; A3 results 10-04 10:50, whose normalization was
frozen 10-02 11:32 with `frozen_before_fresh_evaluation: true`).

## 3. Fresh-cohort integrity

PASS with one P1 — see `COHORT_IDENTITY_AUDIT.md`. Funnel 1638→508→507→493→450→300
re-derived from artifacts; deterministic selection (seed 20261002); zero UID
intersection with all 12 historical sources + safety bucket. One duplicate
**source asset** pair found (pixel-identical renders, 51/51 views): cohort has
299 distinct visual contents across 300 UIDs.

## 4. Silent-substitution audit (mandatory P0 gate)

**PROVEN CLEAN** — see `INPUT_IDENTITY_AUDIT.md`. Five independent evidence
lines: (1) 0 substitution prints in 20 shard logs; (2) in-runner integrity
abort never fired; (3) fingerprint uniqueness (single exception root-caused to
the duplicate source asset); (4) bit-level re-derivation of all six input
hashes for 30 objects spanning every shard boundary — 30/30 exact; (5) live
end-to-end reproduction — 9/9 rows and 9/9 PNGs byte-identical.
Per-row table: `audit_scripts/OBJECT_IDENTITY_PER_ROW.csv` (16,950 rows).

## 5. Engineering-fix semantic audit

PASS — all eight fixes (threads, data-root, global embeds, CSV batching,
ledger-first rebuild, depth conversion, mask cache, stdout) are
SEMANTICS_PRESERVING; the mask cache is vestigial (not referenced by the v3
runner). Empirical drift check: A2 baseline vs A3 baseline bit-identical across
processes; B3 interrupted-pass vs resume-rerun 1050/1050 bit-identical; live
reproduction exact. One implementation regime; no pooling hazard.

## 6. A2 row integrity

PASS — `ROW_INTEGRITY_AUDIT.md`: 4800/4800 rows, unique pairs complete, no
NaN/Inf, all hashes present, shard placement exact, residual logs 16×300,
predictions 4800, CSV rebuild = ledger (max |Δ| = 0.0). The ≤15-row CSV lag is
moot; the preliminary analysis used complete data (n=300 per cell in
`layermap_raw.json`).

## 7. A2 numerical reproduction

Cell-level numbers reproduce **exactly** (independent implementation, raw
ledgers): 15/15 Holm-significant FG-LPIPS cells; ΔLPIPS 0.00036–0.00640 (report
says "≤0.006" — P2 wording); middle_W5 = +0.5145 dB (CI mirrored exactly).
**P0 EXCEPTION**: the Layer×Window interaction p (0.50/0.51) comes from a
zero-power test — see §12.

## 8. A3 actual status

COMPLETE (4800/4800), validated; `a3_baseline` ≡ A2 `a_baseline` bit-for-bit.

## 9. A3 dose-validity verdict

`A3_DOSE_VALIDITY_AUDIT.md`: deep = **VALID_DOSE_NORMALIZED_CONFIRMATION**;
middle = **DOSE_NORMALIZED_DIAGNOSTIC** (approximate: measured E-ratio 5.1× vs
requested 2.73×); shallow = **STRESS_TEST_ONLY** (E-ratio 1394×, 65% >3 dB PSNR
loss, 77% extreme pixels). Spec re-derivation exact (rel. diff 0.0); residual
log semantics correct (post-scale/post-cap injection, requested & effective
scales logged separately).

## 10. B/C actual execution status

B1B2 1800/1800 ✓; B3 2100/2100 unique ✓ (resume artifact documented, replicates
bit-identical); C 2400/2400 ✓. Derived from frozen definitions: 53 conditions ×
300 = 15,900 rows — matches. G formal 1600/1600 (provenance by `source_uid`
only — P2). Nothing was restarted during the audit.

## 11. Visualization cohort provenance

PASS — `select_visualization_24.py` is GT-only (UID + GT texture/coverage/
geometry + technical validity; no method metrics, deltas, rankings, or
win/loss), deterministic (seed 20261002, 9-cell round-robin). **Sandbox re-run
reproduced all four frozen outputs byte-identically** (24/24 UIDs, same order;
frozen artifacts untouched, hashes recorded in the audit log).

## 12. Statistical-pipeline validation

Unit tests (protocol §13): null calibration, injected-interaction recovery,
sign reversal, duplicate-object stress, order invariance — all PASS for the
production machinery **except** the interaction test, which synthetic ground
truth shows has **zero power** (rejects 0/40 at 0.6σ injected interaction;
its bootstrap null mean equals its observed statistic on real data).
Valid cluster-robust Wald re-test on the real data (power- and size-validated):
A2 FG-LPIPS W=481.1, p=8.0e-99 (interaction SS share 43.5%); A2 FG-PSNR W=1880,
p≈0 (56.8%); A3 significantly smaller shares (11.9% / 0.8%). Cross-checked by
naive ANOVA F=117.8 (p=1.9e-179), subsample stability, winsorization. **The
interaction exists on the native-dose map.** Deliverable:
`audit_scripts/STATISTICAL_PIPELINE_UNIT_TESTS.json`,
`audit_scripts/AUDIT_INTERACTION_VALID_TEST.json`.

## 13. Artifact completeness

All campaign artifacts promised by MASTER_PROTOCOL_LOCK are present: ledgers,
rebuilt CSVs, protocol manifests, per-row input hashes, residual logs
(4800/4800 per A2/A3), PNGs, run manifests with checkpoint/object-list SHA256s,
`SHA256SUMS.txt` (304 entries; covers cohort + audit JSONs + source GLBs —
does not cover prediction PNGs: P2, add a SHA index before archiving).
**300M-line debug-log incident**: not independently reconstructable from git
history or disk (no >20 MB log anywhere; history shows only trivial LaTeX log
deletions). Current formal shard logs are complete and small (464 KB/shard,
1200 dataset prints each, 0 substitution prints). If such a log existed it
predates the formal campaign and contained only repetitive loader debug output
of the kind still visible today — **no unique scientific information loss is
detectable, and reproducibility is unaffected** (proven by §4/§5 bit-identical
reproduction). Nothing was deleted during this audit.

## 14. Remote provenance

`git ls-remote origin` fails: `Received HTTP code 502 from proxy` — remote
unreachable (also confirmed by the environment's network policy). Local HEAD
`7e659c7e` **not yet pushed**. Per protocol §1 this is a **P1 operational
provenance issue**: push `codex/scientific-validation-v3-20261002` once the
network allows, after excluding `.codex/`/`.trae/`. Secret scan of the tracked
tree: no credential patterns, no key files; large binaries added by this branch
are limited to `formal_qualitative_archive/contact_sheet_24.png` (50 MB — P2:
prefer SHA-index + artifact location per protocol §16).

## 15. P0 / P1 / P2 issue ledger

| ID | Sev | Issue | Required fix |
|---|---|---|---|
| P0-1 | P0 | Production interaction test (`analyze_v3.py cmd_layermap`) has zero power against object-shared interaction; CLAIM 3 ("interaction NOT SUPPORTED", p=0.50/0.51) and the p=1.0 dose-normalized variant are uninformative. Valid Wald test: interaction highly significant (A2 W=481/1880; A3 W=657/1389; SS shares 43.5%/56.8% → 11.9%/0.8%). | Re-derive CLAIM 3 + the narrative gate with the validated Wald test (`audit_scripts/audit_interaction_valid_test.py`); revise `SCIENTIFIC_VALIDATION_DECISION_REPORT.md` / `NARRATIVE_RESTRUCTURE_REQUIRED.md` wording (interaction present; time-structure variance share strongly reduced at matched dose, esp. FG-PSNR). Analysis-only; no data rerun. |
| P1-1 | P1 | Cohort contains one duplicate source-asset pair (`0099ab6d44…`/`0130e5149b…`; 299 unique contents / 300 UIDs). | Document in cohort description or run leave-one-out sensitivity on summary statistics. |
| P1-2 | P1 | Remote unreachable; branch not pushed; local/remote SHA equality unverifiable. | Push when network allows (after excluding `.codex/`, `.trae/`). |
| P1-3 | P1 | `NARRATIVE_RESTRUCTURE_REQUIRED.md` narrative ("layer-constant representation adequate") partially rests on P0-1. | Re-state after P0-1 resolution. |
| P1-4 | P1 | 300M-line log incident unverifiable from repo/disk (documented as best-effort in §13). | None possible retroactively; note in lab journal. |
| P2-1 | P2 | Report wording "|Δ| ≤ 0.006" understates max 0.0064. | One-word fix in decision report when touched for P0-1. |
| P2-2 | P2 | `SHA256SUMS.txt` does not cover prediction PNGs / rows. | Add SHA index before archival. |
| P2-3 | P2 | 50 MB contact-sheet PNG committed to git. | Prefer SHA-index + artifact location (protocol §16). |
| P2-4 | P2 | G-series ledgers lack `input_hashes` (source_uid only). | Acceptable for the backbone-interface experiment; note in methods. |
| P2-5 | P2 | Vestigial `mask_gt_cache/`; untracked `.codex/`/`.trae/`; stratification in-cell permutation depends on (frozen) cohort row order. | Hygiene notes; no action required for validity. |

## 16. Final gate verdict

Rules: FAIL = any unresolved P0. **P0-1 is unresolved** (its fix is a
re-analysis + document revision that this audit, by mandate, must not perform:
"No new claim may be made before this gate passes").

# ⇒ `PRE_ACCEPTANCE_FAIL`

**Already-produced results that ARE scientifically usable:** every row-level
artifact of A2/A3/B1B2/B3/C/G (integrity, identity, determinism all proven);
A2/A3 cell-effect estimates and CIs; B3 decomposition; E failure-boundary
replication; F bake evidence; the cohort itself (modulo P1-1 documentation).

**Must be rerun:** nothing.

**Which campaigns should resume next:** none, in the protocol's sense — the
campaign is complete. The only permitted next step is the P0-1 re-analysis and
decision-report revision, then user review.

---

## §18 STOP

This audit stops here. Performed actions were strictly read-only with respect
to all pre-existing scientific artifacts (verified: frozen file hashes/mtime
unchanged; sandbox reproduction isolated in /tmp). New files created by this
audit: `CAMPAIGN_STATE_SNAPSHOT.json`, this report, the five section audits,
`A3_DOSE_VALIDITY_AUDIT.md`, and `audit_scripts/` (7 scripts, 5 result JSONs,
`OBJECT_IDENTITY_PER_ROW.csv`, `STATISTICAL_PIPELINE_UNIT_TESTS.json`).

Awaiting user review before any further execution.
