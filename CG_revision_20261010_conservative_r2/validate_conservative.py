"""Validate immutable ancestry/evidence and package this conservative iteration."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,zipfile,difflib
ROOT=Path(__file__).resolve().parent
V=json.loads((ROOT/'VERSION.json').read_text());TAG=V['version'];M=ROOT/'manuscript'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=Path(V['parent']);snapshot=json.loads((ROOT/'PARENT_SNAPSHOT.json').read_text())
assert snapshot['parent']==str(parent)
assert all((parent/p).is_file() and sha(parent/p)==h for p,h in snapshot['files'].items()), 'Parent modified'
assert {str(p.relative_to(parent)) for p in parent.rglob('*') if p.is_file()}==set(snapshot['files']), 'Parent file set changed'
ancestors=json.loads((ROOT/'ANCESTOR_SNAPSHOTS.json').read_text()) if (ROOT/'ANCESTOR_SNAPSHOTS.json').exists() else []
for ancestor in ancestors:
 base=Path(ancestor['parent'])
 assert all((base/p).is_file() and sha(base/p)==h for p,h in ancestor['files'].items()), 'Ancestor modified'
 assert {str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}==set(ancestor['files']), 'Ancestor file set changed'
protected=json.loads((ROOT/'PROTECTED_MANUSCRIPTS.json').read_text())
assert all(sha(Path(p))==h for p,h in protected.items()), 'Other manuscript modified'
for folder in ['evidence','manuscript/figures','source_01549']:
 previous={str(p.relative_to(parent/folder)):sha(p) for p in (parent/folder).rglob('*') if p.is_file()}
 current={str(p.relative_to(ROOT/folder)):sha(p) for p in (ROOT/folder).rglob('*') if p.is_file()}
 assert current==previous, f'{folder} differs from parent'
def tables(s):
 result={}
 for block in re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}',s,re.S):
  label=re.search(r'\\label\{([^}]+)\}',block);tab=re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}',block,re.S)
  if label and tab:result[label.group(1)]=tab.group()
 return result
main=(M/V['main']).read_text();assert tables(main)==tables((parent/V['parent_main']).read_text()), 'Main table values changed'
# Identity of all existing supplementary tables is maintained even if new text is added.
supp=(M/V['supplement']).read_text();prior_tables=tables((parent/V['parent_supplement']).read_text());current_tables=tables(supp)
assert all(current_tables.get(k)==v for k,v in prior_tables.items()), 'Existing supplement tables changed'
assert set(current_tables)-set(prior_tables)=={'tab:control-identity-geotex','tab:control-identity-mva'}, 'Unexpected added table'
for filename,old,anchor in [(f'Changes_from_01549_{TAG}.diff',(ROOT/'source_01549/final_0903.tex').read_text(),'authenticated_01549'),(f'Changes_from_parent_{TAG}.diff',(parent/V['parent_main']).read_text(),'conservative_r1')]:
 expected=''.join(difflib.unified_diff(old.splitlines(True),main.splitlines(True),fromfile=anchor,tofile=V['main']))
 assert (ROOT/'review'/filename).read_text()==expected, 'Stale textual diff'
logs=[M/'build'/f'Manuscript_{TAG}'/f'Manuscript_{TAG}.log',M/'build'/f'Supplementary_{TAG}'/f'Supplementary_{TAG}.log',M/'build'/f'marked_{TAG}'/f'Marked-up_Manuscript_{TAG}.log']
for p in logs:
 s=p.read_text(errors='replace')
 assert all(q not in s for q in ['Fatal error','undefined references','undefined on input line','Float too large']),str(p)
PKG=ROOT/f'delivery_{TAG}';PKG.mkdir(exist_ok=True)
outputs={f'Manuscript_{TAG}.pdf':logs[0].with_suffix('.pdf'),f'Supplementary_{TAG}.pdf':logs[1].with_suffix('.pdf'),f'Marked-up_Manuscript_{TAG}.pdf':logs[2].with_suffix('.pdf'),f'Response_to_Reviewers_{TAG}.pdf':ROOT/'review'/f'Response_to_Reviewers_{TAG}.pdf',f'Response_to_Reviewers_{TAG}.tex':ROOT/'review'/f'Response_to_Reviewers_{TAG}.tex',f'Response_to_Reviewers_{TAG}.docx':ROOT/'review'/f'Response_to_Reviewers_{TAG}.docx',f'Response_to_Reviewers_{TAG}.md':ROOT/'review'/f'Response_to_Reviewers_{TAG}.md',f'Supplementary_Video_{TAG}.mp4':M/f'Supplementary_Video_{TAG}.mp4',f'Reproduction_inherited_{TAG}.zip':ROOT/f'Reproduction_inherited_{TAG}.zip',V['main']:M/V['main'],V['supplement']:M/V['supplement'],f'Marked-up_Manuscript_{TAG}.tex':logs[2].with_suffix('.tex')}
pages={}
for name,p in outputs.items():
 assert p.exists(),str(p);shutil.copy2(p,PKG/name)
 if p.suffix=='.pdf':
  text=subprocess.check_output(['pdftotext',str(p),'-'],text=True);assert '??' not in text,name
  info=subprocess.check_output(['pdfinfo',str(p)],text=True);pages[name]=int(re.search(r'Pages:\s+(\d+)',info).group(1))
# Old video/reproduction content is carried forward byte-for-byte, with a new label.
old_video=next((parent/'manuscript').glob('Supplementary_Video*.mp4'))
old_repro=next(parent.glob('Reproduction_inherited*.zip'))
assert sha(old_video)==sha(M/f'Supplementary_Video_{TAG}.mp4')
assert sha(old_repro)==sha(ROOT/f'Reproduction_inherited_{TAG}.zip')
meta=['VERSION.json','README_ZH.md','ROUND_ANALYSIS_PLAN_ZH.md','ROUND_EXECUTION_ZH.md','PARENT_SNAPSHOT.json','PROTECTED_MANUSCRIPTS.json','INDEPENDENT_REVIEW_ZH.md','ACCEPTANCE_ASSESSMENT_ZH.md','BASELINE_SNAPSHOT.json','ANCESTOR_SNAPSHOTS.json','MARKED_UP_NOTES_ZH.md','CONTROL_ACCOUNTING_conservative_r2.json']
for n in meta:shutil.copy2(ROOT/n,PKG/n)
for p in (ROOT/'review').glob('Changes*.diff'):shutil.copy2(p,PKG/p.name)
shutil.copy2(ROOT/'review/REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv',PKG/'REVIEWER_TO_MANUSCRIPT_TRACEABILITY.csv')
archive=PKG/f'LaTeX_Source_{TAG}.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for folder in [M,ROOT/'source_01549',ROOT/'review',ROOT/'evidence']:
  for p in sorted(folder.rglob('*')):
   if p.is_file() and 'build' not in p.relative_to(folder).parts and '__pycache__' not in p.parts:z.write(p,p.relative_to(ROOT))
 for n in meta+['validate_conservative.py']:z.write(ROOT/n,n)
with zipfile.ZipFile(archive) as z:
 for folder in [M/'figures',ROOT/'review',ROOT/'evidence']:
  for p in folder.rglob('*'):
   if p.is_file():assert z.read(str(p.relative_to(ROOT)))==p.read_bytes()
 for n in [V['main'],V['supplement']]:assert z.read('manuscript/'+n)==(M/n).read_bytes()
report={'version':TAG,'parent':str(parent),'parent_files_unchanged':len(snapshot['files']),'ancestor_files_unchanged':[len(a['files']) for a in ancestors],'other_manuscripts_unchanged':len(protected),'evidence_figures_original01549_byte_identical_to_parent':True,'all_existing_main_and_supplement_table_values_unchanged':True,'builds_and_references':'PASS','source_archive_matches_current_assets_and_tex':True,'video_and_reproduction_byte_identical':True,'pdf_pages':pages,'new_model_experiments':False}
for p in [ROOT/f'VALIDATION_{TAG}.json',PKG/f'VALIDATION_{TAG}.json']:p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
