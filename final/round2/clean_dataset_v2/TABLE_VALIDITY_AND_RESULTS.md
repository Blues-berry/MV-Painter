# Clean-v2 dataset and main-adapter result audit

## Decision

The clean-v2 dataset and the associated main-adapter run are valid for a
controlled, UID-disjoint evaluation of the recovered/retrained checkpoint.
They are usable for internal analysis and for a transparent Round-2 result
update. They are not a drop-in replacement for the old 300-object table if
the paper text assumes the old object composition or the old metric trend.

## Why the dataset is reliable

- The historical 1,118-object training list is preserved and hashed.
- The old 300-object list and all old rendered/inference outputs are preserved.
- Exactly 101 UID-level overlaps were replaced; 199 old disjoint UIDs were
  retained in the original order.
- The resulting 300 UIDs are unique and have zero intersection with the
  historical 1,118-object training list.
- All selected objects have complete views `000`--`016` for image, normal,
  depth, and camera.
- The evaluation runner explicitly forces unique6 `[0,15,12,16,13,14]` and
  records the evaluation-list hash in its manifest.

## Important limitation

The 101 replacements were drawn from the existing complete-render pool
`train_objects_1200.txt`, not newly rendered same-source Objaverse objects.
Therefore clean-v2 removes UID leakage against the historical checkpoint but
also changes the source composition of the 300-object set. The replacement
objects are quarantined and must not be added to a future training list for a
model evaluated on clean-v2.

## Result summary on strict clean holdout (n=276)

| condition | Full PSNR | Full SSIM | Full LPIPS | FG PSNR | FG SSIM | Edge SSIM |
|---|---:|---:|---:|---:|---:|---:|
| no-adapter | 10.5142 | 0.7265 | 0.6271 | 8.7759 | 0.4777 | 0.4786 |
| fixed-low | 15.0864 | 0.8503 | 0.1936 | 7.0296 | 0.3548 | 0.5003 |
| fixed-high | 13.3647 | 0.8233 | 0.1897 | 5.4096 | 0.2291 | 0.4938 |
| C3 | 14.8745 | 0.8549 | 0.1895 | 6.7629 | 0.3483 | 0.5000 |

Paired bootstrap on the same 276 objects shows:

- C3 vs no-adapter: Full PSNR `+4.3604`, but FG PSNR `-2.0130` and FG SSIM
  `-0.1294`; Edge SSIM `+0.0215`.
- C3 vs fixed-low: Full PSNR `-0.2118`, FG PSNR `-0.2667`, FG SSIM `-0.0065`,
  while Full LPIPS improves by `+0.0041` after direction normalization.
- C3 vs fixed-high: C3 is better on Full/FG PSNR, FG SSIM, and Edge SSIM;
  Full LPIPS is effectively tied (`+0.0002`, bootstrap interval crossing zero).

## Recommended use

Use clean-v2 now for leakage-controlled internal conclusions and retain the
full per-object outputs. Do not edit paper numbers based on the old table or
hide the foreground regression. If minimal paper changes are essential, the
next technically clean option is a source-matched clean-v3 set made from 101
newly rendered objects outside both the historical training list and all old
evaluation lists. Until that exists, clean-v2 is the defensible dataset, but
the changed trend must be acknowledged.

No formal independent 3D bake is claimed for clean-v2: the replacement UIDs
do not supply an audited, disjoint exact-GLB/UV pool in the current workspace.
