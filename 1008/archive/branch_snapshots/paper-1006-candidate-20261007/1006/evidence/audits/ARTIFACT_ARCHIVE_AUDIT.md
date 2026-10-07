# Full evidence artifact archive audit — 2026-10-05

The frozen roots listed in `FULL_ARTIFACT_MANIFEST.json` were archived outside
normal Git history. The archive is stored at
`/4T/CXY/MV-Painter_artifacts/scientific_validation_v3_20261005/formal-evidence.tar.zst`.

- Included files: 50,844; symlinks: 0.
- Source file bytes: 10,312,781,213.
- Decompressed TAR bytes: 10,363,586,560.
- Compressed archive bytes: 8,270,677,942.
- SHA256: `0d1bbbcb57cee1c3c8162b29100440d93d314d5baa9182d3291f805ffb0bb61c`.
- `zstd -t` passed; the archive hash was recomputed and matched the recorded value.
- `FULL_ARTIFACT_SHA256SUMS.txt` contains exactly 50,844 file entries, matching
  the manifest file count; all 50,844 entries passed `sha256sum -c`.

The manifest excludes `.codex/`, `.trae/`, the human-study coordinator key,
model/checkpoint caches, and temporary clean-clone outputs. The archive does
not resolve the remaining scientific gates: the clean-clone A2 row-level
reproduction, human responses, and paper-wide table regeneration remain open.


## Separate clean-clone reproduction archive

The completed A2 `a_middle_W5` clean-clone output is kept separately from the
formal campaign archive at
`/4T/CXY/MV-Painter_artifacts/scientific_validation_v3_20261005/clean_clone_A2_a_middle_W5.tar.zst`.
Its SHA256 is
`fba63f5f01e94e4293e0ccd54d9330bbef526f5808e30f222b1b2217264fe729`
(109,603,212 bytes); `zstd -t` passed and all 605 packaged file hashes
passed. It contains the complete ledger, rebuilt CSV, run manifest, predictions,
residual logs, run metadata, and package checksums. It is an independent run
output on the same host, separate from the frozen formal evidence archive.
