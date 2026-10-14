# V4 package build verification

The four PDFs in this package are the frozen V4 artifacts. All four were rebuilt from the packaged TeX and support files before finalization; page counts and `pdftotext -layout` content matched the frozen V4 files exactly. The rebuild changes only PDF creation/modification timestamps, so the frozen originals were retained to preserve their canonical SHA-256 identities.

The package manifest records those final SHA-256 values. Rebuilding is available through the scripts in the package README; a fresh PDF build is text- and page-identical but has a new timestamp and therefore a different byte hash.
