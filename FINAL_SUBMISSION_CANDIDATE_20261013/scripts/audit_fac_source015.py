"""Freeze recovered FAC code and exercise the controller without base weights."""
import ast
from argparse import ArgumentParser
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil

import torch

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"fac_code_snapshot"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recover():
    base=Path("/4T/CXY/MV-Painter")
    earlier=Path("/4T/CXY/MV-Painter-1010")
    mapping={}
    # Preserve original bytes and distinguish entry points; never repair them
    # in place or represent an unbound recovered source as an executed run.
    for name in ["train_fac.py","eval_fac_300.py","eval_fac_ablation.py"]:
        mapping[earlier/"geotex"/name]=ARCHIVE/"earlier_entry/geotex"/name
    for name in ["train_fac_v2.py","train_v2.py","eval_fac_v2.py","inspect_fac_ckpt.py","metrics.py","data_utils.py","eval_unified_300.py"]:
        mapping[base/"geotex"/name]=ARCHIVE/"controller_only_entry/geotex"/name
    for root,target in [(earlier,ARCHIVE/"earlier_entry"),(base,ARCHIVE/"controller_only_entry")]:
        for sub in ["MVPainter/mvpainter","MVPainter/src"]:
            for path in (root/sub).rglob("*.py"):
                mapping[path]=target/path.relative_to(root)
        path=root/"MVPainter/configs/mvpainter-geotex-fac-train.yaml"
        mapping[path]=target/path.relative_to(root)
        for name in ["requirements.txt","LICENSE"]:
            path=root/"MVPainter"/name
            if path.is_file():mapping[path]=target/path.relative_to(root)
    records=[]
    for source,target in mapping.items():
        assert source.is_file(),source
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        assert sha(source)==sha(target)
        if target.suffix==".py":ast.parse(target.read_text())
        records.append({"source":str(source),"path":str(target.relative_to(ARCHIVE)),"sha256":sha(target),"run_bound_identity":False})
    return records


def exercise(path):
    spec=importlib.util.spec_from_file_location("recovered_fac_fixture",path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    results=[]
    for flags in [(True,False,False),(True,True,False),(True,True,True)]:
        torch.manual_seed(20261012)
        ctrl=mod.AdaptiveCorrectionController(num_adapters=9,geo_channels=64,enable_ltag=flags[0],enable_gsg=flags[1],enable_fsc=flags[2])
        correction=torch.randn(1,4,16,16);geo=torch.randn(1,64,16,16)
        ctrl.set_timestep(torch.tensor(500.0))
        # A shallow cap of .8 saturates the initialized LTAG and correctly
        # removes its gradient. Use the deep cap for a gradient-path fixture.
        output=ctrl.apply(correction,geo,adapter_idx=0,max_scale=3.0)
        assert output.shape==correction.shape and torch.isfinite(output).all()
        output.square().mean().backward()
        assert all(torch.isfinite(p.grad).all() for p in ctrl.parameters() if p.grad is not None)
        used=[n for n,p in ctrl.named_parameters() if p.grad is not None]
        nonzero=[n for n,p in ctrl.named_parameters() if p.grad is not None and bool((p.grad!=0).any())]
        assert used and nonzero
        stream=io.BytesIO();torch.save(ctrl.state_dict(),stream);stream.seek(0)
        clone=mod.AdaptiveCorrectionController(num_adapters=9,geo_channels=64,enable_ltag=flags[0],enable_gsg=flags[1],enable_fsc=flags[2])
        clone.load_state_dict(torch.load(stream,weights_only=True));clone.set_timestep(torch.tensor(500.0))
        assert torch.equal(output,clone.apply(correction,geo,adapter_idx=0,max_scale=3.0))
        extra={}
        if ctrl.gsg_modules is not None:
            assert torch.equal(ctrl.gsg_modules[0](geo),torch.ones(1,1,16,16))
            extra["initial_spatial_gate"]="EXACT_UNIT_GATE"
        if ctrl.fsc_modules is not None:
            filtered=ctrl.fsc_modules[0](correction)
            extra["initial_filter_relative_L2_change"]=float((filtered-correction).norm()/correction.norm())
            extra["actual_transform"]="torch.fft.rfft2/irfft2; not DCT despite archival comments"
        results.append({"enabled":dict(zip(["LTAG","GSG","FSC"],flags)),"fixture":"CPU float32, nine adapters, one exercised adapter, 16x16 correction and 64-channel geometry","parameters":ctrl.param_count(),"finite_output_and_gradients":True,"state_roundtrip_bitwise_equal":True,"parameters_with_gradients":used,"parameters_with_nonzero_gradients":nonzero,**extra})
    return results


def main():
    parser=ArgumentParser()
    parser.add_argument("--snapshot-only",action="store_true",help="Use delivered source bytes, without original server paths")
    args=parser.parse_args()
    if args.snapshot_only:
        records=json.loads((ARCHIVE/"SOURCE_AND_COMPONENT_AUDIT.json").read_text())["files"]
        for r in records:
            path=ARCHIVE/r["path"]
            assert sha(path)==r["sha256"],r["path"]
            if path.suffix==".py":ast.parse(path.read_text())
    else:
        records=recover()
    older=(ARCHIVE/"earlier_entry/geotex/train_fac.py").read_text()
    newer=(ARCHIVE/"controller_only_entry/geotex/train_fac_v2.py").read_text()
    assert "if not args.freeze_adapter:" in older and "model.geo_encoder.parameters()" in older
    assert "model.adapters.requires_grad_(False)" in newer and "model.geo_encoder.requires_grad_(False)" in newer
    assert "trainable_params = [p for p in model.correction_controller.parameters() if p.requires_grad]" in newer
    results={}
    unique={}
    for name in ["earlier_entry","controller_only_entry"]:
        path=ARCHIVE/name/"MVPainter/mvpainter/adaptive_correction.py"
        digest=sha(path)
        if digest not in unique:unique[digest]=exercise(path)
        results[name]=unique[digest]
    audit={"status":"PASS_RECOVERED_SOURCE_SYNTAX_AND_STANDALONE_CONTROLLER_CHECKS","files":records,"tests":results,
           "unique_controller_source_versions":len(unique),"unique_controller_fixtures":sum(len(v) for v in unique.values()),
           "entry_differences":{"earlier_entry":"Default permits base-adapter and geometry-encoder optimization; --freeze_adapter is needed to restrict this entry to controller parameters.","controller_only_entry":"Freezes loaded base adapter and geometry encoder; optimizer uses controller parameters. Warm-start, freeze-LTAG and envelope options differ from earlier entry."},
           "not_verified":["Historical executed source/CLI identity","1706-object historical list and its relation to recovered 1200-object config","Historical random seed and optimizer/sampling trajectory","Historical FAC checkpoint and full-model evaluation identity","Fresh full-model training/inference in an isolated environment"],
           "release_scope":"Recoverable source and tested controller components only, not a complete historical FAC replay or a new method."}
    (ARCHIVE/"SOURCE_AND_COMPONENT_AUDIT.json").write_text(json.dumps(audit,indent=2)+"\n")
    (ROOT/"data/gap_closure015/FAC_COMPONENT_VALIDATION.json").write_text(json.dumps({k:v for k,v in audit.items() if k!="files"},indent=2)+"\n")
    print(json.dumps({"status":audit["status"],"files":len(records),"variants":{k:[v['parameters'] for v in vals] for k,vals in results.items()}},indent=2))


if __name__=="__main__":
    main()
