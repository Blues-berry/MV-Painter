
"""Blender script to render images of 3D models.

This script is used to render images of 3D models. It takes in a list of paths
to .glb files and renders images of each model. The images are from rotating the
object around the origin. The images are saved to the output directory.

Example usage:
    blender -b -P blender_script.py -- \
        --object_path my_object.glb \
        --output_dir ./views \
        --engine CYCLES \
        --scale 0.8 \
        --num_images 12 \
        --camera_dist 1.2

Here, input_model_paths.json is a json file containing a list of paths to .glb.
"""

import argparse
import json
import math
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "8"
import random
import sys
import time
import glob
import urllib.request
import uuid
from typing import Tuple
from mathutils import Vector, Matrix

# import OpenEXR
import cv2
import numpy as np
from typing import Any, Callable, Dict, Generator, List, Literal, Optional, Set, Tuple

import bpy
from mathutils import Vector



# import blenderproc as bproc

bpy.app.debug_value=256

parser = argparse.ArgumentParser()
parser.add_argument(
    "--object_path",
    type=str,
    default='/data/54T/wyw/objverse_obj/000-000/ab66a75ccfa24c0da37741a47d5b1a22.glb',
    help="Path to the object file",
)
parser.add_argument("--output_dir", type=str, default="render_temp") #/data/54T/wyw/data/objverse_obj_render_pbr/
parser.add_argument(
    "--engine", type=str, default="CYCLES", choices=["CYCLES", "BLENDER_EEVEE","BLENDER_EEVEE_NEXT"]
)
parser.add_argument('--geo_rotation', type=int, default=-90, help='triposg is -90, huynuan is 0')

parser.add_argument("--scale", type=float, default=0.8)
parser.add_argument("--num_images", type=int, default=16)
parser.add_argument("--random_images", type=int, default=0)
parser.add_argument("--fix_images", type=int, default=16)
parser.add_argument("--random_ortho", type=int, default=2)
parser.add_argument("--device", type=str, default="CUDA")

argv = sys.argv[sys.argv.index("--") + 1 :]
args = parser.parse_args(argv)



# print('===================', args.engine, '===================')

context = bpy.context
scene = context.scene
render = scene.render

cam = scene.objects["Camera"]
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 1.
cam.data.lens = 35
cam.data.sensor_height = 32
cam.data.sensor_width = 32

cam_constraint = cam.constraints.new(type="TRACK_TO")
cam_constraint.track_axis = "TRACK_NEGATIVE_Z"
cam_constraint.up_axis = "UP_Y"


render.engine = args.engine
render.image_settings.file_format = "PNG"
render.image_settings.color_mode = "RGBA"
render.resolution_x = 512
render.resolution_y = 512
render.resolution_percentage = 100
render.threads_mode = 'FIXED'  # 使用固定线程数模式
render.threads = 32  # 设置线程数

scene.cycles.device = "GPU"
scene.cycles.samples = 1   # 128
scene.cycles.diffuse_bounces = 1
scene.cycles.glossy_bounces = 1
scene.cycles.transparent_max_bounces = 3  # 3
scene.cycles.transmission_bounces = 3   # 3
# scene.cycles.filter_width = 0.01
bpy.context.scene.cycles.adaptive_threshold = 0
scene.cycles.use_denoising = True
scene.render.film_transparent = True

# bpy.context.preferences.addons["cycles"].preferences.get_devices()
# Set the device_type
# print( bpy.context.preferences.addons["eevee"])
# assert 1==0
# bpy.context.preferences.addons["cycles"].preferences.compute_device_type = 'CUDA' # or "OPENCL"
cycles_preferences = bpy.context.preferences.addons["cycles"].preferences

cycles_preferences.compute_device_type = "NONE"  # or "OPENCL"
cuda_devices = cycles_preferences.get_devices_for_type("NONE")

# for i in range(len(bpy.context.preferences.addons["cycles"].preferences.devices)):
#     bpy.context.preferences.addons["cycles"].preferences.devices[i]['use']=0

# bpy.context.preferences.addons["cycles"].preferences.devices[2]['use']=1
for device in cuda_devices:
    device.use = True
# cuda_devices=[cuda_devices[6]]
# print(cuda_devices)
# assert 1==0
bpy.context.scene.cycles.tile_size = 8192
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"

# for depth & normal
context.view_layer.use_pass_normal = True
context.view_layer.use_pass_z = True
context.scene.use_nodes = True


