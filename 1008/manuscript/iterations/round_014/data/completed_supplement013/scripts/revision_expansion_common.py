"""Lightweight frozen condition names and atomic evidence-file utilities."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'revision_expansion_20261010'
MVA_CONDITIONS=['native_default_1x','fixed_low_0p75','fixed_mean_0p83','budget_early16','budget_middle16','budget_late16','budget_linear_mean_0p83']
BAKE_CONDITIONS=['native_default_1x','native_gfl','native_gfh','budget_fixed_mean','native_gc3','budget_late16','gen_linear']
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()
def write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)
