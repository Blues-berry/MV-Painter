# Integrated figure provenance

The authoritative builder is `scripts/build_review_figures.py`. Figure 1 is a code-native vector schematic with separate reference and five-channel geometry paths; it contains no experimental thumbnail or AI-generated artwork. Injection sites are abstracted as UNet ResNet groups.

Figures 5–7 retain the originally selected Fresh C objects and source images. Only Figure 5 displays the frozen pixel ROI, identical across methods and enlarged below the context. Figures 6 and 7 use whole-object frames without duplicate detail rows. Each frame is the padded union of foreground extents across all conditions, shared across methods; aspect ratios are preserved. Display frames are recorded in `figures/INTEGRATED_DISPLAY_FRAMES.json`. The Fresh C CSV retains historical ROI coordinates for traceability even where no detail crop is displayed.

Figure 8 retains the first two rights-cleared bake objects at unseen camera 004. Its four columns are Source, GT-256 bake, Fixed Mean and Late-high. Figures S2–S8 retain all seven rights-cleared objects and all nine Source/GT/control images in balanced three-by-three matrices. One frame is derived from all nine images and applied identically, including when only four are shown in the main figure. No per-method crop, color correction or detail repair is applied.

Figure 9 retains the first two frozen native MV-Adapter inputs in the verified rights ledger, view 0. The main figure shows Target/Fixed Mean/Middle-high/Late-high; Figure S9 shows the target and all seven controls. Original backgrounds remain. These previously inspected illustrations are not independent confirmation. `MVA_VISUAL_SELECTION.json` records the rule and UIDs.

`REVIEW2_SOURCE_HASHES.json` binds every loaded image to SHA-256. Source/seed/checkpoint/ROI identities and refreshed output hashes remain in the Fresh C manifest. Original baked/video sources and credits are retained. PNG panels are embedded losslessly in PDFs; display resampling preserves aspect ratio but is not a new metric input. The inherited actual-output video remains unchanged. Figure selection and statistics were not changed to improve visual results.
