from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1];m=json.loads((r/'data/ENCODING_BRANCH_MATRIX.json').read_text())
assert m['status']=='COMPLETE_ENCODING_BRANCH_MATRIX' and len(m['rows'])==12 and m['g256_both_identity_pass']
for uid in m['objects']:
 rows=[x for x in m['rows'] if x['uid']==uid];assert len(rows)==6 and {x['condition'] for x in rows}==set(m['conditions'])
 assert len({x['source_rgba_sha256'] for x in rows})==len({x['conditioning_tensor_hash'] for x in rows})==1
 for size in [256,512]:
  same=[x for x in rows if x['geometry_size']==size];assert len(same)==3
  assert all(x['geometry_input_hash']==same[0]['geometry_input_hash'] and x['geometry_feature_hashes']==same[0]['geometry_feature_hashes'] for x in same)
 for x in rows:
  t=x['trace'];assert t['unet_calls']==50 and t['read_counts']==t['skip_counts']==[50]*9
  assert t['initial_latent']==rows[0]['trace']['initial_latent'] and t['rng_states']==rows[0]['trace']['rng_states'] and len(t['rng_states'])==50
  assert len(t['correction_shapes'])==9 and all(v[0]==2 for v in t['correction_shapes'].values())
  if x['branch_policy']!='both':assert t['max_negative_correction_norm']==[0.]*9
  p=r/'data/encoding_branch_grids'/f"{uid}_{x['condition']}.png";assert hashlib.sha256(p.read_bytes()).hexdigest()==x['output_sha256']
  with Image.open(p) as im:assert im.size==(1024,1536)
  if x['condition']=='g256_both':assert np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(r/'data/native_geometry_grids'/f'{uid}_native_unset.png')))
print('PASS: twelve full native grids, prior pixel controls, geometry-size coupling and negative-branch zero gates')
