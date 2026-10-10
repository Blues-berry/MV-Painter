# Round 008

Independent successor of round007. Native512 training preflight and input integrity pass; frozen 2000-step dual GPU training is in progress. This iteration reports feasibility, not output quality. See 03_RESULTS_AND_RISK.md for reviewer risk and differences.

Build main, supplement and marked manuscripts with build_round_008.sh, build_supplement_round_008.sh, build_marked_round_008.sh. Run scripts/verify_native_training_preflight.py to check packaged transcripts and cohort integrity; it does not rerun hardware training. Other inherited evidence checks remain available.

Executed training sources are in data/native_training_preflight/training_sources; GPU replay requires the recorded original project sources, base weights, rendered inputs and environment. Fixed conditioning payloads and new weights remain in the local experiment run, outside this submission source archive. No external submission has been performed.
