"""Analyze extended scale sweep results: selection criteria, regression analysis, visual audit manifest.

Run after extended sweep completes.
Usage: python geotex/analyze_extended_sweep.py
"""
import csv, numpy as np, os, json

PREV_DIR = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_50obj"
EXT_DIR = "mvpoutput/geotex_refattn_v1/scale_sweep_v1_extended_50obj"
OUTPUT_DIR = EXT_DIR


def load_all_scales():
    """Load per-object data from both previous and extended sweeps."""
    all_data = {}
    for base in [PREV_DIR, EXT_DIR]:
        if not os.path.exists(base):
            continue
        for d in sorted(os.listdir(base)):
            path = f'{base}/{d}/per_object_metrics.csv'
            if not os.path.exists(path):
                continue
            with open(path) as f:
                rows = list(csv.DictReader(f))
            scale = float(rows[0]['scale'])
            all_data[scale] = rows
    return all_data


def compute_stats(all_data, scale):
    """Compute mean, median, positive ratio for key metrics at a given scale."""
    rows = all_data[scale]
    n = len(rows)
    metrics = ['delta_fg_ssim', 'delta_nef_ssim', 'delta_edge_ssim',
               'delta_fg_lpips', 'delta_crop_ssim', 'delta_crop_lpips', 'delta_full_psnr']
    stats = {'scale': scale, 'n': n}
    for m in metrics:
        vals = [float(r[m]) for r in rows if r.get(m) and r[m] != 'None']
        if vals:
            stats[m] = {
                'mean': float(np.mean(vals)),
                'median': float(np.median(vals)),
                'std': float(np.std(vals)),
                'positive': int(np.sum(np.array(vals) > 0)),
                'total': len(vals),
            }
    return stats


def compare_scales(all_data, scale_a, scale_b):
    """Compare two scales per-object. Returns list of (obj_idx, delta) for FG SSIM."""
    da = {int(r['object_idx']): float(r['delta_fg_ssim']) for r in all_data[scale_a]}
    db = {int(r['object_idx']): float(r['delta_fg_ssim']) for r in all_data[scale_b]}
    common = sorted(set(da.keys()) & set(db.keys()))
    diffs = [(obj, db[obj] - da[obj]) for obj in common]
    return diffs


def count_regressions(diffs, threshold):
    """Count objects where delta < -threshold."""
    return sum(1 for _, d in diffs if d < -threshold)


