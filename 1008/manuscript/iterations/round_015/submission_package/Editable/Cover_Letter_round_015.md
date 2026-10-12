Dear Editor,

Please consider our revised manuscript, **Timestep-Conditioned Adapter Scaling for Multi-view Diffusion Texture Generation: A Controlled Empirical Study**, for the Virtual Special Issue CAG_SS_CAD/Graphics 2026. This continues the same manuscript submitted on 7 September 2026; the title now states its empirical scope. A point-by-point response and a marked copy against that authenticated submission are provided.

The paper addresses a practical graphics question: when does allocating geometry-control strength across denoising stages improve generated views and the appearance of the final textured mesh? The revision adds strong fixed/linear comparisons, matched applied-scale budgets, native conditioning-interface checks and actual exported-mesh evaluation. The 300-object GeoTex comparison changes the preferred image-space setting. A ten-object bake finds a small late-allocation benefit; a separate twenty-object GSO study does not detect the same benefit. Native MV-Adapter primaries do not establish a middle-window advantage. New post-inspection seed summaries distinguish group-average effects from objectwise repeatability. Known-color controls verify the shared-UV incoming-view disagreement diagnostic and demonstrate why consistency alone does not imply fidelity. These limits and visible appearance failures remain in the paper.

The closest prior work includes Shao et al., *MVPainter* (arXiv:2505.12635, 2025); Huang et al., *MV-Adapter* (ICCV, 2025); and Kulkarni, *Scheduled Style Injection* (CVPR Workshops/NTIRE, 2026). We acknowledge existing layer/time strength schedules. Our contribution is their controlled evaluation in this texturing task, including competitive controls, implemented scale accounting and downstream application limits; we do not claim a new general scheduling principle or universally optimal C3. Sadat et al.'s adaptive projected guidance (ICLR, 2025) is also included in the separate external comparison.

CAI's independent derivation and optimality claims have been removed. Historical results are distinguished from new checkpoints and protocols; the original +0.96 dB estimate is not called reproduced. Recovered FAC code is now supplied with source-entry differences and independently runnable controller checks; historical full-model training identity remains incomplete. The materials provide reproducible object-level statistics, editable sources, attributed real outputs and playable mesh-comparison videos. The original CAD/Graphics conference submission is retained as a separate historical attachment.

Thank you for considering the revised evidence and its application implications.

Sincerely,
The Authors
