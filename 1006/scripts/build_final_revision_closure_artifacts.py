#!/usr/bin/env python3
"""Build final closure tables from existing frozen evidence; never reads human responses."""
from __future__ import annotations
import csv, hashlib, json, subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUD=ROOT/'1006/evidence/audits'
REMOTE='f5bad8a1e6ca4265c1823eaa26b2775313de4c96'
REMOTE_REF='refs/heads/codex/scientific-validation-v3-20261006'

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ''
def jload(rel): return json.loads((ROOT/rel).read_text())
def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

# Execution semantics: exact sampled records from complete logged table; no interpolation.
sem_src=ROOT/'1006/evidence/audits/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv'
with sem_src.open(newline='') as f: sem=list(csv.DictReader(f))
steps={0,12,24,37,49}
sem_rows=[]
for r in sem:
    if int(r['step']) in steps:
        x=dict(r)
        x['source_file']=str(sem_src.relative_to(ROOT))
        x['source_sha256']=sha(sem_src)
        sem_rows.append(x)
sem_fields=list(sem_rows[0])
write_csv(AUD/'FRESH_C_EXECUTION_SEMANTICS_REPRESENTATIVE.csv',sem_fields,sem_rows)

# The central table is limited to frozen image-space comparisons and explicitly
# identified execution/interaction context that could enter a bounded rewrite.
fields=['claim_id','experiment','cohort','N','condition_A','condition_B','metric','effect','CI_lower','CI_upper','p_raw','p_adjusted','correction_family','favorable_fraction','median','analysis_classification','source_raw_file','source_script','source_hash','source_analysis_file','source_analysis_sha256','source_script_sha256','allowed_wording','forbidden_wording','requested_scale','applied_scale','cap_activation_fraction','applied_correction_l2_median']
rows=[]
primary=jload('1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json')
add=jload('1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json')
direction=jload('1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json')
primary_csv=ROOT/'1006/data/fresh_c/fresh_c_c3_minus_gfl_object_deltas.csv'
add_csv=ROOT/'1006/data/fresh_c/fresh_c_addendum_object_deltas.csv'
main_script=ROOT/'1006/scripts/run_fresh_c_locked_analyses_with_sign_audit.py'
validator=ROOT/'1006/scripts/validate_fresh_c_result_directions.py'
checks={(x['contrast'],x['metric']):x for x in direction['independent_checks']}
for metric,st in primary['tests'].items():
    chk=checks[('C3-GFL',metric)]
    rows.append({
      'claim_id':f'FRESHC_C3_GFL_{metric.upper()}','experiment':'Fresh C primary four-condition run','cohort':'FRESH_C','N':primary['n_objects'],
      'condition_A':'C3','condition_B':'GFL','metric':metric,'effect':st['mean'],
      'CI_lower':st['bootstrap_ci95'][0],'CI_upper':st['bootstrap_ci95'][1],
      'p_raw':chk['p_raw_reported'],'p_adjusted':chk['p_holm_reported'],
      'correction_family':chk['multiplicity_family'],'favorable_fraction':st['favorable_object_fraction'],'median':st['median'],
      'analysis_classification':'registered primary endpoint' if metric=='fg_psnr' else 'registered secondary endpoint',
      'source_raw_file':str(primary_csv.relative_to(ROOT)),'source_script':str(main_script.relative_to(ROOT)),
      'source_hash':sha(primary_csv),'source_analysis_file':'1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json',
      'source_analysis_sha256':sha(ROOT/'1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json'),
      'allowed_wording':'Report as a paired object-level Fresh C contrast for this endpoint; LPIPS is lower-is-better.',
      'forbidden_wording':'Do not infer a cross-metric winner, universal schedule, or typical-object improvement from the mean alone.'})
for st in add['tests']:
    con=st['contrast']; metric=st['metric']; chk=checks[(con,metric)]
    primary_family='six primary endpoint-contrast tests' in st['multiplicity_family']
    rows.append({
      'claim_id':f'FRESHC_ADD_{con.replace("-","_")}_{metric.upper()}','experiment':'Fresh C LLH/generic-linear revision-era addendum','cohort':'FRESH_C_ADDENDUM','N':add['n_objects'],
      'condition_A':st['condition_a'],'condition_B':st['condition_b'],'metric':metric,'effect':st['mean'],
      'CI_lower':st['bootstrap_ci95'][0],'CI_upper':st['bootstrap_ci95'][1],
      'p_raw':chk['p_raw_reported'],'p_adjusted':chk['p_holm_reported'],
      'correction_family':st['multiplicity_family'],'favorable_fraction':st['favorable_object_fraction_for_a'],'median':st['median'],
      'analysis_classification':'revision-era addendum primary family' if primary_family else 'revision-era addendum secondary family',
      'source_raw_file':str(add_csv.relative_to(ROOT)),'source_script':str(ROOT.joinpath('1006/scripts/audit_analyze_fresh_c_addendum.py').relative_to(ROOT)),
      'source_hash':sha(add_csv),'source_analysis_file':'1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json',
      'source_analysis_sha256':sha(ROOT/'1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json'),
      'allowed_wording':'Report as a paired object-level Fresh C addendum contrast for this endpoint; LPIPS is lower-is-better.',
      'forbidden_wording':'A non-significant result is not equivalence; do not infer a cross-metric winner or universal schedule.'})

