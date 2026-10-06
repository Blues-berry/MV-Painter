# Asset attribution and redistribution status

The visual supplement uses 24 Objaverse 1.0 / Sketchfab objects. Their panel
IDs, UIDs, titles, creators, model links, Objaverse license slugs, and current
API checks are recorded in `objaverse_visual_cohort_attribution.csv` and in
`manuscript/objaverse_attribution_table.tex`.

- 22/24 records were corroborated by current Sketchfab API metadata on
  2026-10-06.
- Panel 02's current API response contains no license field. The stored
  Objaverse metadata says `by`, while the stored model description refers to
  personal-project use. The applicable redistribution terms are unresolved.
- Panel 05's model endpoint returns 404. The Objaverse metadata snapshot says
  `by`, but a current source record could not be checked.
- A direct official API recheck at 08:58 UTC on 2026-10-06 returned HTTP 200
  with an empty `license` object for Panel 02 and HTTP 404 for Panel 05. The
  response dates and body hashes are preserved in
  `ASSET_SOURCE_LICENSE_RECHECK_20261006.json`; the readable audit is in
  `../evidence/audits/ASSET_SOURCE_LICENSE_RECHECK_20261006.md`.
- Panel 06 is listed as CC BY-SA 4.0 and requires its attribution and
  ShareAlike terms to be respected for any adaptation.
- No source meshes are included. The contact sheets and compiled supplement
  do contain model-derived rendered imagery.

Do not describe the two snapshot-only entries as fully cleared for public
redistribution. Before a final public or journal package is released, either
confirm their source terms/authorization or remove the affected derivative
images and rebuild the supplement. Attribution is necessary but does not
resolve an inconsistent or missing source license.

The dataset-level Objaverse metadata license does not replace each source
asset's individual license. See the [Objaverse 1.0 API and metadata
documentation](https://objaverse.allenai.org/docs/objaverse-1.0/) and
[Sketchfab's Creative Commons license explanation](https://www.sketchfab.com/blogs/community/an-introduction-to-creative-commons-licenses/).
