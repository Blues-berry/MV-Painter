from pathlib import Path
import json,hashlib,csv,ast
r=Path(__file__).resolve().parents[1]/'data/training_audit';m=json.loads((r/'TRAINING_AUDIT.json').read_text())
assert m['status']=='COMPLETE_RECORDED_TRAINING_AUDIT_WITH_REPLAY_LIMITS'
for name,h in m['recorded_artifact_hashes'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==h
for name,v in m['source_comparisons'].items():assert hashlib.sha256((r/name.replace('/','__')).read_bytes()).hexdigest()==v['source_commit_sha256']
code=ast.parse((r/'geotex__train.py').read_text());assert not any(isinstance(n,ast.Attribute) and n.attr=='drop_cond_prob' for n in ast.walk(code))
values=[ast.literal_eval(n.value) for n in ast.walk(code) if isinstance(n,ast.keyword) and n.arg=='is_drop'];assert values==m['actual_entry_is_drop_values'] and all(x is False for x in values)
rows=list(csv.DictReader((r/'train_metrics.csv').open()));assert [int(x['step']) for x in rows]==list(range(1,2001))
train=set((r/'train_objects_full_1118.txt').read_text().splitlines());fresh=set((r/'fresh_c_objects.txt').read_text().splitlines())
assert len(train)==1118 and len(fresh)==300 and not train&fresh and not m['train_fresh_overlap']
assert hashlib.sha256((r/'fresh_c_objects.txt').read_bytes()).hexdigest()==m['fresh_uid_list_sha256']
assert m['training_image_size']==256 and not m['checkpoint_has_embedded_step'] and len(m['replay_limits'])>=4
print('PASS: recorded source/config/list/step lineage, conditional-only entry and explicit exact-replay limits')
