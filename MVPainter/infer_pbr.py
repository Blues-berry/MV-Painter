import argparse
import os
import json
import torch
from PIL import Image
import numpy as np
from packaging import version

from accelerate import Accelerator
from diffusers.utils.import_utils import is_xformers_available
from diffusers import AutoencoderKL, DDPMScheduler, DDIMScheduler
from transformers import CLIPTextModel, CLIPTokenizer, CLIPImageProcessor

from pbr.models.unet_dr2d_condition import UNetDR2DConditionModel
from pbr.pipelines.pipeline_idarbdiffusion import IDArbDiffusionPipeline
from pbr.data.custom_dataset import CustomDataset
from pbr.data.ortho_6_view_dataset import CustomMVDataset


def reform_image(img_nd):
    albedo, normal = img_nd[0, ...], img_nd[1, ...]
    mro = img_nd[2, ...]
    mtl, rgh = mro[:1, ...], mro[1:2, ...]
    mtl, rgh = np.repeat(mtl, 3, axis=0), np.repeat(rgh, 3, axis=0)
    img_reform = np.concatenate([albedo, normal, mtl, rgh], axis=-1)
    return img_reform.transpose(1, 2, 0)

# 拼接图片的函数
def create_image_grid(image_folder, output_path,suffix = 'basecolor'):
    # 获取文件夹中的图片文件名
    image_files = [f"result_{i}_{suffix}.png" for i in range(1, 7)]
    images = [Image.open(os.path.join(image_folder, img)) for img in image_files]

    # 获取单张图片的宽高（假设所有图片大小相同）
    img_width, img_height = images[0].size

    # 创建空白画布，宽是2张图片的宽度，高是3张图片的高度
    grid_width = 2 * img_width
    grid_height = 3 * img_height
    grid_image = Image.new("RGB", (grid_width, grid_height))

    # 将图片按网格位置粘贴到画布上
    for idx, img in enumerate(images):
        x_offset = (idx % 2) * img_width   # 列索引 * 图片宽度
        y_offset = (idx // 2) * img_height  # 行索引 * 图片高度
        grid_image.paste(img, (x_offset, y_offset))

    # 保存拼接后的图片
    grid_image.save(output_path)
    print(f"拼接完成，结果保存为 {output_path}")

def save_image(out, name):
    Nv = out.shape[0]
    for i in range(Nv):
        img = reform_image(out[i])
        img = (img * 255).astype(np.uint8)
        H,W,C = img.shape
        basecolor_img = img[:,:H,:]
        normal_img = img[:,H:2*H,:]
        metallic_img = img[:,2*H:3*H,:]
        roughness_img = img[:,3*H:,:]
        
        os.makedirs(os.path.join(output_dir, name),exist_ok=True)
        Image.fromarray(basecolor_img).save(os.path.join(output_dir, name,f'result_{(i+1)}_basecolor.png'))
        Image.fromarray(normal_img).save(os.path.join(output_dir, name,f'result_{(i+1)}_normal.png'))
        Image.fromarray(metallic_img).save(os.path.join(output_dir, name,f'result_{(i+1)}_metallic.png'))
        Image.fromarray(roughness_img).save(os.path.join(output_dir, name,f'result_{(i+1)}_roughness.png'))
    
    create_image_grid(os.path.join(output_dir, name),suffix='basecolor',output_path=os.path.join(output_dir,name,'combine_basecolor.png'))
    create_image_grid(os.path.join(output_dir, name),suffix='roughness',output_path=os.path.join(output_dir,name,'combine_roughness.png'))
    create_image_grid(os.path.join(output_dir, name),suffix='metallic',output_path=os.path.join(output_dir,name,'combine_metallic.png'))

def load_pipeline():
    """
    load pipeline from hub
    or load from local ckpts: pipeline = IDArbDiffusionPipeline.from_pretrained("./pipeckpts")
    """
    text_encoder = CLIPTextModel.from_pretrained("lizb6626/IDArb", subfolder="text_encoder")
    tokenizer = CLIPTokenizer.from_pretrained("lizb6626/IDArb", subfolder="tokenizer")
    feature_extractor = CLIPImageProcessor.from_pretrained("lizb6626/IDArb", subfolder="feature_extractor")
    vae = AutoencoderKL.from_pretrained("lizb6626/IDArb", subfolder="vae")
    scheduler = DDIMScheduler.from_pretrained("lizb6626/IDArb", subfolder="scheduler")
    unet = UNetDR2DConditionModel.from_pretrained("/mnt/xlab-nas-1/shaomingqi.smq/projects/aigc3d_dev/aigc3d/IDArb/output/idarb-parallel-arbobjaverse-0416-512/checkpoint-19000", subfolder="unet")
    # unet = UNetDR2DConditionModel.from_pretrained("lizb6626/IDArb", subfolder="unet")
    
    pipeline = IDArbDiffusionPipeline(
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        feature_extractor=feature_extractor,
        vae=vae,
        unet=unet,
        safety_checker=None,
        scheduler=scheduler,
    )
    return pipeline


parser = argparse.ArgumentParser()
parser.add_argument('--mv_res_dir', type=str, default='example/single', help='Input data directory')
args = parser.parse_args()


weight_dtype = torch.float16

pipeline = load_pipeline()

if is_xformers_available():
    import xformers
    xformers_version = version.parse(xformers.__version__)
    pipeline.unet.enable_xformers_memory_efficient_attention()
    print(f'Use xformers version: {xformers_version}')

pipeline.to("cuda")
print("Pipeline loaded successfully")


dataset = CustomMVDataset(
    root_dir=args.mv_res_dir,
    num_views=6,
    use_cam=False,
)

dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)

output_dir = args.mv_res_dir
os.makedirs(output_dir, exist_ok=True)

Nd = 3

for i, batch in enumerate(dataloader):

    imgs_in, imgs_mask, task_ids = batch['imgs_in'], batch['imgs_mask'], batch['task_ids']
    cam_pose = batch['pose']
    imgs_name = batch['data_name']

    imgs_in = imgs_in.to(weight_dtype).to("cuda")
    cam_pose = cam_pose.to(weight_dtype).to("cuda")

    B, Nv, _, H, W = imgs_in.shape

    imgs_in, imgs_mask, task_ids = imgs_in.flatten(0,1), imgs_mask.flatten(0,1), task_ids.flatten(0,2)

    with torch.autocast("cuda"):
        out = pipeline(
                imgs_in,
                task_ids,
                num_views=Nv,
                cam_pose=cam_pose,
                height=H, width=W,
                # generator=generator,
                guidance_scale=1.0,
                output_type='pt',
                num_images_per_prompt=1,
                eta=1.0,
            ).images

        out = out.view(B, Nv, Nd, *out.shape[1:])
        out = out.detach().cpu().numpy()

        for i in range(B):
            save_image(out[i], imgs_name[i])
