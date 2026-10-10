"""Check all frozen evaluation target slots against actual camera metadata."""
import json,numpy as np
from pathlib import Path
from revision_expansion_common import OUT,sha,write
r=OUT/'iteration009_native_checkpoint_evaluation';f=json.loads((r/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());previous=OUT/'iteration006_camera_protocol_audit/CAMERA_CONTRACT_AUDIT.json';official=json.loads(previous.read_text());expected=official['native_grid_directions'];rows=[]
for obj in f['rows']:
 root=Path(obj['source_path']).parents[1];anchor_id=int(Path(obj['source_path']).stem);assert anchor_id in [0,14];ids=[0,15,12,16,13,14] if anchor_id==0 else [14,15,0,16,12,13];cameras={i:np.load(root/'camera'/f'{i:03d}.npy',allow_pickle=True).item() for i in ids};anchor=float(cameras[anchor_id]['azimuth']);slots=[]
 for slot,(i,e) in enumerate(zip(ids,expected)):
  c=cameras[i];elev=float(c['elevation']);az=float(c['azimuth']);relative=(az-anchor)%360;assert abs(elev-e['elevation'])<1e-6 and (abs(elev)==90 or abs(relative-e['relative_azimuth'])<1e-6)
  slots.append({'slot':slot,'raw_view_index':i,'relative_azimuth':relative,'elevation':elev,'camera_file_sha256':sha(root/'camera'/f'{i:03d}.npy'),'pole_rotation_ccw_90':i in [15,16],'nominal_direction_matches':True})
 rows.append({'uid':obj['uid'],'anchor_azimuth':anchor,'slots':slots})
write(r/'CAMERA_SLOT_AUDIT.json',{'status':'PASS_FIFTY_NOMINAL_TARGET_CAMERA_ORDERS','objects':rows,'official_source_audit_sha256':sha(previous),'expected_grid_directions':expected,'dataset_source_sha256':sha('/4T/CXY/MV-Painter/MVPainter/src/data/mvpainter_dataset.py'),'limitations':'Nominal direction contract only; does not prove projection equivalence, pole roll or actual generated camera fidelity. Metrics evaluate declared target slots, and wrong generated views are errors rather than excluded objects.'});print('PASS50 actual target-camera direction mappings; projection and pole-roll limits retained')
