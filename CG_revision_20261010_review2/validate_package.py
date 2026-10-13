from pathlib import Path
import re,json,csv,hashlib,subprocess,shutil,zipfile
ROOT=Path(__file__).resolve().parent
M=ROOT/'manuscript'
OLD=Path('/4T/CXY/MV-Painter-cg-revision-20261010/1008/manuscript/revision_01549_restored')
validation={}
snapshot=json.loads((ROOT/'BASELINE_SNAPSHOT.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in snapshot.items())
validation['original_sources_unchanged']='PASS'
def tables(text):
 result={}
 for match in re.finditer(r'\\begin\{table\*?\}.*?\\end\{table\*?\}',text,re.S):
  block=match.group();label=re.search(r'\\label\{([^}]+)\}',block);tab=re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}',block,re.S)
  if label and tab:result[label.group(1)]=tab.group()
 return result
original=tables((OLD/'manuscript_1008.tex').read_text());new=tables((M/'manuscript_1008.tex').read_text())
assert [k for k,v in original.items() if new[k]!=v]==['tab:new-bake']
assert all(r in new['tab:new-bake'].splitlines() for r in original['tab:new-bake'].splitlines() if '&' in r)
prior=(ROOT/'archive/before_no_experiment_refinement/manuscript_1008.tex').read_text()
old_limits=prior.split('\\section{Limitations}',1)[1].split('\\section{Conclusion}',1)[0].split('\\label{sec:limitations}',1)[1].strip()
old_limits=old_limits.replace('Figure~\\ref{fig:color-failure}','Main Figure~6')
assert old_limits in (M/'Supplementary_1008.tex').read_text()
validation['detailed_limits_preserved_in_supplement']='PASS_S19'
validation['generated_condition_table_rows']='PASS_ALL_ORIGINAL_ROWS_PRESERVED; GT calibration row added'
records=json.loads((M/'figures/REVIEW2_SOURCE_HASHES.json').read_text())
assert all(hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'] for r in records)
validation['loaded_image_sources']={'count':len(records),'hash_check':'PASS'}
with (M/'figures/FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv').open() as f:rows=list(csv.DictReader(f))
names={'fig4':'fig4_freshc_context_roi','fig5':'fig5_freshc_context_roi','fig6_color_diagnostic':'fig6_color_diagnostic_freshc_context_roi'}
for r in rows:assert hashlib.sha256((M/'figures'/(names[r['figure_id']]+'.png')).read_bytes()).hexdigest()==r['output_sha256']
validation['fresh_figure_output_hashes']='PASS'
frames=json.loads((M/'figures/INTEGRATED_DISPLAY_FRAMES.json').read_text())
assert len(frames)==14
assert all(len(f['frame'])==4 and f['frame'][0]<f['frame'][2] and f['frame'][1]<f['frame'][3] for f in frames)
assert all(f.get('detail') is None for f in frames if f['figure']!='fig5_freshc_context_roi')
assert (M/'figures/figS9_mvadapter_all.pdf').exists()
validation['display_frames']='PASS_14_OBJECT_PANELS; shared across all conditions; frozen detail ROI only in Figure 5'

for path in [M/'build/manuscript_1008/manuscript_1008.log',M/'build/supplement_1008/Supplementary_1008.log',M/'build/marked_up_1008_review4/Marked-up_Manuscript_1008.log']:
 text=path.read_text(errors='replace')
 assert 'Fatal error' not in text and 'undefined references' not in text and 'undefined on input line' not in text
validation['pdf_builds']='PASS_CLEAN_MARKED_SUPPLEMENT; no unresolved references'
PKG=ROOT/'submission_refined';PKG.mkdir(exist_ok=True)
files={'Manuscript_refined.pdf':M/'build/manuscript_1008/manuscript_1008.pdf','Marked-up_Manuscript_refined.pdf':M/'build/marked_up_1008_review4/Marked-up_Manuscript_1008.pdf','Supplementary_refined.pdf':M/'build/supplement_1008/Supplementary_1008.pdf','Response_to_Reviewers_refined.pdf':ROOT/'review/Response_to_Reviewers_1008.pdf','Response_to_Reviewers_refined.md':ROOT/'review/Response_to_Reviewers_1008.md','Supplementary_Video_refined.mp4':M/'Supplementary_Video_1008.mp4'}
shutil.copy(ROOT/'Reproduction_inherited_1008.zip',PKG/'Reproduction_inherited_1008.zip')
for name,p in files.items():
 assert p.exists();shutil.copy(p,PKG/name)
 if p.suffix=='.pdf':assert '??' not in subprocess.check_output(['pdftotext',str(p),'-'],text=True)
for name in ['manuscript_1008.tex','Supplementary_1008.tex']:shutil.copy(M/name,PKG/name)
for name in ['README_ZH.md','REVISION_CHANGELOG_ZH.md','LAYOUT_INTEGRATION_ZH.md','INDEPENDENT_REVIEW_ZH.md','ACCEPTANCE_ASSESSMENT_ZH.md']:shutil.copy(ROOT/name,PKG/name)
with zipfile.ZipFile(PKG/'LaTeX_Source_refined.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in [M,ROOT/'source_01549',ROOT/'review',ROOT/'evidence',ROOT/'archive/before_no_experiment_refinement']:
  for p in sorted(folder.rglob('*')):
   if p.is_file() and 'build' not in p.relative_to(folder).parts and '__pycache__' not in p.parts:z.write(p,p.relative_to(ROOT))
 for name in ['BASELINE_SNAPSHOT.json','README_ZH.md','REVISION_CHANGELOG_ZH.md','LAYOUT_INTEGRATION_ZH.md','INDEPENDENT_REVIEW_ZH.md','ACCEPTANCE_ASSESSMENT_ZH.md','validate_package.py']:z.write(ROOT/name,name)
with zipfile.ZipFile(PKG/'LaTeX_Source_refined.zip') as z:
 for name in ['manuscript_1008.tex','Supplementary_1008.tex']:assert z.read('manuscript/'+name)==(M/name).read_bytes()
validation['source_zip_matches_current_tex']='PASS'
validation['inherited_video_unchanged']=hashlib.sha256((PKG/'Supplementary_Video_refined.mp4').read_bytes()).hexdigest()==hashlib.sha256((OLD/'Supplementary_Video_1008.mp4').read_bytes()).hexdigest()
validation['scope']='Editorial/figure revision; no new inference or repair. Default GeoTex, cause of appearance failure, seams/PBR and R2.1 remain unresolved.'
(ROOT/'VALIDATION_INTEGRATED.json').write_text(json.dumps(validation,indent=2)+'\n');shutil.copy(ROOT/'VALIDATION_INTEGRATED.json',PKG/'VALIDATION_INTEGRATED.json')
print(json.dumps(validation,indent=2))
