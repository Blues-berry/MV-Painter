# Round 2 clean evaluation dataset v2

This directory is a new evaluation protocol layer. It does not delete or
modify `data/train_data/rendered_full/test_objects_300.txt`, the old rendered
objects, or any previous inference output.

## Construction

- Historical checkpoint training reference: the preserved 1,118-object list
  in `mvpoutput/reviewer1_main_rerun_20260928/train_objects_full_1118.txt`.
- Original evaluation order is retained wherever the UID was disjoint.
- Exactly 101 positions whose UID occurred in the historical training list
  were replaced, in-place, by complete objects from the existing
  `train_objects_1200.txt` pool that are not in the historical list.
- Every replacement has all required `image`, `normal`, `depth_png`, and
  `camera` files for views `000`--`016`.
- New evaluation/training UID intersection is zero against the historical
  1,118-object checkpoint training list.
- The six-view protocol is explicitly unique6: `[0, 15, 12, 16, 13, 14]`.

The replacement pool is quarantined for this controlled checkpoint protocol.
It must not be used as training data for a future model that is evaluated on
this v2 list. Future retraining should use the preserved historical 1,118 list
or a separately audited train list that excludes the v2 evaluation UIDs.

## Files

- `eval_objects_300_clean_v2.txt`: new ordered 300-object evaluation list.
- `probe_objects_24_clean_v2.txt`: positions `obj_0000`--`obj_0023`.
- `strict_holdout_objects_276_clean_v2.txt`: positions `obj_0024`--`obj_0299`.
- `old_to_new_uid_mapping.csv`: complete old/new mapping by synthetic object ID.
- `dataset_manifest.json`: hashes, overlap audit, and construction rule.
- `replacement_candidate_pool_189.txt`: complete candidate pool used for deterministic replacement.

Use `geotex/round2_main_eval.py --object-list-file` for subsequent main-adapter
inference. The runner now forces `target_view_mode=unique6` and records the
list hash and UID mapping in its evaluation manifest.
