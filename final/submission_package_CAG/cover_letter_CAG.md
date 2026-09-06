# Cover Letter

Dear Editor,

We would like to submit our manuscript entitled "Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation" for consideration for publication in *Computers & Graphics*, as part of the Virtual Special Issue CAG_SS_CAD/Graphics 2026. **This work is recommended by CAD/Graphics 2026** (upon revision, Paper 75). In accordance with the journal's guidelines for extended versions of conference papers, a copy of the original conference paper (Paper 75) is attached as supplementary material, and the manuscript explicitly states the extensions relative to it.

In this manuscript, we study a fine-grained inference-time control problem in geometry-controlled multi-view diffusion texturing: how strongly, and at which denoising stages, a geometric adapter should act. We first show that a uniform adapter scale is a blunt control — aggressive uniform scales improve structural metrics such as FG-SSIM but suppress the texture synthesis capability of the base model, causing surface flattening and loss of high-frequency detail. We then formalize the effect with a measurable Correction–Alignment–Interference (CAI) stage-utility model and derive Timestep-Conditioned Adapter Scaling (TCAS), a training-free low–high–low schedule that concentrates geometric correction in the middle denoising stage. The schedule C3 = (1.25, 2.50, 1.25) is selected using only a 24-object probe set and then evaluated unchanged, without further search, on the strictly disjoint 276-object holdout (pooled 300-object statistics also reported), where it matches the structure of aggressive scaling while improving PSNR by 0.96 dB, retaining substantially more texture, and receiving the highest overall preference (58.1%) in a blinded human study with cluster-aware significance analysis. To the best of our knowledge, no prior work analyzes the shape–texture trade-off of adapter scaling or derives a timestep-conditioned schedule from measurable stage utilities; the closest prior art (MVPainter, arXiv 2025; MV-Adapter, arXiv 2024; ControlNet, ICCV 2023; limited-interval classifier-free guidance, NeurIPS 2024) is cited and compared explicitly in Sections 2.3 and 4.4 of the manuscript.

Thank you very much for your attention and consideration.

Sincerely,

The Authors

(Per the journal's double-anonymized review policy, this cover letter contains no author details; author names, affiliations, and the corresponding author's contact information are provided on the separately uploaded title page and in Editorial Manager.)
