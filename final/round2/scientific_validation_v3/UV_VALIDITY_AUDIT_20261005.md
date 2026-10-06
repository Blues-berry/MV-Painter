# UV addressing validity audit — unified same-draw bake

**Historical status as of 2026-10-05: scientific P1 open.** On 2026-10-06, `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md` closed the renderer-conformance issue for the stored N=20/eight-condition outputs by rendering the exported GLBs with their embedded repeat and mipmap sampler. The old CPU rows and seam values remain preserved as historical diagnostics; they are not silently removed or replaced. Four no-UV exclusions and the human-fidelity gate remain open.

## Finding

The frozen bake says `preserve_original_uv: true`. The CPU baker instead clamps interpolated UVs to the unit square when it splats source-view colors (`geotex/cpu_texture_bake.py:289–290`) and again when rendering unseen views (`:488–489`). Six of the 20 baked objects have substantial UV coordinates outside [0,1]; another two have minor out-of-range excursions. Out-of-range UVs may be intentional tiling, but clamping maps them to the texture edge rather than applying the texture's address mode.

The exported GLBs use `magFilter=9729` and `minFilter=9987` but omit `wrapS` and `wrapT`. Under glTF 2.0, omitted wrap modes default to `REPEAT`, which uses the fractional part of UV coordinates. Thus the baked texture is constructed with edge clamping, and the stored unseen-view render/metrics also use edge clamping, while the exported GLB is specified to repeat. These are different surface mappings for out-of-range UVs. There is a broader renderer mismatch as well: the CPU unseen renderer uses bilinear sampling without mipmaps, while `minFilter=9987` specifies linear mipmap filtering. Therefore UVs within [0,1] do not by themselves establish rendering conformance. See the [Khronos glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

| Baked object | UV pairs | Pairs outside [0,1] | UV bounds (U, V) | Audit note |
|---|---:|---:|---|---|
| `00002bcb84af4a4781174e62619f14e2` | 6,942 | 4,086 (58.9%) | U [−7.83, 21.20], V [−20.60, 8.33] | Tiling/range issue |
| `001dd2c17b1443aab500f61634bc3b89` | 1,579 | 1,579 (100%) | U [0.010, 0.992], V [1.010, 1.992] | All V coordinates exceed 1 |
| `009bc7ad5e26471198c8e5e41637fc60` | 8,916 | 8,450 (94.8%) | U [−1.58, 68.93], V [−79.24, 12.33] | 2,222 pairs have |UV| > 10 |
| `0162260812034687a4d337161f632d09` | 184 | 184 (100%) | U [−9.37, 13.75], V [−11.37, 10.37] | 132 pairs have |UV| > 10 |
| `01e3b853f0f74bd0b44d34ac5106a84f` | 5,459 | 1,481 (27.1%) | U [−1,804.69, 1.86e34], V [−4.95e36, 1,805.69] | 122 pairs have |UV| > 1e6; malformed-scale finite coordinates |
| `0253574c1a8f432797a7fcef9546ce75` | 2,699 | 2,699 (100%) | U [0.0016, 1.366], V [1.0000, 3.797] | Tiling/range issue |

Counts are per UV pair after loading each exact source GLB with `trimesh`, using the strict test `u < 0 or u > 1 or v < 0 or v > 1`; the counts are not surface-area weighted. The two additional baked objects with minor excursions are `00e2a79774964cb08f38c4406407300b` (one coordinate at −1.19e−7) and `0131d08f77284aea9c62ad6de74edc0b` (maximum 1.0001107); this audit does not assign a cause to those excursions. This audit does not label all tiling UVs as malformed. It establishes that the implementation's clamp behavior disagrees with the exported sampler semantics. The four already excluded objects remain excluded under the frozen no-UV rule; `008a72f0e6be408cbf90c81966789547` has some UV-mapped meshes but also meshes without UV layers.

For the most extreme object, the exact source GLB hash matches the frozen handoff (`6cbd1a1642e859afc9cf7371bff544649646363916b96ecccd5981ab99489d1f`). Its three source mesh UV arrays and the corresponding exported GLB retain coordinates of the same extreme scale. The refreshed machine audit checks all 160 exported GLBs (20 objects × 8 methods): sampler filter settings and omitted wrap fields are consistent across the checked files. This is a per-file provenance check, not an image-space conformance comparison.

## Existing-result sensitivity (diagnostic only)

The frozen 20-object comparison is preserved. Removing only `01e3…` as a post-hoc technical sensitivity gives:

| LLH − GFL | N=20 original | N=19 excluding `01e3…` |
|---|---:|---:|
| Unseen masked PSNR | +0.144 dB [−1.316, +1.653] | +0.028 dB [−1.482, +1.576] |
| Unseen FG-LPIPS | −0.02391 [−0.03192, −0.01662] | −0.02425 [−0.03268, −0.01670] |
| Unseen CIEDE2000 | +1.302 [−3.540, +5.769] | +1.663 [−3.265, +6.236] |

Intervals are percentile object-bootstrap 95% CIs, 10,000 resamples, seed 20261005. Excluding this one object does not produce an LLH PSNR advantage and does not change the observed LPIPS direction. This is not a corrected-bake analysis: the other five materially out-of-range baked objects still use clamped UVs, and the GLB renderer mismatch remains.

## Seam audit reproducibility and validity

The tracked generator `scripts/audit_bake_seams_v3.py` exists (SHA256 `856aa315e861fa1df23b9d4f4277c63e53c80477a780c9b0d6a5cd9d7e4c6038`). A fresh run to a temporary output directory reproduced both stored files byte-for-byte:

- `SEAM_AUDIT_PER_OBJECT.csv`: `8974d317fac46f8c7ba44c8f0810df103721de357604716544b12c69bfc3e86c`
- `SEAM_AUDIT_AGGREGATES.json`: `6f65f44ec88c7c1fea8dd1fe237d37fe65230842b935404947ceb216eff52703`

The run also emitted 28 `RuntimeWarning: invalid value encountered in cast` warnings at lines 65–66, all from the extreme-UV object across seven conditions. The analyzer rounds/scales to integer before clipping; values of order 1e36 overflow that cast. Exact output reproduction therefore closes the code/output traceability question but does not validate the seam measurements. More generally, the seam analyzer clamps its samples too, so the six substantially out-of-range objects do not have seam endpoints matching the exported GLB's repeat sampler.

## Manifest coverage discrepancy

`BAKE_RUN_SUMMARY.json` lists 16 objects and 128 method records, while the frozen handoff minus the four no-UV exclusions yields 20 objects. The independent closure audit found the other four objects in the existing per-object metadata, exported GLBs, and 160-row unseen-metrics ledger; their source identities match the frozen handoff. This is a run-summary coverage gap, not evidence that the four objects' outputs are absent. Keep the original summary unchanged and disclose the discrepancy. Machine-readable counts and identity checks are recorded in `audit_scripts/UV_ADDRESSING_AUDIT.json`.

## Historical closure action as of 2026-10-05

`UV_ADDRESSING_VALIDITY = FAIL_FOR_LEGACY_CPU_METRICS`; `UNIFIED_BAKE_STATUS = HISTORICAL_N20_OUTPUTS_PRESERVED; FAITHFUL_GLTF_EVALUATION_OPEN`; `SCIENTIFIC_P1 = OPEN` at that time.

The 2026-10-05 recommendation was to validate unseen rendering with GLB-matched addressing and filtering. That renderer closure is now documented in `GLB_NATIVE_EGL_RENDER_REPORT_20261006.md`, including a negative/>1 UV repeat probe, native minification filtering, exact stored output evaluation, and a fixed extreme-UV sensitivity. The source bake and existing seam outputs remain unchanged; the four no-UV exclusions still bound the result to N=20. No Blender import/export bake was rerun and no UVs were unwrapped.
