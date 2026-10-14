# Figure 2 readability decision — V5

The actual page comparison places the archived four-row V4 figure page beside page 7 from the V5 main PDF. The comparison target is the figure layout and evidence content; surrounding text differs between the historical V4 and final V5 snapshots. See `FIGURE2_FOUR_VS_V5_THREE_ACTUAL_PAGES.pdf` and `.png`.

The V5 three-row version is more readable. It retains every required column—Target, Fixed Low, C3, Fixed High, and Generic Linear—at camera 000, from the same inputs, checkpoint, seed and full-frame view within each object. No method-specific crop or color edit is used. Target is the source RGB conditioning render, not physical albedo. The frozen panel identities and camera hashes are retained in `visual_candidates/FIGURE2_SELECTION_SOURCE_V4.json`; row-level checks are summarized in `FIGURE2_VALIDATION_V5.json`.

The input-property-selected Green Iguan provides a source-selected example. Mosque and Specimen 103 remain explicitly labeled as post-outcome positive and adverse C3−Fixed Low FG-PSNR examples. The caption says the selected cases do not estimate prevalence or establish an overall advantage. The third row preserves adverse evidence. The removed GT-only median row remains in the historical four-row page and provenance record; no cohort, statistic or selection queue changed.
