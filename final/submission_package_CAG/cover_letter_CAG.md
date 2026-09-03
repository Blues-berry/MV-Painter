# Cover Letter

Dear Editor,

We would like to submit our manuscript entitled "Adapter Scaling Trade-off and Timestep-Conditioned Scheduling in Multi-view Diffusion Texture Generation" for consideration for publication in *Computers & Graphics*, as part of the Virtual Special Issue CAG_SS_CAD/Graphics 2026. **This work is recommended by CAD/Graphics 2026** (upon revision, Paper 75).

In this manuscript, we study a fine-grained inference-time control problem in geometry-controlled multi-view diffusion texturing: how strongly, and at which denoising stages, a geometric adapter should act. We first show that a uniform adapter scale is a blunt control — aggressive uniform scales improve structural metrics such as FG-SSIM but suppress the texture synthesis capability of the base model, causing surface flattening and loss of high-frequency detail. We then formalize the effect with a measurable Correction–Alignment–Interference (CAI) stage-utility model and derive Timestep-Conditioned Adapter Scaling (TCAS), a training-free low–high–low schedule that concentrates geometric correction in the middle denoising stage. The selected schedule C3 = (1.25, 2.50, 1.25) is chosen only on a 24-object probe set and transferred unchanged to a 300-object validation set without re-search, where it matches the structure of aggressive scaling while improving PSNR by 0.96 dB, retaining substantially more texture, and receiving the highest overall preference (58.1%) in a blinded human study with cluster-aware significance analysis. To the best of our knowledge, no prior work analyzes the shape–texture trade-off of adapter scaling or derives a timestep-conditioned schedule from measurable stage utilities; the closest prior art (MVPainter, arXiv 2025; MV-Adapter, arXiv 2024; ControlNet, ICCV 2023; classifier-free guidance scheduling, NeurIPS Workshop 2022) is cited and compared explicitly in Sections 2 and 4.7 of the manuscript.

This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission and declare no competing interests.

Thank you very much for your attention and consideration.

Sincerely,

Xueyuan Che (School of Instrument Science and Engineering, Southeast University)

Libo Sun (Corresponding author, School of Instrument Science and Engineering, Southeast University, Nanjing 210096, China; sunlibo@seu.edu.cn)
