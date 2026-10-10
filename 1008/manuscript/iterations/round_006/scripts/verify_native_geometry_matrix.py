from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1]
m=json.loads((r/'data/NATIVE_GEOMETRY_MATRIX.json').read_text())
assert m['status']=='COMPLETE_NATIVE_GEOMETRY_MATRIX' and len(m['rows'])==16
assert m['disabled_identity_pass'] and m['within_object_latent_rng_match'] and m['all_wrapper_counts_pass']
for uid in m['objects']:
 rows=[x for x in m['rows'] if x['uid']==uid];assert len(rows)==8
 assert {x['condition'] for x in rows}==set(m['conditions'])
 for key in ['source_rgba_sha256','conditioning_tensor_hash','geometry_input_hash']:
  assert len({x[key] for x in rows})==1
 assert all(x['geometry_feature_hashes']==rows[0]['geometry_feature_hashes'] for x in rows)
 for x in rows:
  t=x['trace'];assert t['unet_calls']==50 and t['read_counts']==t['skip_counts']==[50]*9
  assert t['initial_latent']==rows[0]['trace']['initial_latent'] and t['rng_states']==rows[0]['trace']['rng_states'] and len(t['rng_states'])==50
  assert len(t['scales'])==50
  if x['condition']!='disabled':assert len(t['correction_shapes'])==9 and all(v[0]==2 for v in t['correction_shapes'].values())
  p=r/'data/native_geometry_grids'/f"{uid}_{x['condition']}.png"
  assert hashlib.sha256(p.read_bytes()).hexdigest()==x['output_sha256']
  with Image.open(p) as im:assert im.size==(1024,1536)
  if x['condition']=='disabled':
   assert np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(r/'data/native_grids'/f'{uid}_50.png')))
print('PASS: complete native matrix, nine wrapper read/write gates, fixed geometry/input/latent/RNG and pixel-identical native baseline')
