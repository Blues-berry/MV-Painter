#!/usr/bin/env python3
"""Recheck Sketchfab metadata only for the frozen 20-group Fresh C atlas."""
from __future__ import annotations
import csv, hashlib, json, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'1006/figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json').read_text())
with (ROOT/'1006/data/fresh_c/candidate_screen_queue.csv').open(newline='') as f:
    queue={r['uid']:r for r in csv.DictReader(f)}
records=[]
for item in manifest['selected_groups']:
    uid=item['object_uid']
    url=f'https://api.sketchfab.com/v3/models/{uid}'
    rec={'uid':uid,'api_url':url,'checked_utc':datetime.now(timezone.utc).isoformat(),
         'snapshot_license_tag':queue.get(uid,{}).get('source_license_tag',''),'http_status':None,
         'api_license':None,'creator_username':None,'response_sha256':None,'error':None}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'MV-Painter asset-rights metadata audit/1.0'})
        with urllib.request.urlopen(req,timeout=20) as res:
            body=res.read(); rec['http_status']=res.status; rec['response_sha256']=hashlib.sha256(body).hexdigest()
        data=json.loads(body)
        rec['api_license']=data.get('license')
        rec['creator_username']=data.get('user',{}).get('username')
        rec['name']=data.get('name')
    except urllib.error.HTTPError as e:
        body=e.read(); rec['http_status']=e.code; rec['response_sha256']=hashlib.sha256(body).hexdigest(); rec['error']=f'HTTP {e.code}'
    except Exception as e:
        rec['error']=f'{type(e).__name__}: {e}'
    records.append(rec)
    time.sleep(0.12)
result={'status':'COMPLETE' if all(x['http_status']==200 and x['api_license'] for x in records) else 'PARTIAL',
        'scope':'20 frozen rank-stratum figure groups only; metadata GET, no model downloads',
        'checked_utc':datetime.now(timezone.utc).isoformat(),'count':len(records),
        'confirmed_count':sum(bool(x['http_status']==200 and x['api_license']) for x in records),
        'records':records}
out=ROOT/'1006/evidence/audits/FRESH_C_ATLAS_ASSET_LICENSE_API_RECHECK_20261007.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'count':result['count'],'confirmed_count':result['confirmed_count'],'output':str(out.relative_to(ROOT))},indent=2))
