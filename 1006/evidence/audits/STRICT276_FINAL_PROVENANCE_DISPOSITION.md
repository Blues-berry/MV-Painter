# strict-276 final provenance disposition

**Final state: `RETROSPECTIVE SUPPORT`.** It is not an independent confirmation.

## Available and traceable

The frozen strict-276 cohort has 276 paired object rows and 14 endpoint/contrast summaries across the retained GC3/GFL and GC3/GFH comparisons. Object-level pairing is present in `1006/data/derived/strict276_c3_object_deltas.csv`; the paired summary table is `1006/data/derived/strict276_c3_paired_summary.csv`. The stored C3−GFL FG-PSNR estimate is +1.207771 dB, nominal object-bootstrap 95% CI [+1.116967, +1.294989], with 259/276 favorable objects.

## Provenance limits

- The legacy runner identity cannot be verified to the required complete standard.
- Complete legacy input-tensor hashes are unavailable.
- The analysis can reconstruct paired metric differences from stored rows, but cannot establish full end-to-end regeneration from the original inputs and runner.
- The stored checkpoint lineage is not sufficient to certify a new independent execution from the archived evidence.
- These estimates are retrospective same-cohort reevaluations; the nominal intervals are not a multiplicity-corrected independent confirmation.

Do not launch another GPU run for strict-276. Use Fresh C as the primary revision-era image-space evidence and keep strict-276 as explicitly labeled retrospective support.
