# Asset rights and redistribution disposition — 2026-10-07

**Candidate-figure rights: `CLOSED_WITH_EXCLUSIONS`. Public release: `FAIL`.**

The preserved [`FINAL_ASSET_RIGHTS_AND_REDISTRIBUTION_LEDGER.csv`](FINAL_ASSET_RIGHTS_AND_REDISTRIBUTION_LEDGER.csv) was not overwritten. It still covers the earlier Fresh C 24-GLB panel and legacy visual 24-asset panel (48 rows: 43 `FIGURE_ONLY`, 5 `UNKNOWN`). Those legacy assets are not inputs to the current Figure A–G candidates; the 5 unknown assets are excluded from the release scope.

## Current candidate figure scope

- Figure D is the only current candidate figure made from model-derived imagery. Its 20 frozen atlas assets were rechecked against the current Sketchfab metadata API: 20/20 returned HTTP 200 with CC BY, matching the source queue tags.
- [`FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`](FRESH_C_ATLAS_ATTRIBUTION_20261007.csv) contains one credit row per panel, source/model URL, creator, license link, API response hash, and downloaded asset hash. Figure D is eligible only with these attributions attached. The source GLBs themselves are not included.
- Figures A–C and E/G are schematics or metric plots and do not reproduce source model imagery.
- [`FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv`](FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv) records all 300 cohort UIDs. The disposition is 20 `FIGURE_ONLY`, 271 `METRICS_ONLY`, and 9 `UNKNOWN`. The 9 unknown rows do not appear in Figure D; neither their GLBs nor derived images enter the candidate package. UID-linked per-object tables are also excluded from the proposed public package; aggregate endpoint results may remain.
- The metadata sweep stopped at 180/300 checks after HTTP 429 and 401 responses: 166 HTTP 200, 8 HTTP 404, 1 HTTP 401, 5 HTTP 429, and 120 not rechecked. Unchecked non-atlas rows retain their source-snapshot license tag and are not treated as permission to redistribute the source model. The 20 atlas items have their own complete current API check.
- Download dates were not captured in the source manifest and remain `NOT_RECORDED_IN_SOURCE_MANIFEST`.

## Release boundary

The current figure scope is closed with the exclusions above and the Figure D credit schedule. No source GLB package is cleared. The 300-row inventory is an audit record, not a release manifest. The public package remains `FAIL` because no compact committed candidate has passed a clean-checkout rebuild and participant-level human files remain in public repository history; this disposition did not inspect human answers or rewrite history.
