import os
import argparse
import numpy as np
import torch
import rembg
from PIL import Image
from torchvision.transforms import v2
from pytorch_lightning import seed_everything
from omegaconf import OmegaConf
from einops import rearrange, repeat
from tqdm import tqdm
from huggingface_hub import hf_hub_download
import subprocess
from src.utils.camera_util import (
    FOV_to_intrinsics,
    get_zero123plus_input_cameras,
    get_circular_camera_poses,
)
import cv2
from src.utils.infer_util import remove_background, resize_foreground, save_video
import shutil
import OpenEXR
import Imath
import time

from mvpainter.mvpainter_pipeline import MVPainter_Pipeline,RefOnlyNoisedUNet,DepthControlUNet
from mvpainter.controlnet import ControlNetModel_Union

# from diffusers import AutoencoderKL, UNet2DConditionModel,EulerAncestralDiscreteScheduler
# from transformers import CLIPVisionModelWithProjection,CLIPImageProcessor

def depth_exr_to_png(exr_file, png_file, depth_channel='V', depth_scale=6.0):
    exr_image = OpenEXR.InputFile(exr_file)
    header = exr_image.header()
    size = (header['displayWindow'].max.x + 1, header['displayWindow'].max.y + 1)
    channel_names = exr_image.header()['channels'].keys()
    depth_channel = exr_image.channel(depth_channel, Imath.PixelType(Imath.PixelType.FLOAT))

    depth_array = np.frombuffer(depth_channel, dtype=np.float32).copy()
    depth_array = depth_array.reshape((size[1], size[0]))

    invalid_mask = depth_array ==1.0

    depth_array /= depth_scale

    depth_array_uint8 = (depth_array * 65535).astype(np.uint16)
    depth_array_uint8[invalid_mask] = 65535

    depth_image = Image.fromarray(depth_array_uint8)

    depth_image.save(png_file)

def get_render_cameras(batch_size=1, M=120, radius=4.0, elevation=20.0, is_flexicubes=False):
    """
    Get the rendering camera parameters.
    """
    c2ws = get_circular_camera_poses(M=M, radius=radius, elevation=elevation)
    if is_flexicubes:
        cameras = torch.linalg.inv(c2ws)
        cameras = cameras.unsqueeze(0).repeat(batch_size, 1, 1, 1)
    else:
        extrinsics = c2ws.flatten(-2)
        intrinsics = FOV_to_intrinsics(30.0).unsqueeze(0).repeat(M, 1, 1).float().flatten(-2)
        cameras = torch.cat([extrinsics, intrinsics], dim=-1)
        cameras = cameras.unsqueeze(0).repeat(batch_size, 1, 1)
    return cameras


def render_frames(model, planes, render_cameras, render_size=512, chunk_size=1, is_flexicubes=False):
    """
    Render frames from triplanes.
    """
    frames = []
    for i in tqdm(range(0, render_cameras.shape[1], chunk_size)):
        if is_flexicubes:
            frame = model.forward_geometry(
                planes,
                render_cameras[:, i:i + chunk_size],
                render_size=render_size,
            )['img']
        else:
            frame = model.forward_synthesizer(
                planes,
                render_cameras[:, i:i + chunk_size],
                render_size=render_size,
            )['images_rgb']
        frames.append(frame)

    frames = torch.cat(frames, dim=1)[0]  # we suppose batch size is always 1
    return frames


###############################################################################
# Arguments.
###############################################################################

parser = argparse.ArgumentParser()
parser.add_argument('--input_glb_dir', type=str, default='', help='input directory.')
parser.add_argument('--input_img_dir', type=str, default='', help='input directory.')
parser.add_argument('--output_dir', type=str, default='outputs_smq/test', help='tput directory.')
parser.add_argument('--geo_rotation', type=int, default=-90, help='roration for input mesh')

