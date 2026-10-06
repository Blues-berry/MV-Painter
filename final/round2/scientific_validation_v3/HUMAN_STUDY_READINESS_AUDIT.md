# Human preference study readiness audit — 2026-10-05

**Status:** `PRECOLLECTION_PACKAGE_FROZEN`; `HUMAN_EVIDENCE_GATE=OPEN`.
The package is built and checked but has not been distributed. No response
CSV exists and no participant has been contacted.

## Final pair and design

The final pre-human-outcome lock is `HUMAN_STUDY_FINAL_PAIR_LOCK.md`.
It includes LLH vs GFL, GFH, GC3, and the registered endpoint-matched
`gen_linear` comparator. B had already been exposed before this lock was
written, so this is not a valid pre-unblind B freeze. It does freeze the
human comparisons before any preference response.

- 40 fixed participant slots; at least 36 valid complete participants are
  required. No replacement slots or significance-based stopping.
- Each person rates all 24 frozen GT-only objects once: six objects per pair.
  Every object/pair cell is assigned to exactly ten slots.
- Q1 appearance fidelity and Q2 texture/shape naturalness stay separate.
- One non-identifying end-of-study comprehension check is recorded. A failed
  check, incomplete assignment, or invalid choice excludes the entire person.
  There is no duration-based exclusion.
- Analysis: equal-object preference probability, two-way participant/object
  cluster bootstrap, 10,000 draws, seed 20261005, ties=0.5, two-sided test
  against 0.5 with plus-one correction, Holm over eight pair-by-question
  endpoints. No combined Q1/Q2 score.

## Stimulus identity and blinding

The generic linear images are the 24 exact frozen `visualization_24` UIDs
from registered Experiment C. The Experiment C manifest shares the frozen
300-object list hash, checkpoint, target views, resolution, sampler, and
50-step setup with the original LLH/native images. No object was selected by
schedule outcome. All 144 participant images are hash-checked by the private
analyzer.

The participant ZIP contains 148 files: page, public assignments, participant
instructions, response template, and 144 anonymous images. The coordinator
pair guide, method key, analysis code, and coordinator directory are absent.
The public package text contains none of the method labels `LLH`, `GFL`,
`GFH`, `GC3`, or `GEN_LINEAR`.

## Package checksums

Final pair lock SHA256:
`8aa4ebc88cccda50705709d67f1ff0070236f4d3948242071785ce29ad9fb6ce`

| Item | SHA256 |
|---|---|
| Participant handoff ZIP | `cfb5c242559934b2c9a720c135d972142959435af93445444f0cfc584313e8f4` |
| Participant page | `e7295f1ec28824866316723e313a9290808c87e71313a5bbc8a1c970a5dd2102` |
| Public assignments | `71dba2840fd722cd42e657b433d8b89d427f828012e3fd3f8695bf6c098436b0` |
| Participant instructions | `ca489c083d675088e1e97f91d558dee4594b56d0f0acdd2431955a8e771b0ee5` |
| Response template | `85e1c1276ba1c5e3c8727ee3121a167f4080e9e0cd68949cb7ee6740a90f29d0` |
| Assignment generator | `ff57f36741b5a0b4b4b7e4b3f8b3228273c0fc6dc923bfc8aec105030ce26eef` |
| Analysis script | `af297b03c7caa3d530ad25a5eb3ab245798b422d157d84ee6874b6114afc3c58` |
| Private assignment key | `a93456259bf38b44bdddec3bc6d4bc251b28c62800032c2860ea091045e5ca03` |

The matching complete hash map is
`human_study_site/coordinator_private/site_package_manifest.json`;
the authoritative participant-facing checksum is in
`human_study_site/HUMAN_STUDY_SITE_FREEZE.md`.

## Build and local-site checks

- Assignment/key validation passed: 40 slots, 96 source tasks, 144 images,
  24 unique objects per person, six assignments per pair, and exactly ten
  exposures per object/pair.
- ZIP integrity passed (148 entries); no private key, coordinator file,
  method label, or analysis script is present.
- Inline page code and public assignment JavaScript passed Node syntax checks.
- Local HTTP smoke check returned 200 for the page, assignment file, response
  template, and an anonymous stimulus image. The test server was stopped.
- No response CSV exists. The 40-slot package remains unlaunched.
