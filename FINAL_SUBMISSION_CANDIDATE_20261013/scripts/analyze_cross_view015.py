"""Report all recorded UV-overlap disagreements after the replay gate passes."""
import csv
import itertools
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/gap_closure015"
LABELS={"native_default_1x":"Constant 1.0 (capped)","native_gfl":"Fixed Low","native_gfh":"Fixed High","budget_fixed_mean":"Fixed Mean","native_gc3":"C3 / Middle-high","budget_late16":"Late-high","gen_linear":"Generic Linear","gt":"GT-256"}


def main():
    gate=json.loads((OUT/"CROSS_VIEW_VALIDATION.json").read_text())
    assert gate["status"]=="PASS_80_REPLAY_ROWS_AND_FOUR_KNOWN_COLOR_CONTROLS"
    with (OUT/"CROSS_VIEW_REPLAY.csv").open() as stream:rows=list(csv.DictReader(stream))
    with (ROOT/"data/primary_studies/BAKE10_OBJECT_METRICS.csv").open() as stream:source=list(csv.DictReader(stream))
    table={(r["uid"],r["method"]):float(r["cross_view_texel_variance"]) for r in rows}
    btable={(r["object_uid"],r["method"]):r for r in source}
    uids=sorted({r["uid"] for r in rows});assert len(uids)==10 and len(table)==80
    methods=list(LABELS);generated=[m for m in methods if m!="gt"]
    means={m:{"cross_view_variance":float(np.mean([table[u,m] for u in uids])),"fg_lpips":float(np.mean([float(btable[u,m]["fg_lpips"]) for u in uids]))} for m in methods}
    signs=np.array(list(itertools.product([-1,1],repeat=10)))
    contrasts=[]
    rng=np.random.default_rng(20261012);indices=rng.integers(0,10,(20000,10))
    for a,b in itertools.combinations(generated,2):
        delta=np.array([table[u,a]-table[u,b] for u in uids])
        p=float((abs((signs*delta).mean(1))>=abs(delta.mean())-1e-12).mean())
        contrasts.append({"a":a,"b":b,"metric":"cross_view_texel_variance","mean_difference":float(delta.mean()),"ci95_descriptive":np.percentile(delta[indices].mean(1),[2.5,97.5]).tolist(),"a_lower_objects":int((delta<0).sum()),"exact_signflip_p":p})
    last=0
    for i,r in enumerate(sorted(contrasts,key=lambda r:r["exact_signflip_p"])):
        last=max(last,min(1,(len(contrasts)-i)*r["exact_signflip_p"]));r["holm21_p"]=last
    result={"status":"COMPLETE_POST_INSPECTION_DIAGNOSTIC","objects":10,"means":means,"contrasts":contrasts,"scope":"All 21 generated-condition pairs on one additional diagnostic, Holm21. Pointwise descriptive object intervals. No confirmatory practical benefit or artifact-free calibration claim."}
    (OUT/"CROSS_VIEW_DIAGNOSTICS.json").write_text(json.dumps(result,indent=2)+"\n")
    lines=[f"{LABELS[m]} & {means[m]['cross_view_variance']:.6f} & {means[m]['fg_lpips']:.5f} \\\\" for m in methods]
    (ROOT/"tables/cross_view_diagnostic015.tex").write_text("\n".join(lines)+"\n")
    lines=[f"{LABELS[r['a']]} -- {LABELS[r['b']]} & ${r['mean_difference']:+.6f}$ & $[{r['ci95_descriptive'][0]:+.6f},{r['ci95_descriptive'][1]:+.6f}]$ & {r['holm21_p']:.5f} \\\\" for r in contrasts]
    (ROOT/"tables/cross_view_contrasts015.tex").write_text("\n".join(lines)+"\n")
    print(json.dumps({"means":means,"named":[r for r in contrasts if {r['a'],r['b']}=={'budget_late16','budget_fixed_mean'}]},indent=2))


if __name__=="__main__":
    main()
