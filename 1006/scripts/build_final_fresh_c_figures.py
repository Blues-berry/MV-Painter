#!/usr/bin/env python3
"""Build frozen Fresh C manuscript-candidate figures from canonical tables."""
from __future__ import annotations
import csv, json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '1006' / 'figures' / 'final_candidate'
OUT.mkdir(parents=True, exist_ok=True)
PRIMARY_JSON = ROOT / '1006/data/fresh_c/fresh_c_c3_minus_gfl_analysis.json'
PRIMARY_DELTA = ROOT / '1006/data/fresh_c/fresh_c_c3_minus_gfl_object_deltas.csv'
ADD_JSON = ROOT / '1006/data/fresh_c/FRESH_C_ADDENDUM_ANALYSIS.json'
ADD_DELTA = ROOT / '1006/data/fresh_c/fresh_c_addendum_object_deltas.csv'

with PRIMARY_JSON.open() as f: primary = json.load(f)
with ADD_JSON.open() as f: addendum = json.load(f)
with PRIMARY_DELTA.open(newline='') as f: primary_rows = list(csv.DictReader(f))
with ADD_DELTA.open(newline='') as f: add_rows = list(csv.DictReader(f))

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 10,
    'axes.labelsize': 9, 'figure.titlesize': 13, 'pdf.fonttype': 42,
    'ps.fonttype': 42, 'axes.spines.top': False, 'axes.spines.right': False,
})

# Figure B: object-level paired deltas plus frozen estimate/CI/favorable fraction.
fig, axes = plt.subplots(2, 2, figsize=(9.0, 5.6), gridspec_kw={'width_ratios': [1.7, 1]})
metrics = [
    ('fg_psnr', 'Foreground PSNR (dB)', '#2b6f9c', 'higher'),
    ('fg_lpips', 'Foreground LPIPS', '#c26a2b', 'lower'),
]
for r, (key, label, color, direction) in enumerate(metrics):
    vals = np.array([float(x[key]) for x in primary_rows])
    st = primary['tests'][key]
    ax = axes[r, 0]
    ax.hist(vals, bins=30, color=color, alpha=.78, edgecolor='white', linewidth=.35)
    ax.axvline(0, color='#444444', linewidth=.9, linestyle='--')
    ax.axvline(st['median'], color='#3e3e3e', linewidth=1, linestyle=':', label=f"median {st['median']:.4g}")
    ax.set_title(label)
    ax.set_xlabel('Per-object paired delta (C3 − GFL)')
    ax.set_ylabel('Objects')
    ax.legend(frameon=False, fontsize=8, loc='upper right')

    ax = axes[r, 1]
    lo, hi = st['bootstrap_ci95']
    ax.errorbar([st['mean']], [-.34], xerr=[[st['mean']-lo], [hi-st['mean']]],
                fmt='o', color=color, capsize=4, markersize=5, linewidth=1.5)
    ax.axvline(0, color='#444444', linewidth=.9, linestyle='--')
    fav = st['favorable_object_fraction']
    ax.text(.04, .98, f"mean {st['mean']:.4g}\n95% CI [{lo:.4g}, {hi:.4g}]\nmedian {st['median']:.4g}\nfavorable {fav:.1%}",
            transform=ax.transAxes, va='top', ha='left', fontsize=7.4,
            bbox={'facecolor':'white','edgecolor':'none','alpha':.92,'pad':1.3})
    ax.set_yticks([])
    ax.set_xlabel('Mean paired delta')
    ax.set_title('Frozen object-level estimate')
    ax.set_ylim(-.65, .65)
    ax.set_xlim(min(lo, 0) - abs(hi-lo)*1.5, max(hi, 0) + abs(hi-lo)*1.5)
