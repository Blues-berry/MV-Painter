# Round009 — in progress

Independent successor of round008 (cbc54193). Prospective native-path cohort, statistical protocol, self-metric calibration and50-object camera-direction audit are frozen. Formal fixed2000-step native512 training has completed and passed the full CSV, seeded-order/dropout, synchronized-gradient and final-weight audit. The50x2 inference stage is live; no completed quality result or completed-round claim.

The TeX and response currently inherit round008 and require integration after actual new results. Do not treat this checkpoint as the completed ninth submission package. 06_THREE_ROUND_SUMMARY_DRAFT.md is explicitly pending.

See 01_ANALYSIS.md and02_PLAN.md. Frozen cohort and executed input evidence are in data/native_checkpoint_evaluation. New evaluation preparation sources committed in experiment worktree0f82297c; the additional read-only fullControlNet asset audits are in c0960c1f. A CPU strict-load audit passes all2543 keys and confirms the HF UNet differs from all1680 corresponding v29 tensors at HF precision; no official full-default deployment equivalence is claimed. The live supervisor waits for existing training, audits full completion, uses free GPUs for50x2 fixed native controls, and scores actual outputs; it never restarts missing training or screens by quality.
