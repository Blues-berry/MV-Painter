"""Freeze exact comparison family and view aggregation before checkpoint outputs."""
import datetime,json
from revision_expansion_common import OUT,sha,write
from pathlib import Path
r=OUT/'iteration009_native_checkpoint_evaluation'
assert not (r/'predictions').exists()
cohort=json.loads((r/'COHORT_AND_ANALYSIS_FREEZE.json').read_text());assert len(cohort['uids'])==50
secondary=[]
for a,b in [('native_unset','disabled'),('budget_late16','budget_fixed_mean')]:
 for m in ['fg_psnr','fg_ssim','ciede2000']:secondary.append([a,b,m])
for b in ['native_gfh','budget_fixed_mean','budget_late16']:
 for m in ['fg_psnr','fg_lpips','fg_ssim','ciede2000']:secondary.append(['native_gc3',b,m])
write(r/'STATISTICAL_PROTOCOL.json',{'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cohort_freeze_sha256':sha(r/'COHORT_AND_ANALYSIS_FREEZE.json'),'primary_comparisons':[['native_unset','disabled','fg_lpips'],['budget_late16','budget_fixed_mean','fg_lpips']],'primary_family_correction':'Holm2','secondary_comparisons':secondary,'secondary_family_correction':'Holm18','primary_view_domain':'five nonreference generated target views, grid indices1..5; firstgrid tile is exactsource input, kept separately','object_aggregation':'arithmetic mean of five per-view metrics; objects equally weighted','source_view':'index0 quality separately descriptive, not pooled into primary','all_six_views':'reported descriptively only','quality_failures':'retain all valid executions, no output-based exclusion','interval':'paired object bootstrap20000, seed20261010, 95percent percentile','test':'two-sided paired sign-flip mean; MonteCarlo200000 common deterministic seed20261010 and plus-one adjustment for N50; exact when N<=20','effect_sign':'raw a-b; lpips/ciede2000 lower is better, psnr/ssim higher is better','scope':'within frozen new checkpoint/native protocol; no old-checkpoint reproduction or globally unseen claim','metric_implementation':'reuse evaluate_fresh_c_native_egl.load_metric_implementations; rawPNG encodedRGB [0,1], per-view512, sameGT mask; GTself and foreground validity calibrate before outputs','source_sha256':sha(Path(__file__))})
print('Frozen Holm2 primary, Holm18 secondary, five nonreference views and object-level resampling')
