# B pre-unblind manifest — retrospective integrity snapshot

**Status: `RETROSPECTIVE_ONLY — NOT A VALID PRE-UNBLIND FREEZE`.**
Created: 2026-10-05T20:11:21+00:00

This file has the requested name because the addendum requires a manifest,
but it was created after the earlier audit had already disclosed B results.
It cannot restore blindness or be represented as a prospective lock. The
prior `FINAL_NARRATIVE_DECISION.md` contains B effect estimates, so outcome
exposure predates this snapshot. The additional pre-unblind documents named
in the new addendum were absent when that exposure occurred. See
`B_UNBLIND_STATUS_RECONCILIATION.md`.

## Outcome-blind campaign state

- No B worker process is active; the run is complete and was not restarted.
- Frozen design: 150 objects × 30 conditions = 4,500 unique object-condition
  rows; shard 0 = 2,250 and shard 1 = 2,250.
- Existing `B_FORMAL_INTEGRITY_GATE.md` records a PASS before condition-level
  statistical analysis: all 13,888 frozen input files verified, 4,500/4,500
  prediction PNGs and residual logs, no duplicate/missing/non-finite rows,
  runner/config/checkpoint/data-root matched, and ledger-to-CSV agreement.
- A fresh key-only scan found 4,500 unique object-condition keys, 150 objects,
  30 conditions, six consistent input fingerprints per object, 4,500 PNGs,
  and 4,500 residual JSON files. It did not compute or print condition means.
- The generic extension is a separate post-lock 1,200-row campaign; it is not
  silently merged into the 30-condition confirmatory registry.

`B_PREUNBLIND_SHA256SUMS.txt` is a retrospective hash inventory. It detects
subsequent changes but does not establish that the files were frozen before
unblinding.

## Retrospective checksum completion

- Inventory: 11,532 files across the complete main B campaign directory, the
  separate generic-extension directory, and all frozen `fresh_confirm_b`
  identity files.
- Verification: `sha256sum -c B_PREUNBLIND_SHA256SUMS.txt` passed for all
  11,532 entries.
- Inventory SHA256: `096062baa91d226900baeb61422cf23a6e61ca9afd2caaf74956abad1613fb83`.
- Scope includes all 4,500 main-campaign prediction PNGs and the recorded
  residual logs. Source-input identity was separately covered by the existing
  formal integrity gate; this inventory records the frozen identity manifests
  rather than copying or rehashing the external source dataset.

This checksum pass is integrity evidence only. Because the inventory was made
after the earlier B result disclosure, it does not satisfy the original
pre-unblind timing requirement.
