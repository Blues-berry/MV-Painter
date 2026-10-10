from pathlib import Path
import json,hashlib,numpy as np
r=Path(__file__).resolve().parents[1]/'data/native_camera_audit'
m=json.loads((r/'CAMERA_CONTRACT_AUDIT.json').read_text())
assert m['status']=='PASS_ALL_TEN_SLOT_DIRECTIONS_WITH_LIMITS' and len(m['objects'])==10
for name,h in m['official_sources'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==h
assert [m['native_grid_raw_indices'][i-1] for i in m['bake_result_permutation']]==list(range(6))
assert not m['pole_image_orientation_verified'] and not m['cross_renderer_projection_verified'] and not m['generated_camera_identities_verified']
for o in m['objects']:
 assert len(o['slots'])==6 and len({s['raw_view_index'] for s in o['slots']})==6
 for s in o['slots']:
  p=r/'camera_metadata'/o['uid']/f"{s['raw_view_index']:03d}.npy"
  assert hashlib.sha256(p.read_bytes()).hexdigest()==s['camera_file_sha256']
  c=np.load(p,allow_pickle=True).item()
  assert c['azimuth']==s['azimuth'] and c['elevation']==s['elevation'] and c['camera']==s['camera']=='ortho'
  assert c['elevation']==s['expected']['elevation']
  if abs(c['elevation'])!=90:assert (c['azimuth']-o['anchor_azimuth'])%360==s['expected']['relative_azimuth']
print('PASS: ten actual camera-metadata sets, official source hashes and nominal direction permutation; limits retained')