# Layer/window interaction values are sourced from the independently audited statistics file.
a2=jload('1006/evidence/authority_sources/a2_interaction.json')
a2src=ROOT/'1006/evidence/authority_sources/a2_interaction.json'
for key,st in a2.items():
    layer=key.split('_')[0];metric=key.split('_',1)[1]
    rows.append({'claim_id':f'{layer}_{metric.upper()}_VALIDATED_WALD','experiment':layer+' layer-by-window characterization','cohort':'FRESH_CONFIRM_300','N':st['n_objects'],
      'condition_A':'8-df layer-by-window term','condition_B':'additive cell response','metric':'validated cluster-robust Wald interaction; SS share',
      'effect':st['interaction_ss_share'],'p_raw':'<1e-300' if st['p']==0 else st['p'],
      'correction_family':'validated 8-df interaction test; no cross-metric family implied',
      'analysis_classification':'secondary characterization; A3 is high-dose stress regime' if layer=='A3' else 'secondary characterization; exploratory A2 reanalysis',
      'source_raw_file':str(a2src.relative_to(ROOT)),'source_script':'final/round2/scientific_validation_v3/audit_scripts/audit_interaction_valid_test.py',
      'source_hash':sha(a2src),'source_analysis_file':str(a2src.relative_to(ROOT)),'source_analysis_sha256':sha(a2src),
      'allowed_wording':'Measurable response heterogeneity under the tested intervention regime; SS share is descriptive magnitude.',
      'forbidden_wording':'Do not claim dose-independent mechanism, universal architecture law, or optimal schedule.'})
# GEE cross-check for A2 is preserved in the original interpretation record.
gee_src=ROOT/'final/round2/scientific_validation_v3/A2_FINAL_INTERPRETATION.md'
for metric,chi,pv in [('fg_lpips',482.708,'3.6e-99'),('fg_psnr',1886.250,'<1e-300')]:
    rows.append({'claim_id':f'A2_{metric.upper()}_GEE_CROSSCHECK','experiment':'A2 layer-by-window characterization','cohort':'FRESH_CONFIRM_300','N':300,
      'condition_A':'8-df layer-by-window term','condition_B':'additive cell response','metric':'object-cluster robust GEE chi-square',
      'effect':chi,'p_raw':pv,'correction_family':'validated object-cluster GEE cross-check',
      'analysis_classification':'secondary characterization; exploratory A2 reanalysis',
      'source_raw_file':str(gee_src.relative_to(ROOT)),'source_script':'final/round2/scientific_validation_v3/audit_scripts/audit_a2_gee_repeated_measures.py',
      'source_hash':sha(gee_src),'source_analysis_file':str(gee_src.relative_to(ROOT)),'source_analysis_sha256':sha(gee_src),
      'allowed_wording':'Convergent statistical evidence for response heterogeneity under the measured A2 regime.',
      'forbidden_wording':'Do not claim dose-independent mechanism, universal architecture law, or optimal schedule.'})
# A3b corrected bounded-map interaction and dose-support limits.
import re
a3b_report=ROOT/'1006/evidence/audits/A3B_BOUNDED_LAYER_TIME_REPORT.md'
for line in a3b_report.read_text().splitlines():
    cells=[x.strip() for x in line.strip().strip('|').split('|')]
    if not cells or cells[0] not in ('FG-LPIPS','FG-PSNR') or len(cells)<6: continue
    metric=cells[0].lower().replace('-','_')
    wm=re.search(r'W=([0-9.]+), p=([^ |]+)',cells[1])
    holm=cells[2]
    share=float(cells[3].rstrip('%'))/100
    rmse=cells[4]
    gm=re.search(r'W=([0-9.]+), p=([^ |]+)',cells[5])
    for test_name,match,adj in [('WALD',wm,holm),('GEE',gm,'')]:
        rows.append({'claim_id':f'A3B_{metric.upper()}_{test_name}','experiment':'A3b bounded layer-by-window map',
          'cohort':'FRESH_CONFIRM_B','N':150,'condition_A':'8-df layer-by-window term','condition_B':'additive cell response',
          'metric':f'{test_name} interaction W(8); SS share={share}; cell RMSE={rmse}',
          'effect':match.group(1),'p_raw':match.group(2),'p_adjusted':adj,
          'correction_family':'16-test Holm family' if test_name=='WALD' else 'independent object-cluster GEE cross-check',
          'analysis_classification':'bounded secondary characterization; post-discovery dose map',
          'source_raw_file':str(a3b_report.relative_to(ROOT)),'source_script':'final/round2/scientific_validation_v3/audit_scripts/analyze_fresh_confirm_b_a3b.py',
          'source_hash':sha(a3b_report),'source_analysis_file':str(a3b_report.relative_to(ROOT)),
          'source_analysis_sha256':sha(a3b_report),
          'allowed_wording':'Measurable heterogeneity for the tested bounded intervention map, with dose-support limitation.',
          'forbidden_wording':'Do not claim dose-independent mechanism, equal-dose effect, universal law, or optimal schedule.'})
