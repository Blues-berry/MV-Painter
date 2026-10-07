# Clean-checkout reproducibility audit — reviewer-closure candidate

Audit date: 2026-10-07
Candidate commit audited: `e267b2d59bbb722827ca5ad72f7ca4475b13c8f1`

## Determination

**`CLEAN_CHECKOUT_REPRODUCIBILITY = PARTIAL / OPEN`.** A detached clean checkout of the candidate was created. The bundled paired-input analyses and both manuscript sources rebuilt successfully. Full run-identity and generation-source integrity remains open because the package does not contain every frozen cohort/input manifest, render input, prediction, and source artifact needed to reconstruct the image-generation runs.

This status does not require a new image-generation or training run. It distinguishes numerical and paper-assembly reproducibility from historical generation-level reconstruction. The older [clean-checkout report](../evidence/audits/FINAL_CLEAN_CHECKOUT_REPRODUCIBILITY_REPORT.md) is explicitly labeled as a prior snapshot.

## Exact-checkout results

| Component | Clean-checkout result | Limit |
|---|---|---|
| Fresh C primary, addendum, C3−GFH, and Fresh B numerical authority | `PASS`: [`verify_bundled_numerical_authority.py`](../scripts/verify_bundled_numerical_authority.py) reaggregated 42 authority rows from four hash-pinned non-human inputs. Maximum absolute difference was 2.22e-16 for effects, 5.55e-17 for medians, 1.11e-16 for lower interval bounds, and 5.2e-18 for upper bounds; fractions, counts, and reported p-values matched. Input and output hashes are recorded in [the machine-readable audit](../evidence/audits/BUNDLED_NUMERICAL_AUTHORITY_REAGGREGATION_20261007.json). | Reaggregation starts from paired per-object results. It does not recreate predictions or rerun the original generation pipeline. The legacy Fresh C analyzers retain `/4T`-specific paths and are not invoked. |
| Fresh B C3−GFH supporting sensitivity | `PASS`: the packaged N=150 input regenerated all seven endpoint summaries. The source SHA-256 is `ce7ba03f6dcb9f1d275b389c633e23dc544404eeac4ddf090e90a11ad278e081`; the bundled script and output hashes are recorded in the authority tables. | This remains a separate retrospective/post-hoc sensitivity, not a confirmatory replication, and is not pooled with Fresh C. |
| Reviewer visual candidate pool | `PASS`: all 20 committed candidate panels match their recorded SHA-256 values; the pool audit reports 20/20 exact copies. The two main-paper selections also match their recorded hashes. | The committed candidate panels and curation records are reproducible as a package. Rebuilding them from all original renders/predictions is outside this audit because those generation assets are not bundled. |
| Revised main manuscript and supplement | `PASS`: both sources compiled from the clean checkout using class/style/logo files extracted from the tracked `final/submission_new_0907/latex.zip`. The main PDF has 8 pages (clean-build SHA-256 `f18905e9ff0cb4b7b60b24ae89d1048a730a9164e8c6fbb3d2d442e43db45f14`); the supplement has 4 pages (SHA-256 `3d74812dc91f7ffd69c42378a2aef007a964dfea0fadbb649a430a5631d3cfe7`). Reviewer response locations were checked against the clean-build main PDF text layer. | PDFs remain local and are excluded from Git by the repository rule for `final/*`. Any manuscript edit requires recompilation and another page/line check. |
| Reviewer response and authority files | `PASS`: both authority tables parse with consistent columns; Fresh C and Fresh B inputs, analysis outputs, and key result files resolve from the checkout. The required R1.4 opening sentence is exact. | Reviewer-source round identity remains `ROUND_IDENTITY_UNCERTAIN`; the external response is a working draft and has not been uploaded. |

## Scope and remaining limit

- The Fresh C integrity and direction audits recorded in the package report `PASS`, but their complete generation manifests and prediction/render payloads are not bundled. The present clean checkout can reproduce the paired statistics, not rerun those source-integrity gates from every original input.
- The packaged Fresh B and Fresh C metrics are non-human generated-output records. No participant-level human responses were accessed or analyzed.
- No GPU job, training, or image generation was started for this audit.
- Reviewer closure remains open: R1.1 is partial, R2.1 retains venue risk, reviewer-round identity is uncertain, and the author review/submission decision remains outstanding.
- No journal submission or reviewer-response upload has occurred.

The remaining open item is full generation-source reconstruction from all original run-bound inputs. The revised claims are already bounded to the packaged evidence; no unsupported generation-level reproducibility claim is made.