parser.add_argument('--diffusion_steps', type=int, default=75, help='Denoising Sampling steps.')
parser.add_argument('--seed', type=int, default=12, help='Random seed for sampling.')
parser.add_argument('--no_rembg', action='store_true', help='Do not remove input background.')
args = parser.parse_args()
seed_everything(args.seed)

###############################################################################
# Stage 0: Configuration.
###############################################################################

config_name = 'mvpainter'


device = torch.device('cuda')


def infer(pipeline, obj_path, image_file, filenames=['000.png', '005.png', '001.png', '004.png', '002.png', '003.png'],
          index_offset=0,blender_path = None):
    """
    Infer multi-view images from a single image.
    """

    # make output directories
    object_uid = os.path.basename(obj_path).split(".")[0]

    image_path = os.path.join(args.output_dir, config_name, object_uid)
    glb_path = os.path.join("render_temp", object_uid,
                            object_uid+".obj")
    
    name = os.path.basename(image_file).split('.')[0]


    if os.path.exists(os.path.join(image_path, f'{name}_{str(index_offset)}_6view.png')):
        return
    

    cmds = [f'{blender_path}', '--background', '-Y',
            '--python',
            'scripts/blender_render_ortho.py', '--',
            '--object_path', f'{obj_path}',
            '--geo_rotation',f'{args.geo_rotation}'
            ]
    print(" ".join(cmds))
    subprocess.run(cmds)
    os.makedirs('render_temp',exist_ok=True)
    normal_path = os.path.join("render_temp", object_uid,
                               "normal")
    
    # 将深度图从exr转换成png
    depth_exr_dir = os.path.join("render_temp", object_uid,
                               "depth")
    depth_png_dir = os.path.join("render_temp", object_uid,
                               "depth_png")
    os.makedirs(depth_png_dir,exist_ok=True)
    for i in range(6):
        depth_exr_path = os.path.join(depth_exr_dir,f'{str(i).zfill(3)}.exr')
        depth_png_path = os.path.join(depth_png_dir,f'{str(i).zfill(3)}.png')
        depth_exr_to_png(depth_exr_path,depth_png_path)


    depth_images = images = [cv2.resize(cv2.imread(os.path.join(depth_png_dir, filename),cv2.IMREAD_UNCHANGED), (512, 512)) for filename in filenames]



    

    images = [cv2.resize(cv2.imread(os.path.join(normal_path, filename)), (512, 512)) for filename in filenames]
    height, width, channel = images[0].shape

    combined_image = np.zeros((height * 3, width * 2, channel), dtype=np.uint8)
    combined_image_depth = np.ones((height * 3, width * 2),dtype = np.uint16) * 65535

    for index, image in enumerate(images):
        x_offset = (index % 2) * width
        y_offset = (index // 2) * height
        combined_image[y_offset:y_offset + height, x_offset:x_offset + width] = image
        combined_image_depth[y_offset:y_offset + height, x_offset:x_offset + width] = depth_images[index]


    # glb_path_low = os.path.join("/home/sunzhaoxu/code/InstantMesh/blender_smq/", object_uid,"blender.obj")


    os.makedirs(image_path, exist_ok=True)
    shutil.copy(glb_path,os.path.join(image_path,"blender.obj"))

    # 对深度图进行归一化
    valid_mask = combined_image_depth < 65535
    combined_image_depth = combined_image_depth.astype(np.float32) / 65535.0

    combined_image_depth[valid_mask] = 1.0 / combined_image_depth[valid_mask]

    
    min_depth = np.min(combined_image_depth[valid_mask])
    max_depth = np.max(combined_image_depth[valid_mask])

    combined_image_depth[valid_mask] = (combined_image_depth[valid_mask] - min_depth) / (max_depth - min_depth) # (6,3,512,512)
    combined_image_depth = np.repeat(combined_image_depth[:, :, np.newaxis], 3, axis=2)
    

 

    
    os.makedirs(image_path, exist_ok=True)
    # 保存拼接后的图像
    cv2.imwrite(os.path.join(image_path,f'combined_image_{str(index_offset)}.png'), combined_image)
    cv2.imwrite(os.path.join(image_path,f'combined_image_{str(index_offset)}_depth.png'), (combined_image_depth * 255).astype(np.uint8))

    # load diffusion model
    print('Loading diffusion model ...')




    ###############################################################################
    # Stage 1: Multiview generation.
    ###############################################################################

    rembg_session = None if args.no_rembg else rembg.new_session()
    depth = Image.open(os.path.join(image_path,f'combined_image_{str(index_offset)}.png'))
    depth_2 = Image.open(os.path.join(image_path,f'combined_image_{str(index_offset)}_depth.png'))

    # remove background optionally
    input_image = Image.open(image_file)
    if not args.no_rembg:
        input_image = remove_background(input_image, rembg_session)
        input_image = resize_foreground(input_image, 0.85)
    

  

    piple_output = pipeline(
        input_image, depth_image=depth,depth_image_2 = depth_2,
        num_inference_steps=args.diffusion_steps,
    )

    print(piple_output)
    piple_output[0].save(os.path.join(image_path, f'{name}_{str(index_offset)}_6view.png'))
    piple_output[1].save(os.path.join(image_path, f'{name}_{str(index_offset)}_cond.png'))
    combine_image = cv2.imread(os.path.join(image_path, f'{name}_{str(index_offset)}_6view.png'))
    depth = cv2.imread(os.path.join(image_path,f'combined_image_{str(index_offset)}.png'))

    for index, image_name in enumerate(filenames):
        x_offset = (index % 2) * width
        y_offset = (index // 2) * height
        cv2.imwrite(os.path.join(image_path, "result_"+str(index + 1 ) + ".png"),
                    combine_image[y_offset:y_offset + height + 1, x_offset:x_offset + width + 1])
        cv2.imwrite(os.path.join(image_path, str(index + 1 ) + "_normal.png"),
                    depth[y_offset:y_offset + height + 1, x_offset:x_offset + width + 1])
    
if __name__ == '__main__':


    # load pipeline modules

    pipeline_path = '/mnt/xlab-nas-1/shaomingqi.smq/projects/aigc3d_dev/aigc3d/开源/ckpts/MVPainter/pipeline'

    pipeline = MVPainter_Pipeline.from_pretrained(
        pipeline_path,
        torch_dtype=torch.float16,
    )
    controlnet = ControlNetModel_Union.from_unet(pipeline.unet).to(dtype=torch.float16,device=pipeline.device)
    pipeline.add_controlnet(controlnet, conditioning_scale=1.0)


    print('Loading custom unet ...')
    ckpt = torch.load(
        # "/mnt/xlab-nas-1/shaomingqi.smq/projects/aigc3d_dev/aigc3d/开源/ckpts/MVPainter/mvpainter_unet/v26_2_step_00024000.ckpt")[
        "../ckpts/MVPainter/pipeline/unet_w_controlnet/v29_25000.ckpt")[
        # "/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/Zero123_Origin/logs_h20/hunyuan-controlnet-train-multi-ccm-v28-2/checkpoints/step=00023000.ckpt")[
        "state_dict"]
    new_ckpt = {k[5:]: v for k, v in ckpt.items() if "unet" in k}
    pipeline.unet.load_state_dict(new_ckpt)


    pipeline = pipeline.to(torch.device('cuda'))

    


    glb_dir = args.input_glb_dir
    img_dir = args.input_img_dir

    obj_path_list = []
    image_file_list = []
    for i in os.listdir(glb_dir):

        base_name = i
        obj_path = os.path.join(glb_dir, i)

        img_path = os.path.join(img_dir, base_name.replace("glb", "png"))
   
        if os.path.exists(obj_path) and os.path.exists(img_path):
            obj_path_list.append(obj_path)
            image_file_list.append(img_path)


    for i in range(len(obj_path_list)):
        print(obj_path_list[i], image_file_list[i])
        
        infer(pipeline, obj_path_list[i], image_file_list[i],blender_path ='../blender-4.2.9-linux-x64/blender')