# A3b common-support result and observed dose intervals, from the frozen sensitivity JSON.
dose=jload('1006/data/fresh_b/RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.json')
dose_src=ROOT/'1006/data/fresh_b/RESIDUAL_DOSE_SENSITIVITY_ANALYSIS.json'
rows.append({'claim_id':'A3B_DOSE_COMMON_SUPPORT','experiment':'A3b realized-dose sensitivity','cohort':'FRESH_CONFIRM_B','N':2250,
  'condition_A':'three-layer dose strata','condition_B':'common observed support','metric':'retained fraction of common-support rows',
  'effect':dose['common_support']['retained_fraction_overall'],'analysis_classification':'dose-support limitation; no overlap',
  'source_raw_file':str(dose_src.relative_to(ROOT)),'source_script':'final/round2/scientific_validation_v3/audit_scripts/analyze_fresh_confirm_b_a3b.py',
  'source_hash':sha(dose_src),'source_analysis_file':str(dose_src.relative_to(ROOT)),'source_analysis_sha256':sha(dose_src),
  'allowed_wording':'No common support was available for the three-layer dose-adjusted comparison.',
  'forbidden_wording':'Do not treat extrapolated adjusted estimates as equal-dose causal evidence.'})
for depth,interval in dose['common_support']['layer_central_90_intervals'].items():
    rows.append({'claim_id':f'A3B_DOSE_CENTRAL90_{depth.upper()}','experiment':'A3b realized-dose sensitivity',
      'cohort':'FRESH_CONFIRM_B','N':dose['n_objects'],'condition_A':depth,'condition_B':'active-window actual post-scale norm',
      'metric':'central 90% observed dose interval','effect':f'{interval[0]} to {interval[1]}',
      'CI_lower':interval[0],'CI_upper':interval[1],'analysis_classification':'descriptive dose support; not a confidence interval',
      'source_raw_file':str(dose_src.relative_to(ROOT)),'source_script':'final/round2/scientific_validation_v3/audit_scripts/analyze_fresh_confirm_b_a3b.py',
      'source_hash':sha(dose_src),'source_analysis_file':str(dose_src.relative_to(ROOT)),'source_analysis_sha256':sha(dose_src),
      'allowed_wording':'Describe as a within-layer central 90% interval for observed dose.',
      'forbidden_wording':'Do not call this a between-layer matched-dose interval.'})
# Exploratory Fresh B GT-texture boundary values plotted in Figure E.
texture=jload('1006/data/fresh_b/SPEARMAN_TEXTURE_BOUNDARY_B.json')
texture_src=ROOT/'1006/data/fresh_b/SPEARMAN_TEXTURE_BOUNDARY_B.json'
for endpoint,ed in texture['tests'].items():
    for gt,st in ed.items():
        if not isinstance(st,dict) or 'rho' not in st: continue
        rows.append({'claim_id':f'FRESHB_TEXTURE_{endpoint.upper()}_{gt.upper()}','experiment':'Fresh B exploratory GT-texture boundary',
          'cohort':'FRESH_CONFIRM_B','N':texture['n'],'condition_A':texture['a'],'condition_B':texture['b'],
          'metric':f'Spearman rho: {endpoint} vs {gt}','effect':st['rho'],'CI_lower':st['ci95'][0],
          'CI_upper':st['ci95'][1],'p_raw':st.get('p_bootstrap_plus_one',''),
          'correction_family':'exploratory correlation family; consult source JSON for full family handling',
          'analysis_classification':'exploratory association; non-causal boundary characterization',
          'source_raw_file':str(texture_src.relative_to(ROOT)),
          'source_script':'final/round2/scientific_validation_v3/analyze_v3.py',
          'source_hash':sha(texture_src),'source_analysis_file':str(texture_src.relative_to(ROOT)),
          'source_analysis_sha256':sha(texture_src),
          'allowed_wording':'Exploratory object-level association in Fresh B only; not a threshold or causal boundary.',
          'forbidden_wording':'Do not claim a universal predictor, causal texture mechanism, or decision threshold.'})

# Cross-interface bounded statistics.
gsrc=ROOT/'1006/data/cross_backbone/mvadapter/AUDIT_INTERACTION_VALID_TEST_G_COMPLETE.json'
gdata=jload('1006/data/cross_backbone/mvadapter/AUDIT_INTERACTION_VALID_TEST_G_COMPLETE.json')
for metric,key in [('fg_lpips','G_fg_lpips'),('fg_psnr','G_psnr')]:
    st=gdata[key]
    rows.append({'claim_id':f'MVADAPTER_{metric.upper()}_WALD','experiment':'MV-Adapter interface boundary','cohort':'MVADAPTER_G','N':st['n_objects'],
      'condition_A':'layer-by-window term','condition_B':'additive response','metric':'validated cluster-robust Wald interaction',
      'effect':st['interaction_ss_share'],'p_raw':st['p'],'p_adjusted':gdata['exploratory_metric_family_holm']['adjusted_p'].get(metric,''),
      'correction_family':'exploratory four-metric Holm family','analysis_classification':'cross-interface boundary; exploratory',
      'source_raw_file':str(gsrc.relative_to(ROOT)),'source_script':'final/round2/scientific_validation_v3/audit_scripts/audit_interaction_valid_test_g.py',
      'source_hash':sha(gsrc),'source_analysis_file':str(gsrc.relative_to(ROOT)),'source_analysis_sha256':sha(gsrc),
      'allowed_wording':'The tested MV-Adapter interface did not reproduce the primary-backbone interaction at the global test level.',
      'forbidden_wording':'Do not claim equivalence or a universal absence of interaction.'})
