# Source-license endpoint recheck — 2026-10-06

At 08:58:49–08:58:50 UTC, the official Sketchfab model API was queried
directly for the two visual-panel assets whose attribution is only supported
by the Objaverse snapshot. Request details, selected response fields, HTTP
dates, and response-body SHA-256 digests are recorded in
`1006/licenses/ASSET_SOURCE_LICENSE_RECHECK_20261006.json`.

| Panel | Model | API result | Disposition |
|---|---|---|---|
| 02 | `001cfadfb9204424bccc45501ce6b90e` (“Cart Texture”, johnguataquira) | HTTP 200; `license` is `{}` | Current API metadata does not confirm a license. Keep rights unresolved. |
| 05 | `00820c449b8c4c84b3ae58d3d168ca7b` | HTTP 404 | Source record is unavailable; rights cannot be confirmed. |

This recheck does not grant or infer permission. Before a public artifact or
submission package is treated as cleared, obtain source-level terms or
authorization for both assets. If that is not possible, remove the affected
images and every derivative, including contact sheets and compiled PDFs, then
rebuild and re-audit the package. The current public branch remains a review
snapshot with an open rights gate.
