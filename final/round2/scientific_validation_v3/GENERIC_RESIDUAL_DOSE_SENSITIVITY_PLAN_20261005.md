# FRESH_CONFIRM_B generic-schedule dose sensitivity plan — 2026-10-05

**Status:** The pairwise family was frozen in
`FRESH_CONFIRM_B_GENERIC_EXTENSION_LOCK_20261005.md`. This supplemental model
was fixed before aggregate extension outcomes were computed; a separate note
documents that one raw extension record was accidentally exposed during
metadata inspection. This remains same-cohort, post-lock sensitivity evidence,
not independent confirmation.

For each object and each of the nine schedules (`layer_llh` plus the eight
frozen generic variants), derive the actual total integrated post-scale
correction norm as the sum over 50 steps of the Euclidean norm across all
logged wrapper corrections. The logs and manifest determine native cap
semantics. Define common support as the intersection of each method's
5th–95th percentile dose interval, calculated from dose only. Retain rows
inside that interval without using metric outcomes; report retention by method.

On common support, fit each FG-PSNR and FG-LPIPS endpoint with method fixed
effects, `log(total integrated post-scale norm)`, and object fixed effects,
using object-cluster robust covariance. Report LLH-minus-generic conditional
contrasts at the retained sample's mean log dose with unadjusted model CIs.
These are descriptive conditional associations, not equal-dose causal
estimates. If the intersection is empty or any method retains fewer than 20
rows, report the dose-adjusted comparison as not estimable; do not widen the
support or switch dose definitions.

The confirmatory H4 inference remains the locked paired-object bootstrap and
eight-test Holm family, separately for FG-PSNR and FG-LPIPS. The dose model
does not add tests to or replace that family.
