# Independent editorial and actual-PDF visual review

2026-10-13. Read-only reviewer. Scope: the independent candidate's main manuscript, supplement, response and marked manuscript. Author approval remains **PENDING**. No narrative rewriting or figure redesign was performed by this reviewer.

## Evidence and coverage

- Main manuscript: all **15 PDF pages** inspected through `audit/visual/main_contact_1.jpg` and `_2.jpg`; Figure 1 on **PDF p4** inspected separately at 1800-pixel page height (`main4_large.png`). Extracted PDF text read for the abstract/introduction/contributions, intervention and controlled comparisons, downstream evaluation, discussion/limitations, conclusion and references.
- Supplement: all **71 PDF pages** inspected through `audit/visual/supp_contact_1.jpg` through `_6.jpg`; pages **1–3, 6, 12, 70–71** separately rendered at 1400-pixel page height. The front reader map and TOC are actual PDF content, not merely source headings.
- Response: all **5 PDF pages** inspected in `response_contact.jpg`; R2.1 text on **p3** read, including evidence, remaining limits and locations.
- Marked manuscript: all **22 PDF pages** inspected in `marked_contact_1.jpg` and `_2.jpg`; **p1** separately inspected in `marked1_large.png` because the compiler warned about the height of the initial two-column argument.

Contact sheets check gross placement and page coverage; detailed scientific typography was checked on selected enlarged pages. This is not a claim that every small numerical glyph in every supplementary table was manually validated. Compilation success was not used as the visual criterion.

## Blocking issue found and bounded repair

The initially rendered Supplement **p6, Table S2 continuation** detached signed numerical fragments across lines in the combined mean/CI column. A thin plus could be mistaken for minus, and negative CI signs separated from their digits at a wrap were especially misleading. The authoritative source's signs were confirmed by the main agent; the issue was visual presentation rather than a revised estimate. The recommended and authorized single minimal repair separates mean and CI columns and keeps signed numerical cells in explicit math, without changing estimates, interpretation or font size. The final post-repair inspection is recorded below.

No other blocking content, layout or visible unresolved-reference problem was found in the reviewed documents.

## Figure 1 and page layout

Main **p4**: the final Reference conditioning label moved left/down and now sits near its gray path without colliding with the Frozen diffusion U-Net heading. Input texture and six generated-view textures are discernible. The camera labels fit; no picture/frame/arrow truncation is visible. Existing wrapper/native cap and existing numeric caps are explicitly gray; TCAS requested schedule and scalar application are teal. Deep/middle and shallow applied values are separately described. The independent Bake10 panel has its own UID and internal evaluation arrow; no main-sample-to-bake arrow exists. Its enlarged unseen render communicates the textured 3D target while preserving appearance failure. The caption and following method text fit cleanly below the figure.

Main **pp6–12**: controlled-study tables, full-object/ROI figures, bake figures and interface/allocation plot fit within the page. The reference/output differences are plainly visible rather than concealed by framing. Main **pp14–15** references do not show visible unresolved citation placeholders. Marked **p1** is dense because both removed and inserted abstract passages appear, but remains on the page with a clear bottom margin; the height warning is not a visual submission blocker.

## Editorial coherence and R2.1

Main **pp1–3** now starts with a graphics problem: generated views become assets, and the control interface and evaluation endpoint govern what a schedule comparison means. It then identifies TCAS as a request on an existing residual interface, distinguishes applied scale from realized correction, and credits prior scheduling work. The three contributions on **p2** are implementation-aware allocation, measured baked appearance and transfer limits; they do not promise a new learned controller.

Main **pp5–12** follows competitive controls → matched allocation → appearance and actual baking → native conditioning interfaces and historical sensitivity. Main **pp13–14** connects the evidence back to interpretation and practical graphics decisions: stronger simple controls outperform C3 on means, the specified middle contrast is not detected, the small local bake gain does not establish material fidelity, and interface-specific numerical scales are not a common dose. The conclusion is consistent with those boundaries.

Response **p3** states **R2.1 = PARTIALLY ADDRESSED**, credits ControlNet and SSI, explains the operator and task differences, supplies controlled numeric evidence and identifies persistent novelty limits. Its argument is knowledge about an actual 3D texturing intervention and its evaluation, not newly asserted algorithmic novelty. This is coherent and evidence-bounded; it cannot guarantee the reviewer will find the methodological contribution sufficient.

## Supplement organisation and nonblocking concerns

Supplement **pp1–3** gives a question/study/evidence-status reader map and a usable TOC. Fresh C, native MV-Adapter, GSO and Bake10 are explicitly distinct. The current controlled evidence appears before historical/FAC and auxiliary explorations. Supplement **pp48–66** preserves those records with historical or auxiliary boundaries, while **pp70–71** explains disposition rather than counting ledger entries as independent experiments. This resolves most chronology/audit-story burden without deleting negative evidence.

Nonblocking concerns:

- Supplement is long (71 pages) and some float-only pages, notably **pp9–10**, have substantial whitespace. Complete records and captions remain usable; this does not require another structural rewrite.
- Long numerical tables on **pp12–13** are compact. The enlarged **p12** inspection shows readable aligned cells with no clipping, but readers will normally zoom when auditing individual estimates.
- The manuscript repeats the distinction between non-detection/equivalence, interface-specific budgets and material fidelity in several sections. Those repetitions are mostly attached to different evidence; reducing them is an optional editorial preference, not a blocker.
- Minor double punctuation in run-in headings (e.g. Main **p10–11**, “comparison..” / “sensitivity..”) is stylistic and nonblocking. It is not a reason to restart rewriting after the one controlled repair.

## Disposition

Candidate is editorially coherent and visually reviewable, with the recorded Table S2 visual repair now verified. The root integration audit separately confirms final response references after recompilation. The remaining decision about submission and sufficiency of methodological novelty belongs to the author/editor. This report grants neither author approval nor publication acceptance.

## Final single-repair verification

After the bounded Table S2 repair, directly inspected the final Supplement **pp5–7**, including `supp_S2_repaired.png`, `supp5_large.png` and `supp7_large.png`, and regenerated/viewed `supp_contact_1.jpg` from the final PDF. The separate mean and CI columns keep plus/minus signs with their numbers. The previously ambiguous FG-SSIM and LLH–C3 FG-PSNR values are clearly positive; negative CI endpoints are clearly negative and intact. Table S2 remains on pp5–6, and Table S3 continues cleanly from p6 to p7 with no detached caption, overlap or clipping. Supplement remains 71 pages; no reference-location displacement is introduced. This resolves the only blocking visual issue found by this reviewer.

The final reviewer response was rebuilt to five pages and the root reports 68 resolved manuscript/supplement locations; the inspected response layout already had those five complete pages and clear R2.1 partial closure. No additional substantive figure or narrative modification is requested. Independent editorial/visual audit outcome: **no remaining blocking issue found within the stated inspection scope**. **AUTHOR_APPROVAL = PENDING**.
