# AUDIT — What did the dev-24 "3 seeds" actually vary? (2026-10-01)

Question (external review, priority 5): the R0/R1 robustness pair varies only
the reference-preprocessing realization, so `ROBUSTNESS_SUPPORTED` must not
be worded as general stochastic robustness. Do the EXISTING 24-object
3-seed runs vary the generation noise (initial latent / VAE cond latent) or
only the preprocessing draw?

## Evidence (code inspection, geotex/layer_lhl_ablation_shared.py)

The three frozen probe runs
`/4T/tmp/mvpainter-layer-lhl-ablation/seed{42,43,44}/`
(protocol layer-lhl-shared-input-ablation-v1, 24 probe objects, 6 methods,
manifests committed with the frozen evidence) execute, per object:

    seed_all(seed_argument + object_idx)      # L125: python/numpy/torch
    batch = collate_batch(...)                # cond stretch draw <- object_seed
    ...
    torch.manual_seed(object_seed)            # L132
    shared_latent = torch.randn(...)          # L133: INITIAL LATENT <- object_seed
    per method: torch.manual_seed(object_seed) # L140: VAE cond latent <- object_seed

Because `object_seed = seed_argument + object_idx` and the three runs use
seed_argument 42/43/44, EVERY stochastic component differs across the three
runs: reference stretch realization, initial latent, and VAE cond-latent
sample. The manifest fields "shared_inputs" (shared WITHIN a run across
methods) and "condition_vae_seed_reset_per_method" are per-run sharing —
they do not pin the latent across seeds.

## Conclusion

- The dev-24 3-seed evidence (factorial 576 rows, probe ablations) varies
  the FULL per-object stochastic stack, i.e. it is genuine generation-noise
  robustness evidence at n=24, in addition to preprocessing robustness.
- The strict-276 R0/R1 pair varies ONLY the preprocessing realization
  (latent seed pinned at 42 in both), i.e. preprocessing-only robustness at
  n=276. Wording in future paper text must keep the two claims separate:
  "preprocessing-realization robustness (n=276, two realizations)" and
  "generation-noise robustness incl. initial latent (n=24, three seeds)".
- Priority-5 experiment (second latent seed on a 76-object subset) is NOT
  required by this audit: latent variation is already covered by the 3-seed
  dev evidence. Any further latent-seed replication remains optional.
