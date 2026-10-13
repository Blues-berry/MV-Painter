# Coordination Decision Log

All decisions below are scoped to the Round-2 evidence audit. They do not
revert or overwrite pre-existing worktree changes.

## 2026-09-29 — D0: adopt the local repository as the source of truth

- Basis: direct inspection found newer B unified results, A serialization
  trace artifacts, and D CPU bake outputs than some agent status files.
- Decision: use the newest protocol-linked artifact for experiment state, while
  retaining stale status files as provenance and marking their conflicts.
- Risk: a live process can change an output directory during audit.
- Action: do not edit the live D bake directory; record it as `IN_PROGRESS`.
- Acceptance: after process exit, require complete record counts and hashes.

## 2026-09-29 — D1: freeze the old `+0.96 dB` narrative

- Basis: historical evaluation/training UID overlap, missing original v1
  checkpoint, and clean-v2 fixed-low comparisons.
- Decision: do not use the old value in any new table or claim; do not alter
  data/model selection to recover it.
- Alternative rejected: replacing more objects, changing C3, retraining, or
  selecting a favorable metric path.
- Acceptance: every paper-facing number names the clean-v2 protocol and
  checkpoint hash.

## 2026-09-29 — D2: Full-SSIM is a stop-gate, not a paper number

- Basis: all-300 reconciliation gives C3−fixed-low `+0.004563` on recorded
  float-eval A, but `−0.000587` on the selected PNG/raw-GT C branch; original
  A/B tensors are unavailable.
- Decision: preserve A, B and C separately; do not patch metrics or insert a
  new Full-SSIM ranking into the manuscript.
- Next owner: A runs the fixed 12-object same-generation trace; D independently
  checks the interpretation.
- Acceptance: exact A/B/C tensor metadata, pixel error and same implementation
  SSIM are available; then one path is frozen and all four conditions are
  recomputed consistently.

## 2026-09-29 — D3: release B from GPU and freeze its interpretation

- Basis: B delivered complete unified CSV/Markdown and paired JSON over the
  same 76-object Exact Mesh cohort.
- Decision: no additional MV-Adapter inference in this cycle. Treat selected
  pair and LHL as separate diagnostic families; retain `undefined_set_valued`.
- Acceptance: complete numerical handoff and GPU handoff are present; both
  were verified from the local files.

## 2026-09-29 — D4: preserve and complete D's CPU bake

- Basis: two-object outputs are actual textured GLBs, UV-preserving exports,
  unseen renders and metrics. A 12-object CPU bake is already active.
- Decision: let the live process finish; do not start CUDA baking or a second
  CPU bake. Evaluate its outputs afterward.
- Acceptance: 12 objects × four methods × metadata/texture/coverage/GLB/render
  outputs; 11 unseen views/object; GT-relative metrics; raw and inpainted
  coverage reported; GLB mesh/UV identity checks pass.
- Limitation: even a successful 12-object result is stratified descriptive
  evidence, not a 276-object population estimate.

## 2026-09-29 — D5: next GPU order

- Decision: after D's CPU bake remains isolated, use the first confirmed CUDA
  slot for A's 12-object Full-SSIM trace. Only after the trace command is
  verified and the device is free, run A's frozen 276-object stage placement.
- Preferred allocation: GPU0 for the short trace, then GPU1 for the longer
  stage run, subject to a fresh `nvidia-smi`/PyTorch check. No process is to be
  killed to obtain a slot.
- Acceptance: same seeds/checkpoint/list hashes as the frozen protocols; no
  cohort, model or metric changes.

## 2026-09-29 — D6: Codex C remains blocked

- Basis: G1, G2 and G4 are not all accepted, and the claim ledger contains
  unresolved metric and 3D scope restrictions.
- Decision: C may prepare formatting, LaTeX compilation and response-letter
  scaffolding only. C may not revise Abstract/Results/Discussion/Conclusion
  with final numeric claims.

## 2026-09-29 — D7: translate the attached reviews into gates

- Basis: the preserved R1/R2/R3 PDF and the current paper source were read
  together with the local artifacts.
- Decision: R1's practical-value request maps to D's real Exact-GLB bake and
  unseen-view validation; R1's metric request maps to A's Full-SSIM trace and
  final metric freeze. R2's novelty request maps to A's equal-mean placement
  experiment and B's bounded cross-backbone interpretation.
- Interpretation: R3's positive assessment does not waive unresolved R1/R2
  evidence. Review comments are constraints, not authorization to mutate
  experimental state.
- Operational orders: `AGENT_ORDERS.md`; review provenance and matrix:
  `REVIEW_CONSTRAINTS.md`.

