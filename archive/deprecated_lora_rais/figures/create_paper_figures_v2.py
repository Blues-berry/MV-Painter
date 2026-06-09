"""Generate comprehensive paper figures with 20 objects."""
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import re

base = '/4T/CXY/MV-Painter/MVPainter'
baseline_dir = f'{base}/PBR/results/baseline-73-20'
ours_dir = f'{base}/PBR/results/ours-73-v2-20'
output_dir = f'{base}/PBR/figures_20'
os.makedirs(output_dir, exist_ok=True)

baseline_entries = set(os.listdir(baseline_dir))
ours_entries = set(os.listdir(ours_dir))
print(f"Baseline: {len(baseline_entries)} entries, Ours: {len(ours_entries)} entries")
print(f"Baseline sample: {sorted(baseline_entries)[:3]}")
print(f"Ours sample: {sorted(ours_entries)[:3]}")
common_objs = sorted(baseline_entries & ours_entries)
common_objs = [o for o in common_objs if o.startswith('object_')]
print(f"Found {len(common_objs)} common objects")

# Figure 1: Main comparison (20 objects, 4 columns: GT, Baseline, Ours, Error)
n_objs = min(20, len(common_objs))
fig, axes = plt.subplots(n_objs, 4, figsize=(16, 4*n_objs))

for i, obj in enumerate(common_objs[:n_objs]):
    gt = os.path.join(baseline_dir, obj, 'gt_view0_albedo.png')
    bl = os.path.join(baseline_dir, obj, 'pred_view0_albedo.png')
    ou = os.path.join(ours_dir, obj, 'pred_view0_albedo.png')

    if os.path.exists(gt): axes[i,0].imshow(Image.open(gt))
    axes[i,0].axis('off')
    if i==0: axes[i,0].set_title('GT', fontsize=12)

    if os.path.exists(bl): axes[i,1].imshow(Image.open(bl))
    axes[i,1].axis('off')
    if i==0: axes[i,1].set_title('Baseline', fontsize=12)

    if os.path.exists(ou): axes[i,2].imshow(Image.open(ou))
    axes[i,2].axis('off')
    if i==0: axes[i,2].set_title('Ours (MV-Cons)', fontsize=12)

    if os.path.exists(gt) and os.path.exists(ou):
        g = np.array(Image.open(gt)).astype(float)
        o = np.array(Image.open(ou).resize((g.shape[1],g.shape[0]))).astype(float)
        e = np.mean(np.abs(g-o), axis=2)/255.0
        axes[i,3].imshow(e, cmap='hot', vmin=0, vmax=0.3)
    axes[i,3].axis('off')
    if i==0: axes[i,3].set_title('Error', fontsize=12)

plt.suptitle('Albedo Comparison: Baseline vs Ours (20 objects)', fontsize=14)
plt.tight_layout()
plt.savefig(f'{output_dir}/paper_main_comparison_20.png', dpi=150, bbox_inches='tight')
print('Saved paper_main_comparison_20.png')
plt.close()

# Figure 2: Normal map comparison (10 objects)
fig, axes = plt.subplots(10, 4, figsize=(16, 40))
for i, obj in enumerate(common_objs[:10]):
    gt = os.path.join(baseline_dir, obj, 'gt_view0_normal.png')
    bl = os.path.join(baseline_dir, obj, 'pred_view0_normal.png')
    ou = os.path.join(ours_dir, obj, 'pred_view0_normal.png')

    if os.path.exists(gt): axes[i,0].imshow(Image.open(gt))
    axes[i,0].axis('off')
    if i==0: axes[i,0].set_title('GT', fontsize=12)

    if os.path.exists(bl): axes[i,1].imshow(Image.open(bl))
    axes[i,1].axis('off')
    if i==0: axes[i,1].set_title('Baseline', fontsize=12)

    if os.path.exists(ou): axes[i,2].imshow(Image.open(ou))
    axes[i,2].axis('off')
    if i==0: axes[i,2].set_title('Ours', fontsize=12)

    if os.path.exists(gt) and os.path.exists(ou):
        g = np.array(Image.open(gt)).astype(float)
        o = np.array(Image.open(ou).resize((g.shape[1],g.shape[0]))).astype(float)
        e = np.mean(np.abs(g-o), axis=2)/255.0
        axes[i,3].imshow(e, cmap='hot', vmin=0, vmax=0.3)
    axes[i,3].axis('off')
    if i==0: axes[i,3].set_title('Error', fontsize=12)

plt.suptitle('Normal Map Comparison: Baseline vs Ours', fontsize=14)
plt.tight_layout()
plt.savefig(f'{output_dir}/comparison_normal_10.png', dpi=150, bbox_inches='tight')
print('Saved comparison_normal_10.png')
plt.close()

# Figure 3: Material comparison (10 objects)
fig, axes = plt.subplots(10, 4, figsize=(16, 40))
for i, obj in enumerate(common_objs[:10]):
    gt = os.path.join(baseline_dir, obj, 'gt_view0_material.png')
    bl = os.path.join(baseline_dir, obj, 'pred_view0_material.png')
    ou = os.path.join(ours_dir, obj, 'pred_view0_material.png')

    if os.path.exists(gt): axes[i,0].imshow(Image.open(gt))
    axes[i,0].axis('off')
    if i==0: axes[i,0].set_title('GT', fontsize=12)

    if os.path.exists(bl): axes[i,1].imshow(Image.open(bl))
    axes[i,1].axis('off')
    if i==0: axes[i,1].set_title('Baseline', fontsize=12)

    if os.path.exists(ou): axes[i,2].imshow(Image.open(ou))
    axes[i,2].axis('off')
    if i==0: axes[i,2].set_title('Ours', fontsize=12)

    if os.path.exists(gt) and os.path.exists(ou):
        g = np.array(Image.open(gt)).astype(float)
        o = np.array(Image.open(ou).resize((g.shape[1],g.shape[0]))).astype(float)
        e = np.mean(np.abs(g-o), axis=2)/255.0
        axes[i,3].imshow(e, cmap='hot', vmin=0, vmax=0.3)
    axes[i,3].axis('off')
    if i==0: axes[i,3].set_title('Error', fontsize=12)

