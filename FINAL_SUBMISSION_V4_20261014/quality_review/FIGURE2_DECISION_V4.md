# Figure 2 readability decision — final V4

The actual comparison uses the archived four-row V4 page 7 and the final revised three-row page 7. The page-level PDF and side-by-side PNG are `FIGURE2_FOUR_VS_FINAL_THREE_ACTUAL_PAGES_V4.pdf` and `.png`.

The three-row version is more readable. It keeps every required column—Target, Fixed Low, C3, Fixed High, and Generic Linear—at camera 000, with the same input, checkpoint, seed, output frame and crop within each object. It uses a shared full-object fit without per-method crop or color adjustment. All displayed source and output frame identities are hash-checked in the provenance manifest.

Rows are clearly labelled by how they were selected: Green Iguan is an input-property-selected illustration; Mosque and Specimen 103 are post-outcome positive and adverse C3−Fixed Low FG-PSNR examples. The caption states that these selected cases do not estimate prevalence or establish an overall advantage. Target is the source RGB conditioning render, not physical albedo. The third row's adverse evidence remains visible in the main figure; the removed Lipno median example remains documented in the four-row comparison and provenance record.

The four-row page preserves an additional GT-only median example but uses side annotations that reduce the image area. The three-row figure enlarges the method comparisons while keeping the adverse case and all five columns; no values or statistical queues were removed.
