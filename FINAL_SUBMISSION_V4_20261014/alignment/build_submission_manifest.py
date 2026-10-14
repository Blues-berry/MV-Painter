"""Validate and hash the current V4 continuation, with scientific judgement recorded separately."""
from pathlib import Path
import csv,hashlib,json,re,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUTPUT=ROOT/'alignment/SUBMISSION_MANIFEST_V4.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pages(p):
 return int(next(x.split(':',1)[1] for x in subprocess.check_output(['pdfinfo',str(p)],text=True).splitlines() if x.startswith('Pages:')))
def texts(p):return subprocess.check_output(['pdftotext','-raw',str(p),'-'],text=True).split('\f')
def locate(t,prefix):
 found=[i+1 for i,page in enumerate(t) if any(line.startswith(prefix) for line in page.splitlines())]
 if len(found)!=1:raise RuntimeError(f'Ambiguous caption location: {prefix}: {found}')
 return found[0]
def main():
 pdfs={k:ROOT/f'FINAL_V4_{v}.pdf' for k,v in [('main','MANUSCRIPT'),('supplement','SUPPLEMENTARY'),('response','RESPONSE_TO_REVIEWERS'),('marked','MARKED_MANUSCRIPT')]}
 counts={k:pages(p) for k,p in pdfs.items()};assert counts['main']>=14 and counts['supplement']==71 and counts['response']==5 and counts['marked']>=21,counts
 maintext=texts(pdfs['main']);supp=texts(pdfs['supplement'])
 locations={
 'Figure 2':locate(maintext,'Fig. 2. Fresh C'),
 'Figure 3':locate(maintext,'Fig. 3. GeoTex Bake10'),
 'Figure 4':locate(maintext,'Fig. 4. Fresh C'),
 'Table 5':locate(maintext,'Table 5. Unseen-view'),
 'Table 6':locate(maintext,'Table 6. Native-camera'),
 'Table 7':locate(maintext,'Table 7. Specified'),
 'Table S35':locate(supp,'Table S35:'),
 'Table S36':locate(supp,'Table S36:'),
 }
 assert '[41]' in maintext[-2]
 primary=maintext[locations['Table 7']-1]
 for number in ['0.033877','0.117170','0.051422','0.432378']:assert number in primary,number
 frozen=json.loads((ROOT/'quality_review/FROZEN_CONTENT_CHECK_V4.json').read_text());assert frozen['status']=='PASS'
 selection=json.loads((ROOT/'visual_candidates/FIGURE3_SELECTION_V4.json').read_text());assert selection['selected_candidate']=='C';assert [x['uid'] for x in selection['rows']]==['21678bd623654182b52c11d013de4e71'];assert len(selection['effect_plot']['values_by_uid_prefix'])==10
 for row in selection['rows']:
  for panel in row['panels']:
   p=ROOT/panel['source_asset'];assert sha(p)==panel['source_sha256'] and Image.open(p).size==(512,512)
   assert sha(ROOT/panel['display_asset'])==panel['display_sha256']
 for name in ['FIGURE3_IDENTITY_VALIDATION_V4.json','MARKED_MANUSCRIPT_CHECK_V4.json']:
  assert json.loads((ROOT/'quality_review'/name).read_text())['status']=='PASS'
 readiness=json.loads((ROOT/'quality_review/FINAL_READINESS_V4.json').read_text())
 files={}
 for p in sorted(x for x in ROOT.rglob('*') if x.is_file()):
  rel=p.relative_to(ROOT)
  if p==OUTPUT or p.name=='FINAL_V4_BUILD_REPORT.json' or any(x in rel.parts for x in ['build','build_response','__pycache__','.git']):continue
  files[rel.as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
 out={'version':'V4','revision':'final_quality_continuation_20261014','baseline_head':'c3017645f990993d668ce71926f4ccb4304e9edb','status':'PASS','pdf_pages':counts,'actual_locations':locations,'original_timing_primary':{'table':7,'contrast':'Middle − mean(Early, Late)','estimate_db':-0.0338775,'ci95_db':[-.117170,.051422],'p':.432378},'figure3_selection':selection,'author_review_ready':readiness['AUTHOR_REVIEW_READY'],'submission_ready':readiness['SUBMISSION_READY'],'scientific_readiness_record':'quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md','files':files,'note':'Own hash and ignored build intermediates excluded; compilation is not the basis of scientific readiness.'}
 OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('V4 continuation manifest PASS',counts,len(files),'files')
if __name__=='__main__':main()
