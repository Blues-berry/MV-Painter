# C — Fresh C appearance-condition chain audit

## Scope and result

This is a read-only audit of the frozen Fresh C `n=300` inputs and saved method outputs. No model was loaded and no GPU inference was run. **All checked object, condition, embedding and asset identities pass**; this audit found no object mix-up, stale embedding cache, condition-tensor mismatch or changed vision-asset identity that explains the color residuals. It does not show that one reference view contains enough information to reproduce every target-view color.

Primary source: `/4T/CXY/MV-Painter-1008/1008/audits/source_evidence/r2/fresh_c/FRESH_C_INPUT_EMBEDDINGS_MANIFEST.json`, SHA-256 `50f28b3f17ef5537ec0ab56a36c3c3c142486e5a7333adaf2a51d87cc83c8a2f`. Its checkpoint SHA is `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`; its source code and vision-asset hashes are checked against current files and the manifest. The runner/config identities are respectively `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3` and `295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b`.

## What enters the model

1. **One appearance source view is selected for each object.** The dataset compares the number of zero-alpha pixels in `000.png` and `014.png`; if `000` has more, it selects `014`, otherwise `000`. The manifest's actual source image SHA was checked per UID. The cohort uses view `000` for 127 objects and view `014` for 173.
2. **The dataset RGB condition is deterministic and white-composited.** `MVPainter/src/data/mvpainter_dataset.py` reads RGBA, applies the frozen per-object random resize/stretch operations under seed `42 + index`, composites alpha against white, and returns an RGB float32 tensor in `[0,1]`. The rebuilt tensor is `[3,512,512]`; its byte SHA matches the pre-inference manifest on 300/300 UIDs. Its hash also matches both GFL and LLH `cond` input hashes on all objects.
3. **The VAE and global-embedding paths use different processors on that same condition tensor.** The runner resizes the RGB condition to `model.img_size=256` with antialiased bicubic interpolation, converts it to PIL and passes it through the frozen `feature_extractor_vae`. Its processor config specifies RGB conversion, rescale by `1/255`, resize/center-crop to 512, and normalize with mean/std `0.5/0.5`. The global embedding builder converts the same dataset tensor to PIL and uses the frozen 224-pixel `vision_processor`, whose ImageNet-like CLIP mean/std are recorded in its hashed config. The two frozen vision encoders produce a float32 `[1,1,2048]` embedding.
4. **The embedding bytes and use-site identity pass.** For all 300 UIDs, the `.npy` file SHA and contiguous tensor SHA match the manifest. Those tensor hashes match the `global_embeds` hashes in both method run rows. All five vision processor/encoder files listed in the manifest and all six source-code files match their recorded hashes. The full object-level audit is `C_APPEARANCE_CONDITION_OBJECT_AUDIT.csv`; its summary and source hashes are in `C_APPEARANCE_CONDITION_AUDIT.json`.

## Color information in the selected views

The selected source views contain varied foreground colors; they are not blank or uniformly gray inputs. Across the 300 original source PNGs, the alpha-defined foreground fraction has mean `0.174` (median `0.140`, range `0.019–0.576`). Foreground mean Lab values across objects have mean `L*=55.83`, `a*=2.20`, `b*=3.92`; per-object `a*` means range `−45.06…+44.69` and `b*` means `−61.21…+48.58`. The entire white-composited input tensor has channel means near `0.94` because most image pixels are white background; those full-frame means are not object color statistics.

The model receives one selected appearance view plus an object-level global embedding, while it generates six unique target views. It is not given six per-target-view RGB targets. Therefore, the source provides real appearance/color information but does not guarantee pixel-aligned color supervision for each unseen target view. The measured color differences are relative to rendered GT views. Without a calibrated physical-color reference, this report does not equate every GT mismatch with a physically impossible color.

## Findings and limits

- The exact selected `000/014` source, deterministic condition tensor, global embedding file, embedding tensor, checkpoint lineage, encoder assets and method input hashes all match. No preprocessing/identity correction is justified by this audit.
- This procedure verifies that a frozen embedding is the one generated for the correct source condition and encoder assets. It does not independently re-run both vision encoders to recreate the embedding, inspect semantic attention, or demonstrate that the representation carries enough view-specific material color.
- A global embedding or a single-view RGB condition may be a modeling limitation, but the current evidence does not prove it is the unique cause of a given color shift. The unresolved color-generation root cause stays `PARTIAL`; this is an information-path limitation, not a confirmed software bug.
- The previous VAE encode/decode control found that ordinary GT round-trip error was much smaller than the reviewed generated color mismatch and did not reproduce its direction. That makes ordinary VAE round-trip drift insufficient as a complete explanation; it does not rule out decoder interactions with generated latents.

Supporting files: `C_APPEARANCE_CONDITION_OBJECT_AUDIT.csv`, `C_APPEARANCE_CONDITION_AUDIT.json`, `C_CAUSAL_PROBE_RESULTS.csv`, `C_CAUSAL_PROBE_STATISTICS.csv`, and the preserved prior VAE result in `../color_failure/final_closure/COLOR_CAUSAL_DIAGNOSIS.md`.
