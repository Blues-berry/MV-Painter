"""Refresh the existing local V4 journal-upload directory without changing videos."""
from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile

ROOT=Path(__file__).resolve().parents[1]
J=Path('/4T/CXY/TCAS_PRE_SUBMISSION_AUDIT_20261013/working/1014v4_FINAL_QUALITY_CONTINUATION_20261014/journal_upload_v4')
VIDEO=json.loads((ROOT/'quality_review/VIDEO_VALIDATION_V4.json').read_text())

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def main():
 assert J.is_dir(),J
 for item in VIDEO.values():
  p=J/item['filename']
  assert p.is_file() and sha(p)==item['sha256'],p
 for name in ['FINAL_V4_MANUSCRIPT.pdf','FINAL_V4_SUPPLEMENTARY.pdf','FINAL_V4_RESPONSE_TO_REVIEWERS.pdf','FINAL_V4_MARKED_MANUSCRIPT.pdf']:
  shutil.copy2(ROOT/name,J/name)
 subprocess.run(['pandoc',str(ROOT/'review/FINAL_V4_RESPONSE_TO_REVIEWERS.md'),'-o',str(J/'FINAL_V4_RESPONSE_TO_REVIEWERS.docx')],check=True)
 source=J/'Manuscript_LaTeX_Sources_V4.zip'
 with zipfile.ZipFile(source,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for name in ['FINAL_V4_MANUSCRIPT.tex','FINAL_V4_SUPPLEMENTARY.tex','fig2.pdf','fig3.pdf','build_v4_manuscript.py','MAIN_TEXT_EVIDENCE_REINTEGRATION.md','R1_R2_EVIDENCE_VALUE_MATRIX.md','FIGURE_AND_TABLE_REDESIGN_PLAN.md','SCIENTIFIC_CONTENT_ADDITION_LOG.md','TABLE_1_TO_7_LAYOUT_AUDIT.md']:
   z.write(ROOT/name,name)
  for folder in ['figures','tables','sections','vendor','visual_candidates','marked','review']:
   for p in sorted((ROOT/folder).rglob('*')):
    if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ['build','build_response','__pycache__']):z.write(p,str(p.relative_to(ROOT)))
  for name in ['cag.sty','elsarticle.cls','cag-logo.pdf','elsevier-logo.pdf']:z.write(ROOT/'vendor'/name,name)
 with zipfile.ZipFile(source) as z:
  assert z.testzip() is None
  assert z.read('FINAL_V4_MANUSCRIPT.tex')==(ROOT/'FINAL_V4_MANUSCRIPT.tex').read_bytes()
  assert 'figures/fig3_bake10_distribution_v4.pdf' in z.namelist()
 files={}
 for p in sorted(J.iterdir()):
  if p.is_file() and p.name!='JOURNAL_SUBMISSION_MANIFEST_V4.json':files[p.name]={'local_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 out={'version':'V4 evidence reintegration','status':'PASS','journal_directory':str(J),'main_pages':14,'supplement_pages':71,'response_pages':5,'marked_pages':21,'videos':VIDEO,'files':files,'portal_submission':'NOT_PERFORMED'}
 (J/'JOURNAL_SUBMISSION_MANIFEST_V4.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 shutil.copy2(J/'JOURNAL_SUBMISSION_MANIFEST_V4.json',ROOT/'quality_review/JOURNAL_DELIVERY_MANIFEST_V4.json')
 print('Refreshed',len(files),'journal files in',J)

if __name__=='__main__':main()
