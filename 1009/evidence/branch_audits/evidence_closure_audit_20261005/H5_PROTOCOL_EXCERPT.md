# H5 protocol record

Source: `final/round2/scientific_validation_v3/PRIMARY_HYPOTHESES.md` at
`c1fb1b75814c91dc063aeab55007bbd66601fd3f` (2026-10-02 10:59:54 UTC).
That source file predates the archived B1B2/B3 outcome bundle commit
`7e3a8d4b` (2026-10-04).

The source hypothesis states:

- H0: paired LLH−GFL FG-PSNR and FG-LPIPS deltas are independent of GT-only
  texture-complexity descriptors.
- Tests: Spearman correlation with bootstrap confidence intervals against
  GT Laplacian variance, RGB standard deviation, gradient energy, HF energy,
  and foreground coverage; quartile effects and win/loss rates.
- Family E: 2 metrics × 5 GT statistics = 10 Spearman tests, Holm correction.
- No result-based object exclusion.

This excerpt records the source protocol text and commit order. The current
main `B_MULTIPLICITY_FAMILY_LOCK.md` labels its family lock
`RETROSPECTIVE_LOCK_AFTER_PRIOR_OUTCOME_EXPOSURE`; that separate status remains
in force until the earlier exposure and safeguarding timeline is reconciled.
The data result is reported with that caveat, not as an unrestricted claim of
confirmatory evidence.