fig.suptitle('Fresh C confirmation: C3 − GFL (N = 300 objects)', y=.99)
fig.text(.5, .01, 'Positive LPIPS deltas favor GFL because lower LPIPS is better. No cross-metric winner is implied.', ha='center', fontsize=8)
fig.tight_layout(rect=[0, .035, 1, .96])
fig.savefig(OUT / 'FIGURE_B_FRESH_C_C3_GFL.pdf', bbox_inches='tight')
fig.savefig(OUT / 'FIGURE_B_FRESH_C_C3_GFL.png', dpi=320, bbox_inches='tight')
plt.close(fig)

# Figure C: three direct strategy contrasts, showing both metrics and object distributions.
contrasts = [
    ('LLH-C3', 'LLH − C3'), ('LLH-linear', 'LLH − generic linear'), ('C3-linear', 'C3 − generic linear')
]
metric_specs = [
    ('fg_psnr', 'Foreground PSNR (dB)', '#2b6f9c', 'higher'),
    ('fg_lpips', 'Foreground LPIPS', '#c26a2b', 'lower'),
]
fig, axes = plt.subplots(2, 3, figsize=(12.0, 6.2))
for ci, (contrast, title) in enumerate(contrasts):
    rows = [x for x in add_rows if x['contrast'] == contrast]
    tests = {x['metric']: x for x in addendum['tests'] if x['contrast'] == contrast}
    for ri, (metric, metric_label, color, direction) in enumerate(metric_specs):
        ax = axes[ri, ci]
        vals = np.array([float(x[metric]) for x in rows])
        st = tests[metric]
        ax.hist(vals, bins=25, color=color, alpha=.76, edgecolor='white', linewidth=.3)
        ax.axvline(0, color='#444444', linewidth=.85, linestyle='--')
        ax.axvline(st['median'], color='#3e3e3e', linewidth=1, linestyle=':')
        lo, hi = st['bootstrap_ci95']
        fav = st['favorable_object_fraction_for_a']
        # Compact frozen summary; no significance star or global score.
        ax.text(.03, .96,
                f"mean {st['mean']:.4g} [{lo:.4g}, {hi:.4g}]\nmedian {st['median']:.4g} | A favorable {fav:.1%}",
                transform=ax.transAxes, va='top', ha='left', fontsize=7.5,
                bbox={'facecolor':'white','edgecolor':'none','alpha':.8,'pad':1.5})
        ax.set_xlabel('Paired object delta (A − B)')
        if ci == 0: ax.set_ylabel(metric_label + '\nObjects')
        if ri == 0: ax.set_title(title)
fig.suptitle('Fresh C addendum: endpoint and object-level trade-offs (N = 300 objects)', y=.995)
fig.text(.5, .01, 'A favorable means higher PSNR or lower LPIPS for condition A. Distributions are paired object deltas; no overall winner is defined.', ha='center', fontsize=8)
fig.tight_layout(rect=[0, .04, 1, .96])
fig.savefig(OUT / 'FIGURE_C_FRESH_C_TRADEOFFS.pdf', bbox_inches='tight')
fig.savefig(OUT / 'FIGURE_C_FRESH_C_TRADEOFFS.png', dpi=320, bbox_inches='tight')
plt.close(fig)

# Figure provenance manifest contains exact frozen source hashes and output hashes.
import hashlib

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {
    'status': 'GENERATED_FROM_FROZEN_CANONICAL_TABLES',
    'cohort': 'Fresh C, N=300 objects',
    'sources': {str(p.relative_to(ROOT)): sha(p) for p in [PRIMARY_JSON, PRIMARY_DELTA, ADD_JSON, ADD_DELTA]},
    'generator': str(Path(__file__).relative_to(ROOT)),
    'figures': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p), 'bytes': p.stat().st_size}
                for p in sorted(OUT.glob('FIGURE_*')) if p.suffix in {'.pdf', '.png'}],
    'interpretation_limit': 'These figures summarize the frozen image-space analyses only. They do not establish human perceptual fidelity, 3D appearance, or an overall winning strategy.'
}
(OUT / 'FIGURE_SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'output_dir':str(OUT),'figures':[x['path'] for x in manifest['figures']]}, indent=2))