## 2026-09-29 — D8: preserve paper source until evidence freeze

- Basis: `final/round2/final_round2.tex` still contains old or stronger
  statements, including the historical 0.96 dB abstract path, broad
  middle-stage robustness language, and baking-based evidence language.
- Decision: no paper edit is authorized in this coordination turn. C may only
  prepare placeholders and compilation scaffolding. After G1–G4, E will issue
  a narrative decision and then authorize the minimum necessary source edits.

## 2026-09-29 — D9: accept D's 12-object bake with explicit limits

- Basis: 48 textured Exact-GLB exports, 528 unseen-view rows, finite CPU
  metrics, Blender import audit, and visual spot checks.
- Decision: G4 moves to `PASS_WITH_LIMITATIONS`. The evidence is sufficient to
  answer R1's “is there a real bake path?” question at implementation/case-study
  scope, but not to claim a population-level TCAS advantage.
- Limits: Blender exporter vertex reindexing is observed for obj_0048 while
  polygon/UV-loop semantics remain stable; DISTS is unavailable; the 12-object
  run has no `gt` bake and the evaluator's `gt_to_gt_sanity_rows` field is not
  accepted as evidence of one.
- Paper consequence: C may cite real baked unseen-view feasibility only with
  these scope limits after G1/G2 are also accepted; no 12-object superiority
  table is released as a general result.

## 2026-09-29 — D10: close the live bake task and preserve its limits

- Basis: process exit, 48 completed method records, 528 unseen-view records,
  finite enabled metrics, Blender audit, and visual spot checks.
- Decision: D's bake execution task is closed for this cycle. The existing
  outputs are accepted only as stratified case-study/implementation evidence;
  no duplicate bake, expanded cohort, DISTS substitution, or 12-object GT
  rerun is authorized before the G1/G2 decision.
- Bookkeeping: the dated addendum in `CODEX_D_STATUS.md` and
  `BAKE_12_VALIDATION_AUDIT.md` are the current acceptance records; earlier
  next-step text remains provenance.

## 2026-09-29 — D11: use durable orders instead of duplicating A/B work

- Basis: A and B are active in separate conversations, while D remains
  active elsewhere. The cross-thread listing endpoint did not return usable
  thread identifiers in this turn.
- Decision: two temporary read-only preflight proxies were started only to
  check the A/B handoff conditions, with explicit no-GPU/no-write constraints.
  They timed out without producing a result and were closed. No experiment,
  file edit, or resource allocation was caused by those proxies.
- Operational source of truth: send A/B the exact orders in
  `AGENT_ORDERS.md`; enforce the serialized GPU queue in `GPU_QUEUE.md`.
  Do not create duplicate A/B experiments while their original conversations
  remain active.

## 2026-09-29 — D12: advance the frozen A queue after D completion

- A-1 controlled trace completed on GPU0 with 48 rows and 168 tensors. It
  confirms identical A/B pre-save tensors and a nonzero B→C PNG reload
  boundary; the historical 300-object tensor limitation remains.
- Decision: G1 is `PASS_WITH_LIMITATIONS`; the PNG-reloaded float32/raw-GT
  branch is the saved-artifact recommendation and no metric patch is applied.
- A-2 was then launched on GPU1 in the new
  `stage_placement_276_20260929` directory with the frozen checkpoint,
  strict-276 list, seed 42, 50 steps, unique6 mapping and `--resume`.
  Partial records are not accepted as evidence and no duplicate launch is
  allowed.

## 2026-09-29 — D13: convert A-2 to an independent resumable run

- The original interactive execution stopped without a terminal manifest
  after producing valid atomic records. A read-only audit found 204 valid
  records and no error log; the launcher observed 209 valid records at its
  start, so it resumed rather than recomputing completed objects.
- Decision: A-2 now runs independently through
  `scripts/run_stage_placement_276_20260929.py` with `CUDA_VISIBLE_DEVICES=1`,
  fixed run ID `stage_placement_276_20260929_resume_v2`, durable
  `status.json`, `final_manifest.json`, `DONE/FAILED`, and a fixed log path.
- The launcher estimated completion at `2026-09-29T05:45:07Z` from the
  observed per-object throughput. No intermediate records or GPU status are
  to be polled before that checkpoint unless an external failure event occurs.

## 2026-09-29 — D14: remove a stale interactive duplicate

- The one-time launch safety check found the old interactive A-2 PID 687819
  still writing the same output directory alongside the new independent
  launcher (PID 691881/691883).
