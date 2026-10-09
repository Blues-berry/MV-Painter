# E5 residual-dose feasibility record (2026-10-06)

This compact package selectively preserves a technical feasibility audit from archived branch `codex/human-confirmatory-analysis-20261007` (HEAD `86292c8b5822533e52a1621cc04e6c076dbdc153`). It is development-only evidence, recorded after V3 outcomes, and contains no image-quality metrics.

The report records 174/174 generations and 4,860 active target-read wrapper-step interventions. All values were finite, all steps met the predeclared 5% relative-dose error bound (largest error 0.47%), no zero-norm or infeasible steps occurred, and all 4,860 reference-write calls were unchanged. The separate cap context is limiting: after dtype rounding, shallow exceeded its native cap in 164/540 steps at alpha 0.005, 211/540 at 0.01, and 360/540 at 0.02; deep and middle had no cap-exceeding steps. The equivalent total scale is an L2 norm ratio, not an exact scalar multiplier or a deployed result.

These measurements establish numerical feasibility only on six previously used development objects. They do not test output quality, establish a dose-independent Layer × Window mechanism, or support a positive method claim. The shallow cap prevents a three-group cap-respecting dose match under this diagnostic. Do not retune the intervention using these observed outcomes or promote this package as confirmatory evidence.

The compact report, protocol, lock, and aggregate gate summaries are preserved. Ignored raw per-wrapper traces, model assets, and run outputs remain in their original local locations and were not copied. No new GPU work was run.

The source `E5_LOCK.json` SHA-256 was `d189bcf02a3608ba410992a2502828c3b36453e4cf617f06da45a9c239a25813`. In the retained copy, machine-specific absolute paths were normalized to repository-relative paths; hashes and experimental settings were preserved. The original source lock remains recoverable from the archived branch object.
