# Reviewer-source provenance audit — 2026-10-07

## Determination

**ROUND_IDENTITY_UNCERTAIN**

The reviewer text used for this closure is internally consistent as one supplied R1–R3 comment set, but the available records do not prove which formal journal decision round it belongs to or link its manuscript number conclusively to the frozen 01549 source. Continue responding to this supplied set. Do not mention this internal uncertainty in the external response.

## Sources checked

| Source | Observed identity | Finding |
|---|---|---|
| final/round2/coordination/reviewer_materials/CAG-D-26-00962-reviews.pdf | Three-page PDF titled “CAG-D-26-00962 reviews”; SHA-256 fac855473563faf5dc35cc5d24fd084a56a8961e9c390ec12462fe351a7781eb; PDF creation/modification time 2026-09-28 12:43:43 UTC | Contains the R1/R2/R3 comments dated 14, 24, and 28 September 2026. Each section labels its date “Initial submission.” |
| Three attached copies of CAG-D-26-00962-reviews.pdf | Attachments under IDs 4ef9c631-9d49-49b8-a652-30c069f7bb6d, 5b05ebe6-962a-4a69-ad5e-2654ff84be28, and 81bc2495-9f7b-4356-91f9-378b3b8a98c7 | All have the same SHA-256 as the archived PDF, so they are duplicate copies of the same export, not additional reviewer sets. |
| final/round2/coordination/reviewer_materials/CAG-D-26-00962-reviews.txt | Plain-text companion to the PDF; SHA-256 1d2efb8f9250f8162304be57ce1d71c6d654d35511a186ad6e3c9b869ace5af5 | Contains the same dated R1/R2/R3 set. Its text serialization is not byte-identical to the independently normalized supplied copy. |
| 1006/review/second_round_reviewer_comments.txt and root 第二轮审稿意见.txt | Both SHA-256 52d5a02718cbcf1b452293fe5a6953231f10fc9ce4cdf6cce400e86deb521245 | Byte-identical copies of the file named as the second-round comments; content corresponds to the archived CAG-D review export. |
| 1006/revision_evidence_archive_20261007/source/reviewer/reviewer_comments_supplied.txt | SHA-256 461b4f9d523e607612e833e2f3e96945c5f00b3dcd1e9924d8cc94250ba7b3e6 | Preserved reviewer-text snapshot with the same R1/R2/R3 concerns. Its normalization differs from the separately stored second-round text; it is not treated as byte-identical evidence. |
| Root 第一轮审稿意见.txt | SHA-256 5cb391d17d59b4cf8b8f70b78ffa528a38c9cfc48b5c789c40f48f54aaaede3f | A distinct, earlier reviewer set with materially different comments. It is not the R1–R3 set addressed by this closure. |
| /tmp/mvpainter-cg-evidence-closure/审稿意见.txt | Conference forwarding/acceptance notice for CAD/Graphics 2026 Paper 75 | Confirms the conference-to-journal revision context and deadline, but is not a Computers & Graphics decision notice identifying CAG-D-26-00962 or its formal round. |
| Attached CAG-S-26-01549 (1)(1).pdf | 48-page manuscript PDF created 2026-09-08; its “Manuscript Number” field is blank | Supports the internal 01549 label and article-title match, but does not itself establish a formal ID crosswalk to CAG-D-26-00962. |

## Round and manuscript identity

The round2 archive paths and the filenames 第二轮审稿意见.txt / second_round_reviewer_comments.txt identify the supplied set as the later working set in the project archive. The official-looking CAG-D PDF, however, labels every reviewer entry “Initial submission.” The date range and a project directory name cannot resolve that conflict on their own.

The CAG-D review export names manuscript CAG-D-26-00962; the frozen manuscript package is referred to internally as 01549, and the checked CAG-S PDF leaves the manuscript-number field empty. The available conference forwarding notice does not bridge these identifiers. No separate Computers & Graphics decision email or later dated reviewer set linking the two identities was found among the audited review archive and attached materials.

## Scope decision

- Use the archived CAG-D-26-00962 R1–R3 comments as the supplied reviewer set for the current response and evidence matrix.
- Keep the separate earlier reviewer set out of this point-by-point response.
- Do not describe the formal review round as verified.
- Do not add this provenance caveat to the external reviewer letter.
