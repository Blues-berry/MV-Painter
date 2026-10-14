# Actual PDF table audit

Inspected the complete 14-page final manuscript at page scale. Source baseline was PR #1 `0aa1c9b3`; Table 3 prose and compact-table alternatives were both compiled. `VISUAL_AND_TABLE_BEFORE_AFTER.pdf` contains the actual pages for Tables 3, 5 and 7 before/after.

| Table | Final page / width | Decision |
|---|---|---|
| 1 | p6, double column | Eight study identities and selection scopes remain. Dense but readable; shortening any more would lose cohort/protocol caveats. Detailed execution stays S1. |
| 2 | p6, double column | Strong Fixed High and Generic Linear controls remain visible with four endpoints; no clipping or hidden comparator. |
| 3 | p7, single column | Four distinct fields now align contrast, ΔCIEDE2000, 95% CI and 24/26 direction count. Retained over prose variant because both positive and negative contrasts are easier to compare and table numbering stays stable. The 26-object failure-enriched limitation remains adjacent. |
| 4 | p8, single column | GT-256 reference and all original controls remain legible; footnote states reference bake is not a theoretical bound. |
| 5 | p9, single column | Two study-specific LPIPS estimates, separate intervals, and p values align. Test types move into note; N=10/N=20 and non-pooling remain explicit. |
| 6 | p10, single column | Native MV-Adapter 50-object means fit four endpoints; actual native interface is named. |
| 7 | p11, double column | First row is original GeoTex Middle−mean(Early,Late) primary. Distinct study, contrast, N, ΔFG-PSNR, interval and p columns are legible; sign-flip draw counts are in note. No forest figure. |

No table has a detected overfull box or an interval crossing into the next numeric column. The Table 3 prose alternative was a real 14-page TeX build, retained only in the comparison PDF; the final source uses the compact table.
