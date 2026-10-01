# Final qualitative figure selection audit — 2026-10-01

The active complete-object panel in `final/round2/final_round2.tex:267-273`
shows `obj_0066` and calls it “a representative object,” with a disclaimer
that it was not selected as a best-case metric example. Under the current
Core-7 LLH−GFL FG-PSNR comparison, independent recomputation gives
`+7.1576 dB`, rank **2/276** (object index 42). It is therefore not a defensible
unqualified “representative” example under the current headline metric.

The image predates the Core-7 comparison and was generated under the earlier
clean-v2 figure workflow; its selection date/rule is not recorded. The current
rank is a cross-check against the new headline comparison, not proof of the
original selection criterion.

Required action in the next manuscript rewrite: either reselect by a declared
rule (e.g. median-band example, plus a separately labeled strong case and
failure case) or retain `obj_0066` and describe it as a **high-improvement
qualitative example**, disclosing the selection context. Do not call it a
random/median representative or claim its old selection was metric-blind.

`VALIDATED_WITH_LIMITATION`. No figure was regenerated and no manuscript
caption was edited in this task.
