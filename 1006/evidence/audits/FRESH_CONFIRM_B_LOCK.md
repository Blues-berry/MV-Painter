# FRESH_CONFIRM_B lock

Frozen before any method output: 2026-10-05T07:35:37.465457+00:00

The cohort is the complete remainder of the 450 technically valid identities
after removing all 300 IDs in `fresh_confirm_300.txt`, sorted by source UID.
No candidate has a prior method-result row in the V3 object-condition ledgers
or per-object metric files. Every object has its frozen source GLB and complete
render directory hashed in `FRESH_CONFIRM_B_MANIFEST.json`.

Identity audit: 150 candidates; zero prior-output overlap; zero source-GLB byte
duplicates; zero 17-view decoded-pixel duplicate groups within the candidate
or crossing from the previous 300. The known pixel-identical pair
0099ab6d44b742b0b62a40a7c70c29b1 / 0130e5149b6f4156b9799daa5e4006da is wholly
inside the already-used 300 and is preserved in the audit. No outcome-driven
selection or object replacement was performed.

Manifest SHA256: `c987cbc3a3205cd6ed083b2c53b02160dab41366fb41a8a6e2c2989278601050`
Frozen UID-list SHA256: `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`
Identity-audit SHA256: `a39f0438b1223972bbb4edc650f20193b5db7d102cd6f04b2301f9af3892c683`