def main():
    all_data = load_all_scales()
    scales = sorted(all_data.keys())
    print(f"Loaded {len(scales)} scales: {scales}\n")

    # === Task 3: Selection criteria ===
    print("=" * 80)
    print("TASK 3: BEST SCALE SELECTION CRITERIA")
    print("=" * 80)

    # Reference scales
    ref_125 = 1.25 if 1.25 in all_data else None
    ref_150 = 1.50 if 1.50 in all_data else None

    print(f"\n{'Scale':>6} | {'FG mean':>9} {'FG med':>8} {'FG pos':>7} | "
          f"{'NEF mean':>9} {'NEF med':>8} | {'Edge mean':>10} | "
          f"{'Crop L mean':>11} | {'PSNR':>8}")
    print("-" * 100)

    all_stats = {}
    for s in scales:
        stats = compute_stats(all_data, s)
        all_stats[s] = stats
        fg = stats.get('delta_fg_ssim', {})
        nef = stats.get('delta_nef_ssim', {})
        edge = stats.get('delta_edge_ssim', {})
        cl = stats.get('delta_crop_lpips', {})
        psnr = stats.get('delta_full_psnr', {})
        print(f"{s:6.2f} | {fg.get('mean',0):+.4f}  {fg.get('median',0):+.4f}  "
              f"{fg.get('positive',0)}/{fg.get('total',0):2d} | "
              f"{nef.get('mean',0):+.4f}  {nef.get('median',0):+.4f} | "
              f"{edge.get('mean',0):+.4f} | {cl.get('mean',0):+.4f} | "
              f"{psnr.get('mean',0):+.2f}")

    # Find best scale by FG SSIM mean
    best_fg_scale = max(scales, key=lambda s: all_stats[s].get('delta_fg_ssim', {}).get('mean', -999))
    best_nef_scale = max(scales, key=lambda s: all_stats[s].get('delta_nef_ssim', {}).get('mean', -999))
    print(f"\nBest FG SSIM: s={best_fg_scale:.2f} (mean={all_stats[best_fg_scale]['delta_fg_ssim']['mean']:+.4f})")
    print(f"Best NEF SSIM: s={best_nef_scale:.2f} (mean={all_stats[best_nef_scale]['delta_nef_ssim']['mean']:+.4f})")

    # Regression analysis vs s=1.25 and s=1.50
    print(f"\n--- Regression analysis vs s=1.25 ---")
    if ref_125:
        for s in scales:
            if s <= 1.25:
                continue
            diffs = compare_scales(all_data, ref_125, s)
            n = len(diffs)
            better = sum(1 for _, d in diffs if d > 0)
            worse = sum(1 for _, d in diffs if d < 0)
            sev_03 = count_regressions(diffs, 0.03)
            sev_05 = count_regressions(diffs, 0.05)
            mean_d = np.mean([d for _, d in diffs])
            print(f"  s={s:.2f} vs 1.25: {better}/{n} better, {worse}/{n} worse, "
                  f"mean={mean_d:+.4f}, reg>0.03={sev_03}, reg>0.05={sev_05}")

    print(f"\n--- Regression analysis vs s=1.50 ---")
    if ref_150:
        for s in scales:
            if s <= 1.50:
                continue
            diffs = compare_scales(all_data, ref_150, s)
            n = len(diffs)
            better = sum(1 for _, d in diffs if d > 0)
            worse = sum(1 for _, d in diffs if d < 0)
            sev_03 = count_regressions(diffs, 0.03)
            sev_05 = count_regressions(diffs, 0.05)
            mean_d = np.mean([d for _, d in diffs])
            print(f"  s={s:.2f} vs 1.50: {better}/{n} better, {worse}/{n} worse, "
                  f"mean={mean_d:+.4f}, reg>0.03={sev_03}, reg>0.05={sev_05}")

    # Worst-10 regressions at best scale vs s=1.25
    if ref_125 and best_fg_scale != ref_125:
        print(f"\n--- Worst-10 FG SSIM regressions: s={best_fg_scale:.2f} vs s=1.25 ---")
        diffs = compare_scales(all_data, ref_125, best_fg_scale)
        diffs.sort(key=lambda x: x[1])
        for obj, d in diffs[:10]:
            print(f"  obj={obj:3d} Δ={d:+.4f}")

    # === Task 4: Stop condition ===
    print(f"\n{'='*80}")
    print("TASK 4: STOP CONDITION CHECK")
    print("=" * 80)

    fg_trend = [(s, all_stats[s]['delta_fg_ssim']['mean']) for s in scales if 'delta_fg_ssim' in all_stats[s]]
    nef_trend = [(s, all_stats[s]['delta_nef_ssim']['mean']) for s in scales if 'delta_nef_ssim' in all_stats[s]]

    print(f"\nFG SSIM trend:")
    for i in range(1, len(fg_trend)):
        delta = fg_trend[i][1] - fg_trend[i-1][1]
        marker = " ← DECLINING" if delta < 0 else ""
        print(f"  s={fg_trend[i-1][0]:.2f} → s={fg_trend[i][0]:.2f}: {delta:+.4f}{marker}")

    print(f"\nNEF SSIM trend:")
    for i in range(1, len(nef_trend)):
        delta = nef_trend[i][1] - nef_trend[i-1][1]
        marker = " ← DECLINING" if delta < 0 else ""
        print(f"  s={nef_trend[i-1][0]:.2f} → s={nef_trend[i][0]:.2f}: {delta:+.4f}{marker}")

    # Check stop condition
    stop = False
    if len(fg_trend) >= 2:
        fg_last_delta = fg_trend[-1][1] - fg_trend[-2][1]
        nef_last_delta = nef_trend[-1][1] - nef_trend[-2][1] if len(nef_trend) >= 2 else 0
        if fg_last_delta < 0 and nef_last_delta <= 0:
            print(f"\n*** STOP: FG SSIM declining ({fg_last_delta:+.4f}) AND NEF declining ({nef_last_delta:+.4f}) ***")
            stop = True

    # Check severe regression escalation
    if ref_150:
        for s in sorted([s for s in scales if s > 1.50]):
            diffs = compare_scales(all_data, ref_150, s)
            sev_05 = count_regressions(diffs, 0.05)
            if sev_05 > 5:
                print(f"\n*** STOP: s={s:.2f} has {sev_05} severe regressions (>0.05) vs s=1.50 ***")
                stop = True

    if not stop:
        print(f"\nNo stop condition triggered.")

    # === Task 5: Visual sanity manifest ===
    print(f"\n{'='*80}")
    print("TASK 5: VISUAL SANITY MANIFEST")
    print("=" * 80)

    best_scale = best_fg_scale
    manifest_rows = []

    # Best scale worst-10 vs s=1.25
    if ref_125 and best_scale != ref_125:
        diffs = compare_scales(all_data, ref_125, best_scale)
        diffs.sort(key=lambda x: x[1])
        print(f"\n--- Best scale (s={best_scale:.2f}) worst-10 FG regressions vs s=1.25 ---")
        for obj, d in diffs[:10]:
            fg_125 = float(all_data[ref_125][obj]['delta_fg_ssim']) if obj < len(all_data[ref_125]) else 0
            fg_best = float(all_data[best_scale][obj]['delta_fg_ssim']) if obj < len(all_data[best_scale]) else 0
            manifest_rows.append({
                'list': f'best_{best_scale:.2f}_worst_vs_1p25',
                'object_idx': obj, 'delta_fg_ssim': d,
                's1p25_fg': fg_125, 'best_fg': fg_best,
                'failure_type': 'unknown'
            })
            print(f"  obj={obj:3d} Δ={d:+.4f}")

    # s=1.50 to best scale worst-10
    if ref_150 and best_scale != ref_150:
        diffs = compare_scales(all_data, ref_150, best_scale)
        diffs.sort(key=lambda x: x[1])
        print(f"\n--- s={best_scale:.2f} worst-10 FG regressions vs s=1.50 ---")
        for obj, d in diffs[:10]:
            manifest_rows.append({
                'list': f'best_{best_scale:.2f}_worst_vs_1p50',
                'object_idx': obj, 'delta_fg_ssim': d,
                'failure_type': 'unknown'
            })
            print(f"  obj={obj:3d} Δ={d:+.4f}")

    # s=1.25 to best scale best-10 improvements
    if ref_125 and best_scale != ref_125:
        diffs = compare_scales(all_data, ref_125, best_scale)
        diffs.sort(key=lambda x: x[1], reverse=True)
        print(f"\n--- s={best_scale:.2f} best-10 FG improvements vs s=1.25 ---")
        for obj, d in diffs[:10]:
            manifest_rows.append({
                'list': f'best_{best_scale:.2f}_best_vs_1p25',
                'object_idx': obj, 'delta_fg_ssim': d,
                'failure_type': ''
            })
            print(f"  obj={obj:3d} Δ={d:+.4f}")

    # Save manifest
    if manifest_rows:
        csv_path = f"{OUTPUT_DIR}/visual_sanity_manifest.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=manifest_rows[0].keys())
            writer.writeheader()
            writer.writerows(manifest_rows)
        print(f"\nSaved: {csv_path}")

    # === Task 6: 300-object gate ===
    print(f"\n{'='*80}")
    print("TASK 6: 300-OBJECT VALIDATION GATE")
    print("=" * 80)

    gain_vs_150 = all_stats[best_scale]['delta_fg_ssim']['mean'] - all_stats.get(1.50, {}).get('delta_fg_ssim', {}).get('mean', 0)
    gain_vs_125 = all_stats[best_scale]['delta_fg_ssim']['mean'] - all_stats.get(1.25, {}).get('delta_fg_ssim', {}).get('mean', 0)
    print(f"\nBest scale s={best_scale:.2f}:")
    print(f"  FG SSIM gain vs s=1.50: {gain_vs_150:+.4f}")
    print(f"  FG SSIM gain vs s=1.25: {gain_vs_125:+.4f}")

    if ref_150 and best_scale != ref_150:
        diffs_150 = compare_scales(all_data, ref_150, best_scale)
        sev_05_150 = count_regressions(diffs_150, 0.05)
    else:
        sev_05_150 = 0

    gate_pass = False
    reasons = []
    if gain_vs_150 >= 0.005:
        reasons.append(f"FG SSIM gain vs s=1.50 ≥ +0.005 ({gain_vs_150:+.4f})")
        gate_pass = True
    if gain_vs_125 >= 0.02 and sev_05_150 <= 5:
        reasons.append(f"FG SSIM gain vs s=1.25 ≥ +0.02 ({gain_vs_125:+.4f}) with controlled regressions")
        gate_pass = True

    if gate_pass:
        print(f"\n✅ GATE PASSED — 300-object eval RECOMMENDED")
        for r in reasons:
            print(f"  - {r}")
        print(f"\nRun: python geotex/eval_scale_inline.py --scale {best_scale} --num_objects 300 "
              f"--output_dir mvpoutput/geotex_refattn_v1/eval_300obj_scale_{best_scale:.2f}".replace('.', 'p'))
    else:
        print(f"\n❌ GATE FAILED — 300-object eval NOT justified")
        print(f"  Gain vs s=1.50: {gain_vs_150:+.4f} (need ≥ +0.005)")
        print(f"  Gain vs s=1.25: {gain_vs_125:+.4f} (need ≥ +0.02 with ≤5 severe regressions)")
        if sev_05_150 > 5:
            print(f"  Severe regressions vs s=1.50: {sev_05_150} (need ≤ 5)")

    # Save analysis results
    results = {
        'scales': scales,
        'best_fg_scale': best_fg_scale,
        'best_nef_scale': best_nef_scale,
        'gate_pass': gate_pass,
        'gain_vs_150': gain_vs_150,
        'gain_vs_125': gain_vs_125,
        'severe_regressions_vs_150': sev_05_150,
        'all_stats': {str(k): v for k, v in all_stats.items()},
    }
    with open(f"{OUTPUT_DIR}/selection_analysis.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved: {OUTPUT_DIR}/selection_analysis.json")


if __name__ == '__main__':
    main()
