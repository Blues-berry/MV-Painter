# Source-view color and appearance-input audit

## Data-path identity

The frozen `unique6` dataset selects view 000 or 014 by comparing the transparent-pixel counts of those two source renders. The selected RGB source is target tile 0 in both orders: `[0,15,12,16,13,14]` when not reversed and `[14,15,0,16,12,13]` when reversed. In the four locked development objects, target tile 0 was byte-identical to the corresponding raw source RGB in all four cases. The source tile is not rotated in the reverse branch; rotations are applied only to the other mapped views.

The condition path intentionally transforms only `cond_imgs`: it applies random foreground stretch/compress and a random canvas resize, while target RGBs remain untransformed. The four development condition/target foreground-mask IoUs range from 0.3215 to 0.8053. Pixelwise registration of the condition to target tile 0 is therefore not a valid color comparison; the color audit uses robust foreground distributions and geometry masks.

## Processor and encoder paths

- VAE condition path: resize the 512×512 `cond_imgs` tensor to 256×256 with antialiased bicubic interpolation, convert to PIL, then use the frozen `CLIPImageProcessor` at 512 with center crop, RGB conversion, `1/255` rescaling, and `(x-0.5)/0.5` normalization. The actual processor output tensor and posterior sample/RNG identities are logged in the Phase B run.
- Global appearance path: convert the current 512×512 `cond_imgs` tensor to PIL, use the frozen 224-pixel vision processor with its recorded CLIP mean/std, run both frozen vision encoders, concatenate their 768+1280 features, multiply by the frozen 77-token ramp, and add to `uc_text_emb`. The actual prompt contribution and its change from the cached feature are traced by the intervention runner.
- Processor configs are under `/4T/CXY/MV-Painter/checkpoints/hf_repo/{feature_extractor_vae,vision_processor}/preprocessor_config.json`; their hashes and the inference checkpoint/config identities are recorded in the runtime trace.

## Fresh B cache correspondence (input-only)

The frozen 150-object Fresh B list was audited before opening any generated PNG or quality metric. Recomputing the two vision encoders from the exact seeded current `cond_imgs` matches the stored cache within max-absolute difference `0.03` for `0/150` (median `3.3992`, P95 `5.1092`, maximum `6.8746`). Recomputing from the unaugmented selected source RGB also matches `0/150` (median `3.3004`, P95 `5.3485`, maximum `6.8331`).

On eight preselected source-view sentinels, all four objects whose official selected source was 014 had a cache closer to raw view 000 than raw view 014. The full input-only check over all 98 source-014 objects confirms that raw view 000 is closer by max-absolute distance for `84/98` and has higher cosine similarity for `94/98`. Median cache distance is `3.6740` to selected raw view 014 and `2.5664` to raw view 000, but neither is an exact match within `0.03` for any of the 98 objects. The cache therefore has a systematic view-000 correspondence signal plus an additional unresolved embedding/preprocessing difference. This is a concrete source/cache mismatch, not yet proof that it causes the color cast.

Fresh C cache provenance behaves differently: the two Fresh C development objects in this audit match the exact current transformed condition embedding within numerical identity, while their raw untransformed embeddings differ. This agrees with the Fresh C cache builder's locked preprocessing path.

## Color-output comparison and causal result

The locked Phase B intervention completed 64/64 calls on four development objects. Within each object, the initial latent, geometry-feature mapping, and pre-posterior RNG hashes matched across conditions. Runtime identities, actual `EulerDiscreteScheduler`, FP16 precision, VAE/vision processor configurations, and PNG SHA-256 values are recorded in `runs/phase_b/runtime.json`, `run_manifest.json`, and `COLOR_INTERVENTION_RESULTS.csv`.

- A ±6 Lab perturbation applied only through the VAE image path produced sub-0.3 mean aligned output shifts and failed the locked directional criterion on both a* and b*. Under this intervention, the VAE route did not reliably carry source chroma into the six-view prediction.
- Global-embedding-only a* perturbations passed the locked source and unseen-view directional criterion in both signs on all 4/4 objects. Global-embedding-only +b* passed on 4/4; −b* passed on 2/4. This identifies a causal appearance-control path, not a successful repair.
- Replacing the cached embedding with one recomputed from the exact current transformed condition changed the two Fig. 4 failure outputs in opposite directions: unseen-view mean ΔCIEDE2000 was −0.370 for row 2 and +0.284 for row 1. The normal and high-texture Fresh C development outputs were pixel-identical to their cached GFL outputs. The cache mismatch can affect failure outputs but does not provide a stable correction.
- On these four objects, No Adapter had a much larger mean unseen-view CIEDE2000 than GFL (+20.07 relative to GFL), alongside very large geometry/lightness changes; this does not isolate a pure adapter-induced hue effect. LLH was mixed per object and had a mean unseen-view CIEDE2000 penalty of +2.56 relative to GFL, with mean L* SSIM versus GFL of 0.576. The locked readouts do not establish a fine-detail benefit from LLH.

The complete object-level reference comparison is `runs/phase_b/B_REFERENCE_CONDITION_COMPARISON.csv`; directional arm results are in `B_CHANNEL_RESPONSE_RULE.csv`. The full causal interpretation and the C1 visual-gate failure are recorded in `B_CAUSAL_VERDICT.md` and `runs/phase_c/dev/C1_DEV_MANUAL_REVIEW.json`. The full color-generation root cause remains unresolved; the evidence supports the global embedding path as a color-control channel and a cache-mismatch contributor on the two failure objects, not as a complete explanation.

## Evidence files

- `runs/phase_b/A_CONDITION_ENCODING_TRACE.csv` — four development source, tensor, mask, processor, and cache/recompute identity records.
- `runs/phase_a/FRESHB_INPUT_EMBEDDING_AUDIT.csv` and `.json` — original current-condition-only input audit.
- `runs/phase_a/FRESHB_INPUT_EMBEDDING_PROVENANCE.csv` and `.json` — current-condition versus unaugmented selected-source comparison.
- `runs/phase_a/FRESHB_CACHE_ALTERNATE_VIEW_AUDIT.csv` and `.json` — eight input-only alternate-view sentinels.
- `runs/phase_a/FRESHB_VIEW0_CACHE_ORIGIN_AUDIT.csv` and `.json` — all 98 selected-014 objects, input-only.
- `runs/phase_b/B_REFERENCE_CONDITION_COMPARISON.csv` and `.md` — paired No Adapter/GFL/LLH/cache-refresh comparison on the four development objects only.

Fresh B list SHA-256: `f681e33cc4d2e7b86cba8bf986ff44bdabe927a1de34f88743eb976c09e4bb28`. Checkpoint SHA-256: `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`. Config SHA-256: `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.
