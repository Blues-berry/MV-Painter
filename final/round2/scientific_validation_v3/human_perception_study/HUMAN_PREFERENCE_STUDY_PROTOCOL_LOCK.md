# Blinded human preference study protocol lock

Frozen before any human response is collected: 2026-10-05.

## Question and scope

Does LLH look closer to the reference, or preserve more natural surface
texture/detail while retaining plausible shape, than native GFL, native GFH,
and native GC3 in the frozen 24-object visual cohort? This study measures
human preferences for these fixed generated views. It does not test unseen
cameras, UV seams, or final 3D bake quality.

## Objects, stimuli, and pairings

- Use all 24 IDs in `scientific_validation_v3/visualization_24.txt`, frozen
  from GT-only texture/coverage/geometry strata before model outcomes.
- For each object, present the six GT views next to one method pair:
  `layer_llh` vs `native_gfl`, `layer_llh` vs `native_gfh`, and `layer_llh`
  vs `native_gc3`.
- Predictions are the same-draw formal images already archived for
  Experiment D. Both methods in each pair share object, reference views,
  model, and latent seed. No metric-ranked examples are preferentially
  sampled; every frozen object and all three comparisons are included.
- Method names are hidden from participants and displayed as A/B. The
  reference is labeled separately. The survey randomizes A/B assignment and
  trial order independently for each participant.

## Participants and presentation

- Target: 30 complete adult volunteer participants. Do not inspect interim
  preferences or stop early. If fewer than 30 complete responses are
  obtained, report the achieved number and treat the study as under-target.
- No names, emails, demographics, or other identifying fields are collected.
  The coordinator supplies each participant a unique pseudonymous study
  code.
- Each participant completes 72 trials (24 objects × 3 comparisons), with
  two separate forced-choice questions per trial and a “no clear difference”
  option for each question. Object/trial order and left/right method display
  are randomized. Images use the same display size and layout.
- Participation is voluntary; the first screen describes the task and asks
  participants to confirm they are at least 18 and agree to participate.
  The local survey stores responses in the participant's browser for CSV
  download; it does not transmit data to a server.

## Questions

1. Reference appearance: “Which generated result more closely matches the
   reference's overall appearance, including color and material?”
2. Texture/detail with shape plausibility: “Which result better preserves
   natural surface texture and fine detail while keeping the object shape
   plausible?”

Responses are A, B, or no clear difference. The questions are stored and
analyzed separately.

## Frozen outcome and analysis

- Outcomes are preference shares for LLH on each question and each of the
  three comparisons. Encode LLH choice as 1, comparator choice as 0, and tie
  as 0.5; also report tie rate and raw A/B/tie counts.
- Require one complete response for each of 72 object-comparison trials.
  Exclude an incomplete participant as a whole; no object/trial is excluded
  based on the selected image or response.
- For each of six comparison × question endpoints, report the mean LLH
  preference share and 95% two-way participant/object bootstrap CI (10,000
  resamples, seed 20261005). Test against 0.5 using the frozen two-way
  bootstrap tail rule and plus-one Monte Carlo correction. Holm-correct the
  six endpoints together. Also report subgroup preference shares by the
  frozen GT texture strata descriptively, without separate significance
  claims.
- Report every comparison, including ties and results favoring the baseline.
  Do not pool the two questions into one score or hide null/contradictory
  outcomes.

## Data handling and interpretation

The survey asks for no personal information and runs locally. The coordinator
must collect downloaded CSVs under the pseudonymous participant codes and
place them in `responses/` before the locked analysis. Human responses are the
only missing input; no synthetic or model-generated “human” choices may be
used. The study is a preference check on fixed 2D views and cannot validate
population-wide material fidelity or 3D-bake quality.
