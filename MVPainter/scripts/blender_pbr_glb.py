import bpy
import os
import argparse
import sys
import cv2
# from PIL import Image
import warnings
import numpy as np
import shutil
from glob import glob
parser = argparse.ArgumentParser()

parser.add_argument("--basecolor_dir", type=str, default="CUDA")
parser.add_argument("--metallic_dir", type=str, default="CUDA")
parser.add_argument("--roughness_dir", type=str, default="CUDA")
parser.add_argument("--output_dir", type=str, default="CUDA")


argv = sys.argv[sys.argv.index("--") + 1 :]
args = parser.parse_args(argv)


basecolor_dir = args.basecolor_dir
metallic_dir = args.metallic_dir
roughness_dir = args.roughness_dir
output_dir = args.output_dir
os.makedirs(output_dir,exist_ok=True)
obj_paths = glob(os.path.join(basecolor_dir,'*.obj'))
for obj_path in obj_paths:
    print(obj_path)
    basename = os.path.basename(obj_path).replace('.obj','')

    obj_file_path = obj_path
    roughness_texture_path = os.path.join(roughness_dir,basename+'.png')
    metallic_texture_path = os.path.join(metallic_dir,basename+'.png')

    glb_export_path = os.path.join(output_dir,basename+'.glb') 

    bpy.ops.wm.read_factory_settings(use_empty=True)

    # import OBJ 
    bpy.ops.wm.obj_import(filepath=obj_file_path)
    imported_object = bpy.context.selected_objects[0]  #象


    material=imported_object.data.materials[0]

    # node tree
    nodes = material.node_tree.nodes
    links = material.node_tree.links


    # create metallic node
    metallic_node = nodes.new(type='ShaderNodeTexImage')
    metallic_node.image = bpy.data.images.load(metallic_texture_path)
    metallic_node.image.colorspace_settings.name = 'sRGB'

    # create roughness node
    roughness_node = nodes.new(type='ShaderNodeTexImage')
    roughness_node.image = bpy.data.images.load(roughness_texture_path)
    roughness_node.image.colorspace_settings.name = 'sRGB'

    math_node = nodes.new(type="ShaderNodeMath")
    math_node.operation = 'MULTIPLY'
    math_node.inputs[1].default_value = 1


    principled_node =nodes["Principled BSDF"]
    links.new(metallic_node.outputs["Color"], principled_node.inputs["Metallic"])    
    links.new(roughness_node.outputs["Color"], math_node.inputs[0])   
    links.new(math_node.outputs[0], principled_node.inputs["Roughness"]) 
 
    nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value= 1.3
    
    # export glb
    bpy.ops.export_scene.gltf(
        filepath=glb_export_path,
        export_format='GLB',
        use_selection=False,
        export_image_format='JPEG',  
        # export_vertex_color=False
    )
    print("Textured PBR glb is exported to: ",glb_export_path)






