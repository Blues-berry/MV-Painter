# GeoTex Code Structure (Final)

```
geotex/
├── __init__.py                 # Package marker
├── metrics.py                  # PSNR, SSIM, edge mask, latent scaling (87 lines)
├── data_utils.py               # Batch preparation, collation (60 lines)
├── vis_utils.py                # Comparison, error map visualization (37 lines)
├── train.py                    # Training entry point (231 lines)
├── eval.py                     # Evaluation with region metrics + LPIPS (442 lines)
├── audit.py                    # Sanity, leakage, range checks (209 lines)
├── analyze_300obj.py           # 300-object result analysis (317 lines)
├── make_comparison_figures.py  # Visual comparison figures (220 lines)
├── make_paper_figures.py       # Bar charts, scatter, histograms (216 lines)
└── mv_consistency.py           # Multi-view consistency (220 lines)

MVPainter/mvpainter/
└── model_unet_geotex.py        # GeoEncoder, GeoTexAdapter, MVDiffusionGeoTex

MVPainter/configs/
└── mvpainter-geotex-full-train.yaml

mvpoutput/geotex/
├── checkpoints/                # step_500, step_1000, step_1500, step_2000
├── eval_300obj_region/         # 300-object formal evaluation
│   ├── per_object_metrics.csv
│   ├── region_metrics.csv
│   ├── summary_metrics.json
│   ├── region_summary.json
│   ├── geotex_300obj_final_report.md
│   ├── result_claim_audit.md
│   ├── paper_figures/
│   ├── comparison_figures/
│   └── mv_consistency/
├── baselines/checkpoint_progression/
├── refactor/
├── autorun_10h/
├── geotex_stage1_fix_report.md
└── conversation_summary.md
```

## Entry Points

| Script | Purpose | Key Args |
|--------|---------|----------|
| `train.py` | Train adapter | --config, --steps, --save_every, --device |
| `eval.py` | Evaluate with regions | --config, --checkpoint, --num_objects, --save_vis |
| `audit.py` | Credibility checks | --config, --check all |
| `analyze_300obj.py` | Formal report | --input_dir |
| `make_comparison_figures.py` | Visual figures | --config, --checkpoint, --input_dir |
| `make_paper_figures.py` | Metric figures | --input_dir |
| `mv_consistency.py` | Cross-view metrics | --config, --checkpoint, --num_objects |
