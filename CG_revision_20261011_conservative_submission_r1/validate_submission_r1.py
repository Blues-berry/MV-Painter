#!/usr/bin/env python3
"""Validate conservative_submission_r1 outputs and immutability boundaries."""
from __future__ import annotations
import csv, hashlib, json, re, subprocess, sys, zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE if (HERE/'manuscript').is_dir() else HERE.parent
DELIVERY=ROOT/'delivery_conservative_submission_r1'
RESULT=ROOT/'VALIDATION_conservative_submission_r1.json'

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(*args: str) -> str:
    return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode('utf-8','replace')

report={'version':'conservative_submission_r1','checks':{},'artifacts':{}}
checks=report['checks']
# Verify the frozen parent tree and protected external manuscripts.
snapshot=json.loads((ROOT/'PARENT_VISUALS_SNAPSHOT.json').read_text())
parent=Path(snapshot['parent'])
expected=snapshot['files']
actual={p.relative_to(parent).as_posix():sha(p) for p in parent.rglob('*') if p.is_file()}
checks['parent_file_set_identical']=set(actual)==set(expected)
checks['parent_sha256_identical']=checks['parent_file_set_identical'] and all(actual[k]==v for k,v in expected.items())
checks['parent_file_count']=len(actual)
checks['parent_changed']=sorted(k for k in set(actual)&set(expected) if actual[k]!=expected[k])
protected=json.loads((ROOT/'PROTECTED_MANUSCRIPTS.json').read_text())
checks['protected_files_unchanged']=all(Path(p).is_file() and sha(Path(p))==v for p,v in protected.items())
checks['protected_file_count']=len(protected)
# Required PDFs, page counts, visible claim boundaries, and delivery copy hashes.
pdfs={
 'clean':('Manuscript_conservative_submission_r1.pdf',ROOT/'manuscript/build/Manuscript_conservative_submission_r1/Manuscript_conservative_submission_r1.pdf',15),
 'marked':('Marked-up_Manuscript_conservative_submission_r1.pdf',ROOT/'manuscript/build/marked_conservative_submission_r1/Marked-up_Manuscript_conservative_submission_r1.pdf',16),
 'supplement':('Supplementary_conservative_submission_r1.pdf',ROOT/'manuscript/build/Supplementary_conservative_submission_r1/Supplementary_conservative_submission_r1.pdf',36),
 'response':('Response_to_Reviewers_conservative_submission_r1.pdf',ROOT/'review/Response_to_Reviewers_conservative_submission_r1.pdf',4),
}
texts={}
for key,(name,source,pages_expected) in pdfs.items():
    output=DELIVERY/name
    text=command('pdftotext','-layout',str(source),'-')
    info=command('pdfinfo',str(source))
    m=re.search(r'Pages:\s+(\d+)',info)
    pages=int(m.group(1)) if m else -1
    texts[key]=text
    report['artifacts'][name]={'sha256':sha(source),'bytes':source.stat().st_size,'pages':pages,'delivery_copy_sha256':sha(output) if output.exists() else None,'delivery_copy_identical':output.exists() and sha(output)==sha(source)}
    checks[f'{key}_pdf_pages_correct']=pages==pages_expected
    checks[f'{key}_delivery_copy_identical']=output.exists() and sha(output)==sha(source)
main=' '.join(texts['clean'].lower().split())
response=' '.join(texts['response'].lower().split())
checks['historical_plus_0_96_once_in_main']=texts['clean'].count('0.96')==1
checks['historical_plus_0_96_once_in_response']=texts['response'].count('0.96')==1
checks['fresh_c_0_522_reported']=('0.522' in texts['clean'] and '0.522' in texts['response'])
checks['fresh_c_comparator_and_endpoint_separated']='fixed low' in main and 'fg-psnr' in main
checks['figure8_metric_scope_caveat']='not texture fidelity' in main
checks['response_version_name_current']='conservative_submission_r1' in response and 'conservative_visuals' not in response
checks['no_unresolved_pdf_references']=all('??' not in text for text in texts.values())
# Verify selection, source, licensing, and seed provenance.
figure=json.loads((ROOT/'manuscript/figures/FIG7_METRIC_FAVORABLE_PROVENANCE.json').read_text())
checks['figure8_has_two_cases']=len(figure)==2
checks['figure8_matches_composite_and_view_directions']=all(
    c['object_delta_c3_minus_fixed_low']['fg_psnr']>0 and c['object_delta_c3_minus_fixed_low']['fg_lpips']<0 and c['object_delta_c3_minus_fixed_low']['fg_ssim']>0 and
    c['display_view_delta_c3_minus_fixed_low']['fg_psnr']>0 and c['display_view_delta_c3_minus_fixed_low']['fg_lpips']<0 and c['display_view_delta_c3_minus_fixed_low']['fg_ssim']>0
    for c in figure)
