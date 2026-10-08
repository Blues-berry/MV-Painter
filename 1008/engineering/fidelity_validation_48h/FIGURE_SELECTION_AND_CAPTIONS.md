# Figure selection and caption candidates

No formal manuscript figure was replaced. The original Fig. 4 and Fig. 6 remain the paper agent's decision. Candidates below are for supplementary evidence or response-letter attachment.

## Candidate A — Fresh B fixed-stratum examples

Use `B_FAILURE_AND_SUCCESS_GALLERY.pdf` (3 pages) and `B_GALLERY_SELECTION.csv`. It shows one object from each of the frozen Fresh B GT-texture Q1, Q3, and Q4 strata. Selection was the object nearest the within-stratum median GT Laplacian variance, with ascending UID as tie-break; generated images and outcome metrics were not used for selection. Each page contains the same six target views for GT, GFL, and LLH. The gallery is illustrative only; inferential estimates come from the full independent `n=150` paired cohort.

| Stratum | UID | GT panel SHA-256 | GFL PNG SHA-256 | LLH PNG SHA-256 | LLH−GFL CIEDE2000 |
|---|---|---|---|---|---:|
| Q1 | `00bc54b70fea4c94bf54bdb4d041522c` | `aa61a8697f9930832cf4419d08a84c9908a502feac9e6c83b24676aff054caa7` | `3a52faeba9e1a81969c489d744d484a6f0780997399445729895a018d726894a` | `d57a71e4554c25055a5bcbbb66a41d275f58a37bbaf728efb48e53421b967eb7` | `+0.893` |
| Q3 | `0013d88f17a245b0bff5ebe713bd72ab` | `db16c03254bb071d35576758ee389955a1a7fdac8db48bb923f63547427f89ff` | `40eba534874a4bc29d7cc6e8180809d5c0286ec7ab98ee61f49ba8ba2c41ce57` | `ebe9ac07471ccafbe35fdac74b5c3b66845cf4a4340f7af7d1e935660333b293` | `+2.094` |
| Q4 | `00c01670fa9545fc82e1fbfb9f70a259` | `e7da4f5889282eab4fcdcd26d34e06fc90f22b0b41bd20823d3d7e3957699f55` | `3b45f139812a4a914433a1fb800416343094dcce38e68a97936b241c1bc53f71` | `0c3e155ad79bfa3d81fb3410399d3b4920874779b2e61dc21869af00fc57c6f8` | `+9.847` |

Suggested caption:

> **GT, GFL, and LLH outputs for three illustrative objects from the disjoint Fresh B holdout.** Objects were selected before visual inspection as the GT-texture median-nearest member of Q1, Q3, or Q4; this gallery is descriptive and is not an estimate of subgroup performance. All columns use the same six unique target views. The high-texture example illustrates the failure boundary; cohort conclusions are based on paired object-level statistics over all 150 objects.

## Candidate B — Original Fig. 4 row 1 causal/trajectory panel

`CASE_IMAGES/FIG4_ROW1/` contains exact, unaltered source PNG copies for one previously reviewed original Fig. 4 object. The copies are hash-identical to the frozen source files listed below. UID `eac4b392b7b448a2b6ec77e8936abe1b`, object index 4, seed 46, checkpoint `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`, runner `e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3`, six views `[14,15,0,16,12,13]`.

| Panel | SHA-256 | Source |
|---|---|---|
| GT | `635c6001dff80148f6e144dad479d28274fc05bb7be562c3b62a0fb3a212b386` | `raw_rgb/fig4_row1/reference.png` |
| No Adapter | `b8efd3c0a60f389e12d102735aac978f501cabff93ab75433b72c2e451f88a8f` | `raw_rgb/fig4_row1/no_adapter.png` |
| GFL | `2d6f3273dc3600f0ab3db0538468bdce65852e21ed043f2f29dbd585bf55943a` | `raw_rgb/fig4_row1/native_gfl.png` |
| LLH | `4dfe29eafb1e5d35a6d321e6cddab3b748ee5b4841c4e98c1b59b88e3790c06b` | `raw_rgb/fig4_row1/layer_llh.png` |
| GFL intermediate decode at scheduler update 40 | `676e2d692c45b8854f526836a21870cd18339c2a0096c1376f2815cf3635f871` | `final_closure/evidence_rgb/stage_fig4_row1_gfl/after_step_40.png` |
| GT VAE posterior-mode round trip | `c1cfff802d0f0d555f245c91a494f45c72bf6f32cf6dbaad0cc3003be97c03df` | `final_closure/evidence_rgb/vae_fig4_row1/vae_roundtrip_mode.png` |

For the paired final rows, CIEDE2000 is 55.157 (No Adapter), 22.032 (GFL), and 32.262 (LLH); the visible pink/purple label is present in all three. The GFL RGB shows a pink surface by update 40, before baking/export. GT VAE mode round-trip CIEDE2000 is about 4.086, so ordinary GT round-trip does not reproduce the generated shift at the observed magnitude. These are forensic examples, not a population frequency estimate or proof of a unique cause.

Suggested caption:

> **A visible color mismatch is already present in the unmodified output and remains under adapter conditions.** The six-view target, No Adapter, GFL, and LLH panels use the same object and target set. A decoded GFL intermediate at scheduler update 40 shows the shift before texture baking; the separate GT VAE round trip does not reproduce it at comparable magnitude. These panels localize the observed artifact to the generated RGB path but do not identify a unique mechanism.

## Placement and limits

- Keep the original Fig. 4/6 PDFs unchanged. Candidate B is best suited to a response-letter attachment or supplement because it is one diagnostic object.
- Candidate A provides fixed-rule examples from the independent holdout and should accompany, not replace, the full-cohort table.
- The existing `../color_failure/final_closure/COLOR_FAILURE_CASEBOOK.pdf` contains the broader 26-object diagnostic comparison, including No Adapter. Label it as a targeted forensic set.
- Neither gallery establishes baked unseen-view quality, seam behavior, or a measured physical-color standard. Those claims require separate evidence.
