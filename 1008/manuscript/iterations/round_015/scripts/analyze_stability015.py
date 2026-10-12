"""Post-inspection, object-level stability summaries; no new hypothesis tests."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/gap_closure015"
SEEDS = [42, 2026, 31415]


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def interval(values, seed=20261012):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    return np.percentile(values[rng.integers(0, len(values), (20000, len(values)))].mean(1), [2.5, 97.5]).tolist()


def aggregate(records, conditions, metric, nonreference=False):
    cells = {}
    for row in records:
        if row["condition"] not in conditions or (nonreference and row["role"] != "nonreference"):
            continue
        key = (row["uid"], int(row["seed"]), row["condition"])
        cells.setdefault(key, []).append(float(row[metric]))
    expected = 5 if nonreference else (11 if "role" not in records[0] else 6)
    assert all(len(v) == expected for v in cells.values()), (metric, expected)
    return {k: float(np.mean(v)) for k, v in cells.items()}


def main():
    OUT.mkdir(exist_ok=True)
    sources = [ROOT/"data/final_supplement_audit013/ALL_GSO100_VIEW_METRICS.csv", ROOT/"data/completed_supplement013/analysis/BAKE_VIEW_METRICS.csv", ROOT/"data/primary_studies/MATCHED300_OBJECT_METRICS.csv"]
    image, bake, fresh = [rows(p) for p in sources]
    assert len(image) == 21600 and len(bake) == 8140
    all_uids = json.loads((ROOT/"data/GSO100_UID_ORDER.json").read_text())
    jobs = [
        ("GSO100 Middle--Mean PSNR", image, all_uids, "middle_high", "fixed_mean", "fg_psnr", False),
        ("GSO100 Late--Mean PSNR", image, all_uids, "late_high", "fixed_mean", "fg_psnr", False),
        ("GSO100 Late--Mean nonreference LPIPS", image, all_uids, "late_high", "fixed_mean", "fg_lpips", True),
        ("GSO20 Late--Mean unseen LPIPS", bake, all_uids[:20], "late_high", "fixed_mean", "fg_lpips", False),
    ]
    contrasts, detailed = [], []
    for label, records, uids, a, b, metric, nonreference in jobs:
        cells = aggregate(records, [a, b], metric, nonreference)
        assert len(cells) == len(uids)*3*2
        delta = np.array([[cells[u,s,a]-cells[u,s,b] for s in SEEDS] for u in uids])
        direction = 1 if metric == "fg_psnr" else -1
        oriented = delta*direction
        favorable = (oriented > 0).all(1)
        adverse = (oriented < 0).all(1)
        summary = {"label":label,"a":a,"b":b,"metric":metric,"objects":len(uids),
                   "seed_order":SEEDS,"per_seed":[{"seed":s,"mean":float(delta[:,i].mean()),"ci95_descriptive":interval(delta[:,i]),"favorable_objects":int((oriented[:,i]>0).sum())} for i,s in enumerate(SEEDS)],
                   "seed_averaged_mean":float(delta.mean()),"all_three_favorable":int(favorable.sum()),"all_three_adverse":int(adverse.sum()),
                   "mixed_or_tied":int((~(favorable|adverse)).sum()),"all_three_favorable_proportion_ci95":interval(favorable),
                   "interpretation":"Fixed seeds; object-resampled descriptive intervals. Sign agreement has no practical-effect threshold. No new significance/equivalence claim."}
        contrasts.append(summary)
        for i,u in enumerate(uids):
            detailed.append({"study":label,"uid":u,**{f"delta_seed_{s}":float(delta[i,j]) for j,s in enumerate(SEEDS)},"all_three_favorable":bool(favorable[i]),"all_three_adverse":bool(adverse[i])})
    ftable={(r["object_uid"],r["condition"]):r for r in fresh}
    uids=sorted({r["object_uid"] for r in fresh});assert len(uids)==300 and len(ftable)==1800
    conditions=["Fixed Low","Fixed High","Fixed Applied Mean","Early-high","Late-high"]
    metrics=["fg_psnr","fg_lpips","fg_ssim","edge_ssim"]
    orientations=np.array([1,-1,1,1])
    dominance, dominators = [], []
    for c in conditions:
        d=np.array([[float(ftable[u,c][m])-float(ftable[u,"Middle-high"][m]) for m in metrics] for u in uids])*orientations
        dominates=(d>=0).all(1)&(d>0).any(1)
        c3dominates=(d<=0).all(1)&(d<0).any(1)
        dominators.append(dominates)
        dominance.append({"control":c,"dominates_C3":int(dominates.sum()),"dominated_by_C3":int(c3dominates.sum()),"incomparable_or_equal":int((~(dominates|c3dominates)).sum()),"dominates_C3_proportion_ci95":interval(dominates)})
    any_dom=np.stack(dominators).any(0)
    result={"status":"COMPLETE_DESCRIPTIVE_POST_INSPECTION_ANALYSIS","source_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "seed_contrasts":contrasts,"freshC_dominance":{"objects":300,"endpoints":metrics,"conditions":conditions,"rules":"Point-estimate weak dominance on all four recorded composite endpoints and strict improvement on at least one; no dominance of unmeasured quality and no inferential separation.","comparisons":dominance,"dominated_by_at_least_one":int(any_dom.sum()),"proportion_ci95":interval(any_dom)}}
    (OUT/"STABILITY_AND_DOMINANCE.json").write_text(json.dumps(result,indent=2)+"\n")
    with (OUT/"SEED_OBJECT_DELTAS.csv").open("w") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(detailed[0]));writer.writeheader();writer.writerows(detailed)
    with (OUT/"FRESH_C_DOMINANCE.csv").open("w") as stream:
        writer=csv.DictWriter(stream,fieldnames=["uid",*conditions,"dominated_by_any"]);writer.writeheader()
        for i,u in enumerate(uids):writer.writerow({"uid":u,**{c:bool(dominators[j][i]) for j,c in enumerate(conditions)},"dominated_by_any":bool(any_dom[i])})
    table=[]
    for r in contrasts:
        values=[f"{x['mean']:+.5f}" if r["metric"]=="fg_psnr" else f"{x['mean']:+.6f}" for x in r["per_seed"]]
        table.append(f"{r['label']} & {' & '.join(values)} & {r['all_three_favorable']}/{r['objects']} & {r['all_three_adverse']}/{r['objects']} \\\\")
    (ROOT/"tables/seed_stability015.tex").write_text("\n".join(table)+"\n")
    table=[f"{r['control']} & {r['dominates_C3']} & {r['dominated_by_C3']} & {r['incomparable_or_equal']} \\\\" for r in dominance]
    (ROOT/"tables/dominance015.tex").write_text("\n".join(table)+"\n")
    fig,axes=plt.subplots(2,2,figsize=(10,6.5))
    for ax,r in zip(axes.flat,contrasts):
        scale=1 if r["metric"]=="fg_psnr" else 1000
        for i,s in enumerate(r["per_seed"]):
            mean=s["mean"]*scale;lo,hi=np.array(s["ci95_descriptive"])*scale
            ax.errorbar(mean,i,xerr=[[mean-lo],[hi-mean]],fmt="o",color="#2e607c",capsize=3)
        ax.axvline(0,color="#777",linestyle="--",linewidth=1)
        ax.set_yticks(range(3),SEEDS);ax.set_ylabel("Fixed sampling seed")
        ax.set_title(r["label"].replace("nonreference ","nonref. "),fontsize=10)
        ax.set_xlabel("Paired difference (dB)" if scale==1 else "Paired LPIPS difference × 1,000")
        ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Fixed-seed sensitivity: pointwise 95% object intervals",fontsize=13)
    fig.tight_layout()
    for ext in ["pdf","png"]:fig.savefig(ROOT/"figures"/f"fig_seed_stability015.{ext}",dpi=160)
    plt.close(fig)
    print(json.dumps({"seed_contrasts":contrasts,"freshC_dominance":result["freshC_dominance"]},indent=2))


if __name__ == "__main__":
    main()
