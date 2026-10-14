# Figure 2 readability decision — V5

The actual page comparison places the archived four-row V4 figure page beside page 7 from the V5 main PDF. The comparison target is the figure layout and evidence content; surrounding text differs between the historical V4 and final V5 snapshots. See `FIGURE2_FOUR_VS_V5_THREE_ACTUAL_PAGES.pdf` and `.png`.

The V5 three-row version is more readable. It retains every required column—Target, Fixed Low, C3, Fixed High, and Generic Linear—at camera 000, from the same inputs, checkpoint, seed and full-frame view within each object. No method-specific crop or color edit is used. Target is the source RGB conditioning render, not physical albedo. The active panel identities and camera hashes are recorded in `visual_candidates/VISUAL_SELECTION_MANIFEST_V5_PUBLIC.csv`; row-level checks are summarized in `FIGURE2_VALIDATION_V5.json`.

The three rows show Green Iguan, Building 03 and Specimen 103. Building 03 and Specimen 103 illustrate positive and adverse C3−Fixed Low FG-PSNR endpoints, respectively; the third row preserves adverse evidence. The caption limits the examples to endpoint heterogeneity and says they do not estimate prevalence or establish an overall advantage. The removed GT-only median row remains in the historical four-row page and provenance record; the cohort and analysis statistics are unchanged.