# MVDiffusion interface-boundary paired summaries; nominal, not cross-interface pooled.
mvd=ROOT/'1006/data/derived/evidence_alignment/mvdiffusion_interface_effects.csv'
with mvd.open(newline='') as f: mvdrows=list(csv.DictReader(f))
for st in mvdrows:
    rows.append({'claim_id':f"MVDIFF_{st['comparison']}_{st['metric']}",'experiment':'MVDiffusion correspondence-aware interface boundary',
      'cohort':'MVDIFFUSION_PANEL','N':st['n_objects'],'condition_A':st['left'],'condition_B':st['right'],
      'metric':st['metric'],'effect':st['mean_favorable_oriented_delta'],'CI_lower':st['ci95_low_nominal'],
      'CI_upper':st['ci95_high_nominal'],'favorable_fraction':st['favorable_object_rate'],
      'correction_family':st['multiplicity'],'analysis_classification':'interface-specific nominal paired comparison',
      'source_raw_file':str(mvd.relative_to(ROOT)),'source_script':'1006/scripts/generate_evidence_alignment_figures.py',
      'source_hash':sha(mvd),'source_analysis_file':str(mvd.relative_to(ROOT)),'source_analysis_sha256':sha(mvd),
      'allowed_wording':'Report only within the tested MVDiffusion correspondence-aware interface.',
      'forbidden_wording':'Do not pool with MVPainter/MV-Adapter or infer architecture causality.'})
# MV-Adapter global cluster-bootstrap result.
gcells=ROOT/'1006/data/cross_backbone/mvadapter/layermap_g_complete.json'
groot=jload('1006/data/cross_backbone/mvadapter/layermap_g_complete.json')
rows.append({'claim_id':'MVADAPTER_GLOBAL_INTERACTION_CLUSTER_BOOTSTRAP','experiment':'MV-Adapter interface boundary','cohort':'MVADAPTER_G','N':98,
  'condition_A':'layer-by-window term','condition_B':'additive response','metric':'cluster-bootstrap interaction test',
  'effect':groot['interaction']['observed'],'p_raw':groot['interaction']['p_cluster_bootstrap'],
  'correction_family':'single global interaction test in frozen bootstrap audit',
  'analysis_classification':'cross-interface boundary; exploratory',
  'source_raw_file':str(gcells.relative_to(ROOT)),'source_script':'not preserved as a standalone cluster-bootstrap script; see frozen layermap JSON',
  'source_hash':sha(gcells),'source_analysis_file':str(gcells.relative_to(ROOT)),'source_analysis_sha256':sha(gcells),
  'allowed_wording':'The tested MV-Adapter global interaction was not detected.',
  'forbidden_wording':'Do not state equivalence or universal absence of an interaction.'})
# Frozen integrity and direction-audit counts.
for cid,rel,cohort,label in [
 ('FRESHC_PRIMARY_COMPLETION','1006/data/fresh_c/FRESH_C_INTEGRITY_GATE.json','FRESH_C','1200/1200 expected rows'),
 ('FRESHC_ADDENDUM_COMPLETION','1006/data/fresh_c/FRESH_C_ADDENDUM_INTEGRITY_GATE.json','FRESH_C_ADDENDUM','600/600 expected rows')]:
    gate=jload(rel)
    rows.append({'claim_id':cid,'experiment':label,'cohort':cohort,'N':gate['cohort_n'],
      'condition_A':'frozen protocol conditions','condition_B':'integrity gate','metric':'verified/expected rows',
      'effect':f"{gate['verified_rows']}/{gate['expected_rows']}",'analysis_classification':'integrity bookkeeping',
      'source_raw_file':rel,'source_script':'1006/scripts/run_fresh_c_locked_analyses_with_sign_audit.py',
      'source_hash':sha(ROOT/rel),'source_analysis_file':rel,'source_analysis_sha256':sha(ROOT/rel),
      'allowed_wording':'State exact row integrity result for the frozen cohort.',
      'forbidden_wording':'Do not describe the revision-era cohort as original-preregistration replication.'})
rows.append({'claim_id':'FRESHC_DIRECTION_AUDIT','experiment':'independent sign/direction audit','cohort':'FRESH_C','N':direction['n_objects'],
  'condition_A':'frozen primary/addendum contrasts','condition_B':'independent rederivation','metric':'contrast checks and sign errors',
  'effect':f"{len(direction['independent_checks'])} checks; {direction['sign_direction_error_count']} sign errors",
  'analysis_classification':'independent numerical direction audit','source_raw_file':'1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json',
  'source_script':'1006/scripts/validate_fresh_c_result_directions.py','source_hash':sha(ROOT/'1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json'),
  'source_analysis_file':'1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json',
  'source_analysis_sha256':sha(ROOT/'1006/data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json'),
  'allowed_wording':'The 28 frozen numerical direction checks had zero sign/direction errors.',
  'forbidden_wording':'This is a validation audit, not an additional cohort or experiment.'})
# Native cap constants are read from the canonical per-step cap table.
capcsv=ROOT/'1006/figures/strategy_comparison_gallery/cap_scale_semantics.csv'
with capcsv.open(newline='') as f: caprows=list(csv.DictReader(f))
cap_by_layer={}
for x in caprows: cap_by_layer.setdefault(x['layer_group'],float(x['cap']))
for layer,cap in cap_by_layer.items():
    rows.append({'claim_id':f"NATIVE_CAP_{layer.upper()}",'experiment':'Fresh C execution semantics','cohort':'FRESH_C',
      'condition_A':layer,'condition_B':'native cap','metric':'wrapper scale cap','effect':cap,
      'analysis_classification':'implementation constant from frozen execution profile',
      'source_raw_file':str(capcsv.relative_to(ROOT)),'source_script':'1006/scripts/plot_cap_scale_semantics.py',
      'source_hash':sha(capcsv),'source_analysis_file':'1006/evidence/audits/CAP_SCALE_SEMANTICS_FIGURE_NOTE_20261006.md',
      'source_analysis_sha256':sha(ROOT/'1006/evidence/audits/CAP_SCALE_SEMANTICS_FIGURE_NOTE_20261006.md'),
      'allowed_wording':'State as the native wrapper cap for the named layer group.',
      'forbidden_wording':'Do not interpret the cap as a matched realized residual dose.'})
