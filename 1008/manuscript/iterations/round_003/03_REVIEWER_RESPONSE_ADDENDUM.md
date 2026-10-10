# Round 003 reviewer-response addendum

R1.1 — Full-path quality diagnostic. We now execute the complete native base pipeline on the two previously displayed failure objects, without GeoTex, at 50 and 75 steps. All four calls complete; actual UNet calls and two-member CFG batches are logged, and paired initial latents match. Source correspondence is checked against the previous conditioning hashes. Complete grids retain visible imperfections, while their front-looking views preserve reference colors/details that were lost in the controlled generator.

The native API requires RGBA, and its preprocessing mutates some bright foreground pixels. The initial RGB attempt failed before generation and is retained. The valid rerun uses the same original single-reference RGBA sources. The native pipeline differs in resolution, feature computation, guidance and scheduler; camera equivalence is unverified. We therefore do not compute cross-protocol paired GT metrics or attribute the difference to one cause. These are two seen failure cases, not independent quality confirmation or complete GeoTex deployment validation.

R1.4 — Evidence scope. No inferential tests are added for the qualitative diagnostic. All prior paired results and their multiplicity families remain unchanged. The inverse image-scaling formulas are algebraically equivalent, so we do not claim a decoding bug from their names.

R2.1 — Priority and limitation. The low-cost diagnostic changes the next action: separate the sampling differences before attempting another schedule or developing a new algorithm. It does not establish algorithmic novelty, overall material fidelity or a calibrated acceptance probability.
