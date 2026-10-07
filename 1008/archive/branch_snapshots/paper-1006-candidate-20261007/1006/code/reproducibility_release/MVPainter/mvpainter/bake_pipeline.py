from mvpainter_pipeline import MVPainter_Pipeline
import os
import trimesh
import argparse

import logging
import os

import numpy as np
import torch
from PIL import Image

from differentiable_renderer.mesh_render import MeshRender

from uv_warp_utils import mesh_uv_wrap

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()
args, extra = parser.parse_known_args()
parser.add_argument("--input_dir", default="")
parser.add_argument("--save_dir",default="")
parser.add_argument("--offset",default=0)
parser.add_argument("--suffix",default="")


args = parser.parse_args()
def scale_image(img, scale=0.99):
    # 打开图像
    # img = Image.open(image_path)
    
    # 获取原始尺寸
    original_width, original_height = img.size

    # 计算缩放后的尺寸
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    # 缩放图像
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 将缩放后的图像放回到原始分辨率大小的画布上（居中）
    output_img = Image.new("RGB", (original_width, original_height), (255, 255, 255))
    paste_x = (original_width - new_width) // 2
    paste_y = (original_height - new_height) // 2
    output_img.paste(resized_img, (paste_x, paste_y))

    # 保存新图像
    return output_img
class BakeConfig:

    def __init__(self,offset,candidate_view_weights):
        self.device = 'cuda'
        # self.light_remover_ckpt_path = light_remover_ckpt_path
        # self.multiview_ckpt_path = multiview_ckpt_path
        # offset = -90
        self.candidate_camera_azims = [0 + offset, 90 + offset, 180 + offset, 270+offset, 0 + offset, 0+offset]
        self.candidate_camera_elevs = [0, 0, 0, 0, -90, 90]
        # self.candidate_view_weights = [1, 0.1, 0.5, 0.1, 0.05, 0.05]
        # self.candidate_view_weights = [1, 0.1, 0.1, 0.1, 0.05, 0]
        # self.candidate_view_weights = [0,0,0,0,0.1,0]
        self.candidate_view_weights = candidate_view_weights
        print(self.candidate_view_weights)

        self.render_size = 2048
        self.texture_size = 1024
        self.bake_exp = 4
        self.merge_method = 'fast'


class BakePipeline:
    def __init__(self,offset = -90,candidate_view_weights = [1, 0.1, 0.1, 0.1, 0.0, 0.05]):
        # self.config = config
        self.models = {}
        self.config = BakeConfig(offset,candidate_view_weights)
        self.render = MeshRender(
            default_resolution=self.config.render_size,
            texture_size=self.config.texture_size,
            camera_distance=4
            )



    def render_normal_multiview(self, camera_elevs, camera_azims, use_abs_coor=True):
        normal_maps = []
        for elev, azim in zip(camera_elevs, camera_azims):
            normal_map = self.render.render_normal(
                elev, azim, use_abs_coor=use_abs_coor, return_type='pl')
            normal_maps.append(normal_map)

        return normal_maps

    def render_position_multiview(self, camera_elevs, camera_azims):
        position_maps = []
        for elev, azim in zip(camera_elevs, camera_azims):
            position_map = self.render.render_position(
                elev, azim, return_type='pl')
            position_maps.append(position_map)

        return position_maps

    def bake_from_multiview(self, views, camera_elevs,
                            camera_azims, view_weights, method='graphcut'):
        project_textures, project_weighted_cos_maps = [], []
        project_boundary_maps = []
        for view, camera_elev, camera_azim, weight in zip(
            views, camera_elevs, camera_azims, view_weights):
            project_texture, project_cos_map, project_boundary_map = self.render.back_project(
                view, camera_elev, camera_azim)
            project_cos_map = weight * (project_cos_map ** self.config.bake_exp)
            project_textures.append(project_texture)
            project_weighted_cos_maps.append(project_cos_map)
            project_boundary_maps.append(project_boundary_map)

        if method == 'fast':
            texture, ori_trust_map = self.render.fast_bake_texture(
                project_textures, project_weighted_cos_maps)
        else:
            raise f'no method {method}'
        return texture, ori_trust_map > 1E-8

    def texture_inpaint(self, texture, mask):

        texture_np = self.render.uv_inpaint(texture, mask)
        # texture_np = self.render.uv_inpaint_vroni(texture,mask)
        texture = torch.tensor(texture_np / 255).float().to(texture.device)

        return texture

    def recenter_image(self, image, border_ratio=0.2):
        if image.mode == 'RGB':
            return image
        elif image.mode == 'L':
            image = image.convert('RGB')
            return image

        alpha_channel = np.array(image)[:, :, 3]
        non_zero_indices = np.argwhere(alpha_channel > 0)
        if non_zero_indices.size == 0:
            raise ValueError("Image is fully transparent")

        min_row, min_col = non_zero_indices.min(axis=0)
        max_row, max_col = non_zero_indices.max(axis=0)

        cropped_image = image.crop((min_col, min_row, max_col + 1, max_row + 1))

        width, height = cropped_image.size
        border_width = int(width * border_ratio)
        border_height = int(height * border_ratio)

        new_width = width + 2 * border_width
        new_height = height + 2 * border_height

        square_size = max(new_width, new_height)

        new_image = Image.new('RGBA', (square_size, square_size), (255, 255, 255, 0))

        paste_x = (square_size - new_width) // 2 + border_width
        paste_y = (square_size - new_height) // 2 + border_height

        new_image.paste(cropped_image, (paste_x, paste_y))
        return new_image


    
    @torch.no_grad()
    def call_bake(self, mesh, image_paths):
        multiviews = []
        for path in image_paths:
            image_prompt = Image.open(path)
  
            multiviews.append(image_prompt)

        mesh = mesh_uv_wrap(mesh)

        self.render.load_mesh(mesh)

        selected_camera_elevs, selected_camera_azims, selected_view_weights = \
            self.config.candidate_camera_elevs, self.config.candidate_camera_azims, self.config.candidate_view_weights


        for i in range(len(multiviews)):
            multiviews[i] = multiviews[i].resize(
                (self.config.render_size, self.config.render_size))

        texture, mask = self.bake_from_multiview(multiviews,
                                                 selected_camera_elevs, selected_camera_azims, selected_view_weights,
                                                 method=self.config.merge_method)

        mask_np = (mask.squeeze(-1).cpu().numpy() * 255).astype(np.uint8)

        texture = self.texture_inpaint(texture, mask_np)

        self.render.set_texture(texture)
        textured_mesh = self.render.save_mesh()

        return textured_mesh
    



pipeline = BakePipeline(offset=int(args.offset))


if __name__ == "__main__":


    dir_path = os.path.join('..',args.input_dir)
    save_path = os.path.join('..',args.save_dir)
    suffix = args.suffix
    os.makedirs(save_path,exist_ok=True)
    for casename in os.listdir(dir_path):
        work_dir = os.path.join(dir_path,casename)
        img_paths = [os.path.join(work_dir,f'result_{i}{suffix}.png') for i in [1,3,5,6,4,2]]
        obj = os.path.join(work_dir,'blender_low.obj')
        
        mesh = trimesh.load(obj)
        mesh = pipeline.call_bake(mesh,img_paths)
        mesh.export(os.path.join(save_path,casename+'.glb'))
        print("贴图完成: ", os.path.join(save_path,casename+'.glb'))
        
        
        
        