# Atlas size/selection rule is a figure bookkeeping value, not an inferential sample size.
atlas=ROOT/'1006/figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json'
atlasdata=jload('1006/figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json')
rows.append({'claim_id':'FRESHC_ATLAS_GROUP_COUNT','experiment':'Fresh C qualitative navigation atlas','cohort':'FRESH_C','N':atlasdata['cohort_n'],
  'condition_A':'four frozen contrasts','condition_B':'rank-position strata','metric':'selected unique object groups','effect':len(atlasdata['selected_groups']),
  'analysis_classification':'qualitative navigation only; no per-object significance',
  'source_raw_file':str(atlas.relative_to(ROOT)),'source_script':'1006/scripts/generate_figures.py',
  'source_hash':sha(atlas),'source_analysis_file':str(atlas.relative_to(ROOT)),'source_analysis_sha256':sha(atlas),
  'allowed_wording':'Examples come from predefined rank strata and are a navigation aid, not inferential evidence.',
  'forbidden_wording':'Do not imply the examples were chosen manually after viewing or used to estimate cohort effects.'})

# strict-276 retrospective support row.
strict=ROOT/'1006/data/derived/strict276_c3_paired_summary.csv'
with strict.open(newline='') as f: strict_rows=list(csv.DictReader(f))
st=next(x for x in strict_rows if x['contrast']=='gc3-gfl' and x['metric']=='fg_psnr')
rows.append({'claim_id':'STRICT276_C3_GFL_FG_PSNR_RETROSPECTIVE','experiment':'strict-276 paired historical re-evaluation','cohort':'STRICT276','N':st['n'],
  'condition_A':'C3','condition_B':'GFL','metric':'fg_psnr','effect':st['mean_delta_left_minus_right'],
  'CI_lower':st['ci95_low'],'CI_upper':st['ci95_high'],'correction_family':'none; nominal supplemental interval',
  'favorable_fraction':int(st['favorable_objects'])/int(st['n']),'analysis_classification':'RETROSPECTIVE SUPPORT',
  'source_raw_file':str(strict.relative_to(ROOT)),'source_script':'1006/scripts/analyze_strict276_c3_retrospective.py',
  'source_hash':sha(strict),'source_analysis_file':'1006/data/strict276/CORE7_FINAL_PROVENANCE_AUDIT.md',
  'source_analysis_sha256':sha(ROOT/'1006/data/strict276/CORE7_FINAL_PROVENANCE_AUDIT.md'),
  'allowed_wording':'Retrospective same-cohort paired support, with incomplete historical runner/input provenance.',
  'forbidden_wording':'Do not call independent confirmation or a registered held-out replication.'})
# Account for every representative execution value as descriptive logged quantities.
for r in sem_rows:
    rows.append({'claim_id':f"EXEC_{r['strategy']}_T{int(r['step']):02d}_{r['depth'].upper()}",
      'experiment':'Fresh C implementation-aware execution accounting','cohort':'FRESH_C','N':r['object_count'],
      'condition_A':r['strategy'],'condition_B':'requested profile','metric':'applied correction L2 median (descriptive logged quantity)',
      'effect':r['applied_correction_l2_median'],'analysis_classification':'descriptive implementation accounting; representative recorded timestep',
      'source_raw_file':str(sem_src.relative_to(ROOT)),'source_script':'1006/scripts/summarize_fresh_c_execution_semantics.py',
      'source_hash':sha(sem_src),'source_analysis_file':'1006/evidence/audits/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.json',
      'source_analysis_sha256':sha(ROOT/'1006/evidence/audits/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.json'),
      'allowed_wording':'Report requested scale, applied scale, cap fraction, and applied correction norm as logged for this group and step.',
      'forbidden_wording':'Do not call nominal scales equal realized-dose interventions or interpret correction norm as a quality effect.',
      'requested_scale':r['requested_scale_values'],'applied_scale':r['applied_scale_values'],
      'cap_activation_fraction':r['cap_activated_wrapper_fraction'],'applied_correction_l2_median':r['applied_correction_l2_median']})
for row in rows:
    script_rel=row.get('source_script','')
    script_path=ROOT/script_rel if script_rel and not script_rel.startswith('source script') and not script_rel.startswith('existing validated') else None
    row['source_script_sha256']=sha(script_path) if script_path and script_path.exists() else ''
write_csv(AUD/'FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv',fields,rows)

