# Human preference protocol amendment — balanced incomplete assignments

**Superseded for the active study.** The later
`HUMAN_STUDY_FINAL_PAIR_LOCK.md` replaces this three-pair design with four
pairs, adds the endpoint-matched `gen_linear` competitor, and specifies eight
endpoints. This file remains as the archived earlier amendment; no response
data from its design are reused.

Frozen before any human response is collected: 2026-10-05. This amendment
extends the earlier `HUMAN_PREFERENCE_STUDY_PROTOCOL_LOCK.md` and supersedes
only its participant workload and assignment scheme. The 24-object cohort,
three LLH comparisons, two separate questions, blinded A/B display, response
coding, two-way participant/object bootstrap, seed, and six-endpoint Holm
family remain unchanged. No earlier preference result is reused.

## Frozen sample and assignment design

- Use all 24 objects from the existing GT-only, pre-outcome-frozen
  `visualization_24` cohort. Its texture-tercile counts are 9 / 9 / 6.
- Target 40 complete adult volunteer participants; 36 complete participants
  is the minimum target range. Report the achieved number. Exclude an
  incomplete participant as a whole.
- Fixed stopping rule: use only the 40 pseudonymous assignment slots frozen
  in the site package. Collection closes after every slot is either complete
  or withdrawn; do not add replacement slots or stop based on interim
  preferences, significance, or effect direction. The analyzed complete
  sample will therefore be 0–40; at least 36 complete participants are
  required for the prespecified human-evidence gate. If fewer than 36 are
  complete when all 40 slots are resolved, report the study as below target
  and leave that gate open.
- Each participant completes 24 object-comparison items: 8 LLH-vs-GFL, 8
  LLH-vs-GFH, and 8 LLH-vs-GC3. Each of the 24 objects appears exactly once
  for that participant, so no object is repeated within a participant.
- Each participant receives exactly 3 / 3 / 2 objects from texture terciles
  0 / 1 / 2 within each comparison. Across the 40 frozen slots, each
  object/comparison pair is assigned to 13 or 14 participants. This balances
  object exposure and texture strata without selecting objects by method
  outcomes.
- Slot construction partitions each GT texture stratum into three fixed
  groups. Participant slot and comparison index rotate the group assignment;
  trial order, A/B side, and question order use the frozen assignment seed
  20261005 and SHA256-derived per-slot seeds. No Python `hash()` is used.
- The coordinator distributes the 40 pseudonymous participant IDs to
  volunteers without collecting names, email, phone, or account details.
  Method names and the private image/task key are withheld from participants.

## Questions and outcomes

1. Appearance: which generated result better matches the reference object's
   visible appearance, including color and material?
2. Texture/shape: which result has more natural texture and detail while
   remaining geometrically plausible?

Questions are presented one at a time in randomized order for each item.
Responses are A, B, or no clear difference. For analysis, LLH choice is 1,
comparator choice is 0, and a tie is 0.5. Report preference probability,
95% two-way participant/object bootstrap CI, raw A/B/tie counts, participant
and object counts, and all six comparison × question endpoints. Use 10,000
resamples, seed 20261005, the frozen two-sided bootstrap tail rule with
plus-one correction against 0.5, and Holm correction across six endpoints.
Texture-stratum preference estimates are descriptive only.

## Offline site and data handling

`human_study_site/` is the frozen participant site. It runs locally with
`python3 -m http.server 8000 --bind 127.0.0.1`; it has no response-upload
endpoint and sends no response data. The participant handoff archive excludes
the coordinator's `coordinator_private/` directory. Participants download
their CSV locally and return it to the coordinator using only their assigned
ID. The site source, assignments, private key, and participant handoff SHA256
are recorded in `human_study_site/HUMAN_STUDY_SITE_FREEZE.md` before
collection.

This is a preference study on fixed 2D views from the frozen 24-object cohort.
It does not test unseen cameras, UV seams, final baked 3D quality, or
population-wide material fidelity.
