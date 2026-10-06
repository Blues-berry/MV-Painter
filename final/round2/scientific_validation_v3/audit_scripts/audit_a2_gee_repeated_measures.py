#!/usr/bin/env python3
"""Independent object-clustered repeated-measures model for the A2 3x5 map."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
RAW = V3 / "formal/campaign_A2/per_object_metrics.csv"
OUT = V3 / "audit_scripts/AUDIT_A2_GEE_REPEATED_MEASURES.json"


def main() -> None:
    df = pd.read_csv(RAW)
    baseline = df[df.condition == "a_baseline"].set_index("object_uid")
    cells = df[df.condition != "a_baseline"].copy()
    parts = cells.condition.str.extract(r"^a_(deep|middle|shallow)_W([1-5])$")
    cells["layer"] = parts[0]
    cells["window"] = "W" + parts[1]
    for metric in ("fg_lpips", "fg_psnr"):
        cells[f"delta_{metric}"] = [
            float(row[metric]) - float(baseline.loc[row["object_uid"], metric])
            for _, row in cells.iterrows()
        ]

    output = {
        "source": str(RAW.relative_to(ROOT)),
        "n_objects": int(cells.object_uid.nunique()),
        "observations_per_metric": int(len(cells)),
        "model": "Gaussian GEE; delta=cell-baseline; fixed C(layer)*C(window); object_uid clusters; exchangeable working correlation; robust sandwich covariance",
        "results": {},
        "cell_means_delta": {},
    }
    for metric in ("fg_lpips", "fg_psnr"):
        formula = f"delta_{metric} ~ C(layer) * C(window)"
        fit = smf.gee(formula, groups="object_uid", data=cells,
                      cov_struct=sm.cov_struct.Exchangeable(),
                      family=sm.families.Gaussian()).fit()
        names = list(fit.model.exog_names)
        idx = [i for i, name in enumerate(names) if ":" in name]
        r = np.eye(len(names))[idx]
        test = fit.wald_test(r, scalar=True)
        output["results"][metric] = {
            "formula": formula,
            "interaction_df": len(idx),
            "interaction_wald_chi2": float(test.statistic),
            "interaction_p": float(test.pvalue),
            "converged": bool(fit.converged),
            "working_correlation": "exchangeable (robust sandwich covariance)",
        }
        output["cell_means_delta"][metric] = {
            f"{layer}_{window}": float(group[f"delta_{metric}"].mean())
            for (layer, window), group in cells.groupby(["layer", "window"], sort=True)
        }

    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["results"], indent=2))


if __name__ == "__main__":
    main()