# Figure candidate manifest: claim role and current release status.
figures=[
 {'figure':'A','role':'requested-to-applied-to-correction execution schematic','status':'AVAILABLE','path':'1006/figures/FRESH_C_EXECUTION_SEMANTICS.pdf','source':'1006/evidence/audits/FRESH_C_REQUESTED_APPLIED_RESIDUAL_ACCOUNTING.csv'},
 {'figure':'B','role':'Fresh C C3-GFL image-space confirmation','status':'GENERATED_FROM_CANONICAL_TABLE','path':'1006/figures/final_candidate/FIGURE_B_FRESH_C_C3_GFL.pdf','source':'1006/data/fresh_c/fresh_c_c3_minus_gfl_object_deltas.csv'},
 {'figure':'C','role':'Fresh C C3/LLH/linear endpoint and object tradeoffs','status':'GENERATED_FROM_CANONICAL_TABLE','path':'1006/figures/final_candidate/FIGURE_C_FRESH_C_TRADEOFFS.pdf','source':'1006/data/fresh_c/fresh_c_addendum_object_deltas.csv'},
 {'figure':'D','role':'20-group representative qualitative atlas','status':'AVAILABLE_LICENSE_VERIFIED_ATTRIBUTION_REQUIRED','path':'1006/figures/strategy_comparison_gallery/fresh_c_final/20_groups_contact_sheet.png','source':'1006/figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json; 1006/evidence/audits/FRESH_C_ATLAS_ATTRIBUTION_20261007.csv'},
 {'figure':'E','role':'GT texture complexity and failure-boundary characterization','status':'AVAILABLE_EXPLORATORY_FRESH_B','path':'1006/figures/evidence_alignment/fresh_b_gt_texture_complexity_heterogeneity.pdf','source':'1006/data/fresh_b/GT_TEXTURE_STATS_FRESH_CONFIRM_B.json'},
 {'figure':'F','role':'new 24-object native-UV unseen-view panel','status':'RETIRED_NO_NEW_PANEL','path':'','source':'1006/evidence/audits/FRESH_C_GLB_NATIVE_SAMPLER_INVENTORY.csv'},
 {'figure':'G','role':'cross-interface boundary; supplement candidate','status':'AVAILABLE_BOUNDED','path':'1006/figures/evidence_alignment/mvadapter_fg_lpips_interface_boundary.pdf;1006/figures/evidence_alignment/mvdiffusion_interface_boundary.pdf','source':'1006/data/derived/evidence_alignment/mvadapter_fg_lpips_cells.csv;1006/data/derived/evidence_alignment/mvdiffusion_interface_effects.csv'}]
write_csv(AUD/'FINAL_CANDIDATE_FIGURE_MANIFEST.csv',list(figures[0]),figures)

# Full evidence/path reconciliation against the published remote tree. Commit ancestry,
# current working-tree bytes, and remote blobs are kept separate to avoid calling old
# branch snapshots "unpushed" when they already exist publicly.
import os
remote_live=subprocess.check_output(['git','ls-remote','origin',REMOTE_REF],cwd=ROOT,text=True).strip().split('\t')[0]
counts_txt=subprocess.check_output(['git','rev-list','--left-right','--count','HEAD',REMOTE],cwd=ROOT,text=True).strip()
local_only,remote_only=map(int,counts_txt.split())
merge=subprocess.run(['git','merge-base','HEAD',REMOTE],cwd=ROOT,text=True,capture_output=True)
mergebase=merge.stdout.strip() if merge.returncode==0 else ''
remote_tree_raw=subprocess.check_output(['git','ls-tree','-r','-z','--full-tree',REMOTE],cwd=ROOT)
remote_tree={}
for rec in remote_tree_raw.split(b'\0'):
    if not rec: continue
    meta,path=rec.split(b'\t',1)
    mode,objtype,objhash=meta.decode().split(' ')
    remote_tree[path.decode('utf-8','surrogateescape')]=(mode,objtype,objhash)
raw=subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=all'],cwd=ROOT)
work={}; recs=raw.decode('utf-8','surrogateescape').split('\0');i=0
while i<len(recs) and recs[i]:
    rec=recs[i];i+=1
    code=rec[:2]; path=rec[3:]
    if code[0] in 'RC' or code[1] in 'RC': i+=1
    if path.startswith(('1006/','final/round2/','final/submission_new_0907/')): work[path]=code

def git_blob_sha(path):
    p=ROOT/path
    try:
        if p.is_symlink(): data=os.readlink(p).encode('utf-8','surrogateescape')
        elif p.is_file(): data=p.read_bytes()
        else: return ''
        return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    except (OSError,ValueError): return ''
def classify(path):
    low=path.lower()
    if any(k in low for k in ['human_study_raw_responses','human_study_slot_assignment','human_study_pair_mapping','human_study_object_uids']):
        return 'RESTRICTED_PARTICIPANT_LEVEL_DO_NOT_RELEASE'
    if low.endswith('.glb') or '/assets/' in low or 'contact_sheet' in low or '/panels/' in low:
        return 'THIRD_PARTY_ASSET_OR_DERIVATIVE_RIGHTS_REVIEW'
    if path.startswith(('1006/evidence/','1006/data/','1006/scripts/','1006/figures/','final/round2/scientific_validation_v3/')):
        return 'FORMAL_EVIDENCE_CANDIDATE'
    return 'PROJECT_CHANGE_REVIEW'
manifest=[]
for path,ws in sorted(work.items()):
    local_sha=git_blob_sha(path)
    remote=remote_tree.get(path)
    if remote is None: public_state='LOCAL_PATH_NOT_IN_PUBLIC_REMOTE'
    elif not local_sha: public_state='LOCAL_FILE_MISSING_PUBLIC_PATH_PRESENT'
    elif local_sha==remote[2]: public_state='SAME_BYTES_ALREADY_PUBLIC'
    else: public_state='LOCAL_CONTENT_DIFFERS_FROM_PUBLIC'
    manifest.append({'path':path,'working_tree_status':ws,'public_state':public_state,
      'local_blob_sha1':local_sha,'public_blob_sha1':remote[2] if remote else '',
      'classification':classify(path)})