tree = bpy.context.scene.node_tree
nodes = bpy.context.scene.node_tree.nodes
links = bpy.context.scene.node_tree.links

# Clear default nodes
for n in nodes:
    nodes.remove(n)

# # Create input render layer node.
render_layers = nodes.new('CompositorNodeRLayers')

scale_normal = nodes.new(type="CompositorNodeMixRGB")
scale_normal.blend_type = 'MULTIPLY'
scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
links.new(render_layers.outputs['Normal'], scale_normal.inputs[1])
bias_normal = nodes.new(type="CompositorNodeMixRGB")
bias_normal.blend_type = 'ADD'
bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
links.new(scale_normal.outputs[0], bias_normal.inputs[1])
normal_file_output = nodes.new(type="CompositorNodeOutputFile")
normal_file_output.label = 'Normal Output'
links.new(bias_normal.outputs[0], normal_file_output.inputs[0])

normal_file_output.format.file_format = "OPEN_EXR" # default is "PNG"
normal_file_output.format.color_mode = "RGB"  # default is "BW"


def prepare_depth_outputs():
    tree = bpy.context.scene.node_tree
    links = tree.links
    render_node = tree.nodes['Render Layers']
    depth_out_node = tree.nodes.new(type="CompositorNodeOutputFile")
    depth_map_node = tree.nodes.new(type="CompositorNodeMapRange")
    depth_out_node.base_path = ''
    depth_out_node.format.file_format = 'OPEN_EXR'
    depth_out_node.format.color_depth = '16'

    links.new(render_node.outputs[2],depth_map_node.inputs[0])
    links.new(depth_map_node.outputs[0], depth_out_node.inputs[0])

    return depth_out_node, depth_map_node

depth_file_output, depth_map_node = prepare_depth_outputs()

def add_hdri_lighting(hdri_path):

    # 添加环境贴图节点
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    node_tree = bpy.context.scene.world.node_tree
    env_node = nodes.get("Environment Texture")
    if not env_node:
        env_node = nodes.new(type='ShaderNodeTexEnvironment')
    env_node.image = bpy.data.images.load(hdri_path)
    
    # 设置环境贴图节点为背景和光源
    world.node_tree.links.new(env_node.outputs["Color"], nodes["Background"].inputs["Color"])
    world.node_tree.links.new(env_node.outputs["Color"], nodes["World Output"].inputs["Surface"])


def sample_point_on_sphere(radius: float) -> Tuple[float, float, float]:
    theta = random.random() * 2 * math.pi
    phi = math.acos(2 * random.random() - 1)
    return (
        radius * math.sin(phi) * math.cos(theta),
        radius * math.sin(phi) * math.sin(theta),
        radius * math.cos(phi),
    )

def sample_spherical(radius=3.0, maxz=3.0, minz=0.):
    correct = False
    while not correct:
        vec = np.random.uniform(-1, 1, 3)
        vec[2] = np.abs(vec[2])
        vec = vec / np.linalg.norm(vec, axis=0) * radius
        if maxz > vec[2] > minz:
            correct = True
    return vec

def sample_spherical(radius_min=1.5, radius_max=2.0, maxz=1.6, minz=-0.75):
    correct = False
    while not correct:
        vec = np.random.uniform(-1, 1, 3)
        radius = np.random.uniform(radius_min, radius_max, 1)
        vec = vec / np.linalg.norm(vec, axis=0) * radius[0]
        if maxz > vec[2] > minz:
            correct = True
    return vec



def set_camera_mvdream(azimuth, elevation, distance):
    # theta, phi = np.deg2rad(azimuth), np.deg2rad(elevation)
    azimuth, elevation = np.deg2rad(azimuth), np.deg2rad(elevation)
    point = (
        distance * math.cos(azimuth) * math.cos(elevation),
        distance * math.sin(azimuth) * math.cos(elevation),
        distance * math.sin(elevation),
    )
    print(azimuth,elevation,distance,point)
    camera = bpy.data.objects["Camera"]
    camera.location = point

    direction = -camera.location
    # print("direction",direction)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    return camera

def reset_scene() -> None:
    """Resets the scene to a clean state.

    Returns:
        None
    """
    # delete everything that isn't part of a camera or a light
    for obj in bpy.data.objects:
        if obj.type not in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    # delete all the materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True)

    # delete all the textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture, do_unlink=True)

    # delete all the images
    for image in bpy.data.images:
        bpy.data.images.remove(image, do_unlink=True)


