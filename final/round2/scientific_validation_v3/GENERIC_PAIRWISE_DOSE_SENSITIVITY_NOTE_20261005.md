# Supplemental pairwise generic-dose sensitivity — 2026-10-05

This analysis was added after the locked B generic-extension aggregate results
were opened, after the preregistered all-nine-method common-support rule found
no shared dose range. It is a post-outcome exploratory diagnostic, not a
confirmatory result, and cannot replace the locked paired-bootstrap H4 family
or the all-nine no-common-support finding.

Apply one identical rule to **all eight** LLH-versus-generic comparisons:
intersect the two methods' dose-only 5th–95th percentile intervals, retain
complete object pairs for which both method doses lie inside that interval,
and fit FG-PSNR and FG-LPIPS with method, log actual total integrated
post-scale correction norm, and object fixed effects, using object-cluster
robust covariance. Require at least 20 complete objects; otherwise mark the
pair not estimable. Report every pair's interval, retained count, conditional
LLH-minus-schedule estimate, 95% CI, and unadjusted model p. Holm-correct the
eight model p-values separately by endpoint, assigning p=1 to a pair that is
not estimable. These conditional associations are not equal-dose causal
estimates.