# Preserve explicit public remote records for the participant-level decision even if
# this older local checkout has no corresponding file.
for path in sorted(remote_tree):
    if 'human_study_results_20261006/' not in path: continue
    if any(x['path']==path for x in manifest): continue
    manifest.append({'path':path,'working_tree_status':'not present in local status',
      'public_state':'PUBLIC_REMOTE_ONLY_OR_CLEAN_LOCAL_COPY','local_blob_sha1':'',
      'public_blob_sha1':remote_tree[path][2],
      'classification':'RESTRICTED_PARTICIPANT_LEVEL_DO_NOT_RELEASE'})
write_csv(AUD/'POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv',
 ['path','working_tree_status','public_state','local_blob_sha1','public_blob_sha1','classification'],manifest)
status_counts=Counter(work.values())
public_counts=Counter(x['public_state'] for x in manifest)
class_counts=Counter(x['classification'] for x in manifest)
rights_rows=list(csv.DictReader((AUD/'FINAL_ASSET_RIGHTS_AND_REDISTRIBUTION_LEDGER.csv').open(newline='')))
rights_count=Counter(x['final_disposition'] for x in rights_rows)
cohort_rights=json.loads((AUD/'FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.json').read_text())
cohort_rows=list(csv.DictReader((AUD/'FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv').open(newline='')))
cohort_dispositions=Counter(x['final_disposition'] for x in cohort_rows)
summary={'public_remote_head':remote_live,'expected_public_remote_head':REMOTE,'remote_head_matches_expected':remote_live==REMOTE,
 'local_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'local_branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
 'merge_base':mergebase or None,'local_only_commits':local_only,'remote_only_commits':remote_only,
 'local_head_is_ancestor_of_public_remote':local_only==0,
 'worktree_status_counts_in_scope':dict(status_counts),'public_comparison_counts':dict(public_counts),
 'path_manifest_rows':len(manifest),'path_manifest':str((AUD/'POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv').relative_to(ROOT)),
 'tracked_worktree_status_rows':sum(1 for v in work.values() if v!='??'),
 'untracked_worktree_status_rows':sum(1 for v in work.values() if v=='??'),
 'local_formal_evidence_not_public_or_changed':sum(1 for x in manifest if x['classification']=='FORMAL_EVIDENCE_CANDIDATE' and x['public_state'] in ('LOCAL_PATH_NOT_IN_PUBLIC_REMOTE','LOCAL_CONTENT_DIFFERS_FROM_PUBLIC')),
 'same_bytes_already_public':sum(1 for x in manifest if x['public_state']=='SAME_BYTES_ALREADY_PUBLIC'),
 'restricted_participant_paths':sum(1 for x in manifest if x['classification']=='RESTRICTED_PARTICIPANT_LEVEL_DO_NOT_RELEASE'),
 'asset_or_derivative_paths':sum(1 for x in manifest if x['classification']=='THIRD_PARTY_ASSET_OR_DERIVATIVE_RIGHTS_REVIEW'),
 'asset_rights_candidate_scope':{'fresh_c_cohort_dispositions':dict(cohort_dispositions),
   'cohort_api_checked_count':cohort_rights['current_api_checked_count'],'cohort_api_status_counts':cohort_rights['http_status_counts'],
   'atlas_attribution_verified':cohort_rights['atlas_attribution_verified'],'legacy_48_row_dispositions':dict(rights_count),
   'candidate_figure_scope':'CLOSED_WITH_EXCLUSIONS'},
 'authority_rows':len(rows),'execution_representative_rows':len(sem_rows),
 'note':'The local HEAD is an ancestor of the public tip. The local working tree is dirty and is compared file-by-file to public remote blob contents. No push or checkout change was performed. The path manifest omits its own self-referential hash and records finalized hashes for the reconciliation JSON and Markdown.'}
