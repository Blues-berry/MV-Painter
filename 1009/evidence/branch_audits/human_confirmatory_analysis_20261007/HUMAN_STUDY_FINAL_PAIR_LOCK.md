# Human study final pair lock — 2026-10-05

**State: pre-collection lock; B had already been exposed before this file was
written.** This is the final human-study pair and analysis specification for
the unlaunched local package. It does not restore B blinding. After the first
human response is recorded, pairs, assignments, stimuli, exclusions, stopping
rule, and analysis are immutable.

## Pair selection

Each pair compares LLH with one fixed method on the same object and reference:

1. LLH vs GFL
2. LLH vs GFH
3. LLH vs GC3
4. LLH vs endpoint-matched `gen_linear`

`gen_linear` is included because registered Experiment C found essentially no
FG-PSNR difference from LLH (Δ=+0.0049 dB, 95% CI [−0.0350,+0.0469],
Holm p=0.8148), while the same schedule was the closest FG-PSNR competitor in
the post-lock B generic sensitivity (LLH−linear Δ=−0.0373 dB,
95% CI [−0.0829,+0.0086]). The B extension is not a registered B-core test and
is not treated as independent confirmation. It also shows small FG-LPIPS
effects favoring linear in both C and the B sensitivity. This pair is a
fairness comparator, not a claim that linear is superior.

The human stimulus objects remain the unchanged, GT-only frozen
`visualization_24` cohort. The 24 `gen_linear` images come from registered
Experiment C for those exact UIDs. C and the existing LLH/native images share
the object-list hash, checkpoint, target-view list, resolution, sampler, and
50-step schedule. No object was selected by a schedule result. The images
remain fixed 2D evidence and do not test unseen views or baked 3D quality.

## Assignments and stopping

- Forty pseudonymous assignment slots; minimum evidence gate: 36 complete,
  valid participants.
- Each participant sees all 24 objects exactly once and completes 24 image
  comparisons: six tasks from each of the four pairs.
- Every frozen object/pair combination is assigned to exactly 10 slots. Four
  deterministic six-object blocks have texture-stratum counts 3/2/1, 2/3/1,
  2/2/2, and 2/2/2; rotating the blocks across pair labels balances exposure
  without dropping or repeating an object. Trial order, A/B side, and question
  order are randomized from the frozen assignment seed `20261005`.
- Fixed stop: close only after all 40 slots are complete or withdrawn. No
  replacement slots, outcome-based stopping, or interim preference analysis.
- Do not recruit or distribute the package until the rebuilt package hashes
  and assignment checks are recorded in `HUMAN_STUDY_SITE_FREEZE.md`.

## Questions and check

Q1 (appearance fidelity): “Which result better matches the reference object's
visible appearance, including color and material?”

Q2 (texture and shape): “Which result has more natural texture and detail
while remaining geometrically plausible?”

The two questions are randomized and analyzed separately. A choice is A, B,
or no clear difference; ties score 0.5. No composite score is planned.

After all 24 comparisons, one non-identifying comprehension check asks which
two judgments the study requested. The correct answer is that appearance
fidelity and texture/shape naturalness are separate judgments. An incorrect
answer excludes the participant as a whole. No name, contact information, or
free-text response is collected. There is no speed exclusion; completion time
is not used to remove responses.

## Exclusions and analysis

Apply these rules without viewing preference results:

- Exclude the whole participant for an incomplete or invalid 24-row
  assignment, a missing/invalid choice, or a failed comprehension check.
- Duplicate participant IDs or assignment slots are a hard analysis error to
  resolve from source files; do not choose which duplicate to retain.
- A participant who withdraws or has no response file occupies a frozen slot
  but is not replaced. Fewer than 36 valid completions leaves the human gate
  open.
- Do not exclude by preference direction, object, texture stratum, or method.

For each of the four pairs × two questions, report equal-object preference
probability, 95% two-way participant/object cluster-bootstrap CI, raw A/B/tie
counts, and the unadjusted and Holm-adjusted two-sided bootstrap p-values
against 0.5. Use 10,000 resamples and seed `20261005`; ties count as 0.5; Holm
family size is eight endpoints. Report all eight endpoints and do not merge
Q1 and Q2.

## Pre-collection state

No human response file exists. The earlier three-pair package was not
distributed and is superseded; its files are retained under the coordinator's
pre-collection archive. The rebuilt four-pair archive is offline, contains no
coordinator key or analysis code, and has no upload endpoint. This lock is
pre-human-outcome, but necessarily post-B-outcome.
