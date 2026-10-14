# V3 → V4 change log

- Verified the V3 TeX and PDF hashes against the V3 artifact manifest before making changes.
- Replaced the three-row Bake10 Figure 3 with a single best-case example from the seven rights-cleared display candidates. Selection uses the existing 11-view FG-LPIPS object summaries; UID `238ff3e41c964655b83aa9c8770cc766` ranks first for both displayed schedules.
- Kept the source projection image at raw view 000 separate from the held-out unseen raw view 004 bake panels. The three bake panels use one shared crop. Added the source pixels, attribution, selection ranking, camera/protocol metadata and hashes to the V4 support records.
- Corrected the figure's stated render dimensions to the actual 512×512 PNG size and the renderer's top-level 512-pixel setting. Recorded that per-render `image_size` metadata says 1024×1024 for the same files.
- Updated the Figure 3 interpretation and synchronized the reviewer response. The response continues to disclose the lack of material-fidelity validation.
- Rebuilt the main manuscript, Supplement, reviewer response and marked manuscript with V4 filenames.
- No tables, experiment outputs, frozen estimates, confidence intervals, p-values or reviewer positions were changed. No GPU experiment was run.
