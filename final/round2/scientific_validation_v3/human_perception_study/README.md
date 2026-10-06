# Human-study source package

The only participant handoff is
`../human_study_site/participant_handoff.zip`, governed by
`../HUMAN_STUDY_FINAL_PAIR_LOCK.md` and the matching
`../human_study_site/HUMAN_STUDY_SITE_FREEZE.md`. Do not distribute
`participant_package_blinded.zip` from this source directory.

This directory retains the source images and coordinator-side provenance for
the frozen 24-object study. Its comparisons include LLH vs GFL, GFH, GC3, and
registered endpoint-matched `gen_linear`; the active site builds 40 fixed
assignments of 24 tasks each and keeps the two questions separate.

## Rebuild source stimuli

From the repository root, run:

```sh
python3 final/round2/scientific_validation_v3/human_perception_study/coordinator/prepare_blinded_study.py --refreeze-precollection --confirm-not-distributed
```

An unlaunched package can be replaced only with both explicit
`--refreeze-precollection` and `--confirm-not-distributed` flags. The script
refuses to refreeze after any response CSV exists. It preserves the prior
unlaunched archive and keys under `coordinator/`.

Keep `coordinator/` private. It contains the method and task keys and is not
part of the participant handoff.

## Participant and coordinator workflow

Use the active instructions in `../human_study_site/README_START_STUDY.md`.
The fixed sample is 40 assigned slots; at least 36 valid complete
participants are required. Each participant completes 24 comparisons (six
per pair), with two questions per comparison. Collection stops only after
all 40 slots are complete or withdrawn; no replacements or significance-
based stopping are allowed.

After collection, put participant CSVs in
`../human_study_site/coordinator_private/responses/` and run:

```sh
python3 final/round2/scientific_validation_v3/human_study_site/analyze_human_study.py
```

The active analyzer verifies frozen image/task keys, excludes incomplete
assignments and failed comprehension checks as whole participants, and
reports all eight pair-by-question endpoints. It uses 10,000 two-way
participant/object bootstrap resamples, seed 20261005, ties as 0.5, a
plus-one two-sided bootstrap test against 0.5, and Holm correction across
eight endpoints. Do not create or substitute synthetic responses.
