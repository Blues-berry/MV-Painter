"""Safe eval wrapper that catches errors and saves intermediate results."""
import os
import sys
import json
import csv
import signal
import traceback
import torch
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

# Graceful shutdown handler
_shutdown = False
def _signal_handler(signum, frame):
    global _shutdown
    print(f"\n[SIGNAL] Received signal {signum}, shutting down gracefully...", flush=True)
    _shutdown = True

# signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)

def main():
    import argparse
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    from torchvision.transforms import v2
    from torchvision.utils import save_image
    from diffusers import EulerDiscreteScheduler
    from metrics import compute_psnr, compute_ssim, compute_edge_mask, unscale_latents, unscale_image
    from eval import (load_model, generate_images, get_lpips, compute_lpips,
                      compute_region_metrics, collate_batch, prepare_batch,
                      normalize_background)

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--num_objects', type=int, default=300)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--steps', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--save_vis', action='store_true', default=True)
    parser.add_argument('--vis_count', type=int, default=300)
    parser.add_argument('--resume_from', type=int, default=0)
    args = parser.parse_args()

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    # Load existing partial results
    partial_csv = os.path.join(args.output_dir, 'per_object_metrics_partial.csv')
    results = []
    if os.path.exists(partial_csv):
        with open(partial_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for k, v in row.items():
                    try:
                        row[k] = float(v)
                    except:
                        pass
                results.append(row)
        print(f"Loaded {len(results)} existing results from partial CSV", flush=True)

    print(f"Loading model...", flush=True)
    model = load_model(args.config, args.checkpoint, device)
    config = OmegaConf.load(args.config)
    dataset = instantiate_from_config(config.data.params.validation)
    total = len(dataset)
    num_objects = min(args.num_objects, total)
    print(f"Evaluating {num_objects} objects (resume from {args.resume_from})", flush=True)

    try:
        lpips_fn = get_lpips(device)
        lpips_available = True
    except:
        lpips_fn = None
        lpips_available = False

    warnings_list = []
    start = max(args.resume_from, len(results))

    for obj_idx in range(start, num_objects):
        if _shutdown:
            print(f"[SHUTDOWN] Saving partial results at object {obj_idx}...", flush=True)
            break

        try:
            batch = collate_batch(dataset, obj_idx, device)
            cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
                prepare_batch(batch, model.img_size, device)

            geo_clean = geo_input.float().clamp(0, 1)
            geo_clean = torch.nan_to_num(geo_clean, nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)

            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            torch.manual_seed(args.seed)
            shared_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

            torch.manual_seed(args.seed)
            image_adapter = generate_images(model, batch, device, weight_dtype, geo_feats, args.steps, shared_latents)
            torch.manual_seed(args.seed)
            image_orig = generate_images(model, batch, device, weight_dtype, None, args.steps, shared_latents)

            gt = target_imgs
            edge_source = real_depth_imgs.float() if real_depth_imgs is not None else normal_imgs.float()
            edge_mask = compute_edge_mask(edge_source, threshold=0.1)
            if edge_mask.shape[2:] != gt.shape[2:]:
                edge_mask = torch.nn.functional.interpolate(edge_mask, size=gt.shape[2:], mode='bilinear', align_corners=False)

            fg_mask = mask > 0.5
            total_pixels = fg_mask.numel()
            fg_ratio = fg_mask.sum().item() / total_pixels

            obj_result = {
                'object_idx': obj_idx,
                'fg_ratio': fg_ratio,
                'bg_ratio': 1.0 - fg_ratio,
                'edge_ratio': float((edge_mask > 0.5).sum().item() / total_pixels),
            }

            for region in ['full', 'foreground', 'background', 'edge', 'non_edge_fg']:
                orig_m = compute_region_metrics(image_orig, gt, mask, edge_mask, region, device)
                adapter_m = compute_region_metrics(image_adapter, gt, mask, edge_mask, region, device)
                for metric_name in ['psnr', 'ssim', 'lpips']:
                    obj_result[f'{region}_orig_{metric_name}'] = orig_m[metric_name]
                    obj_result[f'{region}_adapter_{metric_name}'] = adapter_m[metric_name]

            results.append(obj_result)

            fpsnr_d = obj_result['foreground_adapter_psnr'] - obj_result['foreground_orig_psnr']
            fssim_d = obj_result['foreground_adapter_ssim'] - obj_result['foreground_orig_ssim']
            epsnr_d = obj_result['edge_adapter_psnr'] - obj_result['edge_orig_psnr']
            essim_d = obj_result['edge_adapter_ssim'] - obj_result['edge_orig_ssim']
            print(f"  Object {obj_idx}: fg_PSNR {fpsnr_d:+.2f} fg_SSIM {fssim_d:+.4f} "
                  f"edge_PSNR {epsnr_d:+.2f} edge_SSIM {essim_d:+.4f} fg_ratio={fg_ratio:.3f}", flush=True)

            if args.save_vis and obj_idx < args.vis_count:
                vis_dir = os.path.join(args.output_dir, 'visualizations')
                os.makedirs(vis_dir, exist_ok=True)
                prefix = f"obj_{obj_idx:03d}"
                save_image(gt, os.path.join(vis_dir, f'{prefix}_gt.png'))
                save_image(normalize_background(image_orig, mask), os.path.join(vis_dir, f'{prefix}_original.png'))
                save_image(normalize_background(image_adapter, mask), os.path.join(vis_dir, f'{prefix}_adapter.png'))
                err_orig = (image_orig - gt).abs()
                err_adapter = (image_adapter - gt).abs()
                save_image(err_orig * 5, os.path.join(vis_dir, f'{prefix}_original_error.png'))
                save_image(err_adapter * 5, os.path.join(vis_dir, f'{prefix}_adapter_error.png'))
                save_image(mask.expand_as(gt), os.path.join(vis_dir, f'{prefix}_mask.png'))
                save_image(edge_mask.expand_as(gt), os.path.join(vis_dir, f'{prefix}_edge_mask.png'))

            # Save partial results every 10 objects
            if (obj_idx + 1) % 10 == 0:
                _save_partial(results, partial_csv)

        except Exception as e:
            print(f"  ERROR Object {obj_idx}: {e}", flush=True)
            traceback.print_exc()
            continue

    # Save final results
    _save_partial(results, partial_csv)
    _save_final(results, args, lpips_available)
    print(f"\nDone. {len(results)} objects evaluated.", flush=True)


def _save_partial(results, path):
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def _save_final(results, args, lpips_available):
    import numpy as np

    # per_object_metrics.csv
    fieldnames = list(results[0].keys())
    csv_path = os.path.join(args.output_dir, 'per_object_metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # summary_metrics.json
    summary = {
        'config': args.config,
        'checkpoint': args.checkpoint,
        'num_objects': len(results),
        'lpips_available': lpips_available,
    }
    regions = ['full', 'foreground', 'background', 'edge', 'non_edge_fg']
    metrics_list = ['psnr', 'ssim', 'lpips']
    for region in regions:
        for metric in metrics_list:
            key = f'{region}_{metric}'
            orig_vals = [r[f'{region}_orig_{metric}'] for r in results if r.get(f'{region}_orig_{metric}') is not None]
            adapter_vals = [r[f'{region}_adapter_{metric}'] for r in results if r.get(f'{region}_adapter_{metric}') is not None]
            if orig_vals and adapter_vals:
                summary[key] = {
                    'orig_mean': float(np.mean(orig_vals)),
                    'orig_std': float(np.std(orig_vals)),
                    'adapter_mean': float(np.mean(adapter_vals)),
                    'adapter_std': float(np.std(adapter_vals)),
                    'diff': float(np.mean(adapter_vals) - np.mean(orig_vals)),
                    'improved': sum(1 for o, a in zip(orig_vals, adapter_vals) if (a > o if metric != 'lpips' else a < o)),
                    'total': len(orig_vals),
                }
    summary['region_ratios'] = {
        'fg_ratio': float(np.mean([r['fg_ratio'] for r in results])),
    }
    with open(os.path.join(args.output_dir, 'summary_metrics.json'), 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    # region_metrics.csv
    region_csv_path = os.path.join(args.output_dir, 'region_metrics.csv')
    region_rows = []
    for r in results:
        row = {'object_idx': r['object_idx'], 'fg_ratio': r['fg_ratio']}
        for region in regions:
            for metric in metrics_list:
                row[f'{region}_orig_{metric}'] = r.get(f'{region}_orig_{metric}')
                row[f'{region}_adapter_{metric}'] = r.get(f'{region}_adapter_{metric}')
                o = r.get(f'{region}_orig_{metric}')
                a = r.get(f'{region}_adapter_{metric}')
                if o is not None and a is not None:
                    row[f'{region}_diff_{metric}'] = a - o
        region_rows.append(row)
    with open(region_csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=region_rows[0].keys())
        writer.writeheader()
        writer.writerows(region_rows)

    # Print summary
    print(f"\n{'='*70}", flush=True)
    print(f"RESULTS ({len(results)} objects)", flush=True)
    print(f"{'='*70}", flush=True)
    for region in regions:
        print(f"\n  {region.upper()}:", flush=True)
        for metric in metrics_list:
            key = f'{region}_{metric}'
            if key in summary:
                s = summary[key]
                better = '↑' if metric != 'lpips' else '↓'
                print(f"    {metric.upper()}: {s['orig_mean']:.4f} → {s['adapter_mean']:.4f} "
                      f"({s['diff']:+.4f} {better}) [{s['improved']}/{s['total']}]", flush=True)


if __name__ == '__main__':
    main()
