# Clean-checkout package rebuild audit — 2026-10-06

## Scope and checkout identity

This audit checks whether the published `1006` evidence bundle can be rebuilt
from its committed files without relying on the modified working tree. The
tested commit is `00c48915877f592c725d5b13be90905eab347b0a` on
`codex/paper-1006-20261006`.

The GitHub HTTP pack transfer stalled, so the test checkout was created as a
new sparse worktree from the local Git object database at that exact published
commit. It was clean before the rebuild and clean again after generated outputs
were restored. This exercises the committed tree in a fresh checkout layout;
it is not evidence that a direct network clone completed successfully. Before
rebuilding, all 401 entries in the committed `1006/SHA256SUMS.txt` passed
`sha256sum -c`.

## Rebuilt results

From the fresh checkout, the following scripts completed successfully:

```text
python 1006/scripts/analyze_strict276_c3_retrospective.py
python 1006/scripts/analyze_fresh_b_c3_gfl_posthoc.py
python 1006/scripts/build_objaverse_attribution_tex.py
python 1006/scripts/generate_figures.py
```

The strict-276 analysis reproduced 14 endpoint-pair summaries and 552 paired
object deltas. GC3−GFL FG-PSNR was +1.207771 dB (nominal object-bootstrap 95%
CI [+1.116967, +1.294989], 259/276 favorable). The FRESH_CONFIRM_B post-hoc
analysis reproduced seven endpoints over 150 object pairs; GC3−GFL FG-PSNR was
+0.501881 dB (95% CI [+0.341873, +0.662862], 100/150 favorable). The pair was
selected after unblinding, so this rebuild does not change its post-hoc status.
The attribution builder produced 24 panel records.

Both manuscript builds exited successfully with the supplied Elsevier/CAG
class and style files:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main_1006.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary_1006.tex
```

The rebuilt main PDF is 7 pages and 270,926 bytes; the supplement is 11 pages
and 27,171,181 bytes. Extracted text is byte-identical to the committed PDFs.
The supplement PDF is byte-identical; the main PDF differs by three bytes,
consistent with non-content PDF serialization metadata. Five regenerated
figure PDFs (`b_primary_contrasts`, `b_profiles`, `e1_seed_sensitivity`,
`e2_static_factors`, and `glb_native_endpoints`) rasterized identically to the
committed figures at 150 dpi. There were no missing graphics, undefined
citations/references, or build errors. Non-fatal LaTeX layout warnings remain.

Generated files were restored after comparison; the fresh checkout returned
to a clean status. The submitted 01549 manuscript was not edited.

## Boundary of the result

**PASS:** package integrity and rebuild of the included compact analyses,
tables, figures, and candidate LaTeX from a fresh checkout of the published
commit.

**PARTIAL:** end-to-end reconstruction of all historical GPU-generation
results. The package does not contain every historical prediction, residual,
and rendering payload needed to rerun those campaigns from raw inference
inputs. Stored metrics and generation provenance can be audited within their
recorded scopes, but this build does not regenerate omitted model outputs.

This is therefore a clean-checkout compact-bundle rebuild, not a claim of a
fully end-to-end independently reproducible manuscript. The limitation remains
material to R1.5 and should be disclosed in the response and artifact notes.
