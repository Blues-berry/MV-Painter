# Coordinator instructions — keep private

The frozen pairs are LLH vs GFL, GFH, GC3, and endpoint-matched GEN_LINEAR.
Participants do not receive this file or method names. Each participant sees
six objects per pair, and every object/pair combination is assigned to ten of
the 40 slots.

The four-pair participant package is hashed in `HUMAN_STUDY_SITE_FREEZE.md`.
Before inviting anyone, verify the handoff hash there. Give participants only
`participant_handoff.zip` and one assigned participant ID. Never distribute
`coordinator_private/`, this file, or the entire repository.

Use only the 40 frozen participant IDs. Put one downloaded response CSV per
participant in `coordinator_private/responses/`. Do not invite replacements
or inspect preferences while collection is active. Close collection only
after all 40 assigned slots are complete or withdrawn, then run:

```sh
python3 analyze_human_study.py
```

Incomplete assignments and failed comprehension checks are excluded as a
whole. At least 36 valid complete participants are required for the
prespecified human-evidence gate. If fewer than 36 remain after all slots are
resolved, report the achieved count and leave the gate open. Do not stop early
based on significance or effect direction. The analysis reports all four
pairs and both questions separately, including ties and results favoring a
comparator. It uses a two-way participant/object cluster bootstrap and Holm
correction across eight endpoints. Do not create or substitute synthetic
responses.
