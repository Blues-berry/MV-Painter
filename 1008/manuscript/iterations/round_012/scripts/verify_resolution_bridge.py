from pathlib import Path
import json,hashlib
from PIL import Image
r=Path(__file__).resolve().parents[1]
m=json.loads((r/'data/TARGET_RESOLUTION_BRIDGE.json').read_text())
assert m['status']=='COMPLETE_RESOLUTION_BRIDGE' and len(m['rows'])==8
assert m['r256_pixels_identical_to_round004'] and m['within_resolution_positive_rng_matches']
for uid in m['objects']:
 rows=[x for x in m['rows'] if x['uid']==uid]
 assert len(rows)==4 and {x['condition'] for x in rows}==set(m['conditions'])
 assert len({x['cond_hash'] for x in rows})==len({x['global_embedding_hash'] for x in rows})==1
 for size in [256,512]:
  pair=[x for x in rows if x['target_view_resolution']==size];assert len(pair)==2
  assert pair[0]['initial_latent_hash']==pair[1]['initial_latent_hash']
  assert pair[0]['positive_rng_states']==pair[1]['positive_rng_states']
  for x in pair:
   assert x['reference_view_resolution']==256 and len(x['positive_rng_states'])==50
   assert x['negative_calls']==(50 if x['condition'].endswith('cfg2') else 0)
   p=r/'data/resolution_grids'/f"{uid}_{x['condition']}.png"
   assert hashlib.sha256(p.read_bytes()).hexdigest()==x['output_sha256']
   with Image.open(p) as im:assert im.size==(size*2,size*3)
   if size==256:
    prior=r/'data/factorial_grids'/f"{uid}_online_{'cfg2' if x['condition'].endswith('cfg2') else 'off'}.png"
    import numpy as np
    assert np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(prior)))
print('PASS: eight complete grids, fixed reference/features, within-resolution RNG coupling and exact prior controls')
