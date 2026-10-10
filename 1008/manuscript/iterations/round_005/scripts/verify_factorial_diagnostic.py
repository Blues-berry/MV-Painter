"""Verify complete grids and source-coupling gates from delivered evidence."""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'data/GUIDANCE_EMBEDDING_FACTORIAL.json').read_text());assert m['status']=='COMPLETE_FACTORIAL_DIAGNOSTIC'
assert len(m['rows'])==8 and m['cached_off_pixels_identical'] and m['all_positive_rng_trajectories_match']
for uid in m['objects']:
 rows=[x for x in m['rows'] if x['uid']==uid];assert len(rows)==4
 assert set(x['condition'] for x in rows)==set(m['conditions'])
 for x in rows:
  assert x['positive_rng_states']==rows[0]['positive_rng_states'] and len(x['positive_rng_states'])==50
  assert x['cond_hash']==rows[0]['cond_hash'] and x['initial_latent_hash']==rows[0]['initial_latent_hash']
  assert x['negative_calls']==(50 if x['condition'].endswith('cfg2') else 0)
  p=ROOT/'data/factorial_grids'/f"{uid}_{x['condition']}.png"
  assert hashlib.sha256(p.read_bytes()).hexdigest()==x['output_sha256']
  with Image.open(p) as im:assert im.size==(512,768)
print('PASS: all eight complete grids, coupled positive RNG, inputs, latents and call counts')
