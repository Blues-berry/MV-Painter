"""Recompute performance summaries and verify real PNGs against stored quality outputs."""
import argparse,json,hashlib,numpy as np
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();r=a.root;protocol=json.loads((r/'PROTOCOL_FREEZE.json').read_text());result=json.loads((r/'BENCHMARK_ANALYSIS.json').read_text());assert result['status']=='COMPLETE_PIXEL_IDENTICAL_CROSSOVER_BENCHMARK';assert result['timed_calls']==60 and result['warmup_calls']==8;seen=set();allrows=[]
for summary in result['summaries']:
 phase,method,device=summary['phase'],summary['method'],summary['device'];assert protocol['phases'][str(phase)][device]==method;key=(method,device);assert key not in seen;seen.add(key)
 paths=[p for p in r.glob(f'phase{phase}_{method}_{device.replace(":","_")}*') if (p/'RUN_IDENTITY.json').exists() and json.loads((p/'RUN_IDENTITY.json').read_text())['status']=='COMPLETE_PIXEL_IDENTICAL_DEPLOYMENT_BENCHMARK'];assert len(paths)==1;run=paths[0];identity=json.loads((run/'RUN_IDENTITY.json').read_text());rows=identity['rows'];assert rows==json.loads((run/'ROWS.json').read_text());assert len(rows)==17 and sum(x['warmup'] for x in rows)==2;timed=[x for x in rows if not x['warmup']];assert {(x['uid'],x['repeat']) for x in timed}=={(u,i) for u in protocol['uids'] for i in range(3)}
 for x in rows:assert x['seconds']>0 and x['pixel_sha256']==x['expected_pixel_sha256'] and 0<x['baseline_allocated_bytes']<=x['peak_allocated_bytes']<=x['peak_reserved_bytes']
 assert summary['median_seconds']==float(np.median([x['seconds'] for x in timed]));assert summary['peak_allocated_bytes']==max(x['peak_allocated_bytes'] for x in timed);assert summary['peak_reserved_bytes']==max(x['peak_reserved_bytes'] for x in timed)
 for uid in protocol['uids']:
  assert summary['object_median_seconds'][uid]==float(np.median([x['seconds'] for x in timed if x['uid']==uid]));pixel=hashlib.sha256(np.asarray(Image.open(run/f'{uid}.png').convert('RGB')).tobytes()).hexdigest();assert pixel==next(x['expected_pixel_sha256'] for x in timed if x['uid']==uid)
 allrows.extend(timed)
assert len(seen)==4 and len(allrows)==60
for device,ratios in result['full_over_geometry_object_latency_ratios'].items():
 g=next(x for x in result['summaries'] if x['method']=='geometry' and x['device']==device);f=next(x for x in result['summaries'] if x['method']=='full_v29' and x['device']==device)
 for uid in protocol['uids']:assert ratios[uid]==f['object_median_seconds'][uid]/g['object_median_seconds'][uid]
print('PASS60 timed calls,8 warmups,5 objects, GPU crossover, all summaries and20 real PNG pixel identities; GPU execution not rerun')
