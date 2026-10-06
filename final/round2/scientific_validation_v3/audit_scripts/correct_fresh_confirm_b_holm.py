#!/usr/bin/env python3
"""Apply the frozen B2 or cap/budget Holm family to paired-comparison JSONs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V3 = Path(__file__).resolve().parents[1]
RUN = V3 / "formal/campaign_FRESH_CONFIRM_B_20261005"
sys.path.insert(0, str(V3))
import analyze_v3  # noqa: E402

B2 = {
    "H3_LLH-HLL": "paired_layer_llh_minus_layer_hll.json",
    "H3_LLH-LLL": "paired_layer_llh_minus_a3_baseline.json",
}
HLL_LLL = {
    "HLL-LLL_exploratory": "paired_layer_hll_minus_a3_baseline_exploratory.json",
}
CAP = {
    "LLH-GFL": "paired_layer_llh_minus_native_gfl.json",
    "LLH-LFM-EXACT": "paired_layer_llh_minus_lfm_exact.json",
    "LLH-HLL": "paired_layer_llh_minus_layer_hll.json",
    "GFL-TGU-1.25": "paired_native_gfl_minus_true_global_1p25.json",
    "LFM-EXACT-TGU-1.675": "paired_lfm_exact_minus_true_global_1p675.json",
    "TGU-1.25-TGU-0.80": "paired_true_global_1p25_minus_true_global_0p80.json",
    "LLH-TGU-1.675": "paired_layer_llh_minus_true_global_1p675.json",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=("b2", "cap", "hll_lll_exploratory"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    registry = B2 if args.family == "b2" else HLL_LLL if args.family == "hll_lll_exploratory" else CAP
    metrics = ("fg_psnr", "fg_lpips")
    result = {
        "family": ("B2_H3_LLH_HLL_LLL" if args.family == "b2" else
                   "USER_DIRECTED_POSTUNBLIND_HLL_LLL_EXPLORATORY" if args.family == "hll_lll_exploratory" else
                   "B_CAP_BUDGET_DIAGNOSTICS"),
        "cohort": "FRESH_CONFIRM_B",
        "family_size": len(registry) * (2 if args.family in {"b2", "hll_lll_exploratory"} else 1),
        "alpha": 0.05,
        "holm_method": ("Holm-Bonferroni across the four prespecified B2 metric-contrast tests"
                        if args.family == "b2" else
                        "Holm-Bonferroni across the two endpoints for the exploratory HLL-LLL contrast"
                        if args.family == "hll_lll_exploratory" else
                        "Holm-Bonferroni applied separately to the seven cap/budget contrasts for each metric"),
        "p_floor_note": "Where an input p is at the 1/10,000 bootstrap reporting floor, its adjusted value is an upper bound based on that floor.",
    }
    raw: dict[str, float] = {}
    if args.family in {"b2", "hll_lll_exploratory"}:
        for contrast, filename in registry.items():
            path = RUN / filename
            if not path.is_file():
                raise SystemExit(f"missing paired analysis: {path}")
            data = json.loads(path.read_text())
            if data.get("n_objects") != 150:
                raise SystemExit(f"unexpected paired n in {path}")
            for metric in metrics:
                raw[f"{contrast}_{metric}"] = float(data["tests"][metric]["p_bootstrap"])
        adjusted = analyze_v3.holm(raw)
        result["tests"] = {
            key: {"p_raw_upper_bound": p,
                  "p_holm_upper_bound": adjusted[key],
                  "reject_holm_0.05": bool(adjusted[key] < 0.05)}
            for key, p in raw.items()
        }
    else:
        result["metrics"] = {}
        for metric in metrics:
            raw = {}
            for contrast, filename in registry.items():
                path = RUN / filename
                if not path.is_file():
                    raise SystemExit(f"missing paired analysis: {path}")
                data = json.loads(path.read_text())
                if data.get("n_objects") != 150:
                    raise SystemExit(f"unexpected paired n in {path}")
                raw[contrast] = float(data["tests"][metric]["p_bootstrap"])
            adjusted = analyze_v3.holm(raw)
            result["metrics"][metric] = {
                "tests": {
                    contrast: {
                        "p_raw_upper_bound": p,
                        "p_holm_upper_bound": adjusted[contrast],
                        "reject_holm_0.05": bool(adjusted[contrast] < 0.05),
                    }
                    for contrast, p in raw.items()
                }
            }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