# load the glb model
def load_object(object_path: str) -> None:
    """Loads a glb model into the scene."""
    print(object_path)
    if object_path.endswith(".glb"):
        bpy.ops.import_scene.gltf(filepath=object_path, merge_vertices=True)
    elif object_path.endswith(".fbx"):
        bpy.ops.import_scene.fbx(filepath=object_path)
    elif object_path.endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=object_path)
    elif object_path.endswith(".obj"):
        # import pdb;pdb.set_trace()
        # bpy.ops.import_scene.obj(filepath=object_path)
        bpy.ops.wm.obj_import(filepath=object_path)
    else:
        print('-'+object_path+'-')
        raise ValueError(f"Unsupported file type: {object_path}")

def get_valid_pbr(principled_bsdf):

      # 检查 Base Color, Metallic, Roughness, Normal 贴图
    texture_slots = {
        "Base Color": principled_bsdf.inputs['Base Color'],
        "Metallic": principled_bsdf.inputs['Metallic'],
        "Roughness": principled_bsdf.inputs['Roughness'],
        # "Normal": principled_bsdf.inputs['Normal']
    }


    flag = True
    

    for name, input_socket in texture_slots.items():
        if input_socket.is_linked:
            linked_node = input_socket.links[0].from_node
        
            if linked_node.type == 'TEX_IMAGE':
                    if name =='Metallic' :
                        image = linked_node.image

                        if image:
                            # 获取图像文件的名称和路径
                            image_name = image.name
                            image_path = image_name+'.png'
                            
                            # 导出图像
                            image.filepath_raw = image_path
                            image.file_format = 'PNG'  # 可以选择其他格式，如 JPG
                            image.save()

            elif linked_node.type == 'SEPARATE_COLOR':
                input_node = linked_node.inputs[0].links[0].from_node  # 获取与 Separate RGB 节点相连的输入节点
                if input_node.type == 'TEX_IMAGE':
                    image = input_node.image
                    if image:
                        # 获取图像文件的名称和路径
                        image_name = image.name
                        image_path = image_name+'.png'
                        
                        # # 导出图像
                        # image.filepath_raw = image_path
                        # image.file_format = 'PNG'  # 可以选择其他格式，如 JPG
                        # image.save()

                        # image_pil = Image.open(image_path).convert('RGB')
                        # r,g,b = image_pil.split()

                        # # 保存每个通道
                        # r.save('red_channel.png')
                        # g.save('green_channel.png')
                        # b.save('blue_channel.png')
                        
                        # print(f"Exported image: {image_name} to {image_path}")
                        pass
                        # print("使用tex iamge")
                    else:
                        flag = False
                        
                # print(f"  {name} SEPARATE_COLOR")
            elif linked_node.type == 'MATH':
                pass
                # print(f"  {name} 使用MATH")
            else:
                flag = False
        else:
            flag = False
            pass
            # print(f"  {name} Map is missing. ")
    return flag
# 检查 PBR 材质的贴图
def check_pbr_textures(principled_bsdf):
    # 检查 Base Color, Metallic, Roughness, Normal 贴图
    texture_slots = {
        "Base Color": principled_bsdf.inputs['Base Color'],
        "Metallic": principled_bsdf.inputs['Metallic'],
        "Roughness": principled_bsdf.inputs['Roughness'],
        "Normal": principled_bsdf.inputs['Normal']
    }

    

    for name, input_socket in texture_slots.items():
        if input_socket.is_linked:
            linked_node = input_socket.links[0].from_node
        
            print(f"name:{name}  use link_node type:",linked_node.type)
            if linked_node.type == 'TEX_IMAGE':
                    if name =='Metallic' :
                        image = linked_node.image

                        if image:
                            # 获取图像文件的名称和路径
                            image_name = image.name
                            image_path = image_name+'.png'
                            
                            # 导出图像
                            image.filepath_raw = image_path
                            image.file_format = 'PNG'  # 可以选择其他格式，如 JPG
                            image.save()

            elif linked_node.type == 'SEPARATE_COLOR':
                input_node = linked_node.inputs[0].links[0].from_node  
                if input_node.type == 'TEX_IMAGE':
                    image = input_node.image
                    if image:
                        image_name = image.name
                        image_path = image_name+'.png'
                        

                        pass
                        # print("使用tex iamge")
                    else:
                        print(f"No image found in Separate RGB input for material")
                        
                # print(f"  {name} SEPARATE_COLOR")
            elif linked_node.type == 'MATH':
                pass
                # print(f"  {name} 使用MATH")
            else:
                print(f"  {name} is not using an image texture.")
        else:
            pass
            # print(f"  {name} Map is missing. ")
    
