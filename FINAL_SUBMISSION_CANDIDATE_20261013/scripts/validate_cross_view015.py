"""Replay the recorded UV-overlap diagnostic and test known-color controls."""
from argparse import Namespace, ArgumentParser
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/gap_closure015"
CODE = OUT / "bake_source_snapshot"


def load_baker():
    sys.path.insert(0,str(CODE))
    spec=importlib.util.spec_from_file_location("recorded_baker015",CODE/"bake_fresh_c_native_uv.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.bpy is None, "Replay must use the original Trimesh backend"
    return module


def hashfile(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def replay(job):
    record, methods, expected, controls = job
    module=load_baker()
    module.load_scene(Path(record["exact_glb_path"]))
    geometry=module.normalize_geometry(module.extract_geometry(record,0),record)
    cache={}
    for item in record["target_view_mapping"]:
        raw=int(item["raw_view_index"])
        cache[raw,256,256]=module.rasterize(geometry,record["camera_poses_17"][raw],256,256)
    args=Namespace(texture_resolution=1024,gt_source_resolution=256,inpaint_iterations=8,repeat_uv=True)
    results=[]
    for method in methods:
        baked=module.bake_texture(record,geometry,method,args,cache)
        value=baked["cross_view_texel_variance"]
        prior=float(expected[record["uid"],method])
        assert np.isfinite(value) and np.isclose(value,prior,rtol=0,atol=2e-10), (record["uid"],method,value,prior)
        results.append({"uid":record["uid"],"method":method,"cross_view_texel_variance":value,"prior":prior,"absolute_replay_error":abs(value-prior)})
    calibration=[]
    if controls:
        original=module.image_for_record
        # Independent shared-texel incidence for camera-constant RGB controls.
        hits=[]
        for slot,item in enumerate(record["target_view_mapping"]):
            raw=int(item["raw_view_index"])
            _,mask=original(record,"gt",slot,raw,bool(item["rotated_ccw_90"]),256)
            total=np.zeros((1024,1024,3),np.float32);weight=np.zeros((1024,1024),np.float32)
            view_sum=np.zeros_like(total);view_weight=np.zeros_like(weight)
            module.splat_view(total,weight,view_sum,view_weight,geometry,cache[raw,256,256],np.ones((256,256,3),np.float32),mask,1024,repeat_uv=True)
            hits.append(view_weight>1e-8)
        hits=np.stack(hits);count=hits.sum(0);multi=count>1
        assert multi.any()
        colors=np.arange(6,dtype=np.float64)/5
        mean=(hits*colors[:,None,None]).sum(0)[multi]/count[multi]
        analytic=((hits*colors[:,None,None]**2).sum(0)[multi]/count[multi]-mean**2).mean()
        for name in ["constant_black_all_views","different_camera_gray"]:
            def controlled(rec,method,slot,raw,rotated,gt_source_resolution=0):
                image,mask=original(rec,"gt",slot,raw,rotated,256)
                value=0.0 if name=="constant_black_all_views" else slot/5
                return np.full_like(image,value),mask
            module.image_for_record=controlled
            try:
                value=module.bake_texture(record,geometry,"gt",args,cache)["cross_view_texel_variance"]
            finally:
                module.image_for_record=original
            wanted=0.0 if name=="constant_black_all_views" else float(analytic)
            assert abs(value-wanted)<2e-7, (record["uid"],name,value,wanted)
            if name=="different_camera_gray":assert value>1e-5
            calibration.append({"uid":record["uid"],"control":name,"actual_variance":value,"independent_expected":wanted,"shared_texels":int(multi.sum()),"atlas_texels":int(multi.size),"shared_fraction":float(multi.mean()),"formula_error":abs(value-wanted)})
    output={"uid":record["uid"],"status":"PASS_REPLAY_AND_REQUESTED_CONTROLS","rows":results,"controls":calibration}
    (OUT/"cross_view_objects"/f"{record['uid']}.json").write_text(json.dumps(output,indent=2)+"\n")
    return output


def main():
    parser=ArgumentParser();parser.add_argument("--workers",type=int,default=2);args=parser.parse_args()
    handoff_path=OUT/"BAKE_INPUT_HANDOFF_V3.json"
    handoff=json.loads(handoff_path.read_text())
    with (ROOT/"data/primary_studies/BAKE10_OBJECT_METRICS.csv").open() as stream: prior=list(csv.DictReader(stream))
    methods=["gt",*handoff["conditions"]]
    expected={(r["object_uid"],r["method"]):float(r["cross_view_texel_variance"]) for r in prior}
    assert len(expected)==80 and len(handoff["objects"])==10 and len(methods)==8
    input_hashes={str(handoff_path.relative_to(ROOT)):hashfile(handoff_path)}
    for record in handoff["objects"]:
        assert hashfile(record["exact_glb_path"])==record["exact_glb_sha256"]
        for path_key,hash_key in [("gt_rgba_17","gt_rgba_sha256_17"),("foreground_masks_17","foreground_mask_sha256_17"),("camera_pose_files_17","camera_pose_sha256_17")]:
            for path,expected_sha in zip(record[path_key],record[hash_key],strict=True):
                assert hashfile(path)==expected_sha,path
                input_hashes[path]=expected_sha
        for method in handoff["conditions"]:
            for item in record["generated_conditions"][method]["target_views"]:
                assert hashfile(item["path"])==item["sha256"],item["path"]
                input_hashes[item["path"]]=item["sha256"]
    frozen={"plan_sha256":hashfile(ROOT/"00_PLAN.md"),"handoff_sha256":hashfile(handoff_path),"source_sha256":{p.name:hashfile(p) for p in CODE.glob("*.py")},"input_sha256":input_hashes,"methods":methods,"uids":[r["uid"] for r in handoff["objects"]],"control_rule":"First two input-order objects; zero gray shared across cameras and six known camera-specific gray levels. No method-result selection.","frozen_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (OUT/"CROSS_VIEW_PROTOCOL_FREEZE.json").write_text(json.dumps(frozen,indent=2)+"\n")
    (OUT/"cross_view_objects").mkdir(exist_ok=True)
    jobs=[(r,methods,expected,i<2) for i,r in enumerate(handoff["objects"])]
    outputs=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        future={pool.submit(replay,job):job[0]["uid"] for job in jobs}
        for done in as_completed(future):
            result=done.result();outputs.append(result)
            print('REPLAY_PASS',result["uid"],len(outputs),'of',len(jobs),flush=True)
    rows=[row for obj in outputs for row in obj["rows"]]
    with (OUT/"CROSS_VIEW_REPLAY.csv").open("w") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(sorted(rows,key=lambda r:(r["uid"],r["method"])))
    summary={"status":"PASS_80_REPLAY_ROWS_AND_FOUR_KNOWN_COLOR_CONTROLS","objects":10,"methods":methods,"max_absolute_replay_error":max(r["absolute_replay_error"] for r in rows),"controls":[c for o in sorted(outputs,key=lambda o:o["uid"]) for c in o["controls"]],"interpretation":"Pre-bake cross-view disagreement only at UV texels receiving at least two cameras. Natural texture, resampling, UV overlap and view-dependent source appearance can contribute. Constant incorrect color has zero variance; this is not fidelity, seam or PBR validation."}
    (OUT/"CROSS_VIEW_VALIDATION.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)


if __name__ == "__main__":
    main()