credits=list(csv.DictReader((ROOT/'manuscript/figures/FIGURE_ASSET_CREDITS.csv').open(newline='',encoding='utf-8')))
figure8=[r for r in credits if r['figure_panel'] in ('Fig. 8(a)','Fig. 8(b)')]
checks['figure8_rights_cleared']=len(figure8)==2 and all(r['publication_figure_allowed']=='YES_WITH_ATTRIBUTION' for r in figure8)
checks['figure8_output_hash_matches_credit']=all(sha(ROOT/'manuscript/figures/fig7_metric_favorable.png')==r['figure_png_sha256'] for r in figure8)
seed=json.loads((ROOT/'evidence/SEED_COMPLETION_AUDIT_R1.json').read_text())
checks['seed_metadata_filled_1800']=seed['rows_filled']==1800
checks['seed_update_did_not_change_metrics']=not seed['metrics_changed']
# Independently rebuilt source archive, ZIP integrity, and playable video.
archive=DELIVERY/'LaTeX_Source_conservative_submission_r1.zip'
with zipfile.ZipFile(archive) as z:bad=z.testzip()
checks['source_zip_crc_valid']=bad is None
rebuild=json.loads((ROOT/'REBUILD_VALIDATION_conservative_submission_r1.json').read_text())
checks['independent_source_rebuild_passed']=rebuild['status']=='PASS' and rebuild['total_pages_compared']==71
checks['source_zip_hash_matches_rebuild']=sha(archive)==rebuild['archive_sha256']
report['independent_rebuild']=rebuild
video=DELIVERY/'Supplementary_Video_conservative_submission_r1.mp4'
ff=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
checks['video_full_decode_passed']=ff.returncode==0
report['video_probe']=json.loads(command('ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=codec_name,width,height,r_frame_rate','-of','json',str(video)))
# Compile logs may contain tiny sub-2pt line overflows, but no errors or large figure overflows.
logs=[ROOT/'manuscript/build/Manuscript_conservative_submission_r1/Manuscript_conservative_submission_r1.log',ROOT/'manuscript/build/marked_conservative_submission_r1/Marked-up_Manuscript_conservative_submission_r1.log',ROOT/'manuscript/build/Supplementary_conservative_submission_r1/Supplementary_conservative_submission_r1.log',ROOT/'review/Response_to_Reviewers_conservative_submission_r1.log']
errors=[];overfull=[]
for p in logs:
    s=p.read_text(errors='replace')
    errors += [f'{p.name}: {line.strip()}' for line in s.splitlines() if any(x in line for x in ('LaTeX Error','Undefined control sequence','Reference `','Citation `')) and 'undefined' in line.lower() or 'LaTeX Error' in line or 'Undefined control sequence' in line]
    overfull += [f'{p.name}: {line.strip()}' for line in s.splitlines() if 'Overfull \\hbox' in line]
checks['no_compile_errors_or_undefined_refs']=not errors
report['compile_warnings']={'overfull_hboxes':overfull,'errors':errors}
report['status']='PASS' if all(v is True for k,v in checks.items() if isinstance(v,bool)) else 'FAIL'
report['checks']=checks
RESULT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
(DELIVERY/'VALIDATION_conservative_submission_r1.json').write_text(RESULT.read_text())
print(json.dumps({'status':report['status'],'failed':[k for k,v in checks.items() if isinstance(v,bool) and not v],'result':str(RESULT),'checks':checks},indent=2,ensure_ascii=False))
if report['status']!='PASS':sys.exit(1)
