"""Verify delivered complete grids and logged execution invariants."""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'data/NATIVE_BASE_DIAGNOSTIC.json').read_text())
assert r['status']=='COMPLETE_NATIVE_BASE_DIAGNOSTIC' and len(r['outputs'])==4
old={x['object_uid']:x for x in json.loads((ROOT/'data/PREVIOUS_CONTROL_INPUTS.json').read_text())}
for uid in r['objects']:
 rows=[x for x in r['outputs'] if x['uid']==uid];assert len(rows)==2
 assert rows[0]['initial_latent']==rows[1]['initial_latent']
 for row in rows:
  assert row['unet_calls']==row['steps'] and row['batch_sizes']==[2]
  assert row['conditioning_tensor_sha256']==old[uid]['input_hashes']['cond']
  p=ROOT/'data/native_grids'/f"{uid}_{row['steps']}.png"
  assert hashlib.sha256(p.read_bytes()).hexdigest()==row['output_sha256']
  with Image.open(p) as im:assert im.size==(1024,1536)
print('PASS: four complete native grids, execution observations and prior conditioning identities')
