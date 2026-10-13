# Campaign C LLH–linear source-row direction audit — 2026-10-06

**Status: PASS.** The comparison was reconstructed from 300 `layer_llh` rows in campaign B1B2 and 300 `gen_linear` rows in campaign C. The source rows have identical UID sets, object indices, per-object seeds, and all six shared-input hashes for all 300 objects. The two runs also match on object-list hash, runner hash, checkpoint hash, view set, sampler, latent seed, and step count. Both legacy manifests omit the config hash; that limitation remains recorded.

The reconstructed means, medians, bootstrap intervals, bootstrap p-values, and win fractions match the saved pairwise JSON, and Holm p-values match the 16-test C family. Positive `LLH − linear` FG-LPIPS is unfavorable to LLH because lower LPIPS is better.

| Endpoint | LLH − linear | 95% object-bootstrap CI | Holm p | Direction |
|---|---:|---:|---:|---|
| FG-PSNR | +0.004885 dB | [-0.034994, +0.046888] | 0.8148 | no detected LLH advantage |
| FG-LPIPS | +0.001226 | [+0.000692, +0.001816] | 0.0016 | favors linear (lower is better) |

This is a previously inspected 300-object cohort, not a new confirmation. No equivalence, overall-winner, or perceived-fidelity claim follows. See `LINEAR_CONTRAST_DIRECTION_ERRATUM_20261006.md` for the affected historical prose and its correction.
