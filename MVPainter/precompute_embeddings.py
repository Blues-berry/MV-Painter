"""
Pre-compute vision encoder embeddings for all rendered objects.
This avoids loading vision encoders during training, saving ~4 GB VRAM.
"""
import os
import sys
import torch
import numpy as np
from PIL import Image
from torchvision.transforms import v2
from tqdm import tqdm

def main():
    rendered_dir = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
    device = torch.device('cuda:0')

    # Load pipeline to get vision encoders
    print("Loading vision encoders...")
    from mvpainter.mvpainter_pipeline import MVPainter_Pipeline
    pipeline = MVPainter_Pipeline.from_pretrained('../checkpoints/hf_repo', torch_dtype=torch.float16)

    vision_encoder = pipeline.vision_encoder.to(device)
    vision_encoder_2 = pipeline.vision_encoder_2.to(device)
    vision_processor = pipeline.vision_processor

    # Free other components
    del pipeline.vae
    del pipeline.unet
    if hasattr(pipeline, 'text_encoder'):
        del pipeline.text_encoder
    torch.cuda.empty_cache()

    # Process each object
    uids = sorted(os.listdir(rendered_dir))
    print(f"Processing {len(uids)} objects...")

    for uid in tqdm(uids):
        obj_dir = os.path.join(rendered_dir, uid)
        image_dir = os.path.join(obj_dir, 'image')

        if not os.path.exists(image_dir):
            continue

        # Check if embeddings already computed
        embed_dir = os.path.join(obj_dir, 'embeddings')
        if os.path.exists(os.path.join(embed_dir, 'global_embeds.npy')):
            continue

        os.makedirs(embed_dir, exist_ok=True)

        # Process view 000.png (the condition image)
        img_path = os.path.join(image_dir, '000.png')
        if not os.path.exists(img_path):
            continue

        try:
            img = Image.open(img_path).convert('RGB')
            image_pil = [img]
            image_clip = vision_processor(images=image_pil, return_tensors="pt").pixel_values.to(device=device, dtype=torch.float16)

            with torch.no_grad():
                global_embeds_1 = vision_encoder(image_clip, output_hidden_states=False).image_embeds.unsqueeze(-2)
                global_embeds_2 = vision_encoder_2(image_clip, output_hidden_states=False).image_embeds.unsqueeze(-2)
                global_embeds = torch.concat([global_embeds_1, global_embeds_2], dim=-1)

            # Save embeddings
            np.save(os.path.join(embed_dir, 'global_embeds.npy'), global_embeds.cpu().numpy())
        except Exception as e:
            print(f"Error processing {uid}: {e}")
            continue

    print("Done!")

if __name__ == '__main__':
    main()
