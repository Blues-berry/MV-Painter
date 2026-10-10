# 01549 marked-up 0907 source provenance

These three small source files preserve the add-only markup source used for the historical 0907 submission. They came from archived source commit `d9379fe93e51a5dbf28cc1bfce9bd72b80bdbc48` (`new0529`); the active 1008 manuscript was not edited.

The clean `final_0903.tex` already in this directory has SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`, identical to the clean source in that commit. The source commit's `final/submission_new_0907/Marked-up manuscript 0907.pdf` has SHA-256 `191d7f379102408852fef5a506f02a3137f32c09781c2489f63650ef243d7aa3`, identical to the official marked-up PDF already preserved at `official_submission_0907/Marked-up_manuscript_0907.pdf`. The PDF was not copied.

`strip_difdel.py` reads `final_0903_marked.tex` and writes `final_0903_marked_addonly.tex`. In an isolated temporary directory it removed 94 deletion groups, reported balanced braces, and recreated the archived add-only TeX byte-for-byte (SHA-256 `bf6855bc2115564793c979a7c0cd65fb2a7b4994d867f1f37a051a4795616c28`). The three payload hashes are listed in `MARKED_UP_0907_SOURCE_SHA256SUMS.txt`. The generated add-only TeX is preserved byte-for-byte and has three inherited trailing-whitespace lines; they were not normalized so its audited source hash remains exact.

The 79-commit historical branch was not merged. Its old PDFs, archives, checkpoints, generated outputs, and unrelated code remain reachable through the local archive reference. No separate PDF was built and no journal submission was made. `SUBMISSION_APPROVED=NO`.