def check_pbr_process_one(glb_path):
    reset_scene()
    all_flag = True
    bpy.ops.import_scene.gltf(filepath=glb_path)
    
    for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for mat_slot in obj.material_slots:
                    mat = mat_slot.material
                    if mat and mat.use_nodes:
                        nodes = mat.node_tree.nodes
                        principled_bsdf = None
                        
                        # 查找 Principled BSDF 节点
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf = node
                                break
                        
                        if principled_bsdf:
                            # print(f"Object: {obj.name} has PBR material: {mat.name}")
                            
                            # 检查 PBR 贴图
                            # check_pbr_textures(principled_bsdf)
                            flag = get_valid_pbr(principled_bsdf)
                            if flag == False:
                                all_flag = False
                                return all_flag
                            # print(f"{glb_path}",flag )
                        else:
                            pass
    return all_flag

def scene_bbox(
    single_obj: Optional[bpy.types.Object] = None, ignore_matrix: bool = False
) -> Tuple[Vector, Vector]:
    """Returns the bounding box of the scene.

    Taken from Shap-E rendering script
    (https://github.com/openai/shap-e/blob/main/shap_e/rendering/blender/blender_script.py#L68-L82)

    Args:
        single_obj (Optional[bpy.types.Object], optional): If not None, only computes
            the bounding box for the given object. Defaults to None.
        ignore_matrix (bool, optional): Whether to ignore the object's matrix. Defaults
            to False.

    Raises:
        RuntimeError: If there are no objects in the scene.

    Returns:
        Tuple[Vector, Vector]: The minimum and maximum coordinates of the bounding box.
    """
    bbox_min = (math.inf,) * 3
    bbox_max = (-math.inf,) * 3
    found = False
    for obj in get_scene_meshes() if single_obj is None else [single_obj]:
        found = True
        for coord in obj.bound_box:
            coord = Vector(coord)
            if not ignore_matrix:
                coord = obj.matrix_world @ coord
            bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
            bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))

    if not found:
        raise RuntimeError("no objects in scene to compute bounding box for")

    return Vector(bbox_min), Vector(bbox_max)


def get_scene_root_objects() -> Generator[bpy.types.Object, None, None]:
    """Returns all root objects in the scene.

    Yields:
        Generator[bpy.types.Object, None, None]: Generator of all root objects in the
            scene.
    """
    for obj in bpy.context.scene.objects.values():
        if not obj.parent:
            yield obj


def get_scene_meshes() -> Generator[bpy.types.Object, None, None]:
    """Returns all meshes in the scene.

    Yields:
        Generator[bpy.types.Object, None, None]: Generator of all meshes in the scene.
    """
    for obj in bpy.context.scene.objects.values():
        if isinstance(obj.data, (bpy.types.Mesh)):
            yield obj


# Build intrinsic camera parameters from Blender camera data
#
# See notes on this in
# blender.stackexchange.com/questions/15102/what-is-blenders-camera-projection-matrix-model
def get_calibration_matrix_K_from_blender(camd):
    f_in_mm = camd.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camd.sensor_width
    sensor_height_in_mm = camd.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    if (camd.sensor_fit == 'VERTICAL'):
        # the sensor height is fixed (sensor fit is horizontal),
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else: # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal),
        # the sensor height is effectively changed with the pixel aspect ratio
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px * scale / 2
    v_0 = resolution_y_in_px * scale / 2
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((alpha_u, skew,    u_0),
        (    0  , alpha_v, v_0),
        (    0  , 0,        1 )))
    return K


def get_calibration_matrix_K_from_blender_for_ortho(camd, ortho_scale):
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    fx = resolution_x_in_px / ortho_scale
    fy = resolution_y_in_px / ortho_scale / pixel_aspect_ratio

    cx = resolution_x_in_px / 2
    cy = resolution_y_in_px / 2

    K = Matrix(
        ((fx, 0, cx),
        (0, fy, cy),
        (0 , 0, 1)))
    return K


def get_3x4_RT_matrix_from_blender(cam):
    bpy.context.view_layer.update()
    location, rotation = cam.matrix_world.decompose()[0:2]
    R = np.asarray(rotation.to_matrix())
    t = np.asarray(location)

    cam_rec = np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, -1]], np.float32)
    R = R.T
    t = -R @ t
    R_world2cv = cam_rec @ R
    t_world2cv = cam_rec @ t

    RT = np.concatenate([R_world2cv,t_world2cv[:,None]],1)
    return RT


