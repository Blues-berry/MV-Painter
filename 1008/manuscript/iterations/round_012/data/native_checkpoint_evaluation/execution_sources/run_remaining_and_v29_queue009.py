"""Use each free GPU sequentially for frozen remaining conditions and v29 baseline."""
import argparse,subprocess,sys,json,os
from pathlib import Path
from revision_expansion_common import OUT,sha,write
p=argparse.ArgumentParser();p.add_argument('--rank',type=int,choices=[0,1],required=True);a=p.parse_args();here=Path(__file__).resolve().parent;root=here.parents[1];r=OUT/'iteration009_native_checkpoint_evaluation';status=r/f'REMAINING_QUEUE_RANK{a.rank}.json';assert not status.exists();write(status,{'status':'RUNNING_FROZEN_REMAINING_GEOTEX_CONDITIONS','rank':a.rank,'pid':os.getpid(),'source_sha256':sha(Path(__file__))});(r/f'execution_remaining_queue_rank{a.rank}.py').write_bytes(Path(__file__).read_bytes())
try:
 with (r/f'remaining_geotex_rank{a.rank}.log').open('w') as log:subprocess.run([sys.executable,str(here/'run_native_checkpoint_matrix009.py'),'--rank',str(a.rank),'--device',f'cuda:{a.rank}','--conditions','native_gfl,native_gfh,native_gc3,gen_linear'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 write(status,{'status':'RUNNING_FROZEN_V29_FULL_BASELINE','rank':a.rank,'pid':os.getpid()})
 with (r/f'v29_fresh50_rank{a.rank}.log').open('w') as log:subprocess.run([sys.executable,str(here/'run_v29_native_probe009.py'),'--rank',str(a.rank),'--device',f'cuda:{a.rank}','--cohort',str(r/'objects.txt')],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 write(status,{'status':'COMPLETE_FROZEN_REMAINING_AND_V29_RANK','rank':a.rank,'pid':os.getpid()})
except Exception as exc:write(status,{'status':'FAILED_FROZEN_REMAINING_OR_V29_RANK','rank':a.rank,'pid':os.getpid(),'error':f'{type(exc).__name__}: {exc}'});raise
