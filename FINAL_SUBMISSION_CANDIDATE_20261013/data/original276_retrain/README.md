# Original 276 UID leave-out retraining

This run is prepared to address the strict original-cohort gap. The exact 276 object UIDs are positions 24–299 of the original `test_objects_300.txt`; the list matches the preserved `old_uid` mapping. The prior 1,118-object training list contains 79 of these UIDs. Those 79 are removed, leaving 1,039 training objects and zero train/evaluation UID overlap. The other 197 test UIDs were already absent from the prior train list.

The same historical main-adapter training entry point and model source are used, with the recorded 2,000-step schedule and learning rate 1e-4. The earlier controlled run did not record its training seed; this retrain records seed 20261012. The evaluation uses the same four conditions, unique-six views `[0, 15, 12, 16, 13, 14]`, 50 sampling steps, and evaluation seed 42.

The queue entry waits until all GPUs report at most 512 MiB and 5% utilization for 120 seconds and the currently observed MVA experiment processes have exited. It then runs training and evaluation on GPU 0. It will not start while those experiments are using the GPUs.

See `protocol_manifest.json` for hashes and exact paths. Outputs are isolated under `/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_original276_leaveout_20261012`; no existing results are overwritten.