(AUD/'POST_FRESH_C_REPOSITORY_RECONCILIATION_20261007.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

ledger=jload('1006/evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json')
recon=f'''# Post-Fresh-C repository reconciliation — 2026-10-07

## Git identity and local/public comparison

- Public branch `codex/scientific-validation-v3-20261006`: `{summary['public_remote_head']}` (matches the requested public SHA).
- Local branch `{summary['local_branch']}` at `{summary['local_head']}`.
- The local HEAD is an ancestor of the public tip: **0 local-only commits, {summary['remote_only_commits']} public commits beyond local HEAD**. This is not a linear “files after f5” range.
- The worktree was not reset, staged, committed, fetched, or pushed. It remains dirty: **{summary['tracked_worktree_status_rows']:,} tracked status entries and {summary['untracked_worktree_status_rows']:,} untracked file entries** in the reconciled project scope.
- Current local files were compared byte-for-byte with public remote blobs. The inventory has {summary['path_manifest_rows']:,} rows: {summary['public_comparison_counts'].get('SAME_BYTES_ALREADY_PUBLIC',0):,} already-public exact matches, {summary['public_comparison_counts'].get('LOCAL_PATH_NOT_IN_PUBLIC_REMOTE',0):,} local paths absent from the public tree, {summary['public_comparison_counts'].get('LOCAL_CONTENT_DIFFERS_FROM_PUBLIC',0):,} local paths with changed contents, and {summary['public_comparison_counts'].get('PUBLIC_REMOTE_ONLY_OR_CLEAN_LOCAL_COPY',0):,} public participant-level paths not represented as dirty local files.
- Formal local evidence paths absent from or different from the public tree: **{summary['local_formal_evidence_not_public_or_changed']:,}**, listed path-by-path in [`POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv`](POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv). The manifest classifies participant-level and third-party asset/derivative paths separately.

Because the local branch is behind and the tree is highly dirty, this reconciliation is an inventory only. No reset, new staging operation, commit, fetch, push, merge, cherry-pick, cleanup, or history rewrite was performed; pre-existing staged/dirty state was preserved.

## Evidence status

| Evidence item | Current status | Record |
|---|---|---|
| Fresh C primary | PASS — N=300, 1200/1200 | `data/fresh_c/FRESH_C_INTEGRITY_GATE.json`; 7 frozen endpoints. |
| LLH/generic-linear addendum | PASS — same N=300 cohort, 600/600 | `data/fresh_c/FRESH_C_ADDENDUM_INTEGRITY_GATE.json`; 21 frozen tests. |
| Sign/direction audit | PASS — 28 checks, 0 errors | `data/fresh_c/FRESH_C_RESULT_DIRECTION_AUDIT.json`. |
| Fresh C atlas | PASS — 20 locked rank-stratum groups; all 20 source licenses currently verify as CC BY; attribution schedule prepared | `figures/strategy_comparison_gallery/fresh_c_final/gallery_manifest.json`; `FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`. |
| Authority ledger | PASS as evidence bookkeeping — {ledger['run_count']} runs, {ledger['run_condition_record_count']} condition records | `evidence/audits/FINAL_EVIDENCE_AUTHORITY_LEDGER_20261006.json`; validation record remains separate from science freeze. |
| Novelty audit | COMPLETE; R2.1 OPEN / VENUE RISK | `evidence/audits/FINAL_R21_CONTRIBUTION_AUDIT.md`. |
| GLB feasibility | Sampler inventory complete; synthetic checks 11/11 PASS; full 24-object native-UV/alpha gate FAIL | `FRESH_C_GLB_NATIVE_SAMPLER_AUDIT.md`; new 3D panel formally retired. |
| Readiness | HOLD / not ready for manuscript rewrite or release | `gates/NON_HUMAN_EVIDENCE_FREEZE_VERDICT_20261007.md` supersedes the earlier dated readiness snapshot for this closure. |

The numerical authority file has {summary['authority_rows']} rows and includes the frozen Fresh C endpoint contrasts, selected interaction and boundary results, execution records, and source hashes. Figures B/C were regenerated locally from canonical Fresh C paired-delta tables. A clean-checkout rebuild of this current candidate has not passed.

## Files prohibited from any new public/supplement package

- Participant-level files present in the public remote tree: `HUMAN_STUDY_RAW_RESPONSES.csv`, `HUMAN_STUDY_SLOT_ASSIGNMENT.csv`, `HUMAN_STUDY_PAIR_MAPPING.csv`, and `HUMAN_STUDY_OBJECT_UIDS.csv`. The decision is `PUBLIC_RAW_HUMAN_DATA=NO`; no response values or results were analyzed in this phase.
- Source GLBs and the {cohort_dispositions.get('UNKNOWN',0)} `UNKNOWN` Fresh C cohort assets are excluded from the candidate package. The {cohort_rights['atlas_attribution_verified']}-model Figure D atlas is eligible only with the prepared row-level CC BY attributions. UID-linked per-object tables are not part of the proposed public package; aggregate results may be retained.
- The preserved historical 48-row ledger still records {rights_count.get('FIGURE_ONLY',0)} `FIGURE_ONLY` and {rights_count.get('UNKNOWN',0)} `UNKNOWN` rows; its legacy assets are not current candidate figures.
- Forensic/debug history, caches, and experiment run logs in a reviewer-facing package.

## Conditional candidates for an anonymous supplement

After a clean-candidate rebuild and author release approval, the candidate list may include aggregate [`FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv`](FINAL_MANUSCRIPT_NUMERICAL_AUTHORITY.csv), analysis/figure scripts, frozen non-human protocols, synthetic sampler validation, Figures A–C, Figure D with [`FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`](FRESH_C_ATLAS_ATTRIBUTION_20261007.csv), and aggregate Fresh C tables. Figures E/G contain metric plots rather than source-asset imagery. No source GLBs, the 9 unknown assets, or UID-linked per-object tables are eligible under this scope; the 300-row rights inventory remains an audit record, not a release manifest.

'''
(AUD/'POST_FRESH_C_REPOSITORY_RECONCILIATION_20261007.md').write_text(recon)

# The reconciliation outputs are written after the initial inventory pass.
# Refresh their hashes and avoid the impossible self-hash of the path manifest.
manifest_path=str((AUD/'POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv').relative_to(ROOT))
for row in manifest:
    if row['path']==manifest_path:
        row['local_blob_sha1']='SELF_HASH_OMITTED_TO_AVOID_SELF_REFERENCE'
    elif row['path'] in {'1006/evidence/audits/POST_FRESH_C_REPOSITORY_RECONCILIATION_20261007.json',
                         '1006/evidence/audits/POST_FRESH_C_REPOSITORY_RECONCILIATION_20261007.md'}:
        row['local_blob_sha1']=git_blob_sha(row['path'])
write_csv(AUD/'POST_FRESH_C_UNPUSHED_FILE_MANIFEST.csv',
 ['path','working_tree_status','public_state','local_blob_sha1','public_blob_sha1','classification'],manifest)
