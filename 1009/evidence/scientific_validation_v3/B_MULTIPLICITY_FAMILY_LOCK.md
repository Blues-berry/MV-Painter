# B multiplicity-family lock — retrospective reconstruction

**Status: `RETROSPECTIVE_LOCK_AFTER_PRIOR_OUTCOME_EXPOSURE`; not a
prospective multiplicity lock.** The family definitions below are transcribed
from the frozen `PRIMARY_HYPOTHESES.md` and `MASTER_PROTOCOL_LOCK.md`. No new
condition or metric may be promoted after seeing outcomes. The lock is useful
for consistent remaining reporting, but its timing does not cure the missing
pre-unblind safeguards.

| Family | Registered comparison/tests | Primary metric | Secondary metric | Multiplicity | Role in the 30-condition B manifest |
|---|---|---|---|---|---|
| A / H1 | 15 A3 cell-vs-baseline ΔFG-LPIPS tests + one Layer×Window interaction | FG-LPIPS | listed Core-7/texture metrics | Holm, 16 tests | The bounded A3b map is not equal-dose; report raw bounded map and dose sensitivity separately. Do not claim H1 dose-normalized confirmation solely from raw significance. |
| B1 / H2 | LLH − LFM-EXACT | FG-PSNR | FG-LPIPS | Holm, 2 endpoints | Confirmatory, with frozen ±0.5 dB / ±0.01 practical-equivalence interpretation only as specified in H2. |
| B2 / H3 | LLH − HLL and LLH − LLL, each on FG-PSNR and FG-LPIPS | FG-PSNR | FG-LPIPS | Holm, 4 tests | Confirmatory equal nominal high-duration location contrasts. `a3_baseline` is the LLL profile. |
| C / H4 | LLH against four frozen generic schedules × endpoint-matched/budget-matched variants | FG-PSNR | FG-LPIPS | Holm, 8 tests | This is the separate Experiment C family. Post-lock generic-extension analyses are exploratory and cannot inherit H4 status. |
| E / H5 | 2 paired metrics × 5 GT texture statistics | FG-PSNR, FG-LPIPS | — | Holm, 10 Spearman tests | Prospective texture-boundary family; do not exclude objects by outcome. |
| B3 diagnostics | True-global dose controls; capped native controls | Descriptive FG-PSNR | FG-LPIPS and residual-dose diagnostics | No confirmatory family in `PRIMARY_HYPOTHESES.md` | Descriptive/benchmark unless a separate pre-existing registered contrast explicitly applies. |
| Boundary sensitivity | Four frozen late-onset pulse profiles | FG-PSNR/FG-LPIPS | actual-dose profiles | Sensitivity/exploratory; no post-hoc boundary search | Classify the one-third partition; no condition may be selected as a new optimum. |

### Fixed reporting rules

- Report paired object-level mean and median differences, 95% CIs, and win
  rates; p-values alone do not establish importance.
- Use the frozen 10,000-resample paired object bootstrap and seed
  `20261002` for registered B families.
- Keep nominal requested budget and realized residual dose distinct.
- HLL − LLL is not one of the four H3 tests and remains exploratory.
- Keep primary and secondary metrics and each hypothesis family separate.
- No new boundaries, windows, scales, metric families, or favorable-object
  subsets may be introduced.
