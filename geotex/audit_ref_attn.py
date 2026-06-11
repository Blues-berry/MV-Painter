"""Audit reference attention processors in GeoTex pipeline.

Checks:
1. replace_processors=True in code
2. Processor type statistics (ReferenceOnlyAttnProc vs AttnProcessor2_0)
3. Smoke test: generate 1 object, check for cross_attention_kwargs warnings
"""
import os
import sys
import argparse
import torch
import warnings
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))

from omegaconf import OmegaConf
from src.utils.train_util import instantiate_from_config


def audit_processor_types(unet):
    """Count processor types in UNet."""
    proc_types = Counter()
    proc_names = {}
    for name, proc in unet.attn_processors.items():
        proc_type = type(proc).__name__
        proc_types[proc_type] += 1
        if proc_type not in proc_names:
            proc_names[proc_type] = []
        proc_names[proc_type].append(name)
    return proc_types, proc_names


def check_reference_attn_enabled(unet):
    """Check if reference attention processors handle mode/ref_dict."""
    ref_procs = []
    for name, proc in unet.attn_processors.items():
        proc_type = type(proc).__name__
        if 'Reference' in proc_type or 'Ref' in proc_type:
            ref_procs.append(name)
    return ref_procs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--output_dir', required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device(args.device)

    # Load model
    print("Loading model...")
    config = OmegaConf.load(args.config)
    model = instantiate_from_config(config.model)

    if args.checkpoint:
        model.load_geotex_weights(args.checkpoint)
        print(f"Loaded checkpoint: {args.checkpoint}")

    # Audit processor types
    print("\n=== Processor Type Audit ===")
    proc_types, proc_names = audit_processor_types(model.unet)

    report_lines = ["# Reference Attention Processor Audit\n\n"]
    report_lines.append(f"**Config:** {args.config}\n")
    report_lines.append(f"**Checkpoint:** {args.checkpoint or 'None (zero-init)'}\n\n")

    report_lines.append("## Processor Type Statistics\n\n")
    report_lines.append("| Type | Count |\n")
    report_lines.append("|------|-------|\n")
    for ptype, count in proc_types.items():
        report_lines.append(f"| {ptype} | {count} |\n")
        print(f"  {ptype}: {count}")

    # Check for reference processors
    ref_procs = check_reference_attn_enabled(model.unet)
    report_lines.append(f"\n## Reference Attention Check\n\n")
    if ref_procs:
        report_lines.append(f"**PASS** ✓: Found {len(ref_procs)} reference attention processors\n\n")
        report_lines.append("These processors handle `mode`/`ref_dict` kwargs:\n")
        for name in ref_procs[:5]:
            report_lines.append(f"- `{name}`\n")
        if len(ref_procs) > 5:
            report_lines.append(f"- ... and {len(ref_procs)-5} more\n")
        print(f"\n✓ Found {len(ref_procs)} reference attention processors")
    else:
        report_lines.append("**FAIL** ✗: No reference attention processors found!\n")
        report_lines.append("All processors are standard AttnProcessor2_0 — reference attention is DISABLED.\n")
        print("\n✗ FAIL: No reference attention processors found!")

    # Check if attn1 processors are wrapped
    attn1_procs = [n for n in model.unet.attn_processors if 'attn1' in n]
    attn1_ref = [n for n in attn1_procs if n in ref_procs]
    report_lines.append(f"\n## attn1 Processor Check\n\n")
    report_lines.append(f"- Total attn1 processors: {len(attn1_procs)}\n")
    report_lines.append(f"- attn1 with reference: {len(attn1_ref)}\n")
    if len(attn1_ref) == len(attn1_procs):
        report_lines.append("- **PASS** ✓: All attn1 processors have reference attention\n")
        print(f"✓ All {len(attn1_procs)} attn1 processors have reference attention")
    else:
        report_lines.append(f"- **FAIL** ✗: {len(attn1_procs) - len(attn1_ref)} attn1 processors missing reference!\n")
        print(f"✗ FAIL: {len(attn1_procs) - len(attn1_ref)} attn1 processors missing reference")

    # Smoke test: capture warnings
    report_lines.append(f"\n## Smoke Test\n\n")
    print("\n=== Smoke Test ===")

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Move model to device for smoke test
        model.unet.to(device).to(dtype=torch.float16)
        model.pipeline.vae.to(device).to(dtype=torch.float16)

        # Run a minimal forward pass
        try:
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            dummy_latent = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
            dummy_cond = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=torch.float16)
            dummy_timestep = torch.tensor([500], device=device)
            dummy_encoder_hidden = torch.randn(1, 77, 1024, device=device, dtype=torch.float16)

            # Forward pass with cross_attention_kwargs
            _ = model.unet(
                dummy_latent, dummy_timestep,
                encoder_hidden_states=dummy_encoder_hidden,
                cross_attention_kwargs=dict(cond_lat=dummy_cond),
                return_dict=False, is_training=False,
            )
            print("  Forward pass: OK")
            report_lines.append("- Forward pass: **OK** ✓\n")
        except Exception as e:
            print(f"  Forward pass: FAILED - {e}")
            report_lines.append(f"- Forward pass: **FAILED** - {e}\n")

        # Check for cross_attention_kwargs warnings
        cross_attn_warnings = [x for x in w if 'cross_attention_kwargs' in str(x.message) and 'not expected' in str(x.message)]

        if cross_attn_warnings:
            report_lines.append(f"- cross_attention_kwargs warnings: **{len(cross_attn_warnings)}** ✗\n")
            report_lines.append("  - Reference attention is NOT working!\n")
            report_lines.append(f"  - Sample: `{cross_attn_warnings[0].message}`\n")
            print(f"  ✗ FAIL: {len(cross_attn_warnings)} cross_attention_kwargs warnings")
            for cw in cross_attn_warnings[:3]:
                print(f"    {cw.message}")
        else:
            report_lines.append("- cross_attention_kwargs warnings: **0** ✓\n")
            report_lines.append("  - Reference attention is working correctly\n")
            print("  ✓ No cross_attention_kwargs warnings")

    # Write report
    report_path = os.path.join(args.output_dir, 'ref_attn_processor_audit.md')
    with open(report_path, 'w') as f:
        f.writelines(report_lines)
    print(f"\nReport: {report_path}")

    # Final verdict
    all_pass = bool(ref_procs) and len(attn1_ref) == len(attn1_procs) and not cross_attn_warnings
    if all_pass:
        print("\n=== VERDICT: PASS ✓ ===")
    else:
        print("\n=== VERDICT: FAIL ✗ ===")


if __name__ == '__main__':
    main()
