# 1008 second-round submission folder

This is the local, complete draft package directory. Open `Manuscript_1008.tex` and `Manuscript_1008.pdf` directly from this folder. The authoritative editable manuscript remains `1008/manuscript/revision_01549_restored/manuscript_1008.tex`; the package copy is checked byte-for-byte against it when assembled.

The package is marked `DRAFT`. The cover letter, highlights, graphical abstract, and title page require author review. The 0907 title page, acknowledgements, and declaration are carried forward in a separate folder for verification; the 0907 cover letter, highlights, and graphical abstract were excluded because their scientific claims are superseded. The original conference submission is preserved as an editorial-history attachment, with its continued requirement to be confirmed.

To refresh the paper files after an approved revision, run `python3 1008/scripts/assemble_submission_1008.py` from the repository root. The script rebuilds the clean source archive, copies the current manuscript/supplement package, produces convenience response formats, regenerates hashes, and refuses to package if the active TeX and author-review TeX differ.

No journal upload or submission was made. `SUBMISSION_APPROVED=NO`.
