# Authenticated 01549 source baseline

## Submission identity

- **01549 status:** post-first-round revision submitted on 2026-09-07. The current R1/R2/R3 packet is the second-round review; this restored tree is the editable historical base for 1008.
- Official archive: `1008/manuscript/source_01549/01549_latex.zip`
- Official archive SHA-256: `67464667d4ada0c467316a7b28c923b4a00796f91126755a2448e90ee0458d0a`
- Archive member `final_0903.tex` / authenticated source SHA-256: `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`
- Official submitted PDF: `1008/manuscript/source_01549/01549_submitted_manuscript_0907.pdf`
- Official submitted PDF SHA-256: `fc9cf793e4922df2a03818e2174310c394d6ea0ab235f124e569ee173a1620da`

## Restored baseline contents

`final_0903.tex` in this directory is copied byte-for-byte from the authenticated source directory and matches the archive member hash. Original figures, class/style files, and logos are referenced from the unchanged `source_01549/` directory and checked against the recorded hashes. The official ZIP, PDF, source TeX, and images remain in that controlled source path.

Run `python3 verify_baseline_source.py` to verify the local copy and its provenance. Run `bash build_original_01549.sh` to compile the restored TeX using the source package's figures and template; output goes into `build/` and does not overwrite source files.

An independent local build of the locked source completed successfully at 15 pages. The official PDF and the clean build were text-identical after layout extraction and pixel-identical across the 15 rendered pages; the PDF container metadata differed. This build record describes that verification and is not a claim that the GitHub-hosted editor compiler completed.
