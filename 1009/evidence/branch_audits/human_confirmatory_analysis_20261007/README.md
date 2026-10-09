# Human confirmatory endpoint audit (2026-10-07)

## Source and disposition

- Archived source branch: `codex/human-confirmatory-analysis-20261007`
- Archived HEAD: `86292c8b5822533e52a1621cc04e6c076dbdc153`
- Source response-export commit used for the aggregate analysis: `f5bad8a1e6ca4265c1823eaa26b2775313de4c96`
- Frozen pair-lock SHA-256: `8aa4ebc88cccda50705709d67f1ff0070236f4d3948242071785ce29ad9fb6ce`
- Original endpoint analyzer SHA-256: `b9274c7a9d7800dec3211ac4d85cef7bde00cf88ed6df290a14690ed36f95f49`
- Source endpoint CSV SHA-256: `f32e99e2ae00388caaa3bc7c8bad1fd313efa18b3a53e95e0d6aae15b15974b5`
- Source aggregate provenance SHA-256: `754d540f7616ed17e420fc758070665a85b9920c1f80026de85489d30637844b`
- Classification: `CONFIRMATORY_HUMAN_PREFERENCE_ANALYSIS_WITH_DOCUMENTED_EXECUTION_DEVIATIONS`
- Branch decision: `SELECTIVE_CONTENT_MERGE`; `FULL_MERGE_REJECTED`.

The four-comparator/two-question endpoint family and analysis were locked before response collection. The study owner assigned the confirmatory classification on 2026-10-07, after the response-export commit. The classification therefore applies to the pre-specified endpoints and does not claim that every execution requirement was followed.

## Findings and limits

The export represents 40 slots; 37 participants passed the frozen completion and comprehension rules (2 comprehension failures and 1 incomplete or missing response). Each of the eight endpoints contains 24 equally weighted objects and 222 valid judgments. All eight point estimates favor LLH, but none survives Holm correction. The largest unadjusted signals are GFL texture (0.647; 95% CI [0.528, 0.755], raw p=0.0123, Holm p=0.0984) and GC3 texture (0.632; 95% CI [0.521, 0.741], raw p=0.0183, Holm p=0.1281). These results establish no LLH preference advantage, equivalence, or non-inferiority.

The prior private-key schedule audit recorded 0/40 matches to the same slot and 0/40 matches to any frozen slot pattern. The endpoint analyzer included here marks that audit unavailable and does not read a private key. Left/right orientation is fixed within all 96 object-by-comparison cells, although aggregate orientation is balanced 12/12 for each comparator. The export omits question order, randomization seed, raw comprehension answers, and a frozen-stimulus hash crosswalk. Coordinator closeout and ethics/consent documentation were not supplied. The results concern relative judgments on fixed 2D stimuli; they do not establish absolute material fidelity, unseen-view quality, baked 3D quality, seams, or full PBR quality.

`PUBLIC_RAW_HUMAN_DATA=NO`. Participant-level response, assignment, object-map, and pair-map files are not included here. The source rows are read in memory by the reproducer from the archived Git object and are never written or printed; its outputs are aggregate CSV/JSON and an aggregate forest plot. The reproducer does not inspect a coordinator key. Running it requires the source commit object to remain available locally. The included provenance records only source hashes, counts, design checks, and aggregate endpoint values.

The included reproducer is adapted from the analyzer whose source hash is recorded above: its optional private-key file probe was removed, repository-root/output-directory options were added, and CSV line endings were normalized to LF. With the key absent, the adapted script regenerated the endpoint CSV and provenance JSON byte-for-byte.

## Reproduction

Run from this checkout with Python, NumPy, and (optionally) Matplotlib available:

```bash
python analyze_confirmatory_human_study_20261007.py \
  --output-dir /tmp/human-confirmatory-reproduction
```

The default source commit is fixed in the script. The output directory receives only the endpoint aggregate CSV, aggregate provenance JSON, and (when Matplotlib is installed) the forest plot. No participant-level source file is materialized.

The reassessment and pair-lock files are preserved as source snapshots; references inside them to `1006/` or `final/` paths identify their original branch locations. The old 2026-10-06 report remains a historical classification snapshot and is superseded by the 2026-10-07 override and reassessment.

No active 1008 TeX, response, figure, or submission-package file was changed. Consent/ethics and participant-data governance remain open; do not use these results as a positive human-preference claim or submit them to the journal without resolving those gates.
