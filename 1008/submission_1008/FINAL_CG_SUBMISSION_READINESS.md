# C&G 1008 Final Submission Readiness

**Captured:** `2026-10-09T15:12:24Z` UTC  
**Package state:** `AUTHOR_REVIEW_READY / DRAFT`  
**Journal submission:** not made  
**Submission approval:** `NO`  
**Starting main baseline:** `7e07a2811385fe411ce45d8a45fe1fdb0a2a98db`.  
**Package-content delivery commit:** `41ba80ff18e2953e1e2e06e35e500a47f0dc80a7`, pushed by normal fast-forward and verified equal to `mvpainter/main` at `2026-10-09T15:17:51Z`. This readiness snapshot is followed by a package/status refresh commit; its resulting `main` tip is reported in the completion handoff.

## Final scientific narrative

The revised paper presents Timestep-Conditioned Adapter Scaling (TCAS) as a task-specific, training-free intervention on the existing GeoTex-Adapter residual path. C3 `(1.25, 2.50, 1.25)` is one evaluated profile, not a universal optimum. In the matched 300-object Fresh C cohort, C3−GFL FG-PSNR is `+0.522352 dB` (95% object-bootstrap CI `[+0.404160,+0.640669]`). GFH and Generic Linear have more favorable cohort means than C3 on all four displayed endpoints. Applied deep/middle scale sums differ (`82.5` versus `62.5`), so the contrast is not timing-only. The separate post-inspection strict-276 placement study favors L–L–H across six formal endpoints but does not match residual doses or provide an independent replication.

Texture-complexity associations are retrospective sensitivity evidence (9/10 plus-one-corrected Holm rejections; FG-LPIPS versus coverage adjusted `p=0.0508`) and are not causal, fidelity, or selector evidence. Fresh B/A3b and M3 remain retrospective where protocol availability is not authenticated. C1 failed the locked visual gate; B2 failed its numeric gate; the 26-object color diagnosis validates no repair. No valid Fresh C bake, seam, PBR, native-default adapter comparison, or new human-preference result is claimed. The recent participant study remains internal-only because consent/ethics and stimulus-identity records are absent.

## Second-round reviewer status

| Point | Status | Boundary |
|---|---|---|
| R1.1 color, artifacts, 3D fidelity | `PARTIAL` | Failure-enriched color diagnosis; no validated repair, native-default result, bake, seam, or PBR evidence. |
| R1.2 matched evaluation | `ADDRESSED WITH LIMITS` | Fresh C supports the named paired image-space contrast; does not reproduce historical `+0.96 dB`. |
| R1.3 texture metrics | `ADDRESSED WITH LIMITS` | Variation is not fidelity; retrospective S12 is not a causal or selector result. |
| R1.4 paired uncertainty | `PARTIAL` | Paired intervals shown; no prespecified equivalence/non-inferiority margin. |
| R1.5 FAC reproducibility | `PARTIAL; FIRST-ROUND RESULT RETAINED` | Configuration-list and run-manifest gaps disclosed. |
| R2.1 methodological contribution | `PARTIAL; EDITORIAL NOVELTY RISK` | Positive task-specific empirical contribution; no general scheduling novelty or optimality claim. |
| R2.2 CAI | `ADDRESSED BY WITHDRAWING CAI CLAIM` | Selector/proof/optimality claim removed. |
| R2.3 cross-backbone | `NOT FULLY ANSWERED` | Existing probes are interface-specific; matched transfer is not established. |
| R3 | `ACKNOWLEDGED` | Positive assessment; no technical request invented. |

Exact verbatim authentication of the second-round review source remains incomplete: the retained PDF is labeled “initial-submission reviews.” The response follows the recorded second-round issue/evidence matrix and remains subject to author comparison with the editor's original comments.

## Delivered files and validation

- Active manuscript: [`1008/manuscript/revision_01549_restored/manuscript_1008.tex`](../manuscript/revision_01549_restored/manuscript_1008.tex), SHA-256 `1a6e7e5365634445ad73e02c146fd1c62b28c5372cfede028ca85028dbdb8409`.
- Active Supplement: [`1008/manuscript/revision_01549_restored/Supplementary_1008.tex`](../manuscript/revision_01549_restored/Supplementary_1008.tex), SHA-256 `eb524d957fb2be30ea2ef5615ba1a031f104a5d5cc002f0df54ead4d5ac7d2c1`.
- Main, marked-up, and Supplement PDFs are each 13 pages. Response PDF is 6 pages.
- Clean source archive: 44 entries, CRC verified, generated/checkpoint/GLB extensions excluded. Fresh extraction rebuilt all three LaTeX outputs; normalized extracted PDF text matches delivered PDFs.
- The built-in Codex compiler was invoked on the saved active TeX but did not return diagnostics after repeated waits. This is not counted as an editor-native compilation pass. Repository build scripts succeeded from the working tree and clean ZIP extraction.
- Updated response locations are checked against the final 13-page Supplement and 13-page main PDF. Main figure pages 11–12; S12 p. 12–13; S13 p. 13.

## Git and branch handling

The task began at the stated baseline. Package content commit `41ba80ff18e2953e1e2e06e35e500a47f0dc80a7` was pushed normally to `mvpainter/main`; local and remote SHAs matched at the recorded verification time. A package/status refresh follows in `main`, updating this readiness file, package manifest, and checksums; its exact final tip is reported in the completion handoff. No force-push, history rewrite, raw-data copy, or journal upload is part of this delivery.

The existing cross-backbone branch is `codex/next-review-response-20260930`. The color audit branch is `codex/r1-color-cast-repair-v2-20261009` in its existing separate worktree/origin history; no new color-repair experiment was started or pushed. `gh-pages` retains its publishing purpose. No branches or data-bearing worktrees were deleted in this paper handoff.

## Author checks before any upload

1. Verify author names/contact information, title page, acknowledgements/funding, and declaration of interests carried forward from 0907.
2. Approve the cover letter, highlights, graphical abstract, and title page; they remain `DRAFT`.
3. Confirm the current manuscript ID/editor instructions and whether the 0907 conference attachment or demo media is required.
4. Review the unresolved R1.1, R2.1, and R2.3 risks and authenticate the second-round comments.

## Final gates

`SCIENTIFIC_EVIDENCE_FREEZE = YES`  
`REVIEWER_RESPONSE_READY = PARTIAL`  
`MANUSCRIPT_BUILD_PASSED = YES`  
`SUBMISSION_PACKAGE_COMPLETE = YES`  
`SUBMISSION_APPROVED = NO`

`MANUSCRIPT_BUILD_PASSED=YES` refers to the repository's two-pass project scripts and clean-archive builds. The editor-native compiler request remained unresolved and is not represented as a pass. `SUBMISSION_PACKAGE_COMPLETE=YES` means the requested local draft files and checksums are assembled for author review; it does not mean author approval or journal submission.