def normalize_scene():

    if len(list(get_scene_root_objects())) > 1:
        print('we have more than one root objects!!')
        # create an empty object to be used as a parent for all root objects
        parent_empty = bpy.data.objects.new("ParentEmpty", None)
        bpy.context.scene.collection.objects.link(parent_empty)

        # parent all root objects to the empty object
        for obj in get_scene_root_objects():
            if obj != parent_empty:
                obj.parent = parent_empty
    box_scale = 0.95
    bbox_min, bbox_max = scene_bbox()
    # print('minmax:',bbox_min,bbox_max)
    scale = box_scale / max(bbox_max - bbox_min)
    for obj in get_scene_root_objects():
        obj.scale = obj.scale * scale
    
    bpy.context.view_layer.update()
    bbox_min, bbox_max = scene_bbox()
    offset = -(bbox_min + bbox_max) / 2
    for obj in get_scene_root_objects():
        obj.matrix_world.translation += offset
    bpy.ops.object.select_all(action="DESELECT")
    bbox_min, bbox_max = scene_bbox()

    bpy.data.objects["Camera"].parent = None
    return scale, offset
def create_shadeless_material(original_material):
    # 创建一个新材质
    mat = bpy.data.materials.new(name=original_material.name + "_Shadeless")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 清除默认节点
    for node in nodes:
        nodes.remove(node)

    # 创建新的 Emission 和 Material Output 节点
    emission = nodes.new(type='ShaderNodeEmission')
    material_output = nodes.new(type='ShaderNodeOutputMaterial')

    # 连接节点
    links.new(emission.outputs['Emission'], material_output.inputs['Surface'])

    # 如果原材质使用节点，将 Base Color 复制到 Emission 节点
    if original_material.use_nodes:
        base_color = original_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
    else:
        base_color = original_material.diffuse_color

    emission.inputs['Color'].default_value = base_color
    emission.inputs['Strength'].default_value = 1.0

    return mat


# 给所有对象设置发射材质
def replace_materials_with_shadeless():
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            new_materials = []
            for original_material in obj.data.materials:
                if original_material:
                    shadeless_material = create_shadeless_material(original_material)
                    new_materials.append(shadeless_material)
                else:
                    new_materials.append(None)

            obj.data.materials.clear()
            for new_material in new_materials:
                obj.data.materials.append(new_material)


# 禁用所有灯光对象
def disable_all_lights():
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            obj.hide_viewport = True
            obj.hide_render = True


# 禁用世界背景光照
def disable_world_light():
    if bpy.context.scene.world.node_tree:
        bg = bpy.context.scene.world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Strength'].default_value = 0

def render_and_save(view_id, object_uid, len_val, azimuth, elevation, distance, ortho=False,prefix=""):
    # print(view_id)
    # render the image
    if prefix=="":
        render_path = os.path.join(args.output_dir, object_uid, 'image', f"{view_id:03d}.png")
        scene.render.filepath = render_path

        if not ortho:
            cam.data.lens = len_val

        depth_map_node.inputs[1].default_value = distance - 1
        depth_map_node.inputs[2].default_value = distance + 1
        depth_file_output.base_path = os.path.join(args.output_dir, object_uid, 'depth')

        depth_file_output.file_slots[0].path = f"{view_id:03d}"
        normal_file_output.file_slots[0].path = f"{view_id:03d}"

        # if not os.path.exists(os.path.join(args.output_dir, object_uid, 'image', f"{view_id:03d}.png")):
        bpy.ops.render.render(write_still=True)

        if os.path.exists(os.path.join(args.output_dir, object_uid, 'depth', f"{view_id:03d}0001.exr")):
            os.rename(os.path.join(args.output_dir, object_uid, 'depth', f"{view_id:03d}0001.exr"),
                      os.path.join(args.output_dir, object_uid, 'depth', f"{view_id:03d}.exr"))

        if os.path.exists(os.path.join(args.output_dir, object_uid, 'normal', f"{view_id:03d}0001.exr")):
            normal = cv2.imread(os.path.join(args.output_dir, object_uid, 'normal', f"{view_id:03d}0001.exr"), cv2.IMREAD_UNCHANGED)
            normal_unit16 = (normal * 65535).astype(np.uint16)
            cv2.imwrite(os.path.join(args.output_dir, object_uid, 'normal', f"{view_id:03d}.png"), normal_unit16)
            os.remove(os.path.join(args.output_dir, object_uid, 'normal', f"{view_id:03d}0001.exr"))

        # save camera KRT matrix
        if ortho:
            K = get_calibration_matrix_K_from_blender_for_ortho(cam.data, ortho_scale=cam.data.ortho_scale)
        else:
            K = get_calibration_matrix_K_from_blender(cam.data)

        RT = get_3x4_RT_matrix_from_blender(cam)
        para_path = os.path.join(args.output_dir, object_uid, 'camera', f"{view_id:03d}.npy")

        paras = {}
        paras['intrinsic'] = np.array(K, np.float32)
        paras['extrinsic'] = np.array(RT, np.float32)
        paras['fov'] = cam.data.angle
        paras['azimuth'] = azimuth
        paras['elevation'] = elevation
        paras['distance'] = distance
        paras['focal'] = cam.data.lens
        paras['sensor_width'] = cam.data.sensor_width
        paras['near'] = distance - 1
        paras['far'] = distance + 1
        paras['camera'] = 'persp' if not ortho else 'ortho'
        np.save(para_path, paras)
    else:
        render_path = os.path.join(args.output_dir, object_uid, prefix, f"{view_id:03d}.png")
        scene.render.filepath = render_path

        if not ortho:
            cam.data.lens = len_val

        if not os.path.exists(os.path.join(args.output_dir, object_uid, prefix, f"{view_id:03d}.png")):
            bpy.ops.render.render(write_still=True)