- Decision: PID 687819 was terminated precisely; the independent launcher was
  preserved. A post-termination check confirmed only PID 691881/691883 remain.
  The final manifest and record validation remain mandatory because the stale
  process had briefly overlapped the resume launch.

## 2026-09-29 — D15: install the low-frequency ETA acceptance handoff

- Basis: the A-2 launcher now owns the GPU1 run with durable `status.json`,
  `final_manifest.json`, `DONE/FAILED`, and a fixed ETA of
  `2026-09-29T05:45:07Z`.
- Decision: no interactive polling or `write_stdin` is permitted during the
  training window. A detached dispatcher waits for the ETA, then runs the
  acceptance gate once; if the run is still active it schedules only the next
  explicit 30-minute checkpoint.
- Acceptance gate: `scripts/validate_stage_placement_276_20260929.py` checks
  276×4 atomic records, finite metrics, exact object/schedule coverage, 50
  actual residual L2/RMS steps, and paired 10,000-resample CIs/win rates.
- Handoff: success creates `NEXT_ITERATION_READY.json` for E G2–G4 review;
  failure creates `NEXT_ITERATION_BLOCKED.json`. Codex C remains blocked from
  paper edits. This local dispatcher cannot open a new Codex conversation;
  it provides the durable continuation marker instead.

## 2026-09-29 — D16: accept A-2 and freeze the saved-artifact Full-SSIM branch

- Basis: A-2 finished at `2026-09-29T05:37:40Z` with exit code 0, 276 records,
  zero errors, four schedules per object, finite metrics and actual 50-step
  residual logs. The terminal acceptance gate used 10,000 object-level paired
  bootstrap resamples.
- Provenance correction: the formal runner computed Full-SSIM before PNG
  serialization. E therefore ran a separate CPU-only postpass over the frozen
  prediction PNGs and original RGBA/white-background GT. No GPU inference,
  dataset, checkpoint, prediction or original formal CSV was modified.
- Serialized Full-SSIM: C3/LHL minus fixed-mean is `+0.00749`
  `[+0.00674,+0.00826]`; minus HLL is `+0.02151`
  `[+0.01984,+0.02319]`; minus LLH is `-0.00170`
  `[-0.00205,-0.00134]`.
- Decision: G2 is `PASS_WITH_LIMITATIONS`. The result supports a reproducible
  adapter-scoped temporal stage-utility/mechanism effect, but LLH is a direct
  counterexample to a unique LHL winner. The old `+0.96 dB` and universal
  superiority claims remain forbidden.
- Paper release: after reviewing G1–G4, E selects the mechanism-study
  narrative and authorizes Codex C for scoped manuscript/response edits under
  `coordination/C_PAPER_EDIT_AUTHORIZATION.md`. E must audit C's diff and
  compiled tables before submission; no further GPU work is queued.

## 2026-09-29 — D17: accept the layer-LHL handoff with a bounded claim

- Basis: the independent handoff verifier passed 8,910 checks over the strict
  276-object evaluation, including exact object/schedule coverage, finite
  metrics, checkpoint and target-view provenance, 276 prediction PNGs,
  same-GPU repeatability, cross-GPU agreement and a ground-truth hash spot
  check.
- Decision: accept layer-LHL as a reproducible, strong balanced inference
  schedule for the frozen clean-v2 protocol. Do not restore the C3/LHL
  universal-optimum claim: LLH still has the lowest mean Full-LPIPS, while
  layer-LHL wins the reported PSNR/SSIM and foreground trade-off.
- Handoff: `coordination/LAYER_LHL_HANDOFF_20260929.md` and the temporary
  evidence/audit directory recorded there. No manuscript or source-code edit
  is implied by this handoff; any paper revision requires author review.

## 2026-09-30 — D18: reopen layer-wise selection for complete binary ablation

- Correction: the prior layer-LHL handoff verified only one candidate schedule.
  The existing global HLL/LLH experiments cannot stand in for layer-wise HLL/
  LLH, and layer-wise LLL/HHH/LHH/HLH/HHL were not all present.
- Decision: do not use layer-LHL as a selected or “stronger replacement” method
  claim yet. Enumerate all eight layer-wise temporal patterns
  `LLL/LLH/LHL/LHH/HLL/HLH/HHL/HHH` with the fixed low/high values, shared
  inputs, three seeds and the 24-object probe. The strict holdout remains
  locked for confirmation and cannot be used to choose the schedule.
- The candidate's existing strict-276 result remains preserved as a valid
  single-condition transfer record. No manuscript/source edit is authorized
  until the complete ablation and its audit are finished.