plt.suptitle('Material Comparison: Baseline vs Ours', fontsize=14)
plt.tight_layout()
plt.savefig(f'{output_dir}/comparison_material_10.png', dpi=150, bbox_inches='tight')
print('Saved comparison_material_10.png')
plt.close()

# Figure 4: Cross-view comparison (3 objects, 4 views)
for obj_idx in range(3):
    obj = common_objs[obj_idx]
    fig, axes = plt.subplots(4, 3, figsize=(12, 16))

    for v in range(4):
        gt = os.path.join(baseline_dir, obj, f'gt_view{v}_albedo.png')
        bl = os.path.join(baseline_dir, obj, f'pred_view{v}_albedo.png')
        ou = os.path.join(ours_dir, obj, f'pred_view{v}_albedo.png')

        if os.path.exists(gt): axes[v,0].imshow(Image.open(gt))
        axes[v,0].axis('off')
        axes[v,0].set_title(f'GT View {v}' if v==0 else f'View {v}', fontsize=10)

        if os.path.exists(bl): axes[v,1].imshow(Image.open(bl))
        axes[v,1].axis('off')
        if v==0: axes[v,1].set_title('Baseline', fontsize=10)

        if os.path.exists(ou): axes[v,2].imshow(Image.open(ou))
        axes[v,2].axis('off')
        if v==0: axes[v,2].set_title('Ours', fontsize=10)

    plt.suptitle(f'{obj}: Cross-View Albedo Comparison', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cross_view_{obj}.png', dpi=150, bbox_inches='tight')
    print(f'Saved cross_view_{obj}.png')
    plt.close()

# Figure 5: Training stability with loss curves
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for name, lf, c in [('Baseline','logs/baseline_73_final.log','steelblue'),('Ours','logs/ours_73_v2.log','coral')]:
    with open(lf) as f: content = f.read()
    losses = [float(x) for x in re.findall(r'step_loss=([0-9.]+)', content)]
    smoothed = np.convolve(losses, np.ones(500)/500, 'valid')
    axes[0].plot(smoothed, color=c, linewidth=1.5, label=name)
axes[0].set_title('Loss Curve', fontsize=12)
axes[0].set_xlabel('Step')
axes[0].set_ylabel('Loss')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(0, 0.3)

for name, lf, c in [('Baseline','logs/baseline_73_final.log','steelblue'),('Ours','logs/ours_73_v2.log','coral')]:
    with open(lf) as f: content = f.read()
    losses = [min(float(x),1.0) for x in re.findall(r'step_loss=([0-9.]+)', content)]
    axes[1].hist(losses, bins=50, color=c, alpha=0.5, label=name, density=True)
axes[1].set_title('Loss Distribution', fontsize=12)
axes[1].set_xlabel('Loss')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

bars = axes[2].bar(['Baseline','Ours'], [407,53], color=['steelblue','coral'], width=0.5)
axes[2].set_title('Loss Spikes (>1.0)', fontsize=12)
axes[2].set_ylabel('Count')
axes[2].grid(True, alpha=0.3, axis='y')
for b in bars:
    h = b.get_height()
    axes[2].annotate(f'{int(h)}', xy=(b.get_x()+b.get_width()/2,h), xytext=(0,3), textcoords='offset points', ha='center', fontsize=11)
plt.suptitle('Training Stability', fontsize=14)
plt.tight_layout()
plt.savefig(f'{output_dir}/training_stability.png', dpi=150, bbox_inches='tight')
print('Saved training_stability.png')
plt.close()

# Figure 6: Ablation weight
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
w = [0, 0.001, 0.01, 0.05, 0.1, 0.5]
psnr = [33.20, 33.16, 32.85, 31.31, 29.82, 23.78]
cv = [17.62, 17.61, 17.58, 17.50, 17.33, 15.59]
axes[0].plot(w, psnr, 'o-', color='steelblue', linewidth=2, markersize=8)
axes[0].set_xlabel('Weight'); axes[0].set_ylabel('PSNR (dB)'); axes[0].set_title('PSNR vs Weight')
axes[0].grid(True, alpha=0.3); axes[0].axvline(x=0.01, color='red', linestyle='--', alpha=0.5, label='Chosen'); axes[0].legend()
axes[1].plot(w, cv, 'o-', color='coral', linewidth=2, markersize=8)
axes[1].set_xlabel('Weight'); axes[1].set_ylabel('CV Albedo'); axes[1].set_title('CV Albedo vs Weight')
axes[1].grid(True, alpha=0.3); axes[1].axvline(x=0.01, color='red', linestyle='--', alpha=0.5, label='Chosen'); axes[1].legend()
plt.suptitle('Ablation: Consistency Weight', fontsize=14)
plt.tight_layout()
plt.savefig(f'{output_dir}/ablation_weight.png', dpi=150, bbox_inches='tight')
print('Saved ablation_weight.png')
plt.close()

print('All paper figures generated!')
