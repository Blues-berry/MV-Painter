# V4 final quality check

Sole source: PR #1, branch codex/cg-final-v4-20261014, c3017645. Current continuation: main 13 pages, complete references ending p13; Supplement 71; response 5; marked manuscript 21.

| Content | Current location |
|---|---:|
| Figure 1 | main p4 |
| Figure 2, three rows / five full columns | main p7 |
| Table 4 and Table 5 | main p8 |
| Figure 3, selected B | main p9 |
| Figure 4 and Table 6 | main p10 |
| Original specified timing primary in Table 7 | main p11 |
| Final reference [41] | main p13 |
| Table S35 / S36 | Supplement p58 / p59 |

Figure 3 A/B and Figure 2 four/three are compared using actual rendered manuscript pages in quality_review. B is selected for explanatory reference mismatch and endpoint tradeoff, without a claim of visibly large schedule gains. Both B objects have verified common geometry/UVs and camera004 across GT/Mean/Late. All method/image hashes, real512 resolution, attribution and selection are recorded. The metadata mismatch saying1024 is preserved.

All main/Supplement table blocks and original data validation remain unchanged. No model/GPU run or inferential recomputation occurred. The GeoTex timing primary is −0.0338775 dB, 95% interval [−0.117170,+0.051422], p=0.432378. Ten-object and GSO bake cohorts retain every object and their separate original tests.

The two MP4s are physically copied into the new journal_upload_v4 directory; full decoding passes, original hashes match, discrete decoded frames match archived pre-encoding frames to normal H264 compression accuracy, and source/camera/condition identities are recorded. GSO's source column is explicitly distinguished from a GT self-bake.

The independent contribution review supports a bounded empirical paper, with moderate-to-weak contribution strength and material novelty/deployment/generalization risks. Those boundaries are scientific scope limits, not closed by successful compilation. AUTHOR_REVIEW_READY and SUBMISSION_READY are judged separately in quality_review/FINAL_READINESS_V4.json.
