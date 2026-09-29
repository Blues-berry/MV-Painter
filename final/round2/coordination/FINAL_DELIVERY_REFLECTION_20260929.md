# Final delivery reflection

Date: 2026-09-29 UTC

## Four-stage completion

### Stage 1 — evidence closure

Completed. The claim matrix, strict-276 protocol audit, fixed-GT SSIM
decomposition and bounded TRB gate are recorded. The optional repeat/order
perturbation inference was not run; because the final paper makes no exact
repeatability or order-invariance claim, this is documented as a limitation
rather than silently presented as passed evidence.

### Stage 2 — targeted evidence

Completed with limitations. The MV-Adapter 76-object package, full-object
visual panels, 12-object baking case study, 48 GLBs and 528 unseen-view rows
are frozen. They support bounded transfer/feasibility statements, not
cross-backbone benefit transfer or population-level 3D superiority.

### Stage 3 — revision integration

Completed. Results are separated by protocol surface; the abstract and
conclusion use bounded method language; Supplementary S7 and R2.5 document the
negative TRB pilot; historical unsupported claims remain inactive.

### Stage 4 — delivery QA

Completed for the author-review build. The manuscript and supplement compile
to 10 and 3 pages, respectively. Key pages were rendered and visually checked;
the abstract, strict-276 table, cross-backbone table, conclusion and S7 show no
missing or clipped content. Key response numbers match the frozen evidence.

## What worked

- Separating evidence closure from prose editing prevented the old LHL story
  from being preserved by inertia.
- The strict TRB development gate converted a promising but uncontrolled pilot
  into a defensible negative result and prevented an unnecessary holdout run.
- Treating the MV-Adapter and baking packages as bounded audits answered R1/R2
  without requiring unsupported claims of universal transfer.
- Running GPU work outside the sandbox avoided a false hardware blocker.

## What should be improved next time

- The execution status files were updated asynchronously and temporarily
  reported a completed pilot as pending; a single run-state manifest should be
  authoritative from the start.
- The initial pilot launch used the wrong working directory and a mismatched
  environment. A preflight should validate dependency imports and relative
  checkpoint paths before background launch.
- The original plan mixed mandatory evidence gates with optional determinism
  checks. Future plans should label these separately and avoid implying that an
  unrun optional test passed.
- The expert-review document should receive an explicit post-edit addendum
  whenever the manuscript changes after review.

## Final scientific reflection

The revision does not establish TCAS as a universally superior schedule or
CAI as a transferable selector. It does establish a concrete, training-free
stage intervention, measurable adapter-dependent trade-offs, a second-backbone
boundary audit, and an honest 3D feasibility/failure case study. The negative
TRB result strengthens the scope of the paper by showing that adding an
input-conditioned controller is not automatically an improvement.

The package is ready for author review, not automatic submission. Submission
and venue acceptance remain author decisions.
