"""Wait for verified live phase0, run GPU crossover, then summarize recorded deployment cost."""
import json,os,time,subprocess,sys,numpy as np
from pathlib import Path
from revision_expansion_common import OUT,write,sha
here=Path(__file__).resolve().parent;r=OUT/'iteration011_deployment_performance';status=r/'SUPERVISOR.json'
def live():
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:a=[x.decode() for x in p.read_bytes().split(b'\0') if x]
  except (OSError,UnicodeDecodeError):continue
  if a and Path(a[0]).name.startswith('python') and any(Path(x).name=='benchmark_native_deployment011.py' for x in a[1:]):return True
 return False
def complete(run):
 p=run/'RUN_IDENTITY.json'
 if not p.exists():return False
 d=json.loads(p.read_text());assert not d['status'].startswith('FAILED'),d.get('error');return d['status']=='COMPLETE_PIXEL_IDENTICAL_DEPLOYMENT_BENCHMARK'
try:
 write(status,{'status':'WAITING_LIVE_PHASE0','pid':os.getpid()})
 runs=[r/'phase0_geometry_cuda_0',r/'phase0_full_v29_cuda_1_attempt02']
 while not all(complete(x) for x in runs):assert live(),'Benchmark not live and incomplete; no automatic retry';time.sleep(2)
 children=[];handles=[];write(status,{'status':'GPU_CROSSOVER_PHASE1','pid':os.getpid()})
 for method,device in [('full_v29','cuda:0'),('geometry','cuda:1')]:
  h=(r/f'phase1_{method}.log').open('w');handles.append(h);children.append(subprocess.Popen([sys.executable,str(here/'benchmark_native_deployment011.py'),'--method',method,'--device',device,'--phase','1'],cwd=here.parents[1],stdout=h,stderr=subprocess.STDOUT));runs.append(r/f'phase1_{method}_{device.replace(":","_")}')
 for child in children:assert child.wait()==0,'Benchmark failed; no automatic retry'
 for h in handles:h.close()
 assert all(complete(x) for x in runs);items=[json.loads((x/'RUN_IDENTITY.json').read_text()) for x in runs];uids=json.loads((r/'PROTOCOL_FREEZE.json').read_text())['uids'];summaries=[];medians={}
 for d in items:
  rows=[x for x in d['rows'] if not x['warmup']];assert len(rows)==15 and all(x['pixel_sha256']==x['expected_pixel_sha256'] for x in d['rows']);values=np.array([x['seconds'] for x in rows]);obj={u:float(np.median([x['seconds'] for x in rows if x['uid']==u])) for u in uids};medians[(d['method'],d['device'])]=obj;summaries.append({'method':d['method'],'device':d['device'],'phase':d['phase'],'timed_calls':15,'warmups':2,'median_seconds':float(np.median(values)),'min_seconds':float(values.min()),'max_seconds':float(values.max()),'peak_allocated_bytes':max(x['peak_allocated_bytes'] for x in rows),'peak_reserved_bytes':max(x['peak_reserved_bytes'] for x in rows),'object_median_seconds':obj,'denoiser_geometry_parameter_count':d['denoiser_geometry_parameter_count']})
 ratios={device:{u:medians[('full_v29',device)][u]/medians[('geometry',device)][u] for u in uids} for device in ['cuda:0','cuda:1']};result={'status':'COMPLETE_PIXEL_IDENTICAL_CROSSOVER_BENCHMARK','summaries':summaries,'full_over_geometry_object_latency_ratios':ratios,'object_count':5,'timed_calls':60,'warmup_calls':8,'protocol_sha256':sha(r/'PROTOCOL_FREEZE.json'),'scope':'warmed synchronous deployment latency on preloaded inputs; model load, disk IO and CPU geometry conversion excluded; quality tradeoff remains from previously studied50 objects','statistics':'descriptive; repeats are not independent object samples; no throughput/energy/whole-app speed claim'};write(r/'BENCHMARK_ANALYSIS.json',result);write(status,{'status':'COMPLETE_CROSSOVER_BENCHMARK_ANALYSIS','pid':os.getpid(),'analysis_sha256':sha(r/'BENCHMARK_ANALYSIS.json')})
except Exception as exc:write(status,{'status':'FAILED_NO_AUTOMATIC_RETRY','error':f'{type(exc).__name__}: {exc}','pid':os.getpid()});raise