def scene_meshes():
    for obj in bpy.context.scene.objects.values():
        if isinstance(obj.data, (bpy.types.Mesh)):
            yield obj

def save_images(object_file,prefix="",fixed_random_list=None):
    """Saves rendered images of the object in the scene."""
    object_uid = os.path.basename(object_file).split(".")[0]

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, object_uid, 'camera'), exist_ok=True)
    if prefix!="":
        os.makedirs(os.path.join(args.output_dir, object_uid, prefix), exist_ok=True)
    reset_scene()
    load_object(object_file)

    lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
    for light in lights:
        bpy.data.objects.remove(light, do_unlink=True)

    add_hdri_lighting('./scripts/overcast_soil_puresky_4k.exr')
    
    scale, offset = normalize_scene()

    # np.save(os.path.join(args.output_dir, object_uid, 'meta.npy'), np.asarray([scale, offset[0], offset[1], offset[1]],np.float32))
    CONTINUE_FLAG=True
    for obj in get_scene_meshes():
        obj.select_set(True)

        bpy.ops.wm.obj_export(
            filepath=os.path.join(args.output_dir, object_uid, 'blender.obj'), )
            # use_selection=True, 
            # use_materials=True)
        object_name = bpy.context.selected_objects[0].name

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)

        bpy.context.view_layer.objects.active = obj  # 设置为活动对象
        bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式

        # 合并多余顶点（按距离合并）
        bpy.ops.mesh.remove_doubles(threshold=0.0001)  # 可修改 threshold 来调整合并距离
        



        bpy.ops.wm.obj_export(filepath=os.path.join(args.output_dir, object_uid, object_uid+'.obj'))

            # use_materials=True)
        print("OBJ Path:",os.path.join(args.output_dir, object_uid, object_uid+'.obj'))

        # 只导出一个mesh
        break
   

    empty = bpy.data.objects.new("Empty", None)
    scene.collection.objects.link(empty)
    cam_constraint.target = empty

    subject_width = 1.0
    # lens = [35, 50, 85, 105, 135]

    normal_file_output.base_path = os.path.join(args.output_dir, object_uid, 'normal')
    random_list=[]


    azimuth_list = []






    azimuth_list = [0,90,180,270,0,0] # 前6个是混元，中间6个是朝旭zero123 ，后3个是正交前后左右以及俯视，类似triposr
    elevation_list = [0,0,0,0,-90,90]


    for i in range(len(azimuth_list)):
    # change the camera to orthogonal
    
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = subject_width
        distance = 3

        # azimuth=azimuth_list[i]-90
        azimuth = azimuth_list[i] + args.geo_rotation
        elevation=elevation_list[i]
        bpy.context.view_layer.update()
        print(i)
        set_camera_mvdream(azimuth, elevation, distance)
        render_and_save(i * (args.random_images+1), object_uid, -1, azimuth, elevation, distance, ortho=True,prefix=prefix)


    return os.path.join(args.output_dir, object_uid), False

if __name__ == "__main__":
    # try:
        start_i = time.time()
        local_path = args.object_path


        a = save_images(local_path)

  
